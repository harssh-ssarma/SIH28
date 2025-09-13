import DashboardLayout from '@/components/dashboard-layout'

export default function CoursesPage() {
  const courses = [
    { id: 1, code: "CS101", name: "Introduction to Programming", credits: 3, department: "Computer Science", semester: 1 },
    { id: 2, code: "CS201", name: "Data Structures", credits: 4, department: "Computer Science", semester: 3 },
    { id: 3, code: "MATH101", name: "Calculus I", credits: 3, department: "Mathematics", semester: 1 },
    { id: 4, code: "CS301", name: "Database Systems", credits: 3, department: "Computer Science", semester: 5 },
  ]

  return (
    <DashboardLayout role="admin">
      <div className="space-y-4 sm:space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <h1 className="text-2xl sm:text-3xl font-bold text-neutral-900 dark:text-neutral-100">Course Management</h1>
          <button className="btn-primary w-full sm:w-auto">
            <span className="mr-2">📚</span>
            Add Course
          </button>
        </div>

        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Courses</h3>
            <div className="flex flex-col sm:flex-row gap-3 sm:gap-4 mt-4">
              <div className="relative flex-1">
                <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-neutral-400">🔍</span>
                <input 
                  placeholder="Search courses..." 
                  className="input-primary pl-10 w-full" 
                />
              </div>
              <div className="flex flex-col sm:flex-row gap-3 sm:gap-2">
                <select className="input-primary w-full sm:w-36">
                  <option>All Departments</option>
                  <option>Computer Science</option>
                  <option>Mathematics</option>
                  <option>Physics</option>
                </select>
                <select className="input-primary w-full sm:w-28">
                  <option>All Semesters</option>
                  <option>Semester 1</option>
                  <option>Semester 2</option>
                  <option>Semester 3</option>
                  <option>Semester 4</option>
                  <option>Semester 5</option>
                  <option>Semester 6</option>
                </select>
              </div>
            </div>
          </div>
          
          {/* Mobile Card View */}
          <div className="block sm:hidden space-y-3">
            {courses.map((course) => (
              <div key={course.id} className="p-4 bg-neutral-50 dark:bg-neutral-800 rounded-lg">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="badge badge-neutral text-xs">{course.code}</span>
                      <span className="text-xs text-neutral-500 dark:text-neutral-400">{course.credits} credits</span>
                    </div>
                    <h4 className="font-medium text-neutral-900 dark:text-neutral-100 text-sm">{course.name}</h4>
                    <p className="text-xs text-neutral-600 dark:text-neutral-400">{course.department}</p>
                  </div>
                  <span className="badge badge-success text-xs ml-2">Sem {course.semester}</span>
                </div>
                <div className="flex gap-2">
                  <button className="btn-ghost text-xs px-3 py-1 flex-1">Edit</button>
                  <button className="btn-ghost text-xs px-3 py-1 flex-1 text-red-600">Delete</button>
                </div>
              </div>
            ))}
          </div>
          
          {/* Desktop Table View */}
          <div className="hidden sm:block overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-neutral-200 dark:border-neutral-700">
                  <th className="text-left p-3 sm:p-4 text-xs sm:text-sm font-medium text-neutral-500 dark:text-neutral-400">Code</th>
                  <th className="text-left p-3 sm:p-4 text-xs sm:text-sm font-medium text-neutral-500 dark:text-neutral-400">Course Name</th>
                  <th className="text-left p-3 sm:p-4 text-xs sm:text-sm font-medium text-neutral-500 dark:text-neutral-400 hidden md:table-cell">Credits</th>
                  <th className="text-left p-3 sm:p-4 text-xs sm:text-sm font-medium text-neutral-500 dark:text-neutral-400 hidden lg:table-cell">Department</th>
                  <th className="text-left p-3 sm:p-4 text-xs sm:text-sm font-medium text-neutral-500 dark:text-neutral-400">Semester</th>
                  <th className="text-left p-3 sm:p-4 text-xs sm:text-sm font-medium text-neutral-500 dark:text-neutral-400">Actions</th>
                </tr>
              </thead>
              <tbody>
                {courses.map((course) => (
                  <tr key={course.id} className="border-b border-neutral-200 dark:border-neutral-700 hover:bg-neutral-50 dark:hover:bg-neutral-800">
                    <td className="p-3 sm:p-4">
                      <span className="font-medium text-neutral-900 dark:text-neutral-100">{course.code}</span>
                    </td>
                    <td className="p-3 sm:p-4">
                      <div className="font-medium text-neutral-900 dark:text-neutral-100">{course.name}</div>
                      <div className="text-xs text-neutral-500 dark:text-neutral-400 md:hidden">
                        {course.credits} credits • {course.department}
                      </div>
                    </td>
                    <td className="p-3 sm:p-4 text-neutral-600 dark:text-neutral-400 hidden md:table-cell">{course.credits}</td>
                    <td className="p-3 sm:p-4 text-neutral-600 dark:text-neutral-400 hidden lg:table-cell">{course.department}</td>
                    <td className="p-3 sm:p-4">
                      <span className="badge badge-neutral text-xs">Sem {course.semester}</span>
                    </td>
                    <td className="p-3 sm:p-4">
                      <div className="flex gap-1 sm:gap-2">
                        <button className="btn-ghost text-xs sm:text-sm px-2 sm:px-3 py-1 sm:py-2">Edit</button>
                        <button className="btn-ghost text-xs sm:text-sm px-2 sm:px-3 py-1 sm:py-2 text-red-600">Del</button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </DashboardLayout>
  )
}