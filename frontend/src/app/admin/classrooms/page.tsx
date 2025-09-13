import DashboardLayout from '@/components/dashboard-layout'

export default function ClassroomsPage() {
  const classrooms = [
    { id: 1, name: "Room 101", type: "Lecture Hall", capacity: 60, building: "Main Building", floor: 1, equipment: ["Projector", "Whiteboard"] },
    { id: 2, name: "Lab 3", type: "Laboratory", capacity: 30, building: "Tech Building", floor: 2, equipment: ["Computers", "Projector"] },
    { id: 3, name: "Seminar Room A", type: "Seminar Room", capacity: 25, building: "Admin Building", floor: 3, equipment: ["Smart Board", "Audio System"] },
    { id: 4, name: "Auditorium", type: "Auditorium", capacity: 200, building: "Main Building", floor: 0, equipment: ["Stage", "Sound System", "Lighting"] },
  ]

  return (
    <DashboardLayout role="admin">
      <div className="space-y-4 sm:space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <h1 className="text-2xl sm:text-3xl font-bold text-neutral-900 dark:text-neutral-100">Classroom Management</h1>
          <button className="btn-primary w-full sm:w-auto">
            <span className="mr-2">🏢</span>
            Add Classroom
          </button>
        </div>

        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Classrooms</h3>
            <div className="flex flex-col sm:flex-row gap-3 sm:gap-4 mt-4">
              <div className="relative flex-1">
                <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-neutral-400">🔍</span>
                <input 
                  placeholder="Search classrooms..." 
                  className="input-primary pl-10 w-full" 
                />
              </div>
              <div className="flex flex-col sm:flex-row gap-3 sm:gap-2">
                <select className="input-primary w-full sm:w-32">
                  <option>All Types</option>
                  <option>Lecture Hall</option>
                  <option>Laboratory</option>
                  <option>Seminar Room</option>
                  <option>Auditorium</option>
                </select>
                <select className="input-primary w-full sm:w-36">
                  <option>All Buildings</option>
                  <option>Main Building</option>
                  <option>Tech Building</option>
                  <option>Admin Building</option>
                </select>
              </div>
            </div>
          </div>
          
          {/* Mobile Card View */}
          <div className="block sm:hidden space-y-3">
            {classrooms.map((classroom) => (
              <div key={classroom.id} className="p-4 bg-neutral-50 dark:bg-neutral-800 rounded-lg">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <h4 className="font-medium text-neutral-900 dark:text-neutral-100">{classroom.name}</h4>
                      <span className="badge badge-neutral text-xs">{classroom.type}</span>
                    </div>
                    <p className="text-sm text-neutral-600 dark:text-neutral-400 mb-1">
                      📍 {classroom.building}, Floor {classroom.floor}
                    </p>
                    <p className="text-sm text-neutral-600 dark:text-neutral-400">
                      👥 {classroom.capacity} seats
                    </p>
                  </div>
                </div>
                <div className="flex flex-wrap gap-1 mb-3">
                  {classroom.equipment.slice(0, 3).map((item, index) => (
                    <span key={index} className="badge badge-neutral text-xs">{item}</span>
                  ))}
                  {classroom.equipment.length > 3 && (
                    <span className="badge badge-neutral text-xs">+{classroom.equipment.length - 3}</span>
                  )}
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
                  <th className="text-left p-3 sm:p-4 text-xs sm:text-sm font-medium text-neutral-500 dark:text-neutral-400">Name</th>
                  <th className="text-left p-3 sm:p-4 text-xs sm:text-sm font-medium text-neutral-500 dark:text-neutral-400">Type</th>
                  <th className="text-left p-3 sm:p-4 text-xs sm:text-sm font-medium text-neutral-500 dark:text-neutral-400 hidden md:table-cell">Capacity</th>
                  <th className="text-left p-3 sm:p-4 text-xs sm:text-sm font-medium text-neutral-500 dark:text-neutral-400 hidden lg:table-cell">Location</th>
                  <th className="text-left p-3 sm:p-4 text-xs sm:text-sm font-medium text-neutral-500 dark:text-neutral-400 hidden xl:table-cell">Equipment</th>
                  <th className="text-left p-3 sm:p-4 text-xs sm:text-sm font-medium text-neutral-500 dark:text-neutral-400">Actions</th>
                </tr>
              </thead>
              <tbody>
                {classrooms.map((classroom) => (
                  <tr key={classroom.id} className="border-b border-neutral-200 dark:border-neutral-700 hover:bg-neutral-50 dark:hover:bg-neutral-800">
                    <td className="p-3 sm:p-4">
                      <div className="font-medium text-neutral-900 dark:text-neutral-100">{classroom.name}</div>
                      <div className="text-xs text-neutral-500 dark:text-neutral-400 md:hidden">
                        {classroom.capacity} seats • {classroom.building}
                      </div>
                    </td>
                    <td className="p-3 sm:p-4">
                      <span className="badge badge-neutral text-xs">{classroom.type}</span>
                    </td>
                    <td className="p-3 sm:p-4 text-neutral-600 dark:text-neutral-400 hidden md:table-cell">{classroom.capacity} seats</td>
                    <td className="p-3 sm:p-4 text-neutral-600 dark:text-neutral-400 hidden lg:table-cell">
                      <div className="flex items-center gap-1 text-sm">
                        <span>📍</span>
                        {classroom.building}, Floor {classroom.floor}
                      </div>
                    </td>
                    <td className="p-3 sm:p-4 hidden xl:table-cell">
                      <div className="flex flex-wrap gap-1">
                        {classroom.equipment.slice(0, 2).map((item, index) => (
                          <span key={index} className="badge badge-neutral text-xs">{item}</span>
                        ))}
                        {classroom.equipment.length > 2 && (
                          <span className="badge badge-neutral text-xs">+{classroom.equipment.length - 2}</span>
                        )}
                      </div>
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