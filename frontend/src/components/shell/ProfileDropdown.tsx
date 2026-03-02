'use client'
/**
 * ProfileDropdown — Google Account–style profile panel.
 *
 * All screen sizes: floating dropdown anchored below avatar in Header.
 * Mobile (<640px): full-width, positioned just below the header.
 *
 * All visual styling lives in globals.css (.profile-* classes).
 * Only layout helpers from Tailwind are used in this file.
 */

import Link from 'next/link'
import { useTheme } from 'next-themes'
import { X, LogOut, Sun, Moon, User as UserIcon, Settings, Globe, HelpCircle } from 'lucide-react'
import Avatar from '@/components/shared/Avatar'

// ─── Types ────────────────────────────────────────────────────────────────────

interface ProfileUser {
  email?: string
  first_name?: string
}

interface ProfileDropdownProps {
  user: ProfileUser | null
  displayName: string
  role: 'admin' | 'faculty' | 'student'
  rolePill: string
  mounted: boolean
  onClose: () => void
  onSignOut: () => void
}

// ─── Component ────────────────────────────────────────────────────────────────

export default function ProfileDropdown({
  user,
  displayName,
  role,
  mounted,
  onClose,
  onSignOut,
}: ProfileDropdownProps) {
  const { resolvedTheme, setTheme } = useTheme()
  const isLoading = !user
  const firstName = user?.first_name || displayName.split(' ')[0]
  const toggleTheme = () => setTheme(resolvedTheme === 'dark' ? 'light' : 'dark')

  return (
    <div className="profile-dropdown">
      {/* Loading bar */}
      <div className="h-[3px] w-full shrink-0 overflow-hidden" aria-hidden="true">
        {isLoading && <div className="profile-load-bar" />}
      </div>

      {/* Row 1: centred email + close button */}
      <div className="profile-header-row">
        {isLoading
          ? <div className="loading-skeleton" style={{ height: '16px', width: '176px' }} />
          : <span className="profile-email">{user?.email ?? ''}</span>
        }
        <button onClick={onClose} aria-label="Close" className="profile-close-btn">
          <X size={20} />
        </button>
      </div>

      {/* Row 2: avatar + Hi greeting + full name */}
      <div className="profile-avatar-section">
        <div className="relative">
          <Avatar name={displayName} size={72} />
          <span className="profile-cam-badge" aria-hidden="true">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="white">
              <path d="M12 15.2A3.2 3.2 0 0 1 8.8 12 3.2 3.2 0 0 1 12 8.8a3.2 3.2 0 0 1 3.2 3.2 3.2 3.2 0 0 1-3.2 3.2m7-10.2h-1.8l-1.5-2H8.3L6.8 5H5C3.9 5 3 5.9 3 7v12c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2z" />
            </svg>
          </span>
        </div>
        {isLoading
          ? <div className="loading-skeleton" style={{ height: '28px', width: '112px', marginTop: '16px' }} />
          : <p className="profile-greeting">Hi, {firstName}!</p>
        }
        <p className="profile-subtext">{displayName}</p>
      </div>

      {/* Scrollable cards */}
      <div className="profile-scroll flex flex-col gap-2 px-3 pb-3">

        {/* Profile | Sign out — pill split card */}
        <div className="profile-card profile-card-split">
          <Link href={`/${role}/profile`} onClick={onClose} className="profile-card-split-item">
            <UserIcon size={20} className="profile-icon" /> Profile
          </Link>
          <div className="profile-card-split-divider" />
          <button onClick={onSignOut} className="profile-card-split-item">
            <LogOut size={20} className="profile-icon" /> Sign out
          </button>
        </div>

        {/* Settings + Theme toggle */}
        <div className="profile-card">
          <Link href={`/${role}/settings`} onClick={onClose} className="profile-menu-item">
            <Settings size={22} className="profile-icon" />
            <span className="flex-1">Settings</span>
          </Link>
          <div className="profile-menu-divider" />
          <button onClick={toggleTheme} className="profile-menu-item">
            {mounted && resolvedTheme === 'dark'
              ? <Sun  size={22} className="profile-icon" />
              : <Moon size={22} className="profile-icon" />
            }
            <span className="flex-1">
              {mounted && resolvedTheme === 'dark' ? 'Light mode' : 'Dark mode'}
            </span>
          </button>
        </div>

        {/* Language | Help */}
        <div className="profile-card profile-card-split">
          <button className="profile-card-split-item">
            <Globe      size={20} className="profile-icon" />
            <span>Language</span>
          </button>
          <div className="profile-card-split-divider" />
          <button className="profile-card-split-item">
            <HelpCircle size={20} className="profile-icon" />
            <span>Help</span>
          </button>
        </div>

        {/* Footer */}
        <p className="profile-footer">
          <a href="/privacy">Privacy Policy</a>
          <span className="mx-1">&bull;</span>
          <a href="/terms">Terms of Service</a>
        </p>

      </div>
    </div>
  )
}
