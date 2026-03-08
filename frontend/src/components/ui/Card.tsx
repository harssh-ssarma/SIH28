// src/components/ui/Card.tsx
// Material Design 3–style Card component (Elevated / Filled / Outlined variants).
// Usage:
//   <Card>…</Card>
//   <Card variant="outlined">…</Card>
//   <Card variant="filled">…</Card>
//   <Card header={<CardHeader title="Title" subtitle="Sub" icon={<Icon />} action={<Button />} />}>…</Card>
//   <Card footer={<CardActions>…</CardActions>}>…</Card>

import { type HTMLAttributes, forwardRef } from 'react'
import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

// ─── Variants ───────────────────────────────────────────────────────────────
// All variants consume global CSS design tokens so they stay in sync with the
// project-wide .card / .card-flat utility classes defined in globals.css.

const variants = {
  /** Surface + shadow + 1px border — mirrors the global `.card` utility class */
  elevated: [
    '[background:var(--color-bg-surface)]',
    'border [border-color:var(--color-border)]',
    '[box-shadow:var(--shadow-card)]',
    'hover:[border-color:var(--color-border-strong)]',
    'transition-shadow duration-200',
  ].join(' '),

  /** Tinted surface (surface-2), no shadow — mirrors `.card-flat` */
  filled: [
    '[background:var(--color-bg-surface-2)]',
    'border [border-color:var(--color-border)]',
  ].join(' '),

  /** White surface + explicit border, no shadow */
  outlined: [
    '[background:var(--color-bg-surface)]',
    'border [border-color:var(--color-border)]',
  ].join(' '),
} as const

type CardVariant = keyof typeof variants

// ─── Card ───────────────────────────────────────────────────────────────────

export interface CardProps extends HTMLAttributes<HTMLDivElement> {
  variant?: CardVariant
  /** Padding preset: 'none' | 'sm' | 'md' (default) | 'lg' */
  padding?: 'none' | 'sm' | 'md' | 'lg'
  /** Optional sticky header rendered above scrollable body */
  header?: React.ReactNode
  /** Optional footer rendered below scrollable body */
  footer?: React.ReactNode
  /** Whether the card body should be independently scrollable */
  scrollable?: boolean
}

const paddingMap = {
  none: '',
  sm:   'p-3',
  md:   'p-5 md:p-6',   // 20px → 24px, aligns with global .card padding
  lg:   'p-6 md:p-8',
}

export const Card = forwardRef<HTMLDivElement, CardProps>(
  (
    {
      variant = 'elevated',
      padding = 'md',
      header,
      footer,
      scrollable = false,
      className,
      children,
      ...rest
    },
    ref,
  ) => {
    const hasSlots = header || footer

    return (
      <div
        ref={ref}
        className={cn(
          '[border-radius:var(--radius-lg)] overflow-hidden',
          variants[variant],
          /* If no header/footer slots, apply padding directly */
          !hasSlots && paddingMap[padding],
          className,
        )}
        {...rest}
      >
        {header && (
          <div className="shrink-0">
            {header}
          </div>
        )}

        <div
          className={cn(
            hasSlots && paddingMap[padding],
            scrollable && 'overflow-y-auto',
          )}
        >
          {children}
        </div>

        {footer && (
          <div className="shrink-0">
            {footer}
          </div>
        )}
      </div>
    )
  },
)
Card.displayName = 'Card'

// ─── CardHeader ─────────────────────────────────────────────────────────────

export interface CardHeaderProps {
  title: React.ReactNode
  subtitle?: React.ReactNode
  /** Leading icon / avatar — rendered in a 40×40 container */
  icon?: React.ReactNode
  /** Trailing element (e.g. IconButton, Menu trigger) */
  action?: React.ReactNode
  className?: string
}

export function CardHeader({ title, subtitle, icon, action, className }: CardHeaderProps) {
  return (
    <div
      className={cn(
        'flex items-center gap-3 px-4 md:px-5 py-3 md:py-4',
        'border-b [border-color:var(--color-border)]',
        className,
      )}
    >
      {icon && (
        <div className="shrink-0 w-10 h-10 flex items-center justify-center rounded-full [background:var(--color-primary-subtle)] [color:var(--color-primary)]">
          {icon}
        </div>
      )}

      <div className="flex-1 min-w-0">
        <p className="text-[15px] font-semibold [color:var(--color-text-primary)] truncate leading-snug">
          {title}
        </p>
        {subtitle && (
          <p className="text-[13px] [color:var(--color-text-secondary)] truncate leading-snug mt-0.5">
            {subtitle}
          </p>
        )}
      </div>

      {action && (
        <div className="shrink-0 ml-auto">
          {action}
        </div>
      )}
    </div>
  )
}

// ─── CardActions ─────────────────────────────────────────────────────────────

export interface CardActionsProps extends HTMLAttributes<HTMLDivElement> {
  /** 'end' (default) | 'start' | 'between' */
  align?: 'start' | 'end' | 'between'
}

export function CardActions({ align = 'end', className, children, ...rest }: CardActionsProps) {
  const alignMap = {
    start:   'justify-start',
    end:     'justify-end',
    between: 'justify-between',
  }
  return (
    <div
      className={cn(
        'flex items-center gap-2 flex-wrap',
        'px-4 md:px-5 py-3',
        'border-t [border-color:var(--color-border)]',
        alignMap[align],
        className,
      )}
      {...rest}
    >
      {children}
    </div>
  )
}

// ─── CardDivider ─────────────────────────────────────────────────────────────

export function CardDivider({ className }: { className?: string }) {
  return (
    <hr
      className={cn(
        'border-none h-px [background:var(--color-border)] mx-4 md:mx-5',
        className,
      )}
    />
  )
}
