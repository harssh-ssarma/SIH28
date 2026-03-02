// src/components/shared/DataTable.tsx
// Google Contacts-style table: hover checkboxes, bulk selection, bulk delete,
// action icons on hover, skeleton loading, empty state, right-aligned pagination.
// Toolbar: Print · Export · ⋮ (Display density, Change column order)
'use client'

import { useState, useCallback, useRef, useEffect } from 'react'
import {
  ChevronLeft, ChevronRight, ChevronDown, Pencil, Trash2, X,
  Printer, Upload, MoreVertical, GripVertical, Check,
} from 'lucide-react'
import ConfirmDeleteDialog from './ConfirmDeleteDialog'
import Avatar from './Avatar'

/* ─── Types ────────────────────────────────────────────────────────────────── */
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
  /** Called when the Print button is clicked; defaults to window.print() */
  onPrint?: () => void
  /** Called when the Export button is clicked; defaults to CSV export */
  onExport?: () => void
  /**
   * When provided, the first column shows a seeded Avatar of the given name.
   * On hover the avatar flips to a checkbox (Google Contacts behaviour).
   * Pass a function: row => nameString (or null to skip for that row).
   */
  avatarColumn?: (row: T) => string | null
  /** Called when the user clicks a data row (not the avatar/checkbox or action buttons) */
  onRowClick?: (row: T) => void
}

/* ─── Skeleton ──────────────────────────────────────────────────────────────── */
function SkeletonRows({ cols, hasAvatar }: { cols: number; hasAvatar: boolean }) {
  return (
    <>
      {Array.from({ length: 8 }).map((_, i) => (
        <tr key={i} style={{ height: 'var(--row-height)' }}>
          <td className="pl-3 pr-2 w-12">
            {hasAvatar
              ? <span className="loading-skeleton block w-8 h-8 rounded-full" />
              : <span className="loading-skeleton block w-4 h-4 rounded" />}
          </td>
          {Array.from({ length: cols }).map((_, j) => (
            <td key={j} className="px-3">
              <span
                className="loading-skeleton block h-4 rounded"
                style={{ width: `${55 + ((i * 3 + j * 7) % 35)}%` }}
              />
            </td>
          ))}
          <td className="pr-3 w-20" />
        </tr>
      ))}
    </>
  )
}

/* ─── Empty State ───────────────────────────────────────────────────────────── */
function EmptyState({ config }: { config: EmptyStateConfig }) {
  const Icon = config.icon
  return (
    <tr>
      <td colSpan={99}>
        <div
          className="flex flex-col items-center gap-3 py-16"
          style={{ color: 'var(--color-text-secondary)' }}
        >
          <Icon size={40} strokeWidth={1.5} />
          <p className="font-medium" style={{ fontSize: '15px', color: 'var(--color-text-primary)' }}>
            {config.title}
          </p>
          {config.description && (
            <p style={{ fontSize: '13px' }}>{config.description}</p>
          )}
          {config.action && (
            <button className="btn-primary mt-1" onClick={config.action.onClick}>
              {config.action.label}
            </button>
          )}
        </div>
      </td>
    </tr>
  )
}

/* ─── Bulk Toolbar ──────────────────────────────────────────────────────────── */
function BulkToolbar({
  count,
  onDelete,
  onClear,
}: {
  count: number
  onDelete: () => void
  onClear: () => void
}) {
  return (
    <div className="bulk-toolbar px-4 flex items-center gap-3">
      <span
        className="font-medium"
        style={{ fontSize: '14px', color: 'var(--bulk-selected-text)' }}
      >
        {count} selected
      </span>
      <button
        onClick={onDelete}
        className="flex items-center gap-1.5 btn-ghost"
        style={{ fontSize: '13px', color: 'var(--color-danger)' }}
        title="Delete selected"
      >
        <Trash2 size={15} />
        Delete
      </button>
      <button
        onClick={onClear}
        className="ml-auto btn-ghost p-1.5"
        title="Clear selection"
        style={{ color: 'var(--color-text-secondary)' }}
      >
        <X size={16} />
      </button>
    </div>
  )
}

/* ─── Display Density Dialog ────────────────────────────────────────────────── */
function DensityDialog({
  open,
  density,
  onDensityChange,
  onClose,
}: {
  open: boolean
  density: Density
  onDensityChange: (d: Density) => void
  onClose: () => void
}) {
  if (!open) return null
  const rowH = density === 'compact' ? 36 : 52
  return (
    <div
      className="fixed inset-0 z-[100] flex items-center justify-center"
      style={{ background: 'rgba(0,0,0,0.32)' }}
      onClick={onClose}
    >
      <div
        className="bg-white dark:bg-[#292a2d] overflow-hidden"
        style={{ borderRadius: '28px', width: '400px', boxShadow: '0 8px 30px rgba(0,0,0,0.24)' }}
        onClick={e => e.stopPropagation()}
      >
        <div className="px-6 pt-6 pb-4">
          <h2 style={{ fontSize: '22px', fontWeight: 400, color: '#1f1f1f' }}>Display density</h2>
        </div>
        {/* Preview */}
        <div className="mx-6 mb-5 overflow-hidden" style={{ borderRadius: '12px', border: '1px solid rgba(0,0,0,0.08)', background: '#f8f9fe' }}>
          {[1, 2, 3, 4, 5].map(i => (
            <div
              key={i}
              className="flex items-center gap-3 px-4"
              style={{ height: `${rowH}px`, borderBottom: i < 5 ? '1px solid rgba(0,0,0,0.06)' : 'none', transition: 'height 0.15s ease' }}
            >
              <div className="shrink-0 rounded-full bg-[#d0d7e3]" style={{ width: 28, height: 28 }} />
              <div className="flex-1 flex gap-4">
                {[55 + i * 8, 30 + i * 4, 20 + i * 3].map((w, j) => (
                  <div key={j} className="rounded-full bg-[#d0d7e3]" style={{ height: 10, width: `${w}%` }} />
                ))}
              </div>
            </div>
          ))}
        </div>
        {/* Comfortable / Compact toggle */}
        <div className="flex justify-center mx-6 mb-6">
          <button
            onClick={() => onDensityChange('comfortable')}
            className="flex items-center gap-1.5 px-5 py-2 text-sm transition-colors"
            style={{
              borderRadius: '20px 0 0 20px',
              border: '1px solid #d0d4da',
              background: density === 'comfortable' ? '#c2e7ff' : 'transparent',
              color: '#1f1f1f',
              fontWeight: density === 'comfortable' ? 500 : 400,
            }}
          >
            {density === 'comfortable' && <Check size={14} />}
            Comfortable
          </button>
          <button
            onClick={() => onDensityChange('compact')}
            className="flex items-center gap-1.5 px-5 py-2 text-sm transition-colors"
            style={{
              borderRadius: '0 20px 20px 0',
              border: '1px solid #d0d4da',
              borderLeft: 'none',
              background: density === 'compact' ? '#c2e7ff' : 'transparent',
              color: '#1f1f1f',
              fontWeight: density === 'compact' ? 500 : 400,
            }}
          >
            {density === 'compact' && <Check size={14} />}
            Compact
          </button>
        </div>
        <div className="flex justify-end px-6 pb-5">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg text-sm font-medium transition-colors hover:bg-[#e8f0fe]"
            style={{ color: '#1967d2' }}
          >
            Done
          </button>
        </div>
      </div>
    </div>
  )
}

/* ─── Column Order Dialog ────────────────────────────────────────────────────── */
function ColumnOrderDialog<T extends Record<string, unknown>>({
  open,
  columns,
  onColumnsChange,
  originalColumns,
  onClose,
}: {
  open: boolean
  columns: Column<T>[]
  onColumnsChange: (cols: Column<T>[]) => void
  originalColumns: Column<T>[]
  onClose: () => void
}) {
  const [localCols, setLocalCols] = useState<Column<T>[]>([])
  const dragIdx = useRef<number | null>(null)

  useEffect(() => { if (open) setLocalCols([...columns]) }, [open]) // eslint-disable-line react-hooks/exhaustive-deps

  if (!open) return null

  const handleDragStart = (idx: number) => { dragIdx.current = idx }
  const handleDragOver = (e: React.DragEvent, idx: number) => {
    e.preventDefault()
    if (dragIdx.current === null || dragIdx.current === idx) return
    const next = [...localCols]
    const [moved] = next.splice(dragIdx.current, 1)
    next.splice(idx, 0, moved)
    dragIdx.current = idx
    setLocalCols(next)
  }

  return (
    <div
      className="fixed inset-0 z-[100] flex items-center justify-center"
      style={{ background: 'rgba(0,0,0,0.32)' }}
      onClick={onClose}
    >
      <div
        className="bg-white dark:bg-[#292a2d]"
        style={{ borderRadius: '28px', width: '440px', boxShadow: '0 8px 30px rgba(0,0,0,0.24)' }}
        onClick={e => e.stopPropagation()}
      >
        <div className="px-6 pt-6 pb-2">
          <h2 style={{ fontSize: '22px', fontWeight: 400, color: '#1f1f1f' }}>Change column order</h2>
          <p style={{ fontSize: '13px', color: '#5f6368', marginTop: '6px', lineHeight: 1.5 }}>
            Drag to reorder columns. Small screens may not display all columns.
          </p>
        </div>
        <div className="px-6 py-3">
          {localCols.map((col, idx) => (
            <div
              key={col.key}
              draggable
              onDragStart={() => handleDragStart(idx)}
              onDragOver={e => handleDragOver(e, idx)}
              onDrop={() => { dragIdx.current = null }}
              className="flex items-center gap-3 rounded-lg cursor-grab active:cursor-grabbing"
              style={{ height: '48px', borderBottom: idx < localCols.length - 1 ? '1px solid rgba(0,0,0,0.06)' : 'none' }}
            >
              <span className="text-sm font-medium shrink-0" style={{ color: '#5f6368', width: '20px', textAlign: 'right' }}>
                {idx + 1}.
              </span>
              <span className="flex-1 text-sm" style={{ color: '#1f1f1f' }}>{col.header}</span>
              <GripVertical size={18} style={{ color: '#9aa0a6' }} className="shrink-0" />
            </div>
          ))}
        </div>
        <div className="flex items-center justify-between px-6 pb-5 pt-2">
          <button
            onClick={() => setLocalCols([...originalColumns])}
            className="text-sm font-medium px-4 py-2 rounded-lg transition-colors hover:bg-[#e8f0fe]"
            style={{ color: '#1967d2' }}
          >
            Reset
          </button>
          <div className="flex gap-2">
            <button
              onClick={onClose}
              className="text-sm font-medium px-4 py-2 rounded-lg transition-colors hover:bg-[rgba(0,0,0,0.04)]"
              style={{ color: '#1967d2' }}
            >
              Cancel
            </button>
            <button
              onClick={() => { onColumnsChange(localCols); onClose() }}
              className="text-sm font-medium px-4 py-2 rounded-lg transition-colors hover:bg-[#e8f0fe]"
              style={{ color: '#1967d2' }}
            >
              Done
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

/* ─── DataTable component ───────────────────────────────────────────────────── */
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

  /* ── toolbar state ── */
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

  // Sync displayColumns when columns prop reference changes (first render only / parent refresh)
  useEffect(() => { setDisplayColumns(columns) }, [columns]) // eslint-disable-line react-hooks/exhaustive-deps

  // Close toolbar dropdown on outside click
  useEffect(() => {
    if (!toolMenuOpen) return
    const handler = (e: MouseEvent) => {
      if (toolMenuRef.current && !toolMenuRef.current.contains(e.target as Node))
        setToolMenuOpen(false)
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [toolMenuOpen])

  // Close select-all dropdown on outside click
  useEffect(() => {
    if (!selectMenuOpen) return
    const handler = (e: MouseEvent) => {
      if (selectMenuRef.current && !selectMenuRef.current.contains(e.target as Node))
        setSelectMenuOpen(false)
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [selectMenuOpen])

  // Close row context menu on outside click
  useEffect(() => {
    if (!rowMenuId) return
    const handler = (e: MouseEvent) => {
      if (rowMenuRef.current && !rowMenuRef.current.contains(e.target as Node))
        setRowMenuId(null)
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [rowMenuId])

  /* ── row heights by density ── */
  const rowH = density === 'compact' ? '36px' : 'var(--row-height)'
  const headerH = density === 'compact' ? '40px' : 'var(--row-header-height)'

  /* ── selection helpers ── */
  const getId = (row: T) => String(row[idField])

  const toggleAll = useCallback(() => {
    if (selectedIds.size === data.length) {
      setSelectedIds(new Set())
    } else {
      setSelectedIds(new Set(data.map(r => String(r[idField]))))
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [data, selectedIds.size, idField])

  const toggleRow = useCallback((id: string) => {
    setSelectedIds(prev => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })
  }, [])

  /* ── delete ── */
  const handleDeleteConfirm = async () => {
    if (!onDelete) return
    setDeleting(true)
    try {
      await onDelete(Array.from(selectedIds))
      setSelectedIds(new Set())
    } finally {
      setDeleting(false)
      setConfirmOpen(false)
    }
  }

  /* ── single-row export ── */
  const exportSingleRow = (row: T) => {
    const headers = displayColumns.map(c => c.header).join(',')
    const values = displayColumns.map(col => {
      const val = row[col.key]
      const str = val == null ? '' : String(val)
      return str.includes(',') ? `"${str}"` : str
    }).join(',')
    const csv = [headers, values].join('\n')
    const blob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url; a.download = 'row-export.csv'; a.click()
    URL.revokeObjectURL(url)
  }

  /* ── print / export ── */
  const handlePrint = () => {
    if (onPrint) { onPrint(); return }
    window.print()
  }

  const handleExport = () => {
    if (onExport) { onExport(); return }
    const headers = displayColumns.map(c => c.header).join(',')
    const rows = data.map(row =>
      displayColumns.map(col => {
        const val = row[col.key]
        const str = val == null ? '' : String(val)
        return str.includes(',') ? `"${str}"` : str
      }).join(',')
    )
    const csv = [headers, ...rows].join('\n')
    const blob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url; a.download = 'export.csv'; a.click()
    URL.revokeObjectURL(url)
  }

  /* ── pagination ── */
  const totalPages = Math.ceil(totalCount / pageSize)
  const pageStart = Math.min((page - 1) * pageSize + 1, totalCount)
  const pageEnd = Math.min(page * pageSize, totalCount)
  const showPagination = totalCount > pageSize

  /* ── derived ── */
  const allSelected = data.length > 0 && selectedIds.size === data.length
  const someSelected = selectedIds.size > 0 && selectedIds.size < data.length

  /* total col count for colSpan */
  const totalCols = (selectable ? 1 : 0) + displayColumns.length + ((onEdit || onDelete) ? 1 : 0)
  const selectionActive = selectable && selectedIds.size > 0

  return (
    <div className="flex flex-col">
      {/* ══ Desktop table — hidden on mobile ═══════════════════════════════ */}
      <div className="hidden md:block overflow-x-auto">
        <table className="w-full border-collapse">
          {/* Column headers */}
          <thead>
            {selectionActive ? (
              /* ════════════════════════════════════════════════
                 SELECTION MODE — full-width blue header bar
                 No layout shift: same <tr> height, same cols
                 ════════════════════════════════════════════════ */
              <tr style={{ height: headerH }}>
                <th
                  colSpan={totalCols}
                  className="px-2 text-left font-normal"
                  style={{
                    background: 'var(--row-selected-bg)',
                    borderBottom: '1px solid rgba(26,115,232,0.25)',
                  }}
                >
                  <div className="flex items-center gap-0.5">
                    {/* Checkbox + caret dropdown */}
                    <div className="relative flex items-center shrink-0" ref={selectMenuRef}>
                      {/* Blue checkbox (indeterminate when partial) */}
                      <span
                        className="flex items-center justify-center w-5 h-5 rounded cursor-pointer mr-0"
                        style={{
                          background: 'var(--checkbox-color)',
                          border: '2px solid var(--checkbox-color)',
                          borderRadius: '4px',
                        }}
                        onClick={() => setSelectedIds(new Set())}
                        title="Clear selection"
                      >
                        {allSelected
                          ? <Check size={13} strokeWidth={3} color="#fff" />
                          : <span className="block w-2.5 h-0.5 rounded-full" style={{ background: '#fff' }} />
                        }
                      </span>
                      {/* Caret dropdown trigger */}
                      <button
                        onClick={() => setSelectMenuOpen(v => !v)}
                        className="ml-0.5 p-0.5 rounded-full transition-colors"
                        style={{ color: '#1967d2' }}
                        onMouseEnter={e => (e.currentTarget.style.background = 'rgba(26,115,232,0.15)')}
                        onMouseLeave={e => (e.currentTarget.style.background = 'transparent')}
                        title="Selection options"
                      >
                        <ChevronDown size={14} strokeWidth={2.5} />
                      </button>
                      {/* Dropdown: All / None / This page */}
                      {selectMenuOpen && (
                        <div
                          className="absolute left-0 top-full z-50 py-1"
                          style={{
                            minWidth: '148px',
                            borderRadius: '8px',
                            background: 'white',
                            boxShadow: '0 4px 16px rgba(0,0,0,0.18)',
                            border: '1px solid rgba(0,0,0,0.08)',
                            marginTop: '6px',
                          }}
                        >
                          <button
                            className="w-full flex items-center px-4 py-2 text-sm text-left transition-colors hover:bg-[rgba(0,0,0,0.05)]"
                            style={{ color: '#1f1f1f' }}
                            onClick={() => {
                              setSelectedIds(new Set(data.map(r => String(r[idField]))))
                              setSelectMenuOpen(false)
                            }}
                          >
                            All
                          </button>
                          <button
                            className="w-full flex items-center px-4 py-2 text-sm text-left transition-colors hover:bg-[rgba(0,0,0,0.05)]"
                            style={{ color: '#1f1f1f' }}
                            onClick={() => {
                              setSelectedIds(new Set())
                              setSelectMenuOpen(false)
                            }}
                          >
                            None
                          </button>
                        </div>
                      )}
                    </div>

                    {/* Count */}
                    <span
                      className="font-medium text-sm px-2 whitespace-nowrap"
                      style={{ color: '#1967d2' }}
                    >
                      {selectedIds.size} selected
                    </span>

                    {/* Action icons */}
                    <button
                      onClick={handlePrint}
                      title="Print"
                      className="p-1.5 rounded-full transition-colors"
                      style={{ color: '#1967d2' }}
                      onMouseEnter={e => (e.currentTarget.style.background = 'rgba(26,115,232,0.12)')}
                      onMouseLeave={e => (e.currentTarget.style.background = 'transparent')}
                    >
                      <Printer size={18} />
                    </button>
                    <button
                      onClick={handleExport}
                      title="Export"
                      className="p-1.5 rounded-full transition-colors"
                      style={{ color: '#1967d2' }}
                      onMouseEnter={e => (e.currentTarget.style.background = 'rgba(26,115,232,0.12)')}
                      onMouseLeave={e => (e.currentTarget.style.background = 'transparent')}
                    >
                      <Upload size={18} />
                    </button>
                    {onDelete && (
                      <button
                        onClick={() => setConfirmOpen(true)}
                        title="Delete selected"
                        className="p-1.5 rounded-full transition-colors"
                        style={{ color: '#1967d2' }}
                        onMouseEnter={e => (e.currentTarget.style.background = 'rgba(26,115,232,0.12)')}
                        onMouseLeave={e => (e.currentTarget.style.background = 'transparent')}
                      >
                        <Trash2 size={18} />
                      </button>
                    )}
                  </div>
                </th>
              </tr>
            ) : (
              /* ════════════════════════════════════════════════
                 NORMAL MODE — column headers + toolbar
                 ════════════════════════════════════════════════ */
              <tr style={{ height: headerH, borderBottom: '1px solid rgba(0,0,0,0.08)' }}>
                {selectable && (
                  <th className="pl-3 pr-1 w-12 text-left">
                    <div className="relative flex items-center" ref={selectMenuRef}>
                      {/* Select-all checkbox */}
                      <input
                        type="checkbox"
                        checked={allSelected}
                        ref={el => { if (el) el.indeterminate = someSelected }}
                        onChange={toggleAll}
                        className="w-4 h-4 rounded cursor-pointer"
                        style={{ accentColor: 'var(--checkbox-color)' }}
                        aria-label="Select all"
                      />
                      {/* Caret */}
                      <button
                        onClick={() => setSelectMenuOpen(v => !v)}
                        className="ml-0.5 p-0.5 rounded-full transition-colors"
                        style={{ color: 'var(--col-header-color)' }}
                        onMouseEnter={e => (e.currentTarget.style.background = 'rgba(0,0,0,0.06)')}
                        onMouseLeave={e => (e.currentTarget.style.background = 'transparent')}
                        title="Selection options"
                      >
                        <ChevronDown size={12} strokeWidth={2.5} />
                      </button>
                      {selectMenuOpen && (
                        <div
                          className="absolute left-0 top-full z-50 py-1"
                          style={{
                            minWidth: '148px',
                            borderRadius: '8px',
                            background: 'white',
                            boxShadow: '0 4px 16px rgba(0,0,0,0.18)',
                            border: '1px solid rgba(0,0,0,0.08)',
                            marginTop: '6px',
                          }}
                        >
                          <button
                            className="w-full flex items-center px-4 py-2 text-sm text-left transition-colors hover:bg-[rgba(0,0,0,0.05)]"
                            style={{ color: '#1f1f1f' }}
                            onClick={() => {
                              setSelectedIds(new Set(data.map(r => String(r[idField]))))
                              setSelectMenuOpen(false)
                            }}
                          >
                            All
                          </button>
                          <button
                            className="w-full flex items-center px-4 py-2 text-sm text-left transition-colors hover:bg-[rgba(0,0,0,0.05)]"
                            style={{ color: '#1f1f1f' }}
                            onClick={() => {
                              setSelectedIds(new Set())
                              setSelectMenuOpen(false)
                            }}
                          >
                            None
                          </button>
                        </div>
                      )}
                    </div>
                  </th>
                )}
                {displayColumns.map(col => (
                  <th
                    key={col.key}
                    className="px-3 text-left font-normal"
                    style={{ fontSize: 'var(--col-header-size)', color: 'var(--col-header-color)', width: col.width }}
                  >
                    {col.header}
                  </th>
                ))}
                {/* Toolbar: Print · Export · ⋮ */}
                <th className="pr-2 text-right font-normal" style={{ width: '120px' }}>
                  <span className="inline-flex items-center justify-end gap-0">
                    <button
                      onClick={handlePrint}
                      title="Print"
                      className="p-1.5 rounded-full transition-colors"
                      style={{ color: 'var(--col-header-color)' }}
                      onMouseEnter={e => (e.currentTarget.style.background = 'rgba(0,0,0,0.06)')}
                      onMouseLeave={e => (e.currentTarget.style.background = 'transparent')}
                    >
                      <Printer size={16} />
                    </button>
                    <button
                      onClick={handleExport}
                      title="Export CSV"
                      className="p-1.5 rounded-full transition-colors"
                      style={{ color: 'var(--col-header-color)' }}
                      onMouseEnter={e => (e.currentTarget.style.background = 'rgba(0,0,0,0.06)')}
                      onMouseLeave={e => (e.currentTarget.style.background = 'transparent')}
                    >
                      <Upload size={16} />
                    </button>
                    <div className="relative" ref={toolMenuRef}>
                      <button
                        onClick={() => setToolMenuOpen(v => !v)}
                        title="More options"
                        className="p-1.5 rounded-full transition-colors"
                        style={{ color: 'var(--col-header-color)', background: toolMenuOpen ? 'rgba(0,0,0,0.06)' : 'transparent' }}
                        onMouseEnter={e => { if (!toolMenuOpen) (e.currentTarget.style.background = 'rgba(0,0,0,0.06)') }}
                        onMouseLeave={e => { if (!toolMenuOpen) (e.currentTarget.style.background = 'transparent') }}
                      >
                        <MoreVertical size={16} />
                      </button>
                      {toolMenuOpen && (
                        <div
                          className="absolute right-0 top-full z-50 py-2"
                          style={{ minWidth: '200px', borderRadius: '12px', background: 'white', boxShadow: '0 4px 20px rgba(0,0,0,0.16)', border: '1px solid rgba(0,0,0,0.08)', marginTop: '4px' }}
                        >
                          <button
                            onClick={() => { setToolMenuOpen(false); handlePrint() }}
                            className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-left transition-colors hover:bg-[rgba(0,0,0,0.04)]"
                            style={{ color: '#1a237e' }}
                          >
                            <Printer size={16} style={{ color: '#1a237e' }} />
                            Print
                          </button>
                          <button
                            onClick={() => { setToolMenuOpen(false); handleExport() }}
                            className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-left transition-colors hover:bg-[rgba(0,0,0,0.04)]"
                            style={{ color: '#1a237e' }}
                          >
                            <Upload size={16} style={{ color: '#1a237e' }} />
                            Export
                          </button>
                          {onDelete && selectedIds.size > 0 && (
                            <button
                              onClick={() => { setToolMenuOpen(false); setConfirmOpen(true) }}
                              className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-left transition-colors hover:bg-[rgba(0,0,0,0.04)]"
                              style={{ color: '#1a237e' }}
                            >
                              <Trash2 size={16} style={{ color: '#1a237e' }} />
                              Delete
                            </button>
                          )}
                          <div style={{ height: '1px', background: 'rgba(0,0,0,0.08)', margin: '4px 0' }} />
                          <button
                            onClick={() => { setToolMenuOpen(false); setDensityOpen(true) }}
                            className="w-full flex items-center px-4 py-2.5 text-sm text-left transition-colors hover:bg-[rgba(0,0,0,0.04)]"
                            style={{ color: '#1f1f1f' }}
                          >
                            Display density
                          </button>
                          <button
                            onClick={() => { setToolMenuOpen(false); setColOrderOpen(true) }}
                            className="w-full flex items-center px-4 py-2.5 text-sm text-left transition-colors hover:bg-[rgba(0,0,0,0.04)]"
                            style={{ color: '#1f1f1f' }}
                          >
                            Change column order
                          </button>
                        </div>
                      )}
                    </div>
                  </span>
                </th>
              </tr>
            )}
          </thead>

          {/* Body */}
          <tbody style={{ borderSpacing: '0 8px', borderCollapse: 'separate' }}>
            {loading ? (
              <SkeletonRows cols={displayColumns.length} hasAvatar={!!avatarColumn} />
            ) : data.length === 0 ? (
              emptyState ? <EmptyState config={emptyState} /> : null
            ) : (
              data.map(row => {
                const id = getId(row)
                const selected = selectedIds.has(id)
                return (
                  <tr
                    key={id}
                    className={`group transition-colors duration-75${onRowClick ? ' cursor-pointer' : ' cursor-default'}${selected ? ' table-row-selected' : ''}`}
                    style={{
                      height: rowH,
                      backgroundColor: selected ? 'var(--row-selected-bg)' : 'var(--color-bg-surface)',
                      outline: 'none',
                    }}
                    onClick={onRowClick ? () => onRowClick(row) : undefined}
                    onMouseEnter={e => { if (!selected) (e.currentTarget as HTMLTableRowElement).style.backgroundColor = 'var(--row-hover-bg)' }}
                    onMouseLeave={e => { if (!selected) (e.currentTarget as HTMLTableRowElement).style.backgroundColor = 'var(--color-bg-surface)' }}
                  >
                    {selectable && (
                      <td className="pl-3 pr-2 w-12" onClick={e => e.stopPropagation()} style={{ borderTopLeftRadius: '8px', borderBottomLeftRadius: '8px' }}>
                        {avatarColumn ? (
                          /* Google Contacts avatar ↔ checkbox flip */
                          <div
                            className="relative w-8 h-8 shrink-0 cursor-pointer"
                            onClick={() => toggleRow(id)}
                          >
                            {/* Avatar — hidden on hover or when selected */}
                            <span
                              className={[
                                'absolute inset-0 rounded-full transition-opacity duration-100',
                                (selected) ? 'opacity-0' : 'opacity-100 group-hover:opacity-0',
                              ].join(' ')}
                              aria-hidden="true"
                            >
                              <Avatar name={avatarColumn(row) ?? ''} size="sm" />
                            </span>
                            {/* Checkbox container — hidden until hover or selected */}
                            <span
                              className={[
                                'absolute inset-0 flex items-center justify-center rounded-full transition-opacity duration-100',
                                selected ? 'opacity-100' : 'opacity-0 group-hover:opacity-100',
                              ].join(' ')}
                              style={{ background: selected ? 'var(--checkbox-color)' : 'rgba(0,0,0,0.08)' }}
                            >
                              {selected
                                ? <Check size={14} strokeWidth={3} color="#fff" />
                                : (
                                  <span
                                    className="w-4 h-4 rounded border-2"
                                    style={{ borderColor: 'var(--color-text-secondary)', background: 'transparent' }}
                                  />
                                )
                              }
                            </span>
                          </div>
                        ) : (
                          <input
                            type="checkbox"
                            checked={selected}
                            onChange={() => toggleRow(id)}
                            className="w-4 h-4 rounded cursor-pointer opacity-0 group-hover:opacity-100 transition-opacity duration-75"
                            style={{ accentColor: 'var(--checkbox-color)', opacity: selected ? 1 : undefined }}
                            aria-label={`Select row ${id}`}
                          />
                        )}
                      </td>
                    )}
                    {displayColumns.map(col => (
                      <td
                        key={col.key}
                        className="px-3"
                        style={{ fontSize: '14px', color: 'var(--color-text-primary)', width: col.width }}
                      >
                        {col.render ? col.render(row[col.key], row) : String(row[col.key] ?? '')}
                      </td>
                    ))}
                    {/* Row ⋮ context menu */}
                    {(onEdit || onDelete) && (
                      <td className="pr-2 text-right" style={{ width: '48px', borderTopRightRadius: '8px', borderBottomRightRadius: '8px' }} onClick={e => e.stopPropagation()}>
                        <div className="relative inline-flex" ref={rowMenuId === id ? rowMenuRef : undefined}>
                          <button
                            onClick={() => setRowMenuId(prev => prev === id ? null : id)}
                            className="p-1.5 rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-75 hover:bg-[rgba(68,71,70,0.08)] dark:hover:bg-[rgba(255,255,255,0.08)]"
                            style={{ color: 'var(--color-text-secondary)', opacity: rowMenuId === id ? 1 : undefined }}
                            title="More actions"
                          >
                            <MoreVertical size={16} />
                          </button>
                          {rowMenuId === id && (
                            <div
                              className="absolute right-0 top-full z-50 py-1"
                              style={{
                                minWidth: '148px',
                                borderRadius: '12px',
                                background: 'white',
                                boxShadow: '0 4px 20px rgba(0,0,0,0.16)',
                                border: '1px solid rgba(0,0,0,0.08)',
                                marginTop: '4px',
                              }}
                            >
                              {onEdit && (
                                <button
                                  onClick={() => { onEdit(row); setRowMenuId(null) }}
                                  className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-left transition-colors hover:bg-[rgba(0,0,0,0.04)]"
                                  style={{ color: '#1f1f1f' }}
                                >
                                  <Pencil size={15} style={{ color: '#5f6368' }} />
                                  Edit
                                </button>
                              )}
                              <button
                                onClick={() => { exportSingleRow(row); setRowMenuId(null) }}
                                className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-left transition-colors hover:bg-[rgba(0,0,0,0.04)]"
                                style={{ color: '#1f1f1f' }}
                              >
                                <Upload size={15} style={{ color: '#5f6368' }} />
                                Export row
                              </button>
                              {onDelete && (
                                <>
                                  <div style={{ height: '1px', background: 'rgba(0,0,0,0.08)', margin: '4px 0' }} />
                                  <button
                                    onClick={() => { setSelectedIds(new Set([id])); setConfirmOpen(true); setRowMenuId(null) }}
                                    className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-left transition-colors hover:bg-[rgba(0,0,0,0.04)]"
                                    style={{ color: 'var(--color-danger)' }}
                                  >
                                    <Trash2 size={15} />
                                    Delete
                                  </button>
                                </>
                              )}
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
      </div>

      {/* ══ Mobile card list — Google Contacts style, visible <768 px only ═ */}
      <div className="block md:hidden">
        {loading ? (
          Array.from({ length: 8 }).map((_, i) => (
            <div key={i} className="flex items-center gap-3 px-4 py-3 border-b border-[rgba(0,0,0,0.06)] animate-pulse">
              <span className="loading-skeleton w-10 h-10 rounded-full shrink-0" />
              <div className="flex-1 space-y-2">
                <span className="loading-skeleton block h-3.5 rounded w-2/3" />
                <span className="loading-skeleton block h-3 rounded w-1/2" />
              </div>
              <span className="loading-skeleton h-5 w-16 rounded-full shrink-0" />
            </div>
          ))
        ) : data.length === 0 ? (
          emptyState ? (
            <div className="flex flex-col items-center gap-3 py-16" style={{ color: 'var(--color-text-secondary)' }}>
              {(() => { const Icon = emptyState.icon; return <Icon size={40} strokeWidth={1.5} /> })()}
              <p className="font-medium" style={{ fontSize: '15px', color: 'var(--color-text-primary)' }}>{emptyState.title}</p>
              {emptyState.description && <p style={{ fontSize: '13px' }}>{emptyState.description}</p>}
              {emptyState.action && <button className="btn-primary mt-1" onClick={emptyState.action.onClick}>{emptyState.action.label}</button>}
            </div>
          ) : null
        ) : (
          data.map(row => {
            const id = getId(row)
            const nameStr = avatarColumn ? (avatarColumn(row) ?? '') : ''
            const primaryCol = displayColumns[0]
            const secondaryCol = displayColumns[1]
            return (
              <div
                key={id}
                role={onRowClick ? 'button' : undefined}
                tabIndex={onRowClick ? 0 : undefined}
                onClick={onRowClick ? () => onRowClick(row) : undefined}
                onKeyDown={onRowClick ? (e) => { if (e.key === 'Enter' || e.key === ' ') onRowClick(row) } : undefined}
                className="flex items-center gap-3 px-4 py-3 border-b border-[rgba(0,0,0,0.06)] transition-colors"
                style={{
                  cursor: onRowClick ? 'pointer' : 'default',
                  background: 'var(--color-bg-surface)',
                  WebkitTapHighlightColor: 'transparent',
                }}
                onTouchStart={e => { (e.currentTarget as HTMLDivElement).style.background = 'var(--row-hover-bg)' }}
                onTouchEnd={e => { (e.currentTarget as HTMLDivElement).style.background = 'var(--color-bg-surface)' }}
              >
                {nameStr && <Avatar name={nameStr} size={40} className="shrink-0" />}
                <div className="flex-1 min-w-0 overflow-hidden">
                  {primaryCol && (
                    <div className="truncate" style={{ fontSize: '14px', color: 'var(--color-text-primary)' }}>
                      {primaryCol.render ? primaryCol.render(row[primaryCol.key], row) : String(row[primaryCol.key] ?? '')}
                    </div>
                  )}
                </div>
                {secondaryCol && (
                  <div className="shrink-0 ml-2">
                    {secondaryCol.render
                      ? secondaryCol.render(row[secondaryCol.key], row)
                      : <span style={{ fontSize: '12px', color: 'var(--color-text-secondary)' }}>{String(row[secondaryCol.key] ?? '')}</span>
                    }
                  </div>
                )}
              </div>
            )
          })
        )}
        {/* Mobile pagination */}
        {showPagination && !loading && (
          <div
            className="flex items-center justify-between px-4 py-3 border-t border-[rgba(0,0,0,0.06)]"
            style={{ fontSize: '13px', color: 'var(--color-text-secondary)' }}
          >
            <span>{pageStart}–{pageEnd} of {totalCount}</span>
            <div className="flex items-center gap-1">
              <button onClick={() => onPageChange?.(page - 1)} disabled={page <= 1}
                className="p-1.5 rounded-full hover:bg-[var(--row-hover-bg)] disabled:opacity-30 disabled:cursor-not-allowed"
                aria-label="Previous page"><ChevronLeft size={18} /></button>
              <button onClick={() => onPageChange?.(page + 1)} disabled={page >= totalPages}
                className="p-1.5 rounded-full hover:bg-[var(--row-hover-bg)] disabled:opacity-30 disabled:cursor-not-allowed"
                aria-label="Next page"><ChevronRight size={18} /></button>
            </div>
          </div>
        )}
      </div>

      {/* ══ Desktop pagination — hidden on mobile ═══════════════════════════ */}
      {showPagination && !loading && (
        <div
          className="hidden md:flex items-center justify-end gap-1 px-4"
          style={{ height: '52px', borderTop: '1px solid rgba(0,0,0,0.06)', fontSize: '13px', color: 'var(--color-text-secondary)' }}
        >
          <span className="mr-2">{pageStart}–{pageEnd} of {totalCount}</span>
          <button
            onClick={() => onPageChange?.(page - 1)}
            disabled={page <= 1}
            className="p-1 rounded-full hover:bg-[var(--row-hover-bg)] disabled:opacity-30 disabled:cursor-not-allowed"
            aria-label="Previous page"
          >
            <ChevronLeft size={18} />
          </button>
          <button
            onClick={() => onPageChange?.(page + 1)}
            disabled={page >= totalPages}
            className="p-1 rounded-full hover:bg-[var(--row-hover-bg)] disabled:opacity-30 disabled:cursor-not-allowed"
            aria-label="Next page"
          >
            <ChevronRight size={18} />
          </button>
        </div>
      )}

      {/* Confirm delete dialog */}
      <ConfirmDeleteDialog
        open={confirmOpen}
        onClose={() => { setConfirmOpen(false); if (selectedIds.size === 1) setSelectedIds(new Set()) }}
        onConfirm={handleDeleteConfirm}
        count={selectedIds.size}
        loading={deleting}
      />

      {/* Display Density dialog */}
      <DensityDialog
        open={densityOpen}
        density={density}
        onDensityChange={setDensity}
        onClose={() => setDensityOpen(false)}
      />

      {/* Column Order dialog */}
      <ColumnOrderDialog
        open={colOrderOpen}
        columns={displayColumns}
        onColumnsChange={setDisplayColumns}
        originalColumns={columns}
        onClose={() => setColOrderOpen(false)}
      />
    </div>
  )
}

