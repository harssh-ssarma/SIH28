'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { ChevronDown } from 'lucide-react'
import type { NavGroup } from '../hooks/useNavItems'

interface NavGroupProps {
  group: NavGroup
  pathname: string
  collapsed: boolean
  onLinkClick?: () => void
}

export default function NavGroupRow({
  group,
  pathname,
  collapsed,
  onLinkClick,
}: NavGroupProps) {
  const isChildActive = group.children.some(
    (c) => pathname === c.href || pathname.startsWith(c.href + '/')
  )
  const [open, setOpen] = useState(isChildActive)

  // Auto-expand when navigating into this group
  useEffect(() => {
    if (isChildActive) setOpen(true)
  }, [isChildActive])

  const Icon = group.icon
  const router = useRouter()

  // ── Single render path for both collapsed (rail) and expanded states ──
  // Using CSS transitions (same approach as NavItem) avoids the React unmount/remount
  // that caused Academics to appear "late" relative to other nav items.
  return (
    <div className="flex flex-col">
      {/* Group header — behaves as a link in rail mode, button when expanded */}
      <button
        onClick={() => {
          if (!collapsed) setOpen((v) => !v)
          else if (group.children[0]) { router.push(group.children[0].href); onLinkClick?.() }
        }}
        title={collapsed ? group.label : undefined}
        className={[
          'relative flex items-center h-[44px] transition-colors duration-150 select-none',
          collapsed
            ? 'justify-center gap-0 w-[44px] rounded-full mx-auto'
            : 'gap-3 px-[18px] w-[244.8px] rounded-[24px] mx-auto',
          // Parent group never shows active state — only the leaf child does.
          // Matches Google Drive: group header is always idle-styled, hover-only.
          'text-[#444746] dark:text-[#bdc1c6] hover:bg-[#e8f0fe] dark:hover:bg-[#1a2640]',
        ].join(' ')}
      >
        {/* Chevron — only visible when expanded */}
        <ChevronDown
          size={14}
          strokeWidth={2.5}
          className={[
            'absolute left-1 shrink-0 transition-[opacity,transform] duration-100',
            collapsed ? 'opacity-0' : 'opacity-100',
            open ? 'rotate-0' : '-rotate-90',
          ].join(' ')}
        />
        <Icon size={20} strokeWidth={1.8} className="shrink-0" />
        {/* Label — same fade transition as NavItem */}
        <span
          className={[
            'text-[14px] font-medium transition-[opacity] duration-100 text-left text-[#444746] dark:text-[#bdc1c6]',
            collapsed ? 'opacity-0 w-0 overflow-hidden' : 'hhIRA opacity-100',
          ].join(' ')}
        >
          {group.label}
        </span>
        {collapsed && <span className="sr-only">{group.label}</span>}
      </button>

      {/* Sub-items */}
      {!collapsed && open && (
        <div className="w-[244.8px] flex flex-col pl-8 mt-0.5 mx-auto">
          {group.children.map((child) => {
            const active =
              pathname === child.href || pathname.startsWith(child.href + '/')
            const ChildIcon = child.icon
            return (
              <Link
                key={child.href}
                href={child.href}
                onClick={onLinkClick}
                className={[
                  'flex items-center gap-2.5 h-9 px-3 rounded-[20px] text-sm transition-colors duration-150 select-none',
                  active
                    ? 'bg-[#c2e7ff] dark:bg-[#1C2B4A] text-[#001d35] dark:text-[#e3e3e3]'
                    : 'text-[#444746] dark:text-[#bdc1c6] hover:bg-[#e8f0fe] dark:hover:bg-[#1a2640]',
                ].join(' ')}
              >
                <ChildIcon size={15} strokeWidth={active ? 2.2 : 1.8} className="shrink-0" />
                <span
                  className={[
                    'hhIRA text-[14px]',
                    active ? 'font-bold text-[#1f1f1f] dark:text-[#e3e3e3]' : 'font-medium text-[#444746] dark:text-[#bdc1c6]',
                  ].join(' ')}
                >
                  {child.label}
                </span>
              </Link>
            )
          })}
        </div>
      )}
    </div>
  )
}
