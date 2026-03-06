'use client'

import { useState, type ReactNode } from 'react'
import { usePathname, useRouter } from 'next/navigation'
import { LogOut } from 'lucide-react'
import { useAuth } from '@/context/AuthContext'
import { Header } from './Header'
import { Sidebar } from './Sidebar'
import ContentArea from './Content/ContentArea'
import { useSidebarState } from './hooks/useSidebarState'
import { useNavItems } from './hooks/useNavItems'

// ─── AppShell ─────────────────────────────────────────────────────────────────

interface AppShellProps {
  children: ReactNode
}

export default function AppShell({ children }: AppShellProps) {
  const { user, logout } = useAuth()
  const pathname = usePathname()
  const router   = useRouter()

  const { sidebarOpen, mobileOpen, isCollapsed, toggle, closeMobile } = useSidebarState()
  const [showSignOut, setShowSignOut] = useState(false)
  const [pendingApprovals] = useState(0) // extend with SWR when needed

  // Derive role from auth context; fall back to pathname so nav is correct
  // even while the user API call is in-flight.
  const role: 'admin' | 'faculty' | 'student' = (() => {
    if (user?.role === 'admin' || user?.role === 'faculty' || user?.role === 'student')
      return user.role
    if (pathname.startsWith('/admin'))   return 'admin'
    if (pathname.startsWith('/faculty')) return 'faculty'
    return 'student'
  })()

  const navItems = useNavItems(role)

  const displayName =
    [user?.first_name, user?.last_name].filter(Boolean).join(' ').trim() ||
    user?.username ||
    'User'

  const rolePill = { admin: 'Admin', faculty: 'Faculty', student: 'Student' }[role]

  const handleSignOut = async () => {
    setShowSignOut(false)
    await logout()
    router.push('/login')
  }

  return (
    <div className="min-h-screen font-sans" style={{ background: 'var(--color-bg-page)' }}>

      <Header
        role={role}
        onMenuClick={toggle}
        displayName={displayName}
        user={user}
        rolePill={rolePill}
        pendingApprovals={pendingApprovals}
        onSignOut={() => setShowSignOut(true)}
      />

      <Sidebar
        navItems={navItems}
        sidebarOpen={sidebarOpen}
        mobileOpen={mobileOpen}
        isCollapsed={isCollapsed}
        pendingApprovals={pendingApprovals}
        role={role}
        onCloseMobile={closeMobile}
      />

      <ContentArea sidebarOpen={sidebarOpen}>
        {children}
      </ContentArea>

      {/* ══ Sign-out confirmation dialog ════════════════════════════════════ */}
      {showSignOut && (
        <div className="fixed inset-0 z-[70] flex items-center justify-center p-4">
          <div
            className="absolute inset-0 bg-black/40 backdrop-blur-sm"
            onClick={() => setShowSignOut(false)}
            aria-hidden="true"
          />
          {/* M3 Alert Dialog — extra-large shape, surface bg, modal elevation */}
          <div
            className="relative w-full max-w-[312px] flex flex-col overflow-hidden"
            style={{
              background:   'var(--color-bg-surface)',
              border:       '1px solid var(--color-border)',
              borderRadius: 'var(--radius-extra-large)',
              boxShadow:    'var(--shadow-modal)',
            }}
          >
            {/* Icon + headline + supporting text — centered, M3 alert dialog spec */}
            <div className="flex flex-col items-center text-center gap-3 pt-7 px-6 pb-5">
              <span
                className="w-12 h-12 rounded-full flex items-center justify-center shrink-0"
                style={{ background: 'var(--color-danger-subtle)' }}
              >
                <LogOut size={20} style={{ color: 'var(--color-danger)' }} />
              </span>
              <h2
                className="text-[24px] font-normal leading-tight"
                style={{ color: 'var(--color-text-primary)' }}
              >
                Sign out?
              </h2>
              <p
                className="text-[14px] leading-snug"
                style={{ color: 'var(--color-text-secondary)' }}
              >
                You will be signed out of Cadence on this device.
              </p>
            </div>
            {/* Actions — M3: right-aligned, text button + filled tonal destructive */}
            <div
              className="flex justify-end gap-1 px-4 pb-5"
            >
              <button
                onClick={() => setShowSignOut(false)}
                className="px-6 h-10 rounded-full text-[14px] font-medium transition-colors duration-150"
                style={{ color: 'var(--color-primary)' }}
                onMouseEnter={e => ((e.currentTarget as HTMLElement).style.background = 'var(--color-primary-subtle)')}
                onMouseLeave={e => ((e.currentTarget as HTMLElement).style.background = 'transparent')}
              >
                Cancel
              </button>
              <button
                onClick={handleSignOut}
                className="px-6 h-10 rounded-full text-[14px] font-medium text-white transition-colors duration-150"
                style={{ background: 'var(--color-danger)' }}
                onMouseEnter={e => ((e.currentTarget as HTMLElement).style.filter = 'brightness(1.1)')}
                onMouseLeave={e => ((e.currentTarget as HTMLElement).style.filter = 'none')}
              >
                Sign out
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
