'use client'

/**
 * DepartmentTree - collapsible department selector.
 * Desktop: 240px left sidebar. Mobile: compact dropdown.
 */

import { useState } from 'react'
import { ChevronDown, ChevronRight, BookOpen, Building2 } from 'lucide-react'
import type { DepartmentOption } from '@/types/timetable'

interface DepartmentTreeProps {
  departments: DepartmentOption[]
  selectedDeptId: string
  onSelect: (deptId: string) => void
  loading?: boolean
}

function DeptRow({ dept, isActive, onClick }: { dept: DepartmentOption; isActive: boolean; onClick: () => void }) {
  return (
    <button
      type="button"
      onClick={onClick}
      title={dept.name}
      className={[
        'flex items-center gap-2 w-full px-[10px] py-[7px] rounded-lg border-0 cursor-pointer text-[13px] text-left transition-colors duration-100',
        isActive ? 'bg-[#c2e7ff] font-semibold text-[#1a1a1a]' : 'bg-transparent font-normal [color:var(--color-text-secondary)]',
      ].join(' ')}
    >
      <Building2
        size={14}
        className={['shrink-0', isActive ? 'text-[#1a73e8]' : '[color:var(--color-text-muted)]'].join(' ')}
      />
      <span className="truncate flex-1">{dept.name}</span>
      {dept.total_entries !== undefined && (
        <span className="text-[10px] shrink-0 px-[5px] py-[1px] rounded [color:var(--color-text-muted)] [background:var(--color-bg-surface-3)]">
          {dept.total_entries}
        </span>
      )}
    </button>
  )
}

function TreeSkeleton() {
  return (
    <div className="flex flex-col gap-1">
      {[1, 2, 3, 4, 5].map((i) => (
        <div key={i} className="animate-pulse h-8 rounded-lg [background:var(--color-bg-surface-3)]" />
      ))}
    </div>
  )
}

function NoDepts() {
  return (
    <div className="flex flex-col items-center py-6 gap-2">
      <BookOpen size={28} className="[color:var(--color-text-muted)]" />
      <p className="text-xs text-center [color:var(--color-text-muted)]">No departments found</p>
    </div>
  )
}

function MobileDropdown({ departments, selectedDeptId, onSelect }: Omit<DepartmentTreeProps, 'loading'>) {
  return (
    <select
      value={selectedDeptId}
      onChange={(e) => onSelect(e.target.value)}
      aria-label="Filter by department"
      title="Filter by department"
      className="w-full px-3 py-2 rounded-lg text-[13px] border [background:var(--color-bg-surface)] [color:var(--color-text-primary)] [border-color:var(--color-border)]"
    >
      <option value="all">All Departments</option>
      {departments.map((d) => (
        <option key={d.id} value={d.id}>{d.name}</option>
      ))}
    </select>
  )
}

export function DepartmentTree({ departments, selectedDeptId, onSelect, loading = false }: DepartmentTreeProps) {
  const [expanded, setExpanded] = useState(true)

  return (
    <>
      {/* Desktop sidebar tree */}
      <div className="hidden md:flex flex-col gap-[2px] w-[240px] shrink-0">
        <button
          type="button"
          className={[
            'flex items-center justify-between w-full px-[10px] py-[7px] rounded-lg border-0 cursor-pointer text-[13px] text-left transition-colors duration-100',
            selectedDeptId === 'all' ? 'bg-[#c2e7ff] font-bold text-[#1a1a1a]' : 'bg-transparent font-medium [color:var(--color-text-secondary)]',
          ].join(' ')}
          onClick={() => { onSelect('all'); setExpanded(true) }}
        >
          <span className="flex items-center gap-[6px]">
            <Building2 size={14} className="shrink-0" />
            All Departments
          </span>
          <span
            className="flex cursor-pointer"
            onClick={(e) => { e.stopPropagation(); setExpanded(!expanded) }}
          >
            {expanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
          </span>
        </button>

        {expanded && (
          <div className="pl-2 flex flex-col gap-[1px]">
            {loading
              ? <TreeSkeleton />
              : departments.length === 0
                ? <NoDepts />
                : departments.map((dept) => (
                    <DeptRow
                      key={dept.id}
                      dept={dept}
                      isActive={selectedDeptId === dept.id}
                      onClick={() => onSelect(dept.id)}
                    />
                  ))}
          </div>
        )}
      </div>

      {/* Mobile dropdown */}
      <div className="flex md:hidden w-full">
        <MobileDropdown departments={departments} selectedDeptId={selectedDeptId} onSelect={onSelect} />
      </div>
    </>
  )
}
