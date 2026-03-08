'use client'

import { useState, useEffect } from 'react'
import { Breadcrumb } from '../Breadcrumb'

interface ContentAreaProps {
  sidebarOpen: boolean
  children: React.ReactNode
}

/**
 * ContentArea — the main scrollable content zone.
 *
 * Manages its own `mounted` flag so the sidebar-margin transition class is
 * SSR-safe: the server always renders `md:ml-[284px]` (expanded default) and
 * the client switches to the responsive class after hydration.
 *
 * CSS preserved from original AppShell:
 *   - margin transition: transition-[margin-left] duration-100 ease-[cubic-bezier(0.4,0,0.2,1)]
 *   - expanded: md:ml-[284px]
 *   - collapsed: md:ml-[72px]
 *   - top offset: mt-[68px] md:mt-[76px]
 */
export default function ContentArea({ sidebarOpen, children }: ContentAreaProps) {
  const [mounted, setMounted] = useState(false)

  useEffect(() => { setMounted(true) }, [])

  const marginCls = mounted
    ? [
        'transition-[margin-left] duration-100 ease-[cubic-bezier(0.4,0,0.2,1)]',
        sidebarOpen ? 'md:ml-[284px]' : 'md:ml-[72px]',
      ].join(' ')
    : 'md:ml-[284px]'

  return (
    <main
      className={[
        marginCls,
        'fixed top-[56px] md:top-[64px] right-0 bottom-0 left-0',
        'flex flex-col',
      ].join(' ')}
    >
      {/* White card — exact margins + 24px radius matching computed styles */}
      <div
        className={[
          'content-scroll',
          'flex-1 min-h-0',
          'flex flex-col',
          'mt-4 mb-4',   /* 16px top/bottom, 4px left, 16px right */
          'overflow-y-auto overflow-x-hidden',
          'rounded-[24px]',         /* 24px — matches M3 large shape */
          'bg-white dark:bg-[#1e1e1e]',
          'p-3 md:p-6',
          '[&>*]:rounded-[24px]',
        ].join(' ')}
      >
        <Breadcrumb />
        {children}
      </div>
    </main>
  )
}
