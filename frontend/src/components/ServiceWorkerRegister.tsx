'use client'

/**
 * ServiceWorkerRegister
 *
 * Production:   registers /sw.js for static-asset caching.
 * Development:  unregisters ALL service workers + clears ALL caches so you
 *               always see the latest edits without needing a hard refresh.
 *               (Industry-standard practice — same approach used by CRA, Vite,
 *               and Google's own internal tooling.)
 *
 * Renders nothing — purely a side-effect component.
 */
import { useEffect } from 'react'

export function ServiceWorkerRegister() {
  useEffect(() => {
    if (typeof window === 'undefined') return
    if (!('serviceWorker' in navigator)) return

    if (process.env.NODE_ENV !== 'production') {
      // ── Development: nuke every SW and every cache ──────────────────────
      // Ensures HMR / fast-refresh changes are never blocked by a stale SW.
      navigator.serviceWorker.getRegistrations().then((regs) => {
        regs.forEach((reg) => reg.unregister())
      })
      caches.keys().then((keys) => {
        keys.forEach((key) => caches.delete(key))
      })
      return
    }

    // ── Production: register after page load so the SW doesn't compete ───
    // with critical resources (fonts, first paint)
    const register = () => {
      navigator.serviceWorker
        .register('/sw.js', { scope: '/' })
        .then((reg) => {
          // Check for SW updates every 60 minutes while the tab is open
          setInterval(() => reg.update(), 60 * 60 * 1000)
        })
        .catch(() => {
          // Service workers are a progressive enhancement — failure is fine
        })
    }

    if (document.readyState === 'complete') {
      register()
    } else {
      window.addEventListener('load', register, { once: true })
    }
  }, [])

  return null
}
