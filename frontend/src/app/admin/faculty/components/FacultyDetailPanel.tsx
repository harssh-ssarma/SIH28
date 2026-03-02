'use client'
// Google Contacts–style detail page for Faculty rows.

import { ArrowLeft, Mail, Phone, Star, Pencil, Trash2, MoreVertical, Users, BookOpen, Clock } from 'lucide-react'
import Avatar from '@/components/shared/Avatar'

interface Faculty {
  id: number
  faculty_id: string
  faculty_code: string
  first_name: string
  middle_name?: string
  last_name: string
  designation: string
  specialization: string
  department: { dept_id: string; dept_name: string }
  max_workload: number
  status: string
  email?: string
  phone?: string
  employment_type?: string
  date_of_joining?: string
  highest_qualification?: string
  is_hod?: boolean
  is_dean?: boolean
  can_approve_timetable?: boolean
  max_credits_per_semester?: number
  max_hours_per_week?: number
  max_consecutive_hours?: number
  last_login?: string
  created_at?: string
}

interface Props {
  faculty: Faculty
  onClose: () => void
  onEdit: () => void
  onDelete: () => void
}

function InfoRow({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="flex items-start gap-3 py-2.5 border-b border-[var(--color-border)]">
      <span className="text-[12px] text-[var(--color-text-secondary)] min-w-[130px] pt-px">{label}</span>
      <span className="text-sm text-[var(--color-text-primary)] flex-1">{value || <span className="text-[var(--color-text-muted)]">—</span>}</span>
    </div>
  )
}

function StatCard({ icon: Icon, label, value }: { icon: React.ElementType; label: string; value: React.ReactNode }) {
  return (
    <div className="flex items-center gap-3 p-3 rounded-lg bg-[var(--color-bg-surface)] border border-[var(--color-border)]">
      <span className="w-8 h-8 rounded-full flex items-center justify-center shrink-0 bg-[#e6f4ea] text-[#188038]">
        <Icon size={15} />
      </span>
      <div>
        <div className="text-[13px] text-[var(--color-text-secondary)]">{label}</div>
        <div className="text-sm font-medium text-[var(--color-text-primary)]">{value ?? '—'}</div>
      </div>
    </div>
  )
}

export default function FacultyDetailPanel({ faculty, onClose, onEdit, onDelete }: Props) {
  const fullName = [faculty.first_name, faculty.middle_name, faculty.last_name].filter(Boolean).join(' ')

  return (
    <div className="flex flex-col min-h-full w-full">
      {/* Top bar */}
      <div className="flex items-center justify-between px-2 py-3 shrink-0 border-b border-[var(--color-border)] min-h-[56px]">
        <button onClick={onClose} className="p-1.5 rounded-full transition-colors hover:bg-[var(--color-bg-surface-2)] text-[var(--color-text-secondary)]" title="Back"><ArrowLeft size={20} /></button>
        <div className="flex items-center gap-1">
          <button className="p-1.5 rounded-full transition-colors hover:bg-[var(--color-bg-surface-2)] text-[var(--color-text-secondary)]" title="Favourite"><Star size={19} /></button>
          <button onClick={onEdit} className="flex items-center gap-1.5 px-4 py-1.5 rounded-full text-sm font-medium transition-colors bg-[#188038] text-white">
            <Pencil size={14} /> Edit
          </button>
          <button onClick={onDelete} className="p-1.5 rounded-full transition-colors hover:bg-[var(--color-danger-subtle)] text-[var(--color-text-secondary)]" title="Delete"><Trash2 size={19} /></button>
          <button className="p-1.5 rounded-full transition-colors hover:bg-[var(--color-bg-surface-2)] text-[var(--color-text-secondary)]" title="More actions"><MoreVertical size={19} /></button>
        </div>
      </div>

      {/* Scrollable body */}
      <div className="flex-1 overflow-y-auto px-4 py-4 md:px-8 md:py-8">
        {/* Profile header */}
        <div className="flex flex-col items-center md:flex-row md:items-start gap-4 md:gap-8 mb-8">
          <div className="md:hidden"><Avatar name={fullName} size={80} /></div>
          <div className="hidden md:block"><Avatar name={fullName} size={162} className="shrink-0" /></div>
          <div className="pt-1 text-center md:text-left">
            <h2 className="text-[28px] font-normal text-[var(--color-text-primary)] leading-tight">{fullName}</h2>
            <p className="text-sm text-[var(--color-text-secondary)] mt-0.5">{faculty.faculty_code}</p>
            <div className="flex items-center justify-center md:justify-start gap-2 flex-wrap mt-2">
              <span className="px-2.5 py-0.5 rounded-full text-xs font-medium bg-[#e6f4ea] text-[#137333]">{faculty.designation}</span>
              <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${faculty.status === 'active' ? 'bg-[#e6f4ea] text-[#137333]' : 'bg-[var(--color-bg-surface-2)] text-[var(--color-text-secondary)]'}`}>
                {faculty.status}
              </span>
              {faculty.employment_type && (
                <span className="px-2.5 py-0.5 rounded-full text-xs font-medium bg-[#e8f0fe] text-[#1967d2]">{faculty.employment_type.replace('_', ' ')}</span>
              )}
            </div>
          </div>
        </div>

        {/* Action buttons */}
        <div className="flex items-center justify-center md:justify-start gap-4 mb-8 pb-6 border-b border-[var(--color-border)]">
          {faculty.email && (
            <a href={`mailto:${faculty.email}`} className="flex flex-col items-center gap-1.5 p-3 rounded-xl transition-colors hover:bg-[var(--color-bg-surface-2)]">
              <span className="w-10 h-10 rounded-full flex items-center justify-center bg-[var(--color-bg-surface-2)] text-[var(--color-text-secondary)]"><Mail size={18} /></span>
              <span className="text-xs text-[var(--color-text-secondary)]">Email</span>
            </a>
          )}
          {faculty.phone && (
            <a href={`tel:${faculty.phone}`} className="flex flex-col items-center gap-1.5 p-3 rounded-xl transition-colors hover:bg-[var(--color-bg-surface-2)]">
              <span className="w-10 h-10 rounded-full flex items-center justify-center bg-[var(--color-bg-surface-2)] text-[var(--color-text-secondary)]"><Phone size={18} /></span>
              <span className="text-xs text-[var(--color-text-secondary)]">Call</span>
            </a>
          )}
        </div>

        {/* Role pills */}
        <div className="flex flex-wrap gap-2 mb-6">
          {faculty.is_hod && <span className="px-3 py-1 rounded-full text-xs font-medium bg-[#fef7e0] text-[#b06000] border border-[#f3d47e]">HOD</span>}
          {faculty.is_dean && <span className="px-3 py-1 rounded-full text-xs font-medium bg-[#fef7e0] text-[#b06000] border border-[#f3d47e]">Dean</span>}
          {faculty.can_approve_timetable && <span className="px-3 py-1 rounded-full text-xs font-medium bg-[#e8f0fe] text-[#1967d2] border border-[#c5d9f7]">Can Approve Timetable</span>}
        </div>

        {/* Two-column cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="rounded-xl p-4 bg-[var(--color-bg-surface-2)] border border-[var(--color-border)]">
            <h3 className="flex items-center gap-2 font-medium mb-3 text-[13px] text-[var(--color-text-secondary)] uppercase tracking-[0.06em]">
              <Users size={13} /> Personal Details
            </h3>
            {faculty.email && <InfoRow label="Email" value={<a href={`mailto:${faculty.email}`} className="text-[var(--color-text-link)]">{faculty.email}</a>} />}
            {faculty.phone && <InfoRow label="Phone" value={<a href={`tel:${faculty.phone}`} className="text-[var(--color-text-link)]">{faculty.phone}</a>} />}
            <InfoRow label="Department" value={faculty.department?.dept_name} />
            <InfoRow label="Specialization" value={faculty.specialization} />
            {faculty.highest_qualification && <InfoRow label="Qualification" value={faculty.highest_qualification} />}
            {faculty.date_of_joining && <InfoRow label="Joined" value={new Date(faculty.date_of_joining).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' })} />}
          </div>

          <div className="rounded-xl p-4 bg-[var(--color-bg-surface-2)] border border-[var(--color-border)]">
            <h3 className="flex items-center gap-2 font-medium mb-3 text-[13px] text-[var(--color-text-secondary)] uppercase tracking-[0.06em]">
              <BookOpen size={13} /> Workload Limits
            </h3>
            <div className="grid grid-cols-2 gap-2">
              <StatCard icon={Clock} label="Max hrs/week" value={`${faculty.max_workload}h`} />
              {faculty.max_credits_per_semester != null && <StatCard icon={BookOpen} label="Max credits/sem" value={faculty.max_credits_per_semester} />}
              {faculty.max_hours_per_week != null && <StatCard icon={Clock} label="Total hrs/week" value={`${faculty.max_hours_per_week}h`} />}
              {faculty.max_consecutive_hours != null && <StatCard icon={Clock} label="Max consecutive" value={`${faculty.max_consecutive_hours}h`} />}
            </div>
          </div>

          {(faculty.last_login || faculty.created_at) && (
            <div className="rounded-xl p-4 bg-[var(--color-bg-surface-2)] border border-[var(--color-border)]">
              <h3 className="font-medium mb-3 text-[13px] text-[var(--color-text-secondary)] uppercase tracking-[0.06em]">History</h3>
              {faculty.created_at && <InfoRow label="Created" value={new Date(faculty.created_at).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' })} />}
              {faculty.last_login && <InfoRow label="Last Login" value={new Date(faculty.last_login).toLocaleString('en-GB', { day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' })} />}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
