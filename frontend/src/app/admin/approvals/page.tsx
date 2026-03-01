'use client'

import { useCallback, useEffect, useRef, useState } from 'react'
import { CheckCircle, Clock, AlertTriangle, Zap, CheckCheck, X, Loader2 } from 'lucide-react'
import apiClient from '@/lib/api'
import { useToast } from '@/components/Toast'
import type { WorkflowListItem } from '@/types/timetable'

// ── Constants ───────────────────────────────────────────────────────────────
const SEMESTER_LABEL: Record<number, string> = {
  1: 'Sem I', 2: 'Sem II', 3: 'Sem III', 4: 'Sem IV',
  5: 'Sem V', 6: 'Sem VI', 7: 'Sem VII', 8: 'Sem VIII',
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString('en-IN', {
    day: '2-digit', month: 'short', year: 'numeric',
  })
}

// ── Skeleton row ────────────────────────────────────────────────────────────
function SkeletonRow() {
  return (
    <tr className="table-row animate-pulse">
      {[120, 80, 80, 80, 100].map((w, i) => (
        <td key={i} className="table-cell">
          <div className="h-4 rounded" style={{ width: w, background: 'var(--color-bg-surface-2)' }} />
        </td>
      ))}
      <td className="table-cell">
        <div className="flex gap-2">
          <div className="h-8 w-20 rounded-full" style={{ background: 'var(--color-bg-surface-2)' }} />
          <div className="h-8 w-20 rounded-full" style={{ background: 'var(--color-bg-surface-2)' }} />
        </div>
      </td>
    </tr>
  )
}

// ── Empty state ─────────────────────────────────────────────────────────────
function EmptyState() {
  return (
    <div className="py-16 flex flex-col items-center gap-4">
      <div
        className="w-16 h-16 rounded-full flex items-center justify-center"
        style={{ background: 'var(--color-success-subtle)' }}
      >
        <CheckCheck className="w-8 h-8" style={{ color: 'var(--color-success)' }} />
      </div>
      <div className="text-center">
        <h3 className="text-base font-semibold" style={{ color: 'var(--color-text-primary)' }}>
          All caught up!
        </h3>
        <p className="text-sm mt-1" style={{ color: 'var(--color-text-secondary)' }}>
          No timetables are pending approval right now.
        </p>
      </div>
    </div>
  )
}

// ── Rejection Modal ──────────────────────────────────────────────────────────
interface RejectModalProps {
  jobId: string
  onConfirm: (reason: string) => void
  onCancel: () => void
  loading: boolean
}

function RejectModal({ jobId: _jobId, onConfirm, onCancel, loading }: RejectModalProps) {
  const [reason, setReason] = useState('')
  const textRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => { textRef.current?.focus() }, [])

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      style={{ background: 'rgba(0,0,0,0.45)' }}
      onClick={e => { if (e.target === e.currentTarget) onCancel() }}
    >
      <div
        className="w-full max-w-md rounded-2xl shadow-xl p-6 flex flex-col gap-4"
        style={{ background: 'var(--color-bg-surface)', border: '1px solid var(--color-border)' }}
      >
        <div className="flex items-center justify-between">
          <h2 className="text-base font-semibold" style={{ color: 'var(--color-text-primary)' }}>
            Reject timetable
          </h2>
          <button
            onClick={onCancel}
            className="w-8 h-8 rounded-full flex items-center justify-center transition-colors duration-200"
            style={{ color: 'var(--color-text-muted)' }}
            aria-label="Close rejection dialog"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        <p className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>
          Please provide a reason. This will be visible to the person who generated the timetable.
        </p>

        <textarea
          ref={textRef}
          value={reason}
          onChange={e => setReason(e.target.value)}
          placeholder="e.g. Faculty conflicts on Monday period 3-4..."
          rows={4}
          className="input-primary w-full resize-none text-sm"
        />

        <div className="flex justify-end gap-3 pt-1">
          <button onClick={onCancel} className="btn-secondary text-sm px-5" disabled={loading}>
            Cancel
          </button>
          <button
            onClick={() => onConfirm(reason.trim())}
            disabled={!reason.trim() || loading}
            className="flex items-center gap-2 rounded-full px-5 py-2 text-sm font-medium transition-all duration-200 disabled:opacity-50"
            style={{ background: 'var(--color-danger)', color: '#fff' }}
          >
            {loading && <Loader2 className="w-3.5 h-3.5 animate-spin" />}
            Confirm rejection
          </button>
        </div>
      </div>
    </div>
  )
}

// ── Mobile approval card ─────────────────────────────────────────────────────
interface CardProps {
  item: WorkflowListItem
  actionLoading: boolean
  onApprove: () => void
  onReject: () => void
}

function ApprovalCard({ item, actionLoading, onApprove, onReject }: CardProps) {
  return (
    <div
      className="p-4 rounded-2xl border transition-opacity duration-200"
      style={{
        background: 'var(--color-bg-surface)',
        borderColor: 'var(--color-border)',
        opacity: actionLoading ? 0.6 : 1,
      }}
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1 min-w-0">
          <p className="font-medium text-sm" style={{ color: 'var(--color-text-primary)' }}>
            {item.academic_year || '—'}
          </p>
          <p className="text-xs mt-0.5" style={{ color: 'var(--color-text-secondary)' }}>
            {item.semester ? (SEMESTER_LABEL[item.semester] ?? `Semester ${item.semester}`) : '—'}
          </p>
        </div>
        <span className="badge badge-warning ml-2 shrink-0">Pending</span>
      </div>
      <p className="text-xs mb-3" style={{ color: 'var(--color-text-muted)' }}>
        Submitted {formatDate(item.created_at)}
      </p>
      <div className="flex gap-2">
        <button
          onClick={onReject}
          disabled={actionLoading}
          className="flex-1 rounded-full border text-sm py-2 font-medium transition-colors duration-200"
          style={{ borderColor: 'var(--color-danger)', color: 'var(--color-danger)' }}
        >
          Reject
        </button>
        <button
          onClick={onApprove}
          disabled={actionLoading}
          className="flex-1 rounded-full text-sm py-2 font-medium text-white transition-opacity duration-200 disabled:opacity-50"
          style={{ background: '#1a73e8' }}
        >
          {actionLoading ? <Loader2 className="w-4 h-4 animate-spin mx-auto" /> : 'Approve'}
        </button>
      </div>
    </div>
  )
}

// ── Main page ────────────────────────────────────────────────────────────────
export default function AdminApprovals() {
  const { showSuccessToast, showErrorToast } = useToast()

  const [workflows, setWorkflows] = useState<WorkflowListItem[]>([])
  const [loading, setLoading] = useState(true)
  const [actionLoading, setActionLoading] = useState<Set<string>>(new Set())
  const [rejectTarget, setRejectTarget] = useState<string | null>(null)
  const [rejectSubmitting, setRejectSubmitting] = useState(false)

  // ── Fetch ────────────────────────────────────────────────────────────────
  const fetchWorkflows = useCallback(async () => {
    setLoading(true)
    const res = await apiClient.getWorkflows('completed')
    if (res.data?.results) {
      setWorkflows(res.data.results)
    } else if (res.error) {
      showErrorToast(`Failed to load approvals: ${res.error}`)
    }
    setLoading(false)
  }, [showErrorToast])

  useEffect(() => { fetchWorkflows() }, [fetchWorkflows])

  // ── Optimistic helpers ───────────────────────────────────────────────────
  const markActionLoading = (id: string, on: boolean) =>
    setActionLoading(prev => { const s = new Set(prev); on ? s.add(id) : s.delete(id); return s })

  const removeOptimistically = (id: string) =>
    setWorkflows(prev => prev.filter(w => w.id !== id))

  const restoreOnError = (item: WorkflowListItem) =>
    setWorkflows(prev =>
      [item, ...prev].sort(
        (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      )
    )

  // ── Approve ──────────────────────────────────────────────────────────────
  const handleApprove = useCallback(async (item: WorkflowListItem) => {
    markActionLoading(item.id, true)
    removeOptimistically(item.id)
    const res = await apiClient.approveWorkflow(item.id, '')
    markActionLoading(item.id, false)
    if (res.error) {
      restoreOnError(item)
      showErrorToast(`Approval failed: ${res.error}`)
    } else {
      showSuccessToast('Timetable approved successfully')
    }
  }, [showSuccessToast, showErrorToast])  // eslint-disable-line react-hooks/exhaustive-deps

  // ── Reject ───────────────────────────────────────────────────────────────
  const handleRejectConfirm = useCallback(async (reason: string) => {
    if (!rejectTarget) return
    const item = workflows.find(w => w.id === rejectTarget)
    if (!item) { setRejectTarget(null); return }
    setRejectSubmitting(true)
    removeOptimistically(item.id)
    const res = await apiClient.rejectWorkflow(item.id, reason)
    setRejectSubmitting(false)
    setRejectTarget(null)
    if (res.error) {
      restoreOnError(item)
      showErrorToast(`Rejection failed: ${res.error}`)
    } else {
      showSuccessToast('Timetable rejected')
    }
  }, [rejectTarget, workflows, showSuccessToast, showErrorToast])  // eslint-disable-line react-hooks/exhaustive-deps

  // ── Derived stats ────────────────────────────────────────────────────────
  const totalPending = workflows.length
  const todayStr = new Date().toDateString()
  const submittedToday = workflows.filter(
    w => new Date(w.created_at).toDateString() === todayStr
  ).length

  return (
    <div className="space-y-4 sm:space-y-6">

      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-normal tracking-tight [color:var(--color-text-primary)]">
            Approvals
          </h1>
        </div>
        <button
          onClick={fetchWorkflows}
          disabled={loading}
          className="btn-secondary self-start sm:self-auto flex items-center gap-2 text-sm"
        >
          {loading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Zap className="w-3.5 h-3.5" />}
          Refresh
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>Total Pending</p>
              <p className="text-2xl font-bold mt-1" style={{ color: 'var(--color-text-primary)' }}>
                {loading ? '—' : totalPending}
              </p>
            </div>
            <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ background: 'var(--color-warning-subtle)' }}>
              <Clock className="w-5 h-5" style={{ color: 'var(--color-warning-text)' }} />
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>Submitted Today</p>
              <p className="text-2xl font-bold mt-1" style={{ color: 'var(--color-info-text)' }}>
                {loading ? '—' : submittedToday}
              </p>
            </div>
            <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ background: 'var(--color-info-subtle)' }}>
              <AlertTriangle className="w-5 h-5" style={{ color: 'var(--color-info-text)' }} />
            </div>
          </div>
        </div>

        <div className="card sm:col-span-2 lg:col-span-1">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>Status</p>
              <p
                className="text-base font-semibold mt-1"
                style={{ color: totalPending === 0 ? 'var(--color-success-text)' : 'var(--color-warning-text)' }}
              >
                {loading ? '—' : totalPending === 0 ? 'All clear' : `${totalPending} awaiting review`}
              </p>
            </div>
            <div
              className="w-10 h-10 rounded-xl flex items-center justify-center"
              style={{ background: totalPending === 0 ? 'var(--color-success-subtle)' : 'var(--color-warning-subtle)' }}
            >
              <CheckCircle
                className="w-5 h-5"
                style={{ color: totalPending === 0 ? 'var(--color-success-text)' : 'var(--color-warning-text)' }}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Pending Requests */}
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">Pending Timetables</h3>
          <p className="card-description">
            {loading ? 'Loading...' : `${totalPending} timetable${totalPending !== 1 ? 's' : ''} awaiting your review`}
          </p>
        </div>

        {/* Mobile cards */}
        <div className="block sm:hidden space-y-3">
          {loading
            ? Array.from({ length: 3 }).map((_, i) => (
                <div
                  key={i}
                  className="h-32 rounded-2xl animate-pulse"
                  style={{ background: 'var(--color-bg-surface-2)' }}
                />
              ))
            : workflows.length === 0
              ? <EmptyState />
              : workflows.map(item => (
                  <ApprovalCard
                    key={item.id}
                    item={item}
                    actionLoading={actionLoading.has(item.id)}
                    onApprove={() => handleApprove(item)}
                    onReject={() => setRejectTarget(item.id)}
                  />
                ))}
        </div>

        {/* Desktop table */}
        <div className="hidden sm:block overflow-x-auto">
          {loading ? (
            <table className="table">
              <thead className="table-header">
                <tr>
                  {['Academic Year', 'Semester', 'Submitted', 'Status', 'ID', 'Actions'].map(h => (
                    <th key={h} className="table-header-cell">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {Array.from({ length: 4 }).map((_, i) => <SkeletonRow key={i} />)}
              </tbody>
            </table>
          ) : workflows.length === 0 ? (
            <EmptyState />
          ) : (
            <table className="table">
              <thead className="table-header">
                <tr>
                  {['Academic Year', 'Semester', 'Submitted', 'Status', 'ID', 'Actions'].map(h => (
                    <th key={h} className="table-header-cell">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {workflows.map(item => (
                  <tr
                    key={item.id}
                    className="table-row transition-opacity duration-200"
                    style={{ opacity: actionLoading.has(item.id) ? 0.5 : 1 }}
                  >
                    <td className="table-cell font-medium" style={{ color: 'var(--color-text-primary)' }}>
                      {item.academic_year || '—'}
                    </td>
                    <td className="table-cell">
                      {item.semester ? (SEMESTER_LABEL[item.semester] ?? `Sem ${item.semester}`) : '—'}
                    </td>
                    <td className="table-cell">{formatDate(item.created_at)}</td>
                    <td className="table-cell">
                      <span className="badge badge-warning">Pending</span>
                    </td>
                    <td className="table-cell">
                      <code className="text-xs" style={{ color: 'var(--color-text-muted)' }}>
                        {item.id.slice(0, 8)}...
                      </code>
                    </td>
                    <td className="table-cell">
                      <div className="flex gap-2">
                        <button
                          onClick={() => setRejectTarget(item.id)}
                          disabled={actionLoading.has(item.id)}
                          className="rounded-full border px-5 py-1.5 text-xs font-medium transition-colors duration-200 disabled:opacity-50"
                          style={{ borderColor: 'var(--color-danger)', color: 'var(--color-danger)' }}
                        >
                          Reject
                        </button>
                        <button
                          onClick={() => handleApprove(item)}
                          disabled={actionLoading.has(item.id)}
                          className="rounded-full px-5 py-1.5 text-xs font-medium text-white transition-opacity duration-200 disabled:opacity-50 flex items-center gap-1.5"
                          style={{ background: '#1a73e8' }}
                        >
                          {actionLoading.has(item.id)
                            ? <Loader2 className="w-3.5 h-3.5 animate-spin" />
                            : <CheckCircle className="w-3.5 h-3.5" />}
                          Approve
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>

      {/* Rejection Modal */}
      {rejectTarget && (
        <RejectModal
          jobId={rejectTarget}
          onConfirm={handleRejectConfirm}
          onCancel={() => setRejectTarget(null)}
          loading={rejectSubmitting}
        />
      )}
    </div>
  )
}
