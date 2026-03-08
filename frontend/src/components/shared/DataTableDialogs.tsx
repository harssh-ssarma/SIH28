// src/components/shared/DataTableDialogs.tsx
// Isolated dialog sub-components for DataTable: DensityDialog + ColumnOrderDialog.
// Extracted to keep DataTable.tsx within the 500-line limit.
'use client'

import { useState, useRef, useEffect } from 'react'
import { GripVertical, Check } from 'lucide-react'
import type { Column, Density } from './DataTable'

// ─── Density Dialog ───────────────────────────────────────────────────────────

interface DensityDialogProps {
  open: boolean
  density: Density
  onDensityChange: (d: Density) => void
  onClose: () => void
}

export function DensityDialog({ open, density, onDensityChange, onClose }: DensityDialogProps) {
  if (!open) return null
  const rowH = density === 'compact' ? 36 : 52

  return (
    <div
      className="fixed inset-0 z-[100] flex items-center justify-center"
      style={{ background: 'rgba(0,0,0,0.32)' }}
      onClick={onClose}
    >
      <div
        className="bg-[var(--color-bg-surface)] overflow-hidden"
        style={{ borderRadius: '28px', width: '400px', boxShadow: '0 8px 30px rgba(0,0,0,0.24)' }}
        onClick={e => e.stopPropagation()}
      >
        <div className="px-6 pt-6 pb-4">
          <h2 style={{ fontSize: '22px', fontWeight: 400, color: 'var(--color-text-primary)' }}>
            Display density
          </h2>
        </div>

        {/* Density preview */}
        <div
          className="mx-6 mb-5 overflow-hidden"
          style={{ borderRadius: '12px', border: '1px solid var(--color-border)', background: 'var(--color-bg-surface-2)' }}
        >
          {[1, 2, 3, 4, 5].map(i => (
            <div
              key={i}
              className="flex items-center gap-3 px-4"
              style={{
                height: `${rowH}px`,
                borderBottom: i < 5 ? '1px solid var(--color-border)' : 'none',
                transition: 'height 0.15s ease',
              }}
            >
              <div className="shrink-0 rounded-full loading-skeleton" style={{ width: 28, height: 28 }} />
              <div className="flex-1 flex gap-4">
                {[55 + i * 8, 30 + i * 4, 20 + i * 3].map((w, j) => (
                  <div key={j} className="rounded-full loading-skeleton" style={{ height: 10, width: `${w}%` }} />
                ))}
              </div>
            </div>
          ))}
        </div>

        {/* Comfortable / Compact segmented toggle */}
        <div className="flex justify-center mx-6 mb-6">
          <button
            onClick={() => onDensityChange('comfortable')}
            className="flex items-center gap-1.5 px-5 py-2 text-sm transition-colors"
            style={{
              borderRadius: '20px 0 0 20px',
              border: '1px solid var(--color-border)',
              background: density === 'comfortable' ? 'var(--color-nav-active)' : 'transparent',
              color: 'var(--color-text-primary)',
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
              border: '1px solid var(--color-border)',
              borderLeft: 'none',
              background: density === 'compact' ? 'var(--color-nav-active)' : 'transparent',
              color: 'var(--color-text-primary)',
              fontWeight: density === 'compact' ? 500 : 400,
            }}
          >
            {density === 'compact' && <Check size={14} />}
            Compact
          </button>
        </div>

        <div className="flex justify-end px-6 pb-5">
          <button onClick={onClose} className="btn-ghost px-4 py-2 text-sm">
            Done
          </button>
        </div>
      </div>
    </div>
  )
}

// ─── Column Order Dialog ──────────────────────────────────────────────────────

interface ColumnOrderDialogProps<T extends Record<string, unknown>> {
  open: boolean
  columns: Column<T>[]
  onColumnsChange: (cols: Column<T>[]) => void
  originalColumns: Column<T>[]
  onClose: () => void
}

export function ColumnOrderDialog<T extends Record<string, unknown>>({
  open,
  columns,
  onColumnsChange,
  originalColumns,
  onClose,
}: ColumnOrderDialogProps<T>) {
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
        className="bg-[var(--color-bg-surface)]"
        style={{ borderRadius: '28px', width: '440px', boxShadow: '0 8px 30px rgba(0,0,0,0.24)' }}
        onClick={e => e.stopPropagation()}
      >
        <div className="px-6 pt-6 pb-2">
          <h2 style={{ fontSize: '22px', fontWeight: 400, color: 'var(--color-text-primary)' }}>
            Change column order
          </h2>
          <p style={{ fontSize: '13px', color: 'var(--color-text-secondary)', marginTop: '6px', lineHeight: 1.5 }}>
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
              style={{
                height: '48px',
                borderBottom: idx < localCols.length - 1 ? '1px solid var(--color-border)' : 'none',
              }}
            >
              <span
                className="text-sm font-medium shrink-0 tabular-nums"
                style={{ color: 'var(--color-text-secondary)', width: '20px', textAlign: 'right' }}
              >
                {idx + 1}.
              </span>
              <span className="flex-1 text-sm" style={{ color: 'var(--color-text-primary)' }}>
                {col.header}
              </span>
              <GripVertical size={18} style={{ color: 'var(--color-text-placeholder)' }} className="shrink-0" />
            </div>
          ))}
        </div>

        <div className="flex items-center justify-between px-6 pb-5 pt-2">
          <button
            onClick={() => setLocalCols([...originalColumns])}
            className="btn-ghost text-sm px-4 py-2"
          >
            Reset
          </button>
          <div className="flex gap-2">
            <button onClick={onClose} className="btn-ghost text-sm px-4 py-2">
              Cancel
            </button>
            <button
              onClick={() => { onColumnsChange(localCols); onClose() }}
              className="btn-ghost text-sm px-4 py-2"
            >
              Done
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
