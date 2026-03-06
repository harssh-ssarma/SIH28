export interface FacultyProfile {
  faculty_id: string
  faculty_code: string
  faculty_name: string
  email: string
  phone: string | null
  department: string | null
  department_code: string | null
  specialization: string | null
  qualification: string | null
  designation: string | null
  max_workload_per_week: number
  is_active: boolean
  assigned_courses: import('./AssignedSubjectsCard').Subject[]
  total_courses: number
}

interface Props {
  profile: FacultyProfile
}

export function FacultyProfileCard({ profile }: Props) {
  return (
    <div className="card">
      <div className="card-header">
        <h3 className="card-title">Faculty Profile</h3>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <div>
          <p className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>Name</p>
          <p className="font-medium" style={{ color: 'var(--color-text-primary)' }}>{profile.faculty_name}</p>
        </div>
        <div>
          <p className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>Faculty Code</p>
          <p className="font-medium" style={{ color: 'var(--color-text-primary)' }}>{profile.faculty_code}</p>
        </div>
        <div>
          <p className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>Email</p>
          <p className="font-medium" style={{ color: 'var(--color-text-primary)' }}>{profile.email}</p>
        </div>
        <div>
          <p className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>Department</p>
          <p className="font-medium" style={{ color: 'var(--color-text-primary)' }}>{profile.department || 'N/A'}</p>
        </div>
        <div>
          <p className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>Designation</p>
          <p className="font-medium" style={{ color: 'var(--color-text-primary)' }}>{profile.designation || 'N/A'}</p>
        </div>
        <div>
          <p className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>Specialization</p>
          <p className="font-medium" style={{ color: 'var(--color-text-primary)' }}>{profile.specialization || 'N/A'}</p>
        </div>
      </div>
    </div>
  )
}
