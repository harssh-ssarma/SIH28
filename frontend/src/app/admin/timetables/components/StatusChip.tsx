const STATUS_BADGE: Record<string, string> = {
  approved:       'badge badge-success',
  completed:      'badge badge-success',
  pending:        'badge badge-warning',
  pending_review: 'badge badge-warning',
  running:        'badge badge-info',
  draft:          'badge badge-neutral',
  rejected:       'badge badge-danger',
  failed:         'badge badge-danger',
}

const STATUS_LABELS: Record<string, string> = {
  approved:       'Approved',
  completed:      'Completed',
  pending:        'Pending',
  pending_review: 'Pending Review',
  running:        'Running',
  draft:          'Draft',
  rejected:       'Rejected',
  failed:         'Failed',
}

export function StatusChip({ status, isRunning }: { status: string; isRunning?: boolean }) {
  const key = isRunning ? 'running' : status
  const cls = STATUS_BADGE[key] ?? STATUS_BADGE['draft']
  const label = STATUS_LABELS[key] ?? (key.charAt(0).toUpperCase() + key.slice(1))
  return <span className={cls}>{label}</span>
}
