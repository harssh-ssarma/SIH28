'use client'

import { forwardRef, useImperativeHandle, useCallback, useRef } from 'react'

/** Imperative handle exposed via ref. */
export interface CardProgressHandle {
  /** Start indeterminate loop animation. */
  start:  () => void
  /** Complete — sweep remaining fill then fade out. */
  finish: () => void
  /** Fade out immediately without completing. */
  reset:  () => void
}

/**
 * CardProgress — same indeterminate looping effect as NavigationProgress.
 *
 * Placement : any `position:relative; overflow:hidden` container.
 * Control   : imperatively via `ref.current.start() / .finish() / .reset()`
 */
export const CardProgress = forwardRef<CardProgressHandle>(
  function CardProgress(_props, ref) {
    const wrapRef = useRef<HTMLDivElement>(null)
    const barRef  = useRef<HTMLDivElement>(null)
    const hideRef = useRef<ReturnType<typeof setTimeout> | null>(null)

    const stopTimers = useCallback(() => {
      if (hideRef.current) { clearTimeout(hideRef.current); hideRef.current = null }
    }, [])

    useImperativeHandle(ref, () => ({
      start() {
        stopTimers()
        const wrap = wrapRef.current
        const bar  = barRef.current
        if (!wrap || !bar) return
        bar.style.animation  = 'cardIndeterminate 1.2s linear infinite'
        bar.style.transform  = ''
        wrap.style.transition = 'opacity 200ms ease'
        wrap.style.opacity   = '1'
      },

      finish() {
        stopTimers()
        const wrap = wrapRef.current
        const bar  = barRef.current
        if (!wrap || !bar) return
        // Stop loop, snap to full solid fill
        bar.style.animation  = 'none'
        bar.style.transform  = 'translateX(0) scaleX(1)'
        hideRef.current = setTimeout(() => {
          if (!wrap) return
          wrap.style.transition = 'opacity 400ms ease'
          wrap.style.opacity    = '0'
          hideRef.current = setTimeout(() => {
            if (bar) { bar.style.animation = 'none'; bar.style.transform = '' }
          }, 420)
        }, 200)
      },

      reset() {
        stopTimers()
        const wrap = wrapRef.current
        const bar  = barRef.current
        if (!wrap || !bar) return
        wrap.style.transition = 'opacity 300ms ease'
        wrap.style.opacity    = '0'
        hideRef.current = setTimeout(() => {
          if (bar) bar.style.animation = 'none'
        }, 320)
      },
    }), [stopTimers])

    return (
      <div
        ref={wrapRef}
        aria-hidden="true"
        style={{
          position:     'absolute',
          top:          0,
          left:         0,
          right:        0,
          height:       '4px',
          overflow:     'hidden',
          opacity:      0,
          pointerEvents:'none',
          borderRadius: '12px 12px 0 0',
        }}
      >
        <div
          ref={barRef}
          style={{
            position:      'absolute',
            top:           0,
            left:          0,
            height:        '100%',
            width:         '100%',
            background:    '#1a73e8',
            transformOrigin: 'left',
          }}
        />
        {/* eslint-disable-next-line react/no-unknown-property */}
        <style jsx>{`
          @keyframes cardIndeterminate {
            0%   { transform: translateX(-100%) scaleX(0.5); }
            100% { transform: translateX(100%)  scaleX(0.5); }
          }
        `}</style>
      </div>
    )
  }
)
