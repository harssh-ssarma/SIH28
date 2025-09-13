import DashboardLayout from '@/components/dashboard-layout'

export default function WorkloadPage() {
  const faculty = [
    { name: 'Dr. Smith', department: 'Computer Science', courses: 3, hours: 18, load: 90, status: 'optimal' },
    { name: 'Prof. Johnson', department: 'Mathematics', courses: 4, hours: 24, load: 120, status: 'overloaded' },
    { name: 'Dr. Brown', department: 'Physics', courses: 2, hours: 12, load: 60, status: 'underloaded' },
    { name: 'Prof. Wilson', department: 'Computer Science', courses: 3, hours: 16, load: 80, status: 'optimal' }
  ]

  return (
    <DashboardLayout role="staff">
      <div className="space-y-4 sm:space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <h1 className="text-2xl sm:text-3xl font-bold text-neutral-900 dark:text-neutral-100">Faculty Workload</h1>
          <button className="btn-primary w-full sm:w-auto">
            <span className="mr-2">📊</span>
            Generate Report
          </button>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 sm:gap-4 lg:gap-6">
          <div className="card p-3 sm:p-4">
            <h3 className="font-medium text-sm sm:text-base text-neutral-900 dark:text-neutral-100 mb-2">Optimal Load</h3>
            <p className="text-xl sm:text-2xl font-bold text-green-600">12</p>
            <p className="text-xs text-neutral-500 dark:text-neutral-400">faculty members</p>
          </div>
          <div className="card p-3 sm:p-4">
            <h3 className="font-medium text-sm sm:text-base text-neutral-900 dark:text-neutral-100 mb-2">Overloaded</h3>
            <p className="text-xl sm:text-2xl font-bold text-red-600">3</p>
            <p className="text-xs text-neutral-500 dark:text-neutral-400">need redistribution</p>
          </div>
          <div className="card p-3 sm:p-4">
            <h3 className="font-medium text-sm sm:text-base text-neutral-900 dark:text-neutral-100 mb-2">Underloaded</h3>
            <p className="text-xl sm:text-2xl font-bold text-yellow-600">2</p>
            <p className="text-xs text-neutral-500 dark:text-neutral-400">can take more</p>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Faculty Workload Analysis</h3>
            <p className="card-description">Monitor and manage teaching loads</p>
          </div>
          
          <div className="space-y-3">
            {faculty.map((member, index) => (
              <div key={index} className="p-3 sm:p-4 bg-neutral-50 dark:bg-neutral-800 rounded-lg">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex-1 min-w-0">
                    <h4 className="font-medium text-sm sm:text-base text-neutral-900 dark:text-neutral-100">{member.name}</h4>
                    <p className="text-xs sm:text-sm text-neutral-600 dark:text-neutral-400">{member.department}</p>
                  </div>
                  <span className={`badge text-xs flex-shrink-0 ${
                    member.status === 'optimal' ? 'badge-success' :
                    member.status === 'overloaded' ? 'badge-danger' : 'badge-warning'
                  }`}>
                    {member.status}
                  </span>
                </div>
                
                <div className="grid grid-cols-3 gap-2 sm:gap-4 text-center">
                  <div>
                    <p className="text-base sm:text-lg font-bold text-neutral-900 dark:text-neutral-100">{member.courses}</p>
                    <p className="text-xs text-neutral-500 dark:text-neutral-400">Courses</p>
                  </div>
                  <div>
                    <p className="text-base sm:text-lg font-bold text-neutral-900 dark:text-neutral-100">{member.hours}</p>
                    <p className="text-xs text-neutral-500 dark:text-neutral-400">Hours/Week</p>
                  </div>
                  <div>
                    <p className={`text-base sm:text-lg font-bold ${
                      member.load > 100 ? 'text-red-600' :
                      member.load < 70 ? 'text-yellow-600' : 'text-green-600'
                    }`}>{member.load}%</p>
                    <p className="text-xs text-neutral-500 dark:text-neutral-400">Load</p>
                  </div>
                </div>
                
                <div className="mt-3">
                  <div className="w-full bg-neutral-200 dark:bg-neutral-700 rounded-full h-2">
                    <div 
                      className={`h-2 rounded-full transition-all duration-300 ${
                        member.load > 100 ? 'bg-red-600' :
                        member.load < 70 ? 'bg-yellow-600' : 'bg-green-600'
                      }`}
                      style={{ width: `${Math.min(member.load, 100)}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </DashboardLayout>
  )
}