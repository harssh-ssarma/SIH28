// src/components/shared/DataTable.tsx
// Google Contacts-style data table: hover checkboxes, bulk selection, bulk delete,
// action icons on hover, skeleton loading, empty state, right-aligned pagination.
// Toolbar: Print · Export · ⋮ (Display density, Change column order)
'use client'

import { useState, useCallback, useRef, useEffect } from 'react'
import {
  ChevronLeft, ChevronRight, ChevronDown,
  Pencil, Trash2, Printer, Upload, MoreVertical, Check,
} from 'lucide-react'
import ConfirmDeleteDialog from './ConfirmDeleteDialog'
import Avatar from './Avatar'
import { DensityDialog, ColumnOrderDialog } from './DataTableDialogs'
import { SkeletonRows, EmptyState, DataTableMobileList } from './DataTableHelpers'

/* ─── Types ─────────────────────────────────────────────────────────────────── */
export type Density = 'comfortable' | 'compact'

export interface Column<T = Record<string, unknown>> {
  key: string
  header: string
  width?: string
  render?: (value: unknown, row: T) => React.ReactNode
}

export interface EmptyStateConfig {
  icon: React.ElementType
  title: string
  description?: string
  action?: { label: string; onClick: () => void }
}

export interface DataTableProps<T extends Record<string, unknown>> {
  columns: Column<T>[]
  data: T[]
  loading?: boolean
  totalCount?: number
  page?: number
  pageSize?: number
  onPageChange?: (page: number) => void
  selectable?: boolean
  onDelete?: (ids: string[]) => Promise<void>
  onEdit?: (row: T) => void
  emptyState?: EmptyStateConfig
  idField?: string
  onPrint?: () => void
  onExport?: () => void
  avatarColumn?: (row: T) => string | null
  onRowClick?: (row: T) => void
}

/* ─── Avatar ↔ Checkbox flip (Google Contacts pattern) ─────────────────────── */
function AvatarOrCheckbox({
  hasAvatar, name, selected, onToggle,
}: {
  hasAvatar: boolean; name: string; selected: boolean; onToggle: () => void
}) {
  if (!hasAvatar) {
    return (
      <input
        type="checkbox"
        checked={selected}
        onChange={onToggle}
        className="w-4 h-4 rounded cursor-pointer opacity-0 group-hover:opacity-100 transition-opacity duration-75"
        style={{ accentColor: 'var(--checkbox-color)', opacity: selected ? 1 : undefined }}
        aria-label="Select row"
      />
    )
  }
  return (
    <div className="relative w-8 h-8 shrink-0 cursor-pointer" onClick={onToggle}>
      <span className={`absolute inset-0 rounded-full transition-opacity duration-100 ${selected ? 'opacity-0' : 'opacity-100 group-hover:opacity-0'}`} aria-hidden="true">
        <Avatar name={name} size="sm" />
      </span>
      <span className={`absolute inset-0 flex items-center justify-center rounded-full transition-opacity duration-100 ${selected ? 'opacity-100' : 'opacity-0 group-hover:opacity-100'}`} style={{ background: selected ? 'var(--checkbox-color)' : 'rgba(0,0,0,0.08)' }}>
        {selected
          ? <Check size={14} strokeWidth={3} color="#fff" />
          : <span className="w-4 h-4 rounded border-2" style={{ borderColor: 'var(--color-text-secondary)', background: 'transparent' }} />}
      </span>
    </div>
  )
}

/* ─── DataTable ──────────────────────────────────────────────────────────────── */
export default function DataTable<T extends Record<string, unknown>>({
  columns,
  data,
  loading = false,
  totalCount = 0,
  page = 1,
  pageSize = 20,
  onPageChange,
  selectable = false,
  onDelete,
  onEdit,
  emptyState,
  idField = 'id',
  onPrint,
  onExport,
  avatarColumn,
  onRowClick,
}: DataTableProps<T>) {
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set())
  const [confirmOpen, setConfirmOpen] = useState(false)
  const [deleting, setDeleting] = useState(false)
  const [density, setDensity] = useState<Density>('comfortable')
  const [displayColumns, setDisplayColumns] = useState<Column<T>[]>(columns)
  const [toolMenuOpen, setToolMenuOpen] = useState(false)
  const [densityOpen, setDensityOpen] = useState(false)
  const [colOrderOpen, setColOrderOpen] = useState(false)
  const [selectMenuOpen, setSelectMenuOpen] = useState(false)
  const [rowMenuId, setRowMenuId] = useState<string | null>(null)
  const toolMenuRef = useRef<HTMLDivElement>(null)
  const selectMenuRef = useRef<HTMLDivElement>(null)
  const rowMenuRef = useRef<HTMLDivElement>(null)

  useEffect(() => { setDisplayColumns(columns) }, [columns]) // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    if (!toolMenuOpen) return
    const h = (e: MouseEvent) => { if (toolMenuRef.current && !toolMenuRef.current.contains(e.target as Node)) setToolMenuOpen(false) }
    document.addEventListener('mousedown', h); return () => document.removeEventListener('mousedown', h)
  }, [toolMenuOpen])

  useEffect(() => {
    if (!selectMenuOpen) return
    const h = (e: MouseEvent) => { if (selectMenuRef.current && !selectMenuRef.current.contains(e.target as Node)) setSelectMenuOpen(false) }
    document.addEventListener('mousedown', h); return () => document.removeEventListener('mousedown', h)
  }, [selectMenuOpen])

  useEffect(() => {
    if (!rowMenuId) return
    const h = (e: MouseEvent) => { if (rowMenuRef.current && !rowMenuRef.current.contains(e.target as Node)) setRowMenuId(null) }
    document.addEventListener('mousedown', h); return () => document.removeEventListener('mousedown', h)
  }, [rowMenuId])

  const rowH = density === 'compact' ? '36px' : 'var(--row-height)'
  const headerH = density === 'compact' ? '40px' : 'var(--row-header-height)'
  const getId = (row: T) => String(row[idField])

  const toggleAll = useCallback(() => {
    if (selectedIds.size === data.length) setSelectedIds(new Set())
    else setSelectedIds(new Set(data.map(r => String(r[idField]))))
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [data, selectedIds.size, idField])

  const toggleRow = useCallback((id: string) => {
    setSelectedIds(prev => { const n = new Set(prev); if (n.has(id)) n.delete(id); else n.add(id); return n })
  }, [])

  const handleDeleteConfirm = async () => {
    if (!onDelete) return
    setDeleting(true)
    try { await onDelete(Array.from(selectedIds)); setSelectedIds(new Set()) }
    finally { setDeleting(false); setConfirmOpen(false) }
  }

  const exportSingleRow = (row: T) => {
    const h = displayColumns.map(c => c.header).join(',')
    const v = displayColumns.map(col => { const s = col.render ? '' : String(row[col.key] ?? ''); return s.includes(',') ? `"${s}"` : s }).join(',')
    const blob = new Blob([[h, v].join('\n')], { type: 'text/csv' })
    const url = URL.createObjectURL(blob); const a = document.createElement('a')
    a.href = url; a.download = 'row-export.csv'; a.click(); URL.revokeObjectURL(url)
  }

  const handlePrint = () => { if (onPrint) { onPrint(); return }; window.print() }

  const handleExport = () => {
    if (onExport) { onExport(); return }
    const h = displayColumns.map(c => c.header).join(',')
    const rows = data.map(row => displayColumns.map(col => { const s = String(row[col.key] ?? ''); return s.includes(',') ? `"${s}"` : s }).join(','))
    const blob = new Blob([[h, ...rows].join('\n')], { type: 'text/csv' })
    const url = URL.createObjectURL(blob); const a = document.createElement('a')
    a.href = url; a.download = 'export.csv'; a.click(); URL.revokeObjectURL(url)
  }

  const totalPages = Math.ceil(totalCount / pageSize)
  const pageStart  = Math.min((page - 1) * pageSize + 1, totalCount)
  const pageEnd    = Math.min(page * pageSize, totalCount)
  const showPagination = totalCount > pageSize
  const allSelected = data.length > 0 && selectedIds.size === data.length
  const someSelected = selectedIds.size > 0 && selectedIds.size < data.length
  const totalCols = (selectable ? 1 : 0) + displayColumns.length + ((onEdit || onDelete) ? 1 : 0)
  const selectionActive = selectable && selectedIds.size > 0

  const menuStyle = { minWidth: '148px', borderRadius: '8px', background: 'var(--color-bg-surface)', boxShadow: '0 4px 16px rgba(0,0,0,0.18)', border: '1px solid var(--color-border)', marginTop: '6px' }

  return (
    <div className="flex flex-col">

      {/* ══ Desktop table ════════════════════════════════════════════════════ */}
      <div className="hidden md:block overflow-x-auto">
        <div className="relative">
        <table className="w-full" style={{ borderCollapse: 'separate', borderSpacing: '0' }}>
          <thead>
            <tr style={{ height: headerH }}>
              {selectable && (
                <th className="pl-3 pr-1 w-12 text-left" style={{ borderBottom: '1px solid rgba(0,0,0,0.08)' }}>
                  <div style={{ width: '36px' }} />
                </th>
              )}
              {displayColumns.map(col => (
                <th key={col.key} className="px-3 text-left font-normal" style={{ fontSize: 'var(--col-header-size)', color: 'var(--col-header-color)', width: col.width, borderBottom: '1px solid rgba(0,0,0,0.08)' }}>{col.header}</th>
              ))}
              <th className="pr-2 text-right font-normal" style={{ width: '120px', borderBottom: '1px solid rgba(0,0,0,0.08)' }}>
                <span className="inline-flex items-center justify-end gap-0">
                  {[{ fn: handlePrint, t: 'Print', I: Printer }, { fn: handleExport, t: 'Export CSV', I: Upload }].map(({ fn, t, I }) => (
                    <button key={t} onClick={fn} title={t} className="p-1.5 rounded-full transition-colors" style={{ color: 'var(--col-header-color)' }} onMouseEnter={e => (e.currentTarget.style.background = 'rgba(0,0,0,0.06)')} onMouseLeave={e => (e.currentTarget.style.background = 'transparent')}><I size={16} /></button>
                  ))}
                  <div className="relative" ref={toolMenuRef}>
                    <button onClick={() => setToolMenuOpen(v => !v)} title="More options" className="p-1.5 rounded-full transition-colors" style={{ color: 'var(--col-header-color)', background: toolMenuOpen ? 'rgba(0,0,0,0.06)' : 'transparent' }} onMouseEnter={e => { if (!toolMenuOpen) e.currentTarget.style.background = 'rgba(0,0,0,0.06)' }} onMouseLeave={e => { if (!toolMenuOpen) e.currentTarget.style.background = 'transparent' }}><MoreVertical size={16} /></button>
                    {toolMenuOpen && !selectionActive && (
                      <div className="absolute right-0 top-full z-50 py-2" style={{ minWidth: '200px', borderRadius: '12px', background: 'var(--color-bg-surface)', boxShadow: '0 4px 20px rgba(0,0,0,0.16)', border: '1px solid var(--color-border)', marginTop: '4px' }}>
                        <button onClick={() => { setToolMenuOpen(false); setDensityOpen(true) }}  className="w-full flex items-center px-4 py-2.5 text-sm text-left transition-colors hover:bg-[var(--color-bg-surface-2)]" style={{ color: 'var(--color-text-primary)' }}>Display density</button>
                        <button onClick={() => { setToolMenuOpen(false); setColOrderOpen(true) }} className="w-full flex items-center px-4 py-2.5 text-sm text-left transition-colors hover:bg-[var(--color-bg-surface-2)]" style={{ color: 'var(--color-text-primary)' }}>Change column order</button>
                      </div>
                    )}
                  </div>
                </span>
              </th>
            </tr>
          </thead>

          <tbody>
            {loading ? (
              <SkeletonRows cols={displayColumns.length} hasAvatar={!!avatarColumn} />
            ) : data.length === 0 ? (
              emptyState ? <EmptyState config={emptyState} /> : null
            ) : (
              data.map(row => {
                const id = getId(row)
                const selected = selectedIds.has(id)
                return (
                  <tr key={id} className={`group transition-colors duration-75${onRowClick ? ' cursor-pointer' : ' cursor-default'}`} style={{ height: rowH, backgroundColor: selected ? 'var(--row-selected-bg)' : 'var(--color-bg-surface)' }} onClick={onRowClick ? () => onRowClick(row) : undefined} onMouseEnter={e => { if (!selected) (e.currentTarget as HTMLTableRowElement).style.backgroundColor = 'var(--row-hover-bg)' }} onMouseLeave={e => { if (!selected) (e.currentTarget as HTMLTableRowElement).style.backgroundColor = 'var(--color-bg-surface)' }}>
                    {selectable && (
                      <td className="pl-3 pr-2 w-12" onClick={e => e.stopPropagation()} style={{ borderTopLeftRadius: '8px', borderBottomLeftRadius: '8px', borderTop: '3px solid var(--color-bg-surface)', borderBottom: '3px solid var(--color-bg-surface)' }}>
                        <AvatarOrCheckbox hasAvatar={!!avatarColumn} name={avatarColumn ? (avatarColumn(row) ?? '') : ''} selected={selected} onToggle={() => toggleRow(id)} />
                      </td>
                    )}
                    {displayColumns.map(col => (
                      <td key={col.key} className="px-3" style={{ fontSize: '14px', color: 'var(--color-text-primary)', width: col.width, borderTop: '3px solid var(--color-bg-surface)', borderBottom: '3px solid var(--color-bg-surface)' }}>
                        {col.render ? col.render(row[col.key], row) : String(row[col.key] ?? '')}
                      </td>
                    ))}
                    {(onEdit || onDelete) && (
                      <td className="pr-2 text-right" style={{ width: '48px', borderTopRightRadius: '8px', borderBottomRightRadius: '8px', borderTop: '3px solid var(--color-bg-surface)', borderBottom: '3px solid var(--color-bg-surface)' }} onClick={e => e.stopPropagation()}>
                        <div className="relative inline-flex" ref={rowMenuId === id ? rowMenuRef : undefined}>
                          <button onClick={() => setRowMenuId(prev => prev === id ? null : id)} className="p-1.5 rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-75 hover:bg-[var(--color-bg-surface-2)]" style={{ color: 'var(--color-text-secondary)', opacity: rowMenuId === id ? 1 : undefined }} title="More actions"><MoreVertical size={16} /></button>
                          {rowMenuId === id && (
                            <div className="absolute right-0 top-full z-50 py-1" style={{ minWidth: '148px', borderRadius: '12px', background: 'var(--color-bg-surface)', boxShadow: '0 4px 20px rgba(0,0,0,0.16)', border: '1px solid var(--color-border)', marginTop: '4px' }}>
                              {onEdit && <button onClick={() => { onEdit(row); setRowMenuId(null) }} className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-left transition-colors hover:bg-[var(--color-bg-surface-2)]" style={{ color: 'var(--color-text-primary)' }}><Pencil size={15} style={{ color: 'var(--color-text-secondary)' }} />Edit</button>}
                              <button onClick={() => { exportSingleRow(row); setRowMenuId(null) }} className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-left transition-colors hover:bg-[var(--color-bg-surface-2)]" style={{ color: 'var(--color-text-primary)' }}><Upload size={15} style={{ color: 'var(--color-text-secondary)' }} />Export row</button>
                              {onDelete && <><div style={{ height: '1px', background: 'var(--color-border)', margin: '4px 0' }} /><button onClick={() => { setSelectedIds(new Set([id])); setConfirmOpen(true); setRowMenuId(null) }} className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-left transition-colors hover:bg-[var(--color-bg-surface-2)]" style={{ color: 'var(--color-danger)' }}><Trash2 size={15} />Delete</button></>}
                            </div>
                          )}
                        </div>
                      </td>
                    )}
                  </tr>
                )
              })
            )}
          </tbody>
        </table>

        {/* ── Selection overlay: sits on top of header, zero layout impact ── */}
        {selectionActive && (
          <div style={{ position: 'absolute', top: 0, left: 0, right: 0, height: headerH, display: 'flex', alignItems: 'center', justifyContent: 'space-between', background: 'var(--color-bg-surface)', borderBottom: '1px solid rgba(0,0,0,0.08)', zIndex: 10 }}>
            {/* Left: checkbox + count */}
            <div className="flex items-center gap-1 pl-3">
              <div className="relative flex items-center" ref={selectMenuRef}>
                <span className="flex items-center justify-center w-5 h-5 cursor-pointer shrink-0" style={{ background: 'var(--checkbox-color)', border: '2px solid var(--checkbox-color)', borderRadius: '4px' }} onClick={() => setSelectedIds(new Set())} title="Clear selection">
                  {allSelected ? <Check size={13} strokeWidth={3} color="#fff" /> : <span className="block w-2.5 h-0.5 rounded-full" style={{ background: '#fff' }} />}
                </span>
                <button onClick={() => setSelectMenuOpen(v => !v)} className="ml-0.5 p-0.5 rounded-full transition-colors" style={{ color: 'var(--color-primary)' }} onMouseEnter={e => (e.currentTarget.style.background = 'var(--color-primary-subtle)')} onMouseLeave={e => (e.currentTarget.style.background = 'transparent')} title="Selection options"><ChevronDown size={12} strokeWidth={2.5} /></button>
                {selectMenuOpen && (
                  <div className="absolute left-0 top-full z-50 py-1" style={menuStyle}>
                    <button className="w-full flex items-center px-4 py-2 text-sm text-left transition-colors hover:bg-[var(--color-bg-surface-2)]" style={{ color: 'var(--color-text-primary)' }} onClick={() => { setSelectedIds(new Set(data.map(r => String(r[idField])))); setSelectMenuOpen(false) }}>All</button>
                    <button className="w-full flex items-center px-4 py-2 text-sm text-left transition-colors hover:bg-[var(--color-bg-surface-2)]" style={{ color: 'var(--color-text-primary)' }} onClick={() => { setSelectedIds(new Set()); setSelectMenuOpen(false) }}>None</button>
                  </div>
                )}
              </div>
              <span className="font-medium text-sm ml-1" style={{ color: 'var(--color-primary)' }}>{selectedIds.size} selected</span>
            </div>
            {/* Right: ⋮ menu with Print / Export / Delete */}
            <div className="pr-2" ref={toolMenuRef}>
              <div className="relative">
                <button onClick={() => setToolMenuOpen(v => !v)} title="More options" className="p-1.5 rounded-full transition-colors" style={{ color: 'var(--color-primary)', background: toolMenuOpen ? 'var(--color-primary-subtle)' : 'transparent' }} onMouseEnter={e => (e.currentTarget.style.background = 'var(--color-primary-subtle)')} onMouseLeave={e => { if (!toolMenuOpen) e.currentTarget.style.background = 'transparent' }}><MoreVertical size={18} /></button>
                {toolMenuOpen && (
                  <div className="absolute right-0 top-full z-50 py-2" style={{ minWidth: '200px', borderRadius: '12px', background: 'var(--color-bg-surface)', boxShadow: '0 4px 20px rgba(0,0,0,0.16)', border: '1px solid var(--color-border)', marginTop: '4px' }}>
                    <button onClick={() => { setToolMenuOpen(false); handlePrint() }}  className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-left transition-colors hover:bg-[var(--color-bg-surface-2)]" style={{ color: 'var(--color-text-primary)' }}><Printer size={16} style={{ color: 'var(--color-text-secondary)' }} />Print</button>
                    <button onClick={() => { setToolMenuOpen(false); handleExport() }} className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-left transition-colors hover:bg-[var(--color-bg-surface-2)]" style={{ color: 'var(--color-text-primary)' }}><Upload  size={16} style={{ color: 'var(--color-text-secondary)' }} />Export</button>
                    {onDelete && <><div style={{ height: '1px', background: 'var(--color-border)', margin: '4px 0' }} /><button onClick={() => { setToolMenuOpen(false); setConfirmOpen(true) }} className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-left transition-colors hover:bg-[var(--color-bg-surface-2)]" style={{ color: 'var(--color-text-primary)' }}><Trash2 size={16} style={{ color: 'var(--color-text-secondary)' }} />Delete</button></>}
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
        </div>

        {showPagination && !loading && (
          <div className="flex items-center justify-end gap-1 px-4" style={{ height: '52px', borderTop: '1px solid var(--color-border)', fontSize: '13px', color: 'var(--color-text-secondary)' }}>
            <span className="mr-2">{pageStart}{'–'}{pageEnd} of {totalCount}</span>
            <button onClick={() => onPageChange?.(page - 1)} disabled={page <= 1} className="p-1 rounded-full hover:bg-[var(--row-hover-bg)] disabled:opacity-30 disabled:cursor-not-allowed" aria-label="Previous page"><ChevronLeft size={18} /></button>
            <button onClick={() => onPageChange?.(page + 1)} disabled={page >= totalPages} className="p-1 rounded-full hover:bg-[var(--row-hover-bg)] disabled:opacity-30 disabled:cursor-not-allowed" aria-label="Next page"><ChevronRight size={18} /></button>
          </div>
        )}
      </div>

      {/* ══ Mobile card list ════════════════════════════════════════════════ */}
      <DataTableMobileList
        loading={loading}
        data={data}
        displayColumns={displayColumns}
        emptyState={emptyState}
        avatarColumn={avatarColumn}
        idField={idField}
        onRowClick={onRowClick}
        showPagination={showPagination && !loading}
        page={page}
        totalPages={totalPages}
        pageStart={pageStart}
        pageEnd={pageEnd}
        totalCount={totalCount}
        onPageChange={onPageChange}
      />

      <ConfirmDeleteDialog open={confirmOpen} onClose={() => { setConfirmOpen(false); if (selectedIds.size === 1) setSelectedIds(new Set()) }} onConfirm={handleDeleteConfirm} count={selectedIds.size} loading={deleting} />
      <DensityDialog open={densityOpen} density={density} onDensityChange={setDensity} onClose={() => setDensityOpen(false)} />
      <ColumnOrderDialog open={colOrderOpen} columns={displayColumns} onColumnsChange={setDisplayColumns} originalColumns={columns} onClose={() => setColOrderOpen(false)} />
    </div>
  )
}
