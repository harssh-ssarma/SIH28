"use client"

import DashboardLayout from '@/components/dashboard-layout'

export default function StudentEnrollments() {
  return (
    <DashboardLayout role="student">
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h2 className="text-xl font-semibold text-neutral-900 dark:text-neutral-100">Course Enrollments</h2>
            <p className="text-sm text-neutral-600 dark:text-neutral-400 mt-1">Manage your course registrations</p>
          </div>
          <div className="flex gap-2">
            <button className="btn-secondary">
              🔍 Check Clashes
            </button>
            <button className="btn-primary">
              ➕ Add Course
            </button>
          </div>
        </div>

        {/* Current Enrollments */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Current Enrollments - Semester 5</h3>
            <p className="card-description">24 Credits Total</p>
          </div>
          <div className="space-y-3">
            {[
              { name: 'Data Structures', code: 'CS301', credits: 4, faculty: 'Dr. Rajesh Kumar', type: 'Core', status: 'Enrolled' },
              { name: 'Database Systems', code: 'CS302', credits: 4, faculty: 'Prof. Meera Sharma', type: 'Core', status: 'Enrolled' },
              { name: 'Software Engineering', code: 'CS303', credits: 4, faculty: 'Dr. Vikram Gupta', type: 'Core', status: 'Enrolled' },
              { name: 'Machine Learning', code: 'CS401', credits: 4, faculty: 'Dr. Anita Verma', type: 'Elective', status: 'Enrolled' },
              { name: 'Web Development', code: 'CS402', credits: 4, faculty: 'Prof. Suresh Reddy', type: 'Elective', status: 'Enrolled' },
              { name: 'Technical Writing', code: 'EN301', credits: 4, faculty: 'Dr. Kavita Joshi', type: 'General', status: 'Enrolled' }
            ].map((course, index) => (
              <div key={index} className="flex items-center justify-between p-4 bg-neutral-50 dark:bg-neutral-800 rounded-lg">
                <div className="flex-1">
                  <div className="flex items-center gap-3">
                    <h4 className="font-medium text-neutral-900 dark:text-neutral-100">{course.name}</h4>
                    <span className="text-sm text-neutral-500">({course.code})</span>
                    <span className={`badge ${
                      course.type === 'Core' ? 'badge-success' :
                      course.type === 'Elective' ? 'badge-warning' : 'badge-neutral'
                    }`}>
                      {course.type}
                    </span>
                  </div>
                  <p className="text-sm text-neutral-600 dark:text-neutral-400">{course.faculty} • {course.credits} Credits</p>
                </div>
                <div className="flex items-center gap-2">
                  <span className="badge badge-success">{course.status}</span>
                  <button className="btn-ghost text-xs px-2 py-1">Drop</button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Available Courses */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Available Courses</h3>
            <p className="card-description">Courses you can enroll in</p>
          </div>
          <div className="space-y-3">
            {[
              { name: 'Mobile App Development', code: 'CS403', credits: 4, faculty: 'Prof. Amit Sharma', type: 'Elective', seats: '5/40' },
              { name: 'Artificial Intelligence', code: 'CS404', credits: 4, faculty: 'Dr. Neha Gupta', type: 'Elective', seats: '12/40' },
              { name: 'Cyber Security', code: 'CS405', credits: 4, faculty: 'Prof. Rohit Verma', type: 'Elective', seats: 'Full' }
            ].map((course, index) => (
              <div key={index} className="flex items-center justify-between p-4 bg-neutral-50 dark:bg-neutral-800 rounded-lg">
                <div className="flex-1">
                  <div className="flex items-center gap-3">
                    <h4 className="font-medium text-neutral-900 dark:text-neutral-100">{course.name}</h4>
                    <span className="text-sm text-neutral-500">({course.code})</span>
                    <span className="badge badge-warning">{course.type}</span>
                  </div>
                  <p className="text-sm text-neutral-600 dark:text-neutral-400">{course.faculty} • {course.credits} Credits</p>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-sm text-neutral-600 dark:text-neutral-400">Seats: {course.seats}</span>
                  <button className={`btn-primary text-xs px-2 py-1 ${course.seats === 'Full' ? 'opacity-50 cursor-not-allowed' : ''}`} disabled={course.seats === 'Full'}>
                    {course.seats === 'Full' ? 'Full' : 'Enroll'}
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </DashboardLayout>
  )
}