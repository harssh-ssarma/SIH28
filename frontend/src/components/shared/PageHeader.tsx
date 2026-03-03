// src/components/shared/PageHeader.tsx
// Google Drive–style breadcrumb title row: "Academic > Schools (15)" left + action right.
'use client'

import Link from 'next/link'
import { type LucideIcon, Plus, ChevronRight } from 'lucide-react'

interface PrimaryAction {
  label: string
  onClick: () => void
  icon?: LucideIcon
}

interface PageHeaderProps {
  title: string
  count?: number
  loading?: boolean
  primaryAction?: PrimaryAction
  secondaryActions?: React.ReactNode
  /** If set, renders a breadcrumb: "<parentLabel> > <title>" */
  parentLabel?: string
  parentHref?: string
}

export default function PageHeader({
  title,
  count,
  loading = false,
  primaryAction,
  secondaryActions,
  parentLabel,
  parentHref,
}: PageHeaderProps) {
  const ActionIcon = primaryAction?.icon ?? Plus

  // ── Loading skeleton: mirrors the real layout so there's no layout shift ──
  if (loading) {
    return (
      <div className="flex items-center justify-between gap-4 mb-1">
        <div
          className="h-8 rounded-full animate-pulse"
          style={{ width: parentLabel ? 224 : 176, background: 'var(--color-bg-surface-2)' }}
        />
        <div className="flex items-center gap-2 shrink-0">
          {secondaryActions}
          {primaryAction && (
            <div
              className="h-10 w-40 rounded-full animate-pulse"
              style={{ background: 'var(--color-bg-surface-2)' }}
            />
          )}
        </div>
      </div>
    )
  }

  return (
    <div className="flex items-center justify-between gap-4 mb-1">
      {/* Title / breadcrumb */}
      <div className="flex items-center gap-0.5 shrink-0 min-w-0">
        {parentLabel && (
          <>
            {parentHref ? (
              <Link
                href={parentHref}
                className="font-normal leading-tight whitespace-nowrap px-2 py-1 rounded-full transition-colors"
                style={{
                  fontSize: 'var(--text-page-title)',
                  color: 'var(--color-text-secondary)',
                  fontWeight: 400,
                }}
                onMouseEnter={e => ((e.currentTarget as HTMLElement).style.background = 'rgba(0,0,0,0.06)')}
                onMouseLeave={e => ((e.currentTarget as HTMLElement).style.background = 'transparent')}
              >
                {parentLabel}
              </Link>
            ) : (
              <span
                className="font-normal leading-tight whitespace-nowrap px-2 py-1 rounded-full"
                style={{ fontSize: 'var(--text-page-title)', color: 'var(--color-text-secondary)', fontWeight: 400 }}
              >
                {parentLabel}
              </span>
            )}
            <ChevronRight size={16} strokeWidth={1.8} style={{ color: 'var(--color-text-secondary)', flexShrink: 0, margin: '0 2px' }} />
          </>
        )}
        <h1
          className="font-normal leading-tight whitespace-nowrap px-2 py-1"
          style={{
            fontSize: 'var(--text-page-title)',
            color: 'var(--color-text-primary)',
            fontWeight: parentLabel ? 500 : 400,
          }}
        >
          {title}
          {count !== undefined && (
            <span style={{ color: 'var(--color-text-secondary)' }}>
              {' '}({count.toLocaleString()})
            </span>
          )}
        </h1>
      </div>

      {/* Actions */}
      <div className="flex items-center gap-2 shrink-0">
        {secondaryActions}
        {primaryAction && (
          <button className="btn-primary" onClick={primaryAction.onClick}>
            <ActionIcon size={16} />
            {primaryAction.label}
          </button>
        )}
      </div>
    </div>
  )
}
