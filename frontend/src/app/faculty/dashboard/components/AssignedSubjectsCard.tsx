'use client'

import { ListSkeleton } from '@/components/LoadingSkeletons'

export interface Subject {
  offering_id: string
  course_code: string
  course_name: string
  credits: number
  department: string | null
  academic_year: string
  semester_type: string
  semester_number: number
  total_enrolled: number
  max_capacity: number | null
  number_of_sections: number
  offering_status: string
}

interface Props {
  subjects: Subject[]
  loading: boolean
}

export function AssignedSubjectsCard({ subjects, loading }: Props) {
  return (
    <div className="card">
      <div className="card-header">
        <h3 className="card-title">Assigned Subjects</h3>
        <p className="card-description">Subjects assigned to you for teaching</p>
      </div>

      {loading ? (
        <ListSkeleton items={3} />
      ) : subjects.length > 0 ? (
        <div className="space-y-3">
          {subjects.map(subject => (
            <div
              key={subject.offering_id}
              className="flex flex-col sm:flex-row sm:items-center justify-between p-4 rounded-lg gap-3"
              style={{ background: 'var(--color-bg-surface-2)' }}
            >
              <div className="flex-1">
                <h4 className="font-medium" style={{ color: 'var(--color-text-primary)' }}>
                  {subject.course_name}
                </h4>
                <p className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>
                  {subject.course_code} • {subject.credits} credits
                </p>
                <p className="text-xs" style={{ color: 'var(--color-text-muted)' }}>
                  {subject.total_enrolled} students enrolled • {subject.number_of_sections} section(s) • {subject.semester_type} {subject.academic_year}
                </p>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-8">
          <div className="text-4xl mb-4">📚</div>
          <h4 className="text-lg font-medium mb-2" style={{ color: 'var(--color-text-primary)' }}>
            No Subjects Assigned
          </h4>
          <p style={{ color: 'var(--color-text-secondary)' }}>
            You don&apos;t have any subjects assigned yet.
          </p>
        </div>
      )}
    </div>
  )
}
