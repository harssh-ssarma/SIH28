'use client'

import { VariantCardSkeleton } from '@/components/timetables/VariantGrid'
import { TimetableGridSkeleton, Skeleton } from '@/components/LoadingSkeletons'

export default function ReviewLoading() {
  return (
    <div className="space-y-6 py-2">
      <div className="space-y-2">
        <Skeleton style={{ height: '20px', width: '220px' }} />
        <Skeleton style={{ height: '14px', width: '320px' }} />
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <VariantCardSkeleton />
        <VariantCardSkeleton />
        <VariantCardSkeleton />
      </div>
      <TimetableGridSkeleton />
    </div>
  )
}
