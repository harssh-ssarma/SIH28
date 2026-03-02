'use client'

import { forwardRef, useImperativeHandle, useCallback, useRef } from 'react'
import { crawlStep } from '@/lib/progressUtils'

/** Imperative handle exposed via ref. */
export interface CardProgressHandle {
  /** Start crawl animation (resets any running animation first). */
  start:  () => void
  /** Snap to 100 %, then fade out. Call on async success. */
  finish: () => void
  /** Fade out immediately without completing. Call on async error. */
  reset:  () => void
}

/**
 * CardProgress — Google-style in-card deterministic progress bar.
 *
 * Placement : any `position:relative; overflow:hidden` container.
 * Control   : imperatively via `ref.current.start() / .finish() / .reset()`
 *
 * Intentionally distinct from NavigationProgress:
 *   NavigationProgress  – fixed to viewport top, indeterminate loop, route-driven
 *   CardProgress        – absolute inside a card, deterministic crawl, API-driven
 */
export const CardProgress = forwardRef<CardProgressHandle>(
  function CardProgress(_props, ref) {
    const wrapRef   = useRef<HTMLDivElement>(null)
    const barRef    = useRef<HTMLDivElement>(null)
    const tickRef   = useRef<ReturnType<typeof setInterval> | null>(null)
    const hideRef   = useRef<ReturnType<typeof setTimeout>  | null>(null)
    const widthRef  = useRef(0)
    const activeRef = useRef(false)

    const setW = useCallback((w: number) => {
      widthRef.current = w
      if (barRef.current) barRef.current.style.width = `${w}%`
    }, [])

    const setOp = useCallback((opacity: number, durationMs = 0) => {
      const el = wrapRef.current
      if (!el) return
      el.style.transition = durationMs ? `opacity ${durationMs}ms ease` : 'none'
      el.style.opacity    = String(opacity)
    }, [])

    const stopTimers = useCallback(() => {
      if (tickRef.current) { clearInterval(tickRef.current); tickRef.current = null }
      if (hideRef.current) { clearTimeout(hideRef.current);  hideRef.current = null }
    }, [])

    useImperativeHandle(ref, () => ({
      start() {
        stopTimers()
        activeRef.current = true
        if (barRef.current) barRef.current.style.transition = 'none'
        setOp(1); setW(0)
        requestAnimationFrame(() => requestAnimationFrame(() => {
          if (!barRef.current) return
          barRef.current.style.transition = 'width 120ms ease-out'
          setW(20)
          setTimeout(() => {
            if (!activeRef.current) return
            tickRef.current = setInterval(() => {
              if (barRef.current) barRef.current.style.transition = 'width 180ms ease-out'
              setW(Math.min(widthRef.current + crawlStep(widthRef.current), 90))
            }, 200)
          }, 140)
        }))
      },

      finish() {
        stopTimers()
        activeRef.current = false
        if (barRef.current)
          barRef.current.style.transition = 'width 200ms cubic-bezier(0.4,0,0.2,1)'
        setW(100)
        hideRef.current = setTimeout(() => {
          setOp(0, 400)
          setTimeout(() => { if (barRef.current) barRef.current.style.transition = 'none'; setW(0) }, 450)
        }, 180)
      },

      reset() {
        stopTimers()
        activeRef.current = false
        if (barRef.current) barRef.current.style.transition = 'none'
        setOp(0, 300)
        setTimeout(() => setW(0), 350)
      },
    }), [stopTimers, setOp, setW])

    return (
      <div ref={wrapRef} aria-hidden="true" className="card-progress-wrap">
        <div ref={barRef} className="card-progress-bar" />
      </div>
    )
  }
)
