'use client'

/**
 * NavigationProgress — Google-style indeterminate looping progress bar.
 *
 * Google's indeterminate bar (YouTube, Chrome, etc.):
 *  - Continuously loops from left to right
 *  - Smooth animation with consistent speed
 *  - Bar expands and contracts as it moves
 *  - No percentage-based progress (truly indeterminate)
 *  - Color: #4285f4 (Google Blue)
 *  - Height: 4px
 */

import { usePathname } from 'next/navigation'
import { useEffect, useRef, useCallback } from 'react'

export function NavigationProgress() {
  const pathname = usePathname()
  const wrapperRef = useRef<HTMLDivElement>(null)
  const prevPathRef = useRef(pathname)
  const activeRef = useRef(false)

  const show = useCallback(() => {
    if (!wrapperRef.current) return
    activeRef.current = true
    wrapperRef.current.style.opacity = '1'
  }, [])

  const hide = useCallback(() => {
    if (!wrapperRef.current) return
    activeRef.current = false
    wrapperRef.current.style.opacity = '0'
  }, [])

  // Intercept link clicks
  useEffect(() => {
    const onClick = (e: MouseEvent) => {
      const anchor = (e.target as Element).closest('a')
      if (!anchor) return

      const href = anchor.getAttribute('href') ?? ''
      const target = anchor.getAttribute('target') ?? ''

      if (
        !href ||
        href.startsWith('#') ||
        href.startsWith('mailto:') ||
        href.startsWith('tel:') ||
        /^https?:\/\//.test(href) ||
        target === '_blank'
      ) return

      try {
        const dest = new URL(href, window.location.href)
        if (dest.pathname === window.location.pathname) return
      } catch {
        // relative URL
      }

      show()
    }

    document.addEventListener('click', onClick, true)
    return () => document.removeEventListener('click', onClick, true)
  }, [show])

  // Hide when pathname changes
  useEffect(() => {
    if (pathname !== prevPathRef.current) {
      prevPathRef.current = pathname
      hide()
    }
  }, [pathname, hide])

  return (
    <div
      ref={wrapperRef}
      aria-hidden="true"
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        height: '4px',
        zIndex: 9999,
        opacity: 0,
        pointerEvents: 'none',
        transition: 'opacity 400ms ease',
        overflow: 'hidden',
        background: 'transparent',
      }}
    >
      <div
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          height: '100%',
          width: '100%',
          background: '#1a73e8',
          transformOrigin: 'left',
          animation: 'indeterminateProgress 1.2s linear infinite',
        }}
      />
      <style jsx>{`
        @keyframes indeterminateProgress {
          0% {
            transform: translateX(-100%) scaleX(0.5);
          }
          100% {
            transform: translateX(100%) scaleX(0.5);
          }
        }
      `}</style>
    </div>
  )
}
