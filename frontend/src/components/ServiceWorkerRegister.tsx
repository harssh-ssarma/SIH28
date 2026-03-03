'use client'

/**
 * ServiceWorkerRegister
 *
 * Registers /sw.js as a Service Worker once the browser is idle.
 * Renders nothing — purely a side-effect component.
 * Does NOT alter any UI behaviour or business logic.
 */
import { useEffect } from 'react'

export function ServiceWorkerRegister() {
  useEffect(() => {
    if (typeof window === 'undefined') return
    if (!('serviceWorker' in navigator)) return

    // Register after page load so the SW installation doesn't compete
    // with critical resources (fonts, first paint)
    const register = () => {
      navigator.serviceWorker
        .register('/sw.js', { scope: '/' })
        .then((reg) => {
          // Check for updates every 60 minutes while the tab is open
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
