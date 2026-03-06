import type { Subject } from './AssignedSubjectsCard'

interface Props {
  subjects: Subject[]
  maxWorkloadPerWeek: number
}

export function FacultyQuickStats({ subjects, maxWorkloadPerWeek }: Props) {
  return (
    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 sm:gap-4">
      <div className="card text-center">
        <div className="text-2xl sm:text-3xl font-bold" style={{ color: 'var(--color-primary)' }}>
          {subjects.length}
        </div>
        <div className="text-sm mt-1" style={{ color: 'var(--color-text-secondary)' }}>Assigned Courses</div>
      </div>
      <div className="card text-center">
        <div className="text-2xl sm:text-3xl font-bold" style={{ color: 'var(--color-success-text)' }}>
          {subjects.reduce((sum, course) => sum + course.number_of_sections, 0)}
        </div>
        <div className="text-sm mt-1" style={{ color: 'var(--color-text-secondary)' }}>Total Sections</div>
      </div>
      <div className="card text-center">
        <div className="text-2xl sm:text-3xl font-bold text-purple-600 dark:text-purple-400">
          {subjects.reduce((sum, course) => sum + course.total_enrolled, 0)}
        </div>
        <div className="text-sm mt-1" style={{ color: 'var(--color-text-secondary)' }}>Total Students</div>
      </div>
      <div className="card text-center">
        <div className="text-2xl sm:text-3xl font-bold" style={{ color: 'var(--color-warning-text)' }}>
          {maxWorkloadPerWeek}h
        </div>
        <div className="text-sm mt-1" style={{ color: 'var(--color-text-secondary)' }}>Max Workload/Week</div>
      </div>
    </div>
  )
}
