// src/components/shared/DataTableHelpers.tsx
// Sub-components used exclusively by DataTable:
//   SkeletonRows · EmptyState · DataTableMobileList
// Extracted to keep DataTable.tsx within file-size limits.
'use client'

import { ChevronLeft, ChevronRight } from 'lucide-react'
import Avatar from './Avatar'
import type { Column, EmptyStateConfig } from './DataTable'

// Pre-computed skeleton widths — avoids dynamic inline styles while still
// providing visual variety across skeleton rows/columns.
const SKELETON_WIDTHS = [
  'w-[55%]', 'w-[58%]', 'w-[62%]', 'w-[65%]', 'w-[69%]',
  'w-[71%]', 'w-[73%]', 'w-[76%]', 'w-[78%]', 'w-[83%]',
  'w-[87%]', 'w-[60%]',
]

// ─── SkeletonRows ─────────────────────────────────────────────────────────────

export function SkeletonRows({ cols, hasAvatar }: { cols: number; hasAvatar: boolean }) {
  return (
    <>
      {Array.from({ length: 8 }).map((_, i) => (
        <tr key={i} className="h-[var(--row-height)]">
          <td className="pl-3 pr-2 w-12">
            {hasAvatar
              ? <span className="loading-skeleton block w-8 h-8 rounded-full" />
              : <span className="loading-skeleton block w-4 h-4 rounded" />}
          </td>
          {Array.from({ length: cols }).map((_, j) => (
            <td key={j} className="px-3">
              <span
                className={`loading-skeleton block h-4 rounded ${SKELETON_WIDTHS[(i * 3 + j * 7) % SKELETON_WIDTHS.length]}`}
              />
            </td>
          ))}
          <td className="pr-3 w-20" />
        </tr>
      ))}
    </>
  )
}

// ─── EmptyState ───────────────────────────────────────────────────────────────

export function EmptyState({ config }: { config: EmptyStateConfig }) {
  const Icon = config.icon
  return (
    <tr>
      <td colSpan={99}>
        <div className="flex flex-col items-center gap-3 py-16 text-[var(--color-text-secondary)]">
          <Icon size={40} strokeWidth={1.5} />
          <p className="font-medium text-[15px] text-[var(--color-text-primary)]">
            {config.title}
          </p>
          {config.description && (
            <p className="text-[13px]">{config.description}</p>
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

// ─── DataTableMobileList ──────────────────────────────────────────────────────

interface DataTableMobileListProps<T extends Record<string, unknown>> {
  loading: boolean
  data: T[]
  displayColumns: Column<T>[]
  emptyState?: EmptyStateConfig
  avatarColumn?: (row: T) => string | null
  idField: string
  onRowClick?: (row: T) => void
  // pagination
  showPagination: boolean
  page: number
  totalPages: number
  pageStart: number
  pageEnd: number
  totalCount: number
  onPageChange?: (page: number) => void
}

const BASE_ROW_CLASS =
  'flex items-center gap-3 px-4 py-3 border-b border-[var(--color-border)] transition-colors bg-[var(--color-bg-surface)] [-webkit-tap-highlight-color:transparent]'
const CLICKABLE_ROW_CLASS = 'cursor-pointer hover:bg-[var(--row-hover-bg)]'

export function DataTableMobileList<T extends Record<string, unknown>>({
  loading,
  data,
  displayColumns,
  emptyState,
  avatarColumn,
  idField,
  onRowClick,
  showPagination,
  page,
  totalPages,
  pageStart,
  pageEnd,
  totalCount,
  onPageChange,
}: DataTableMobileListProps<T>) {
  const getId = (row: T) => String(row[idField])

  if (loading) {
    return (
      <div className="block md:hidden">
        {Array.from({ length: 8 }).map((_, i) => (
          <div key={i} className="flex items-center gap-3 px-4 py-3 border-b border-[rgba(0,0,0,0.06)] animate-pulse">
            <span className="loading-skeleton w-10 h-10 rounded-full shrink-0" />
            <div className="flex-1 space-y-2">
              <span className="loading-skeleton block h-3.5 rounded w-2/3" />
              <span className="loading-skeleton block h-3 rounded w-1/2" />
            </div>
            <span className="loading-skeleton h-5 w-16 rounded-full shrink-0" />
          </div>
        ))}
      </div>
    )
  }

  if (data.length === 0 && emptyState) {
    const Icon = emptyState.icon
    return (
      <div className="block md:hidden flex flex-col items-center gap-3 py-16 text-[var(--color-text-secondary)]">
        <Icon size={40} strokeWidth={1.5} />
        <p className="font-medium text-[15px] text-[var(--color-text-primary)]">{emptyState.title}</p>
        {emptyState.description && <p className="text-[13px]">{emptyState.description}</p>}
        {emptyState.action && (
          <button className="btn-primary mt-1" onClick={emptyState.action.onClick}>{emptyState.action.label}</button>
        )}
      </div>
    )
  }

  const primaryCol = displayColumns[0]
  const secondaryCol = displayColumns[1]

  return (
    <div className="block md:hidden">
      {data.map(row => {
        const id = getId(row)
        const nameStr = avatarColumn ? (avatarColumn(row) ?? '') : ''

        const innerContent = (
          <>
            {nameStr && <Avatar name={nameStr} size="sm" className="shrink-0" />}
            <div className="flex-1 min-w-0 overflow-hidden">
              {primaryCol && (
                <div className="truncate text-sm text-[var(--color-text-primary)]">
                  {primaryCol.render
                    ? primaryCol.render(row[primaryCol.key], row)
                    : String(row[primaryCol.key] ?? '')}
                </div>
              )}
            </div>
            {secondaryCol && (
              <div className="shrink-0 ml-2">
                {secondaryCol.render
                  ? secondaryCol.render(row[secondaryCol.key], row)
                  : (
                    <span className="text-xs text-[var(--color-text-secondary)]">
                      {String(row[secondaryCol.key] ?? '')}
                    </span>
                  )}
              </div>
            )}
          </>
        )

        // Render as <button> when clickable — provides native role="button",
        // keyboard focus, and accessible semantics without an explicit role attr.
        return onRowClick ? (
          <button
            key={id}
            type="button"
            onClick={() => onRowClick(row)}
            aria-label={`View details${nameStr ? ` for ${nameStr}` : ''}`}
            className={`w-full text-left ${BASE_ROW_CLASS} ${CLICKABLE_ROW_CLASS}`}
          >
            {innerContent}
          </button>
        ) : (
          <div key={id} className={BASE_ROW_CLASS}>
            {innerContent}
          </div>
        )
      })}

      {showPagination && (
        <div className="flex items-center justify-between px-4 py-3 border-t border-[var(--color-border)] text-[13px] text-[var(--color-text-secondary)]">
          <span>{pageStart}{'–'}{pageEnd} of {totalCount}</span>
          <div className="flex items-center gap-1">
            <button
              onClick={() => onPageChange?.(page - 1)}
              disabled={page <= 1}
              className="p-1.5 rounded-full hover:bg-[var(--row-hover-bg)] disabled:opacity-30 disabled:cursor-not-allowed"
              aria-label="Previous page"
            >
              <ChevronLeft size={18} />
            </button>
            <button
              onClick={() => onPageChange?.(page + 1)}
              disabled={page >= totalPages}
              className="p-1.5 rounded-full hover:bg-[var(--row-hover-bg)] disabled:opacity-30 disabled:cursor-not-allowed"
              aria-label="Next page"
            >
              <ChevronRight size={18} />
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
