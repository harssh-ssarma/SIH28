'use client'

import React, { useState, useEffect, useRef, useCallback } from 'react'
import Image from 'next/image'
import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'
import { useTheme } from 'next-themes'
import {
  Search,
  Bell,
  LogOut,
  Sun,
  Moon,
  Plus,
  User as UserIcon,
  X,
  LayoutDashboard,
  CalendarDays,
  BookOpen,
  Users,
  GraduationCap,
  CheckCircle2,
  FileText,
  Calendar,
  SlidersHorizontal,
  ShieldCheck,
  Settings,
  BarChart3,
  Clock,
  BookMarked,
  ClipboardList,
  Globe,
  HelpCircle,
  ChevronDown,
  School,
  Building2,
  BookCopy,
  Layers,
  GanttChart,
  DoorOpen,
} from 'lucide-react'
import { useAuth } from '@/context/AuthContext'
import { Breadcrumb } from './Breadcrumb'

// ─── Types ────────────────────────────────────────────────────────────────────

interface NavItem {
  label: string
  href: string
  icon: React.ElementType
  badge?: boolean
  activeBase?: string
}

interface NavGroup {
  label: string
  icon: React.ElementType
  base: string          // pathname prefix used for active detection
  children: NavItem[]
}

type NavEntry = NavItem | NavGroup

function isNavGroup(entry: NavEntry): entry is NavGroup {
  return 'children' in entry
}

interface DashboardLayoutProps {
  children: React.ReactNode
}

// ─── Nav definitions ──────────────────────────────────────────────────────────

const ADMIN_NAV: NavEntry[] = [
  { label: 'Dashboard',  href: '/admin/dashboard',  icon: LayoutDashboard },
  { label: 'Admins',     href: '/admin/admins',     icon: ShieldCheck },
  { label: 'Faculty',    href: '/admin/faculty',    icon: Users },
  { label: 'Students',   href: '/admin/students',   icon: GraduationCap },
  {
    label: 'Academic',
    icon: BookOpen,
    base: '/admin/academic',
    children: [
      { label: 'Schools',     href: '/admin/academic/schools',     icon: School },
      { label: 'Departments', href: '/admin/academic/departments', icon: Layers },
      { label: 'Buildings',   href: '/admin/academic/buildings',   icon: Building2 },
      { label: 'Programs',    href: '/admin/academic/programs',    icon: GanttChart },
      { label: 'Courses',     href: '/admin/academic/courses',     icon: BookCopy },
      { label: 'Rooms',       href: '/admin/academic/rooms',       icon: DoorOpen },
    ],
  },
  { label: 'Timetables', href: '/admin/timetables', icon: CalendarDays },
  { label: 'Approvals',  href: '/admin/approvals',  icon: CheckCircle2, badge: true },
  { label: 'Logs',       href: '/admin/logs',       icon: FileText },
]

const FACULTY_NAV: NavItem[] = [
  { label: 'Dashboard',     href: '/faculty/dashboard',      icon: LayoutDashboard },
  { label: 'My Schedule',   href: '/faculty/schedule',       icon: Calendar },
  { label: 'Preferences',   href: '/faculty/preferences',    icon: SlidersHorizontal },
  { label: 'Notifications', href: '/faculty/notifications',  icon: Bell },
]

const STUDENT_NAV: NavItem[] = [
  { label: 'Dashboard',    href: '/student/dashboard',  icon: LayoutDashboard },
  { label: 'My Timetable', href: '/student/timetable',  icon: CalendarDays },
]

const NAV_MAP: Record<string, NavEntry[]> = {
  admin:   ADMIN_NAV,
  faculty: FACULTY_NAV,
  student: STUDENT_NAV,
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

/** Deterministic hue from a string → Google-style avatar colour. */
function seedHsl(name: string): string {
  let h = 0
  for (let i = 0; i < name.length; i++) h = name.charCodeAt(i) + ((h << 5) - h)
  return `hsl(${Math.abs(h) % 360},55%,45%)`
}

/** Resolve display name + two-letter initials from user object. */
function resolveUser(u: {
  username: string
  email?: string
  first_name?: string
  last_name?: string
}) {
  const full =
    [u.first_name, u.last_name].filter(Boolean).join(' ').trim() || u.username
  // Google-style: single letter — first char of first_name, fallback to username
  const initials = (u.first_name?.[0] ?? u.username[0]).toUpperCase()
  return { full, initials }
}

// ─── Avatar ───────────────────────────────────────────────────────────────────

function Avatar({ name, size = 32 }: { name: string; size?: number }) {
  const { initials } = resolveUser({ username: name })
  const ref = useRef<HTMLSpanElement>(null)
  useEffect(() => {
    const el = ref.current
    if (!el) return
    el.style.setProperty('--av-size', `${size}px`)
    el.style.setProperty('--av-font', `${size * 0.44}px`)
    el.style.setProperty('--av-bg', seedHsl(name))
  }, [size, name])
  return (
    <span
      ref={ref}
      className="inline-flex items-center justify-center rounded-full font-semibold text-white select-none shrink-0 [width:var(--av-size)] [height:var(--av-size)] [font-size:var(--av-font)] [background:var(--av-bg)]"
    >
      {initials}
    </span>
  )
}

// ─── NavItemRow ───────────────────────────────────────────────────────────────

function NavItemRow({
  item,
  active,
  collapsed,
  pendingApprovals,
  onClick,
}: {
  item: NavItem
  active: boolean
  collapsed: boolean
  pendingApprovals: number
  onClick?: () => void
}) {
  const Icon = item.icon
  const showBadge = item.badge && pendingApprovals > 0

  return (
    <Link
      href={item.href}
      onClick={onClick}
      title={collapsed ? item.label : undefined}
      className={[
        'relative flex items-center h-[44px]',
        'transition-colors duration-150 select-none',
        collapsed
          ? 'justify-center gap-0 w-[44px] rounded-full mx-auto'
          : 'gap-3 px-[18px] w-[244.8px] rounded-[24px] mx-auto',
        active
          ? 'bg-[#c2e7ff] dark:bg-[#1C2B4A] font-semibold text-[#001d35] dark:text-[#e3e3e3]'
          : 'text-[#444746] dark:text-[#bdc1c6] hover:bg-[#e8f0fe] dark:hover:bg-[#1a2640]',
      ].join(' ')}
    >
      <span className="relative shrink-0">
        <Icon size={20} strokeWidth={active ? 2.4 : 1.8} />
        {showBadge && (
          <span className="absolute -top-1 -right-1 w-2 h-2 rounded-full bg-red-500 ring-2 ring-white dark:ring-[#202124]" />
        )}
      </span>
      {/* Visible label — hidden when rail is collapsed */}
      <span
        className={[
          'text-sm whitespace-nowrap transition-all duration-200',
          collapsed ? 'opacity-0 w-0 overflow-hidden' : 'opacity-100',
        ].join(' ')}
      >
        {item.label}
      </span>
      {/* Screen-reader label always present so collapsed rail is accessible */}
      {collapsed && <span className="sr-only">{item.label}</span>}
    </Link>
  )
}

// ─── NavGroupRow ─────────────────────────────────────────────────────────────

function NavGroupRow({
  group,
  pathname,
  collapsed,
  onLinkClick,
}: {
  group: NavGroup
  pathname: string
  collapsed: boolean
  onLinkClick?: () => void
}) {
  const isChildActive = group.children.some(
    c => pathname === c.href || pathname.startsWith(c.href + '/')
  )
  const [open, setOpen] = useState(isChildActive)

  // Auto-expand when navigating into this group
  useEffect(() => {
    if (isChildActive) setOpen(true)
  }, [isChildActive])

  const Icon = group.icon

  // Rail (collapsed sidebar): show only the icon; clicking goes to first child
  if (collapsed) {
    return (
      <Link
        href={group.children[0]?.href ?? '#'}
        onClick={onLinkClick}
        title={group.label}
        className={[
          'relative flex items-center justify-center w-[44px] h-[44px] rounded-full mx-auto transition-colors duration-150 select-none',
          isChildActive
            ? 'bg-[#c2e7ff] dark:bg-[#1C2B4A] text-[#001d35] dark:text-[#8AB4F8]'
            : 'text-[#444746] dark:text-[#bdc1c6] hover:bg-[#e8f0fe] dark:hover:bg-[#1a2640]',
        ].join(' ')}
      >
        <Icon size={20} strokeWidth={isChildActive ? 2.2 : 1.8} />
        <span className="sr-only">{group.label}</span>
      </Link>
    )
  }

  return (
    <div className="flex flex-col items-center">
      {/* Group header button */}
      <button
        onClick={() => setOpen(v => !v)}
        className={[
          'w-[244.8px] flex items-center gap-3 px-[18px] h-[44px] rounded-[24px] transition-colors duration-150 select-none relative',
          isChildActive && !open
            ? 'bg-[#c2e7ff] dark:bg-[#1C2B4A] font-semibold text-[#001d35] dark:text-[#e3e3e3]'
            : 'text-[#444746] dark:text-[#bdc1c6] hover:bg-[#e8f0fe] dark:hover:bg-[#1a2640]',
        ].join(' ')}
      >
        {/* Chevron sits to the extreme left, same row */}
        <ChevronDown
          size={14}
          strokeWidth={2.5}
          className={`absolute left-1 shrink-0 transition-transform duration-200 ${open ? 'rotate-0' : '-rotate-90'}`}
        />
        <Icon size={20} strokeWidth={isChildActive ? 2.4 : 1.8} className="shrink-0" />
        <span className="flex-1 text-sm text-left whitespace-nowrap">{group.label}</span>
      </button>

      {/* Sub-items — stacked below the group header */}
      {open && (
        <div className="w-[244.8px] flex flex-col pl-8 mt-0.5">
          {group.children.map(child => {
            const active = pathname === child.href || pathname.startsWith(child.href + '/')
            const ChildIcon = child.icon
            return (
              <Link
                key={child.href}
                href={child.href}
                onClick={onLinkClick}
                className={[
                  'flex items-center gap-2.5 h-9 px-3 rounded-[20px] text-sm transition-colors duration-150 select-none',
                  active
                    ? 'bg-[#c2e7ff] dark:bg-[#1C2B4A] font-semibold text-[#001d35] dark:text-[#e3e3e3]'
                    : 'text-[#5f6368] dark:text-[#9aa0a6] hover:bg-[#e8f0fe] dark:hover:bg-[#1a2640] hover:text-[#444746] dark:hover:text-[#bdc1c6]',
                ].join(' ')}
              >
                <ChildIcon size={15} strokeWidth={active ? 2.2 : 1.8} className="shrink-0" />
                <span className="whitespace-nowrap">{child.label}</span>
              </Link>
            )
          })}
        </div>
      )}
    </div>
  )
}

// ─── QuickLink (profile dropdown row) ────────────────────────────────────────

function QuickLink({
  href,
  icon,
  label,
  onClick,
  badge,
}: {
  href: string
  icon: React.ReactNode
  label: string
  onClick?: () => void
  badge?: boolean
}) {
  return (
    <Link
      href={href}
      onClick={onClick}
      className="flex items-center gap-3 px-5 py-2.5 text-[14px] text-[#444746] dark:text-[#e3e3e3] hover:bg-[#e8eef7] dark:hover:bg-[#303134] transition-colors"
    >
      <span className="shrink-0 text-[#5f6368] dark:text-[#9aa0a6]">{icon}</span>
      <span className="flex-1">{label}</span>
      {badge && <span className="w-2 h-2 rounded-full bg-red-500" />}
    </Link>
  )
}

// ─── AppShell ─────────────────────────────────────────────────────────────────

export default function AppShell({ children }: DashboardLayoutProps) {
  const { user, logout } = useAuth()
  const { theme, setTheme, resolvedTheme } = useTheme()
  const pathname = usePathname()
  const router   = useRouter()

  // ── State ──────────────────────────────────────────────────────────────────
  const [sidebarOpen,  setSidebarOpen]  = useState(true)   // desktop expanded
  const [mobileOpen,   setMobileOpen]   = useState(false)  // mobile drawer
  const [profileOpen,  setProfileOpen]  = useState(false)  // avatar dropdown
  const [showSignOut,  setShowSignOut]  = useState(false)  // confirm dialog
  const [searchOpen,   setSearchOpen]   = useState(false)  // mobile search overlay
  const [newMenuOpen,  setNewMenuOpen]  = useState(false)  // + New dropdown
  const [pendingApprovals]              = useState(0)       // extend with SWR if needed
  const [mounted,      setMounted]      = useState(false)

  const profileRef = useRef<HTMLDivElement>(null)
  const searchRef  = useRef<HTMLInputElement>(null)
  const newMenuRef = useRef<HTMLDivElement>(null)

  // ── Derived ────────────────────────────────────────────────────────────────
  // Prefer the role from the auth context; fall back to pathname so the correct
  // nav is shown even while the user API call is still in-flight or fails.
  const role: 'admin' | 'faculty' | 'student' = (() => {
    if (user?.role === 'admin' || user?.role === 'faculty' || user?.role === 'student')
      return user.role
    if (pathname.startsWith('/admin'))   return 'admin'
    if (pathname.startsWith('/faculty')) return 'faculty'
    return 'student'
  })()
  const navItems   = NAV_MAP[role] ?? ADMIN_NAV
  const { full: displayName } = resolveUser(
    user ?? { username: 'User', email: '', first_name: '', last_name: '' }
  )
  const rolePill = { admin: 'Admin', faculty: 'Faculty', student: 'Student' }[role]

  // ── Mount / responsive init ────────────────────────────────────────────────
  useEffect(() => {
    setMounted(true)
    const init = () => {
      if (window.innerWidth < 1024) {
        setSidebarOpen(false)
        setMobileOpen(false)
      }
    }
    init()
    const onResize = () => {
      if (window.innerWidth >= 768) setMobileOpen(false)
      if (window.innerWidth < 1024) setSidebarOpen(false)
    }
    window.addEventListener('resize', onResize)
    return () => window.removeEventListener('resize', onResize)
  }, [])

  // ── Close profile dropdown on outside click ────────────────────────────────
  useEffect(() => {
    if (!profileOpen) return
    const handler = (e: MouseEvent) => {
      if (profileRef.current && !profileRef.current.contains(e.target as Node))
        setProfileOpen(false)
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [profileOpen])

  // ── Close + New dropdown on outside click ─────────────────────────────────
  useEffect(() => {
    if (!newMenuOpen) return
    const handler = (e: MouseEvent) => {
      if (newMenuRef.current && !newMenuRef.current.contains(e.target as Node))
        setNewMenuOpen(false)
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [newMenuOpen])

  // ── Auto-focus search input when mobile overlay opens ─────────────────────
  useEffect(() => {
    if (searchOpen) setTimeout(() => searchRef.current?.focus(), 60)
  }, [searchOpen])

  // ── Hamburger ─────────────────────────────────────────────────────────────
  const handleHamburger = useCallback(() => {
    if (typeof window !== 'undefined' && window.innerWidth < 768) {
      setMobileOpen((v) => !v)
    } else {
      setSidebarOpen((v) => !v)
    }
  }, [])

  // ── Sign-out ───────────────────────────────────────────────────────────────
  const handleSignOut = async () => {
    setShowSignOut(false)
    await logout()
    router.push('/login')
  }

  // ── Content area left margin — SSR-safe ─────────────────────────────────
  const contentMarginCls = mounted
    ? [
        'transition-[margin-left] duration-200 ease-[cubic-bezier(0.4,0,0.2,1)]',
        sidebarOpen ? 'md:ml-[284px]' : 'md:ml-[72px]',
      ].join(' ')
    : 'md:ml-[284px]'

  const collapsed = !sidebarOpen && !mobileOpen

  // ── Render ─────────────────────────────────────────────────────────────────
  return (
    <div className="min-h-screen bg-[#f6f8fc] dark:bg-[#111111] font-sans">

      {/* ══════════════════════════════════════════════════════════
          HEADER  (fixed, full-width, z-50)
      ══════════════════════════════════════════════════════════ */}
      {/*
          HEADER layout — three fixed zones (same pattern as Google Drive / Gmail):
          ┌──────────────────────────┬───────────────────────────┬──────────────┐
          │  Left  284px (desktop)  │  Center  flex-1  search   │  Right shrink│
          └──────────────────────────────┴───────────────────────────┴──────────────┘
          The left zone is always 284px wide (= expanded sidebar width) so the
          search bar is anchored to a fixed x-position and never moves when the
          sidebar collapses or expands.
      */}
      <header suppressHydrationWarning className="fixed top-0 left-0 right-0 z-50 flex items-center h-14 md:h-16 bg-[#f6f8fc] dark:bg-[#111111]">

        {/* ── Zone 1: Left — always 284px on desktop, natural width on mobile ── */}
        <div className="flex items-center gap-1 shrink-0 pl-2 md:pl-3 md:w-[284px]">
          <button
            onClick={handleHamburger}
            aria-label="Toggle sidebar"
            className="w-10 h-10 flex items-center justify-center rounded-full text-[#444746] dark:text-[#bdc1c6] hover:bg-[#f1f3f4] dark:hover:bg-[#303134] transition-colors"
          >
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round">
              <line x1="3" y1="5"  x2="17" y2="5"/>
              <line x1="3" y1="10" x2="17" y2="10"/>
              <line x1="3" y1="15" x2="17" y2="15"/>
            </svg>
          </button>

          <Link href={`/${role}/dashboard`} className="flex items-center gap-2 px-1 select-none">
            <Image
              src="/logo2.png"
              alt="Cadence"
              width={44}
              height={44}
              className="rounded-full object-contain"
              style={{ mixBlendMode: 'multiply', flexShrink: 0 }}
            />
            <span
              className="hidden sm:inline text-[17px] font-semibold [color:var(--color-text-primary,#202124)] whitespace-nowrap tracking-[-0.01em]"
            >
              Cadence
            </span>
          </Link>
        </div>

        {/* ── Zone 2: Search bar — left-aligned, anchored just after the sidebar, never moves ── */}
        <div className="hidden md:flex flex-1 items-center pl-3">
          <div
            className="flex items-center overflow-hidden transition-shadow duration-150 focus-within:shadow-[0_2px_8px_rgba(32,33,36,0.2)]"
            style={{ width: '720px', height: '48px', background: '#e9eef6', borderRadius: '9999px' }}
            onFocus={e => (e.currentTarget.style.background = '#ffffff')}
            onBlur={e => (e.currentTarget.style.background = '#e9eef6')}
          >
            {/* Search icon — left */}
            <span className="ml-4 mr-2 shrink-0 flex items-center justify-center" style={{ color: '#444746' }}>
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="11" cy="11" r="8"/>
                <line x1="21" y1="21" x2="16.65" y2="16.65"/>
              </svg>
            </span>
            <input
              type="search"
              placeholder="Search timetables, faculty, rooms…"
              className="flex-1 h-full bg-transparent outline-none text-sm text-[#202124] dark:text-[#e8eaed] placeholder:text-[#80868b]"
            />
          </div>
        </div>

        {/* ── Zone 3: Right — actions, shrink-0, never pushes search bar ── */}
        <div className="flex items-center gap-2 ml-auto md:ml-0 shrink-0 pr-2 md:pr-4">

          {/* Mobile search icon */}
          <button
            onClick={() => setSearchOpen(true)}
            aria-label="Search"
            className="md:hidden w-10 h-10 flex items-center justify-center rounded-full text-[#444746] dark:text-[#bdc1c6] hover:bg-[#f1f3f4] dark:hover:bg-[#303134] transition-colors"
          >
            <Search size={20} />
          </button>

          {/* ── + New dropdown — admin only ── */}
          {role === 'admin' && (
            <div className="relative" ref={newMenuRef}>
              <button
                onClick={() => setNewMenuOpen(v => !v)}
                className="flex items-center gap-2 h-9 pl-3 pr-4 rounded-full text-sm font-medium bg-white dark:bg-[#303134] border border-[#dadce0] dark:border-[#5f6368] text-[#202124] dark:text-[#e8eaed] hover:bg-[#f6f8fc] dark:hover:bg-[#3c4043] shadow-sm transition-colors select-none"
              >
                <Plus size={18} strokeWidth={2} className="text-[#1A73E8]" />
                <span className="hidden sm:inline">New</span>
              </button>

              {newMenuOpen && (
                <div className="absolute left-0 top-[calc(100%+6px)] w-[220px] rounded-[16px] shadow-[0_4px_20px_rgba(0,0,0,0.16)] bg-white dark:bg-[#292a2d] border border-[#e0e0e0] dark:border-[#3c4043] overflow-hidden z-[60] py-2">

                  {/* Section: Timetable */}
                  <p className="px-4 pt-1 pb-1 text-[11px] font-semibold uppercase tracking-wider text-[#80868b]">Timetable</p>
                  <Link href="/admin/timetables/new" onClick={() => setNewMenuOpen(false)}
                    className="flex items-center gap-3 px-4 py-2.5 text-[13px] text-[#202124] dark:text-[#e8eaed] hover:bg-[#f1f3f4] dark:hover:bg-[#3c4043] transition-colors">
                    <CalendarDays size={16} className="text-[#1A73E8] shrink-0" />
                    Generate Timetable
                  </Link>

                  <div className="my-1.5 mx-4 h-px bg-[#e0e0e0] dark:bg-[#3c4043]" />

                  {/* Section: People */}
                  <p className="px-4 pt-0.5 pb-1 text-[11px] font-semibold uppercase tracking-wider text-[#80868b]">People</p>
                  <Link href="/admin/faculty" onClick={() => setNewMenuOpen(false)}
                    className="flex items-center gap-3 px-4 py-2.5 text-[13px] text-[#202124] dark:text-[#e8eaed] hover:bg-[#f1f3f4] dark:hover:bg-[#3c4043] transition-colors">
                    <Users size={16} className="text-[#34A853] shrink-0" />
                    Add Faculty
                  </Link>
                  <Link href="/admin/students" onClick={() => setNewMenuOpen(false)}
                    className="flex items-center gap-3 px-4 py-2.5 text-[13px] text-[#202124] dark:text-[#e8eaed] hover:bg-[#f1f3f4] dark:hover:bg-[#3c4043] transition-colors">
                    <GraduationCap size={16} className="text-[#34A853] shrink-0" />
                    Add Student
                  </Link>
                  <Link href="/admin/admins" onClick={() => setNewMenuOpen(false)}
                    className="flex items-center gap-3 px-4 py-2.5 text-[13px] text-[#202124] dark:text-[#e8eaed] hover:bg-[#f1f3f4] dark:hover:bg-[#3c4043] transition-colors">
                    <ShieldCheck size={16} className="text-[#34A853] shrink-0" />
                    Add Admin
                  </Link>

                  <div className="my-1.5 mx-4 h-px bg-[#e0e0e0] dark:bg-[#3c4043]" />

                  {/* Section: Academic */}
                  <p className="px-4 pt-0.5 pb-1 text-[11px] font-semibold uppercase tracking-wider text-[#80868b]">Academic</p>
                  <Link href="/admin/academic/schools" onClick={() => setNewMenuOpen(false)}
                    className="flex items-center gap-3 px-4 py-2.5 text-[13px] text-[#202124] dark:text-[#e8eaed] hover:bg-[#f1f3f4] dark:hover:bg-[#3c4043] transition-colors">
                    <School size={16} className="text-[#FBBC04] shrink-0" />
                    Add School
                  </Link>
                  <Link href="/admin/academic/buildings" onClick={() => setNewMenuOpen(false)}
                    className="flex items-center gap-3 px-4 py-2.5 text-[13px] text-[#202124] dark:text-[#e8eaed] hover:bg-[#f1f3f4] dark:hover:bg-[#3c4043] transition-colors">
                    <Building2 size={16} className="text-[#FBBC04] shrink-0" />
                    Add Building
                  </Link>
                  <Link href="/admin/academic/courses" onClick={() => setNewMenuOpen(false)}
                    className="flex items-center gap-3 px-4 py-2.5 text-[13px] text-[#202124] dark:text-[#e8eaed] hover:bg-[#f1f3f4] dark:hover:bg-[#3c4043] transition-colors">
                    <BookCopy size={16} className="text-[#FBBC04] shrink-0" />
                    Add Course
                  </Link>
                </div>
              )}
            </div>
          )}

          {/* Bell — 4px gap from CTA */}
          <button
            aria-label="Notifications"
            className="relative w-10 h-10 flex items-center justify-center rounded-full text-[#444746] dark:text-[#bdc1c6] hover:bg-[#f1f3f4] dark:hover:bg-[#303134] transition-colors"
          >
            <Bell size={20} />
            {pendingApprovals > 0 && (
              <span className="absolute top-2 right-2 w-2 h-2 rounded-full bg-red-500 ring-[1.5px] ring-white dark:ring-[#202124]" />
            )}
          </button>

          {/* Avatar + dropdown — 2px gap from bell */}
          <div className="relative ml-0.5" ref={profileRef}>
            <button
              onClick={() => setProfileOpen((v) => !v)}
              aria-label="Account menu"
              className="rounded-full focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#1a73e8] focus-visible:ring-offset-1"
            >
              <Avatar name={displayName} size={36} />
            </button>

            {profileOpen && (
              /* Outer panel — light: soft blue-grey #e8edf5 | dark: Google panel #202124 */
              <div className="absolute right-0 top-[calc(100%+8px)] w-[360px] rounded-[28px] shadow-[0_8px_24px_rgba(0,0,0,0.18)] bg-[#e8edf5] dark:bg-[#202124] border border-[#cdd3de] dark:border-[#3c4043] overflow-hidden z-[60]">

                {/* ── Row 1: centered email + X ── */}
                <div className="relative flex items-center justify-center h-12 px-12">
                  <span className="text-[16px] font-normal text-[#1f1f1f] dark:text-[#e8eaed] truncate select-none">
                    {user?.email ?? ''}
                  </span>
                  <button
                    onClick={() => setProfileOpen(false)}
                    aria-label="Close"
                    className="absolute right-3 w-8 h-8 flex items-center justify-center rounded-full text-[#5f6368] dark:text-[#9aa0a6] hover:bg-black/10 dark:hover:bg-white/10 transition-colors"
                  >
                    <X size={16} />
                  </button>
                </div>

                {/* ── Row 2: centered avatar + Hi + full name ── */}
                <div className="flex flex-col items-center px-6 pt-6 pb-5">
                  <Avatar name={displayName} size={72} />
                  <p className="mt-4 text-[22px] font-normal text-[#202124] dark:text-[#e8eaed] leading-snug">
                    Hi, {user?.first_name || displayName.split(' ')[0]}!
                  </p>
                  <p className="mt-0.5 mb-5 text-[14px] text-[#5f6368] dark:text-[#9aa0a6]">
                    {displayName}
                  </p>

                </div>

                {/* ── Cards section ── */}
                <div className="px-3 pb-3 flex flex-col gap-2">

                  {/* Logged in as role */}
                  <div className="bg-white dark:bg-[#2d2f31] rounded-[20px] px-4 py-3 flex items-center gap-2">
                    <ShieldCheck size={16} className="text-[#5f6368] dark:text-[#9aa0a6] shrink-0" />
                    <span className="text-[13px] text-[#5f6368] dark:text-[#9aa0a6] flex-1">Logged in as</span>
                    <span className="text-[11px] font-semibold px-2.5 py-0.5 rounded-full bg-[#c2e7ff] dark:bg-[#1C2B4A] text-[#001d35] dark:text-[#8AB4F8] uppercase tracking-wider">
                      {rolePill}
                    </span>
                  </div>

                    {/* Profile | Sign out */}
                  <div className="flex rounded-full border border-[#c5ccd8] dark:border-[#5f6368] bg-white dark:bg-[#2d2f31] overflow-hidden">
                    <Link
                      href={`/${role}/profile`}
                      onClick={() => setProfileOpen(false)}
                      className="flex-1 flex items-center justify-center gap-2 px-4 py-3.5 text-[14px] font-medium text-[#1f1f1f] dark:text-[#e8eaed] hover:bg-[#f1f3f4] dark:hover:bg-[#3c4043] transition-colors"
                    >
                      <UserIcon size={15} className="shrink-0" />
                      Profile
                    </Link>
                    <div className="w-px my-2 bg-[#c5ccd8] dark:bg-[#5f6368]" />
                    <button
                      onClick={() => { setProfileOpen(false); setShowSignOut(true) }}
                      className="flex-1 flex items-center justify-center gap-2 px-4 py-3.5 text-[14px] font-medium text-[#1f1f1f] dark:text-[#e8eaed] hover:bg-[#f1f3f4] dark:hover:bg-[#3c4043] transition-colors"
                    >
                      <LogOut size={15} className="shrink-0" />
                      Sign out
                    </button>
                  </div>

                  {/* Settings + Theme */}
                  <div className="bg-white dark:bg-[#2d2f31] rounded-[20px] overflow-hidden">
                    <Link
                      href={`/${role}/settings`}
                      onClick={() => setProfileOpen(false)}
                      className="flex items-center gap-3 px-4 py-3.5 text-[14px] text-[#1f1f1f] dark:text-[#e8eaed] hover:bg-[#d8dde9] dark:hover:bg-[#3c4043] transition-colors"
                    >
                      <Settings size={18} className="text-[#5f6368] dark:text-[#9aa0a6] shrink-0" />
                      <span className="flex-1">Settings</span>
                    </Link>
                    <div className="h-px mx-4 bg-[#dde2eb] dark:bg-[#3c4043]" />
                    <button
                      onClick={() => setTheme(resolvedTheme === 'dark' ? 'light' : 'dark')}
                      className="w-full flex items-center gap-3 px-4 py-3.5 text-[14px] text-[#1f1f1f] dark:text-[#e8eaed] hover:bg-[#d8dde9] dark:hover:bg-[#3c4043] transition-colors text-left"
                    >
                      {mounted && resolvedTheme === 'dark'
                        ? <Sun  size={18} className="text-[#5f6368] dark:text-[#9aa0a6] shrink-0" />
                        : <Moon size={18} className="text-[#5f6368] dark:text-[#9aa0a6] shrink-0" />
                      }
                      <span className="flex-1">
                        {mounted && resolvedTheme === 'dark' ? 'Light mode' : 'Dark mode'}
                      </span>
                      <span className="text-[12px] text-[#5f6368] dark:text-[#9aa0a6]">Off</span>
                    </button>
                  </div>

                  {/* Language | Help */}
                  <div className="bg-white dark:bg-[#2d2f31] rounded-[20px] overflow-hidden flex">
                    <button className="flex-1 flex items-center gap-2 px-4 py-3.5 text-[14px] text-[#1f1f1f] dark:text-[#e8eaed] hover:bg-[#d8dde9] dark:hover:bg-[#3c4043] transition-colors">
                      <Globe      size={17} className="text-[#5f6368] dark:text-[#9aa0a6] shrink-0" />
                      <span>Language</span>
                    </button>
                    <div className="w-px my-3 bg-[#dde2eb] dark:bg-[#3c4043]" />
                    <button className="flex-1 flex items-center gap-2 px-4 py-3.5 text-[14px] text-[#1f1f1f] dark:text-[#e8eaed] hover:bg-[#d8dde9] dark:hover:bg-[#3c4043] transition-colors">
                      <HelpCircle size={17} className="text-[#5f6368] dark:text-[#9aa0a6] shrink-0" />
                      <span>Help</span>
                    </button>
                  </div>

                  {/* Footer */}
                  <p className="text-center text-[12px] text-[#5f6368] dark:text-[#9aa0a6] pt-1 pb-1">
                    <a href="/privacy" className="hover:underline">Privacy Policy</a>
                    <span className="mx-1.5">&bull;</span>
                    <a href="/terms" className="hover:underline">Terms of Service</a>
                  </p>

                </div>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* ══════════════════════════════════════════════════════════
          MOBILE SEARCH OVERLAY
      ══════════════════════════════════════════════════════════ */}
      {searchOpen && (
        <div className="md:hidden fixed inset-0 z-[60] bg-white dark:bg-[#202124] flex flex-col">
          <div className="flex items-center h-14 px-2 gap-1 border-b border-[#e0e0e0] dark:border-[#3c4043]">
            <button
              aria-label="Close search"
              onClick={() => setSearchOpen(false)}
              className="w-10 h-10 flex items-center justify-center rounded-full text-[#444746] dark:text-[#bdc1c6] hover:bg-[#f1f3f4] dark:hover:bg-[#303134] transition-colors shrink-0"
            >
              <X size={20} />
            </button>
            <input
              ref={searchRef}
              type="search"
              placeholder="Search timetables, faculty, rooms…"
              className="flex-1 h-10 px-2 text-sm bg-transparent outline-none text-[#202124] dark:text-[#e8eaed] placeholder:text-[#9aa0a6]"
            />
          </div>
        </div>
      )}

      {/* ══════════════════════════════════════════════════════════
          MOBILE BACKDROP
      ══════════════════════════════════════════════════════════ */}
      {mobileOpen && (
        <div
          className="md:hidden fixed inset-0 z-40 bg-black/40"
          onClick={() => setMobileOpen(false)}
          aria-hidden="true"
        />
      )}

      {/* ══════════════════════════════════════════════════════════
          SIDEBAR
      ══════════════════════════════════════════════════════════ */}
      <aside
        className={[
          'fixed left-0 top-0 h-full z-[45] flex flex-col',
          'bg-[#f6f8fc] dark:bg-[#111111]',
          'pt-14 md:pt-16',
          'transition-[width,transform] duration-200 ease-[cubic-bezier(0.4,0,0.2,1)]',
          mobileOpen ? 'translate-x-0 w-[284px]' : '-translate-x-full w-[284px] md:translate-x-0',
          !mobileOpen && (sidebarOpen ? 'md:w-[284px]' : 'md:w-[72px]'),
        ].filter(Boolean).join(' ')}
      >
        {/* Nav items */}
        <nav className="flex-1 overflow-y-auto overflow-x-hidden py-2">
          {(navItems as NavEntry[]).map((entry) => {
            if (isNavGroup(entry)) {
              return (
                <NavGroupRow
                  key={entry.base}
                  group={entry}
                  pathname={pathname}
                  collapsed={collapsed}
                  onLinkClick={() => { if (mobileOpen) setMobileOpen(false) }}
                />
              )
            }
            const base   = entry.activeBase ?? entry.href
            const active = pathname === entry.href || pathname.startsWith(base + '/')
            return (
              <NavItemRow
                key={entry.href}
                item={entry}
                active={active}
                collapsed={collapsed}
                pendingApprovals={pendingApprovals}
                onClick={() => { if (mobileOpen) setMobileOpen(false) }}
              />
            )
          })}
        </nav>


      </aside>

      {/* ══════════════════════════════════════════════════════════
          CONTENT AREA
      ══════════════════════════════════════════════════════════ */}
      <main
        className={[
          contentMarginCls,
          'mt-14 md:mt-16',
        ].join(' ')}
      >
        {/* ── Content card ──────────────────────────────────────────────── */}
        <div
          className={[
            'mr-2 md:mr-3 mb-2 md:mb-3',
            'min-h-[calc(100vh-58px)] md:min-h-[calc(100vh-68px)]',
            'rounded-2xl',
            'bg-white dark:bg-[#1e1e1e]',
            'p-3 md:p-6',
            '[&>*]:rounded-2xl',
          ].join(' ')}
        >
          {/* ── Path title — Google Drive-style, lives inside the card ── */}
          <Breadcrumb />
          {children}
        </div>
      </main>

      {/* ══════════════════════════════════════════════════════════
          SIGN-OUT CONFIRMATION DIALOG
      ══════════════════════════════════════════════════════════ */}
      {showSignOut && (
        <div className="fixed inset-0 z-[70] flex items-center justify-center p-4">
          <div
            className="absolute inset-0 bg-black/40 backdrop-blur-sm"
            onClick={() => setShowSignOut(false)}
            aria-hidden="true"
          />
          <div className="relative w-full max-w-sm bg-white dark:bg-[#292a2d] rounded-2xl shadow-2xl border border-[#e0e0e0] dark:border-[#3c4043] p-6 flex flex-col gap-4">
            <div className="flex items-start gap-3">
              <span className="w-10 h-10 rounded-full bg-red-100 dark:bg-red-900/30 flex items-center justify-center shrink-0 mt-0.5">
                <LogOut size={18} className="text-red-600 dark:text-red-400" />
              </span>
              <div>
                <h2 className="text-base font-semibold text-[#202124] dark:text-[#e8eaed]">
                  Sign out?
                </h2>
                <p className="text-sm text-[#5f6368] dark:text-[#9aa0a6] mt-1">
                  Are you sure you want to sign out of Cadence?
                </p>
              </div>
            </div>
            <div className="flex gap-2 justify-end">
              <button
                onClick={() => setShowSignOut(false)}
                className="px-5 py-2 rounded-full text-sm font-medium text-[#444746] dark:text-[#e3e3e3] hover:bg-[#f1f3f4] dark:hover:bg-[#303134] transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleSignOut}
                className="px-5 py-2 rounded-full text-sm font-medium bg-red-600 hover:bg-red-700 active:bg-red-800 text-white transition-colors"
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
