'use client'
// Google Contacts–style detail panel for Student rows.

import { X, Mail, Phone, Star, Pencil, Trash2, MoreVertical, GraduationCap, BookOpen, User } from 'lucide-react'
import Avatar from '@/components/shared/Avatar'

interface Student {
  id: number
  student_id: string
  name: string
  email?: string
  phone?: string
  department: { department_id: string; department_name: string }
  course: { course_id: string; course_name: string }
  electives: string
  year: number
  semester: number
  faculty_advisor: { faculty_id: string; faculty_name: string } | null
  enrollment_number?: string
  roll_number?: string
  cgpa?: number
  academic_status?: string
  admission_date?: string
  admission_year?: number
  blood_group?: string
  address?: string
  city?: string
  state?: string
  is_hosteller?: boolean
  hostel_name?: string
  room_number?: string
  fee_status?: string
  scholarship?: string
  last_login?: string
  created_at?: string
  updated_at?: string
}

interface Props {
  student: Student
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

const FEE_CLASSES: Record<string, string> = {
  PAID:    'bg-[#e6f4ea] text-[#137333]',
  UNPAID:  'bg-[#fce8e6] text-[#c5221f]',
  PARTIAL: 'bg-[#fef7e0] text-[#b06000]',
  WAIVED:  'bg-[#e8f0fe] text-[#1967d2]',
}

export default function StudentDetailPanel({ student, onClose, onEdit, onDelete }: Props) {
  const semLabel = student.semester ? `Sem ${student.semester}` : null
  const yearLabel = student.year ? `Year ${student.year}` : null
  const feeClass = student.fee_status
    ? (FEE_CLASSES[student.fee_status] ?? 'bg-[var(--color-bg-surface-2)] text-[var(--color-text-secondary)]')
    : ''

  return (
    <>
      <div className="fixed inset-0 z-40 bg-black/[0.18]" onClick={onClose} />
      <div className="fixed top-0 right-0 bottom-0 z-50 flex flex-col overflow-hidden w-[min(540px,100vw)] bg-[var(--color-bg-surface)] shadow-[-4px_0_24px_rgba(0,0,0,0.14)]">
        {/* Top bar */}
        <div className="flex items-center justify-between px-4 py-3 shrink-0 border-b border-[var(--color-border)] min-h-[56px]">
          <button onClick={onClose} className="p-1.5 rounded-full transition-colors hover:bg-[var(--color-bg-surface-2)] text-[var(--color-text-secondary)]" title="Close"><X size={20} /></button>
          <div className="flex items-center gap-1">
            <button className="p-1.5 rounded-full transition-colors hover:bg-[var(--color-bg-surface-2)] text-[var(--color-text-secondary)]" title="Favourite"><Star size={19} /></button>
            <button onClick={onEdit} className="flex items-center gap-1.5 px-4 py-1.5 rounded-full text-sm font-medium bg-[var(--color-primary)] text-white">
              <Pencil size={14} /> Edit
            </button>
            <button onClick={onDelete} className="p-1.5 rounded-full transition-colors hover:bg-[var(--color-danger-subtle)] text-[var(--color-text-secondary)]" title="Delete"><Trash2 size={19} /></button>
            <button className="p-1.5 rounded-full transition-colors hover:bg-[var(--color-bg-surface-2)] text-[var(--color-text-secondary)]" title="More actions"><MoreVertical size={19} /></button>
          </div>
        </div>

        {/* Scrollable body */}
        <div className="flex-1 overflow-y-auto px-6 py-6 space-y-6">

          {/* Profile header */}
          <div className="flex flex-col items-center gap-3 text-center">
            <Avatar name={student.name} size="lg" className="!w-20 !h-20" />
            <div>
              <h2 className="text-[22px] font-normal text-[var(--color-text-primary)]">{student.name}</h2>
              <p className="text-[13px] text-[var(--color-text-secondary)] font-mono mt-0.5">{student.student_id}</p>
            </div>
            <div className="flex items-center gap-2 flex-wrap justify-center">
              <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-[#e8f0fe] text-[#1967d2]">
                <GraduationCap size={11} /> Student
              </span>
              {student.academic_status && (
                <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${student.academic_status === 'ACTIVE' ? 'bg-[#e6f4ea] text-[#137333]' : 'bg-[#fef7e0] text-[#b06000]'}`}>
                  {student.academic_status}
                </span>
              )}
            </div>
          </div>

          {/* Action buttons */}
          <div className="flex items-center justify-center gap-4">
            {student.email && (
              <a href={`mailto:${student.email}`} className="flex flex-col items-center gap-1.5 p-3 rounded-xl transition-colors hover:bg-[var(--color-bg-surface-2)]">
                <span className="w-10 h-10 rounded-full flex items-center justify-center bg-[var(--color-bg-surface-2)] text-[var(--color-text-secondary)]"><Mail size={18} /></span>
                <span className="text-xs text-[var(--color-text-secondary)]">Email</span>
              </a>
            )}
            {student.phone && (
              <a href={`tel:${student.phone}`} className="flex flex-col items-center gap-1.5 p-3 rounded-xl transition-colors hover:bg-[var(--color-bg-surface-2)]">
                <span className="w-10 h-10 rounded-full flex items-center justify-center bg-[var(--color-bg-surface-2)] text-[var(--color-text-secondary)]"><Phone size={18} /></span>
                <span className="text-xs text-[var(--color-text-secondary)]">Call</span>
              </a>
            )}
          </div>

          {/* Tag pills */}
          <div className="flex flex-wrap gap-2">
            {yearLabel && <span className="px-3 py-1 rounded-full text-xs font-medium bg-[#e8f0fe] text-[#1967d2] border border-[#c5d9f7]">{yearLabel}</span>}
            {semLabel && <span className="px-3 py-1 rounded-full text-xs font-medium bg-[#e6f4ea] text-[#137333] border border-[#b5d9c1]">{semLabel}</span>}
            {student.enrollment_number && <span className="px-3 py-1 rounded-full text-xs font-medium bg-[var(--color-bg-surface-2)] text-[var(--color-text-secondary)] border border-[var(--color-border)]">Enroll: {student.enrollment_number}</span>}
          </div>

          {/* Academic Details */}
          <div className="rounded-xl p-4 bg-[var(--color-bg-surface-2)] border border-[var(--color-border)]">
            <h3 className="flex items-center gap-2 font-medium mb-3 text-[13px] text-[var(--color-text-secondary)] uppercase tracking-[0.06em]">
              <BookOpen size={13} /> Academic Details
            </h3>
            <InfoRow label="Department" value={student.department?.department_name} />
            <InfoRow label="Course" value={student.course?.course_name} />
            <InfoRow label="Year / Semester" value={[yearLabel, semLabel].filter(Boolean).join(' · ')} />
            {student.electives && <InfoRow label="Electives" value={student.electives} />}
            {student.admission_date && <InfoRow label="Admission Date" value={new Date(student.admission_date).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' })} />}
            {student.cgpa != null && (
              <InfoRow label="CGPA" value={
                <span className="flex items-center gap-1.5">
                  <span className="font-semibold">{student.cgpa.toFixed(2)}</span>
                  <span className="text-xs text-[var(--color-text-muted)]">/ 10</span>
                </span>
              } />
            )}
            {student.faculty_advisor && <InfoRow label="Faculty Advisor" value={
              <span className="flex items-center gap-1 text-[var(--color-text-secondary)]"><User size={12} />{student.faculty_advisor.faculty_name}</span>
            } />}
          </div>

          {/* Personal Details */}
          {(student.email || student.phone || student.blood_group || student.city) && (
            <div className="rounded-xl p-4 bg-[var(--color-bg-surface-2)] border border-[var(--color-border)]">
              <h3 className="flex items-center gap-2 font-medium mb-3 text-[13px] text-[var(--color-text-secondary)] uppercase tracking-[0.06em]">
                <User size={13} /> Personal Details
              </h3>
              {student.email && <InfoRow label="Email" value={<a href={`mailto:${student.email}`} className="text-[var(--color-text-link)]">{student.email}</a>} />}
              {student.phone && <InfoRow label="Phone" value={<a href={`tel:${student.phone}`} className="text-[var(--color-text-link)]">{student.phone}</a>} />}
              {student.blood_group && <InfoRow label="Blood Group" value={student.blood_group} />}
              {student.city && <InfoRow label="City / State" value={[student.city, student.state].filter(Boolean).join(', ')} />}
            </div>
          )}

          {/* Hostel & Finance */}
          {(student.is_hosteller != null || student.fee_status) && (
            <div className="rounded-xl p-4 bg-[var(--color-bg-surface-2)] border border-[var(--color-border)]">
              <h3 className="font-medium mb-3 text-[13px] text-[var(--color-text-secondary)] uppercase tracking-[0.06em]">Hostel & Finance</h3>
              <InfoRow label="Hosteller" value={
                <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${student.is_hosteller ? 'bg-[#e6f4ea] text-[#137333]' : 'bg-[var(--color-bg-surface-2)] text-[var(--color-text-secondary)]'}`}>
                  {student.is_hosteller ? 'Yes' : 'No'}
                </span>
              } />
              {student.hostel_name && <InfoRow label="Hostel / Room" value={`${student.hostel_name}${student.room_number ? ` · Room ${student.room_number}` : ''}`} />}
              {student.fee_status && feeClass && <InfoRow label="Fee Status" value={<span className={`px-2 py-0.5 rounded-full text-xs font-medium ${feeClass}`}>{student.fee_status}</span>} />}
              {student.scholarship && <InfoRow label="Scholarship" value={student.scholarship} />}
            </div>
          )}

          {/* History */}
          {(student.last_login || student.created_at) && (
            <div className="rounded-xl p-4 bg-[var(--color-bg-surface-2)] border border-[var(--color-border)]">
              <h3 className="font-medium mb-3 text-[13px] text-[var(--color-text-secondary)] uppercase tracking-[0.06em]">History</h3>
              {student.created_at && <InfoRow label="Added" value={new Date(student.created_at).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' })} />}
              {student.updated_at && <InfoRow label="Last Updated" value={new Date(student.updated_at).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' })} />}
              {student.last_login && <InfoRow label="Last Login" value={new Date(student.last_login).toLocaleString('en-GB', { day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' })} />}
            </div>
          )}
        </div>
      </div>
    </>
  )
}
