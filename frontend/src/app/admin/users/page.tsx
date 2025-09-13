import DashboardLayout from '@/components/dashboard-layout'

export default function UsersPage() {
  const users = [
    { id: 1, name: "Dr. John Smith", email: "john.smith@university.edu", role: "Faculty", department: "Computer Science", status: "Active" },
    { id: 2, name: "Sarah Johnson", email: "sarah.johnson@university.edu", role: "Staff", department: "Administration", status: "Active" },
    { id: 3, name: "Mike Wilson", email: "mike.wilson@university.edu", role: "Faculty", department: "Mathematics", status: "Active" },
    { id: 4, name: "Emily Davis", email: "emily.davis@university.edu", role: "Student", department: "Computer Science", status: "Active" },
  ]

  return (
    <DashboardLayout role="admin">
      <div className="space-y-4 sm:space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <h1 className="text-2xl sm:text-3xl font-bold text-neutral-900 dark:text-neutral-100">User Management</h1>
          <button className="btn-primary w-full sm:w-auto">
            <span className="mr-2">➕</span>
            Add User
          </button>
        </div>

        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Users</h3>
            <div className="flex flex-col sm:flex-row gap-3 sm:gap-4 mt-4">
              <div className="relative flex-1">
                <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-neutral-400">🔍</span>
                <input 
                  placeholder="Search users..." 
                  className="input-primary pl-10 w-full" 
                />
              </div>
              <div className="flex flex-col sm:flex-row gap-3 sm:gap-2">
                <select className="input-primary w-full sm:w-32">
                  <option>All Roles</option>
                  <option>Admin</option>
                  <option>Staff</option>
                  <option>Faculty</option>
                  <option>Student</option>
                </select>
                <select className="input-primary w-full sm:w-36">
                  <option>All Departments</option>
                  <option>Computer Science</option>
                  <option>Mathematics</option>
                  <option>Physics</option>
                </select>
              </div>
            </div>
          </div>
          
          {/* Mobile Card View */}
          <div className="block sm:hidden space-y-3">
            {users.map((user) => (
              <div key={user.id} className="p-4 bg-neutral-50 dark:bg-neutral-800 rounded-lg">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1 min-w-0">
                    <h4 className="font-medium text-neutral-900 dark:text-neutral-100 truncate">{user.name}</h4>
                    <p className="text-sm text-neutral-600 dark:text-neutral-400 truncate">{user.email}</p>
                  </div>
                  <span className="badge badge-success ml-2">{user.status}</span>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex gap-2">
                    <span className="badge badge-neutral">{user.role}</span>
                    <span className="text-xs text-neutral-500 dark:text-neutral-400">{user.department}</span>
                  </div>
                  <div className="flex gap-1">
                    <button className="btn-ghost text-xs px-2 py-1">Edit</button>
                    <button className="btn-ghost text-xs px-2 py-1 text-red-600">Delete</button>
                  </div>
                </div>
              </div>
            ))}
          </div>
          
          {/* Desktop Table View */}
          <div className="hidden sm:block overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-neutral-200 dark:border-neutral-700">
                  <th className="text-left p-3 sm:p-4 text-xs sm:text-sm font-medium text-neutral-500 dark:text-neutral-400">Name</th>
                  <th className="text-left p-3 sm:p-4 text-xs sm:text-sm font-medium text-neutral-500 dark:text-neutral-400 hidden md:table-cell">Email</th>
                  <th className="text-left p-3 sm:p-4 text-xs sm:text-sm font-medium text-neutral-500 dark:text-neutral-400">Role</th>
                  <th className="text-left p-3 sm:p-4 text-xs sm:text-sm font-medium text-neutral-500 dark:text-neutral-400 hidden lg:table-cell">Department</th>
                  <th className="text-left p-3 sm:p-4 text-xs sm:text-sm font-medium text-neutral-500 dark:text-neutral-400">Status</th>
                  <th className="text-left p-3 sm:p-4 text-xs sm:text-sm font-medium text-neutral-500 dark:text-neutral-400">Actions</th>
                </tr>
              </thead>
              <tbody>
                {users.map((user) => (
                  <tr key={user.id} className="border-b border-neutral-200 dark:border-neutral-700 hover:bg-neutral-50 dark:hover:bg-neutral-800">
                    <td className="p-3 sm:p-4">
                      <div className="font-medium text-neutral-900 dark:text-neutral-100">{user.name}</div>
                      <div className="text-xs text-neutral-500 dark:text-neutral-400 md:hidden">{user.email}</div>
                    </td>
                    <td className="p-3 sm:p-4 text-neutral-600 dark:text-neutral-400 hidden md:table-cell">{user.email}</td>
                    <td className="p-3 sm:p-4">
                      <span className="badge badge-neutral text-xs">{user.role}</span>
                    </td>
                    <td className="p-3 sm:p-4 text-neutral-600 dark:text-neutral-400 hidden lg:table-cell">{user.department}</td>
                    <td className="p-3 sm:p-4">
                      <span className="badge badge-success text-xs">{user.status}</span>
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