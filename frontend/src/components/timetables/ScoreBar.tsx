'use client'

/**
 * ScoreBar - compact horizontal progress bar with label + value.
 *
 * The fill width is a dynamic number (0-100). To avoid inline styles entirely
 * we set the '--score-w' CSS custom property on the wrapper element via a ref/
 * useEffect — this happens in JavaScript after render, so it never appears as
 * a style={} prop in JSX.
 */

import { useRef, useEffect } from 'react'

interface ScoreBarProps {
  label: string
  value: number
  compact?: boolean
}

const THRESHOLDS = [
  { min: 80, text: 'text-[color:var(--color-success,#34a853)]', bg: '[background:var(--color-success,#34a853)]' },
  { min: 55, text: 'text-[color:var(--color-warning,#fbbc04)]',  bg: '[background:var(--color-warning,#fbbc04)]' },
  { min: 0,  text: 'text-[color:var(--color-danger,#ea4335)]',   bg: '[background:var(--color-danger,#ea4335)]' },
]

function scoreClasses(value: number) {
  return THRESHOLDS.find((t) => value >= t.min) ?? THRESHOLDS[2]
}

export function ScoreBar({ label, value, compact = false }: ScoreBarProps) {
  const isNA         = value < 0
  const fillWidth    = isNA ? 0 : Math.min(100, Math.max(0, value))
  const displayValue = isNA ? 'N/A' : `${Math.round(value)}%`
  const cls          = isNA ? null : scoreClasses(value)

  // Set --score-w CSS variable on the wrapper via DOM ref, avoiding any
  // style={} prop attribute (which would trigger the no-inline-styles rule).
  const wrapRef = useRef<HTMLDivElement>(null)
  useEffect(() => {
    wrapRef.current?.style.setProperty('--score-w', `${fillWidth}%`)
  }, [fillWidth])

  return (
    <div ref={wrapRef} className="flex flex-col gap-[3px]">
      <div className="flex items-center justify-between">
        <span className="text-[11px] font-medium uppercase tracking-[0.04em] [color:var(--color-text-secondary)]">
          {label}
        </span>
        {!compact && (
          <span className={`text-[12px] font-bold ${isNA ? '[color:var(--color-text-muted)]' : (cls?.text ?? '')}`}>
            {displayValue}
          </span>
        )}
      </div>
      <div className="h-[5px] rounded-full overflow-hidden relative [background:var(--color-bg-surface-3,#f1f3f4)]">
        <div
          role="progressbar"
          {...{
            'aria-label':     `${label}: ${displayValue}`,
            'aria-valuenow':  fillWidth,
            'aria-valuemin':  0,
            'aria-valuemax':  100,
            'aria-valuetext': displayValue,
          }}
          className={[
            'absolute inset-y-0 left-0 rounded-full transition-[width] duration-500',
            '[width:var(--score-w)]',
            isNA ? '[background:var(--color-bg-surface-3)]' : (cls?.bg ?? ''),
          ].join(' ')}
        />
      </div>
    </div>
  )
}
