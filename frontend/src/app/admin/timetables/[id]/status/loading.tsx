import { Skeleton } from '@/components/LoadingSkeletons'

export default function StatusLoading() {
  return (
    <div className="max-w-2xl mx-auto px-4 py-12 space-y-6">
      {/* Header */}
      <div className="space-y-2">
        <Skeleton style={{ height: '28px', width: '60%' }} />
        <Skeleton style={{ height: '16px', width: '40%' }} />
      </div>
      {/* Progress bar area */}
      <div className="rounded-xl border p-6 space-y-4" style={{ background: 'var(--color-bg-surface)', borderColor: 'var(--color-border)' }}>
        <div className="flex justify-between items-center">
          <Skeleton style={{ height: '18px', width: '30%' }} />
          <Skeleton style={{ height: '18px', width: '12%' }} />
        </div>
        <Skeleton style={{ height: '10px', width: '100%', borderRadius: '9999px' }} />
        <Skeleton style={{ height: '14px', width: '50%' }} />
      </div>
      {/* Stage details */}
      <div className="rounded-xl border p-6 space-y-3" style={{ background: 'var(--color-bg-surface)', borderColor: 'var(--color-border)' }}>
        <Skeleton style={{ height: '16px', width: '40%' }} />
        <Skeleton style={{ height: '14px', width: '70%' }} />
        <Skeleton style={{ height: '14px', width: '55%' }} />
      </div>
    </div>
  )
}
