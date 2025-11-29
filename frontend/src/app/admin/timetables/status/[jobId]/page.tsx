'use client'

import { useParams, useRouter } from 'next/navigation'
import TimetableProgressTracker from '@/components/ui/ProgressTracker'

export default function TimetableStatusPage() {
  const params = useParams()
  const router = useRouter()
  const jobId = params.jobId as string

  const handleComplete = (timetableId: string) => {
    // Redirect to review page when generation completes
    router.push(`/admin/timetables/${timetableId}/review`)
  }

  const handleCancel = () => {
    // Redirect back to timetables list when cancelled
    router.push('/admin/timetables')
  }

  return (
    <div className="h-screen flex items-center justify-center p-4 overflow-hidden">
      <TimetableProgressTracker 
        jobId={jobId} 
        onComplete={handleComplete}
        onCancel={handleCancel}
      />
    </div>
  )
}
