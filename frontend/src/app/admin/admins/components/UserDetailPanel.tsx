'use client'
// Google Contacts–style detail panel for Admin / User rows.

import { X, Mail, Star, Pencil, Trash2, MoreVertical, ShieldCheck, UserCog } from 'lucide-react'
import Avatar from '@/components/shared/Avatar'

interface User {
  id: number
  username: string
  first_name: string
  last_name: string
  email: string
  role: string
  department: string
  is_active: boolean
  is_superuser?: boolean
  is_staff?: boolean
  date_joined?: string
  last_login?: string
  org_id?: string
}

interface Props {
  user: User
  onClose: () => void
  onEdit: () => void
  onDelete: () => void
}

function InfoRow({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="flex items-start gap-3 py-2.5 border-b border-[var(--color-border)]">
      <span className="text-[12px] text-[var(--color-text-secondary)] min-w-[120px] pt-px">{label}</span>
      <span className="text-sm text-[var(--color-text-primary)] flex-1">{value || <span className="text-[var(--color-text-muted)]">—</span>}</span>
    </div>
  )
}

function BoolChip({ value, trueLabel = 'Yes', falseLabel = 'No' }: { value?: boolean; trueLabel?: string; falseLabel?: string }) {
  return (
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${value ? 'bg-[var(--color-success-subtle)] text-[var(--color-success-text)]' : 'bg-[var(--color-bg-surface-2)] text-[var(--color-text-secondary)]'}`}>
      {value ? trueLabel : falseLabel}
    </span>
  )
}

export default function UserDetailPanel({ user, onClose, onEdit, onDelete }: Props) {
  const fullName = [user.first_name, user.last_name].filter(Boolean).join(' ') || user.username

  return (
    <>
      {/* Backdrop */}
      <div className="fixed inset-0 z-40 bg-black/[0.18]" onClick={onClose} />

      {/* Panel */}
      <div className="fixed top-0 right-0 bottom-0 z-50 flex flex-col overflow-hidden w-[min(520px,100vw)] bg-[var(--color-bg-surface)] shadow-[-4px_0_24px_rgba(0,0,0,0.14)]">
        {/* ── Top bar ── */}
        <div className="flex items-center justify-between px-4 py-3 shrink-0 border-b border-[var(--color-border)] min-h-[56px]">
          <button onClick={onClose} className="p-1.5 rounded-full transition-colors hover:bg-[var(--color-bg-surface-2)] text-[var(--color-text-secondary)]" title="Close">
            <X size={20} />
          </button>
          <div className="flex items-center gap-1">
            <button className="p-1.5 rounded-full transition-colors hover:bg-[var(--color-bg-surface-2)] text-[var(--color-text-secondary)]" title="Favourite"><Star size={19} /></button>
            <button onClick={onEdit} className="flex items-center gap-1.5 px-4 py-1.5 rounded-full text-sm font-medium transition-colors bg-[var(--color-primary)] text-white">
              <Pencil size={14} /> Edit
            </button>
            <button onClick={onDelete} className="p-1.5 rounded-full transition-colors hover:bg-[var(--color-danger-subtle)] text-[var(--color-text-secondary)]" title="Delete">
              <Trash2 size={19} />
            </button>
            <button className="p-1.5 rounded-full transition-colors hover:bg-[var(--color-bg-surface-2)] text-[var(--color-text-secondary)]" title="More"><MoreVertical size={19} /></button>
          </div>
        </div>

        {/* ── Scrollable body ── */}
        <div className="flex-1 overflow-y-auto px-6 py-6 space-y-6">

          {/* Profile header */}
          <div className="flex flex-col items-center gap-3 text-center">
            <Avatar name={fullName} size="lg" className="!w-20 !h-20" />
            <div>
              <h2 className="text-[22px] font-normal text-[var(--color-text-primary)]">{fullName}</h2>
              <p className="text-sm text-[var(--color-text-secondary)] mt-0.5">@{user.username}</p>
            </div>
            <div className="flex items-center gap-2 flex-wrap justify-center">
              <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-[#fce8e6] text-[#c5221f]">
                <ShieldCheck size={11} /> {user.role || 'ADMIN'}
              </span>
              <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium ${user.is_active ? 'bg-[var(--color-success-subtle)] text-[var(--color-success-text)]' : 'bg-[var(--color-bg-surface-2)] text-[var(--color-text-secondary)]'}`}>
                <span className={`w-1.5 h-1.5 rounded-full inline-block ${user.is_active ? 'bg-[var(--color-success)]' : 'bg-[var(--color-text-muted)]'}`} />
                {user.is_active ? 'Active' : 'Inactive'}
              </span>
            </div>
          </div>

          {/* Action buttons */}
          <div className="flex items-center justify-center gap-4">
            {[{ icon: Mail, label: 'Email', href: `mailto:${user.email}` }].map(({ icon: Icon, label, href }) => (
              <a key={label} href={href} className="flex flex-col items-center gap-1.5 p-3 rounded-xl transition-colors hover:bg-[var(--color-bg-surface-2)]">
                <span className="w-10 h-10 rounded-full flex items-center justify-center bg-[var(--color-bg-surface-2)] text-[var(--color-text-secondary)]">
                  <Icon size={18} />
                </span>
                <span className="text-xs text-[var(--color-text-secondary)]">{label}</span>
              </a>
            ))}
          </div>

          {/* Tag pills */}
          <div className="flex flex-wrap gap-2">
            {user.is_superuser && <span className="flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium bg-[#fef7e0] text-[#b06000] border border-[#f3d47e]">👑 Superuser</span>}
            {user.is_staff && <span className="px-3 py-1 rounded-full text-xs font-medium bg-[var(--color-bg-surface-2)] text-[var(--color-text-secondary)] border border-[var(--color-border)]">Staff</span>}
            {user.department && <span className="px-3 py-1 rounded-full text-xs font-medium bg-[var(--color-primary-subtle)] text-[var(--color-info)] border border-[#c5d9f7]">{user.department}</span>}
          </div>

          {/* Account Details card */}
          <div className="rounded-xl p-4 bg-[var(--color-bg-surface-2)] border border-[var(--color-border)]">
            <h3 className="flex items-center gap-2 font-medium mb-3 text-[13px] text-[var(--color-text-secondary)] uppercase tracking-[0.06em]">
              <UserCog size={13} /> Account Details
            </h3>
            <InfoRow label="Email" value={user.email ? <a href={`mailto:${user.email}`} className="text-[var(--color-text-link)]">{user.email}</a> : null} />
            <InfoRow label="Username" value={user.username} />
            <InfoRow label="Department" value={user.department} />
            {user.date_joined && <InfoRow label="Date Joined" value={new Date(user.date_joined).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' })} />}
          </div>

          {/* Permissions card */}
          <div className="rounded-xl p-4 bg-[var(--color-bg-surface-2)] border border-[var(--color-border)]">
            <h3 className="flex items-center gap-2 font-medium mb-3 text-[13px] text-[var(--color-text-secondary)] uppercase tracking-[0.06em]">
              <ShieldCheck size={13} /> Permissions
            </h3>
            <InfoRow label="Active" value={<BoolChip value={user.is_active} trueLabel="Active" falseLabel="Inactive" />} />
            <InfoRow label="Staff" value={<BoolChip value={user.is_staff} />} />
            <InfoRow label="Superuser" value={<BoolChip value={user.is_superuser} />} />
            <InfoRow label="Role" value={<span className="px-2 py-0.5 rounded-full text-xs font-medium bg-[#fce8e6] text-[#c5221f]">{user.role}</span>} />
          </div>

          {/* History */}
          {user.last_login && (
            <div className="rounded-xl p-4 bg-[var(--color-bg-surface-2)] border border-[var(--color-border)]">
              <h3 className="font-medium mb-3 text-[13px] text-[var(--color-text-secondary)] uppercase tracking-[0.06em]">History</h3>
              <InfoRow label="Last Login" value={new Date(user.last_login).toLocaleString('en-GB', { day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' })} />
            </div>
          )}
        </div>
      </div>
    </>
  )
}
