"use client"

import DashboardLayout from '@/components/dashboard-layout'

export default function AdminApprovals() {
  const pendingApprovals = [
    { id: 1, type: 'Timetable', requester: 'Dr. Smith', department: 'Computer Science', date: '2024-01-15', priority: 'High' },
    { id: 2, type: 'Room Change', requester: 'Prof. Johnson', department: 'Mathematics', date: '2024-01-14', priority: 'Medium' },
    { id: 3, type: 'Faculty Leave', requester: 'Dr. Brown', department: 'Physics', date: '2024-01-13', priority: 'Low' },
    { id: 4, type: 'Course Update', requester: 'Prof. Davis', department: 'Chemistry', date: '2024-01-12', priority: 'High' },
  ]

  const handleApprove = (id: number) => {
    console.log('Approved:', id)
  }

  const handleReject = (id: number) => {
    console.log('Rejected:', id)
  }

  return (
    <DashboardLayout role="admin">
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-xl sm:text-2xl font-bold text-neutral-900 dark:text-neutral-100">
              Pending Approvals
            </h1>
            <p className="text-sm text-neutral-600 dark:text-neutral-400 mt-1">
              Review and approve pending requests
            </p>
          </div>
          <div className="flex items-center gap-2">
            <select className="px-3 py-2 text-sm border border-neutral-300 dark:border-neutral-600 rounded-lg bg-white dark:bg-neutral-800">
              <option>All Types</option>
              <option>Timetable</option>
              <option>Room Change</option>
              <option>Faculty Leave</option>
              <option>Course Update</option>
            </select>
            <select className="px-3 py-2 text-sm border border-neutral-300 dark:border-neutral-600 rounded-lg bg-white dark:bg-neutral-800">
              <option>All Priority</option>
              <option>High</option>
              <option>Medium</option>
              <option>Low</option>
            </select>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-white dark:bg-neutral-800 rounded-lg p-4 border border-neutral-200 dark:border-neutral-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-neutral-600 dark:text-neutral-400">Total Pending</p>
                <p className="text-2xl font-bold text-neutral-900 dark:text-neutral-100">12</p>
              </div>
              <div className="w-10 h-10 bg-yellow-100 dark:bg-yellow-800 rounded-lg flex items-center justify-center">
                <span className="text-lg">⏳</span>
              </div>
            </div>
          </div>
          
          <div className="bg-white dark:bg-neutral-800 rounded-lg p-4 border border-neutral-200 dark:border-neutral-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-neutral-600 dark:text-neutral-400">High Priority</p>
                <p className="text-2xl font-bold text-red-600">3</p>
              </div>
              <div className="w-10 h-10 bg-red-100 dark:bg-red-800 rounded-lg flex items-center justify-center">
                <span className="text-lg">🚨</span>
              </div>
            </div>
          </div>
          
          <div className="bg-white dark:bg-neutral-800 rounded-lg p-4 border border-neutral-200 dark:border-neutral-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-neutral-600 dark:text-neutral-400">Approved Today</p>
                <p className="text-2xl font-bold text-green-600">8</p>
              </div>
              <div className="w-10 h-10 bg-green-100 dark:bg-green-800 rounded-lg flex items-center justify-center">
                <span className="text-lg">✅</span>
              </div>
            </div>
          </div>
          
          <div className="bg-white dark:bg-neutral-800 rounded-lg p-4 border border-neutral-200 dark:border-neutral-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-neutral-600 dark:text-neutral-400">Avg. Response Time</p>
                <p className="text-2xl font-bold text-blue-600">2.4h</p>
              </div>
              <div className="w-10 h-10 bg-blue-100 dark:bg-blue-800 rounded-lg flex items-center justify-center">
                <span className="text-lg">⏱️</span>
              </div>
            </div>
          </div>
        </div>

        {/* Approvals Table */}
        <div className="bg-white dark:bg-neutral-800 rounded-lg border border-neutral-200 dark:border-neutral-700 overflow-hidden">
          <div className="px-4 py-3 border-b border-neutral-200 dark:border-neutral-700">
            <h3 className="text-lg font-semibold text-neutral-900 dark:text-neutral-100">
              Pending Requests
            </h3>
          </div>
          
          {/* Mobile View */}
          <div className="block sm:hidden">
            {pendingApprovals.map((approval) => (
              <div key={approval.id} className="p-4 border-b border-neutral-200 dark:border-neutral-700 last:border-b-0">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h4 className="font-medium text-neutral-900 dark:text-neutral-100">{approval.type}</h4>
                    <p className="text-sm text-neutral-600 dark:text-neutral-400">{approval.requester}</p>
                    <p className="text-xs text-neutral-500 dark:text-neutral-500">{approval.department}</p>
                  </div>
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                    approval.priority === 'High' ? 'bg-red-100 text-red-800 dark:bg-red-800 dark:text-red-200' :
                    approval.priority === 'Medium' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-800 dark:text-yellow-200' :
                    'bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-200'
                  }`}>
                    {approval.priority}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-xs text-neutral-500 dark:text-neutral-500">{approval.date}</span>
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleReject(approval.id)}
                      className="px-3 py-1 text-xs font-medium text-red-700 bg-red-100 hover:bg-red-200 dark:bg-red-800 dark:text-red-200 dark:hover:bg-red-700 rounded transition-colors"
                    >
                      Reject
                    </button>
                    <button
                      onClick={() => handleApprove(approval.id)}
                      className="px-3 py-1 text-xs font-medium text-green-700 bg-green-100 hover:bg-green-200 dark:bg-green-800 dark:text-green-200 dark:hover:bg-green-700 rounded transition-colors"
                    >
                      Approve
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Desktop View */}
          <div className="hidden sm:block overflow-x-auto">
            <table className="w-full">
              <thead className="bg-neutral-50 dark:bg-neutral-700">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-neutral-500 dark:text-neutral-400 uppercase tracking-wider">
                    Type
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-neutral-500 dark:text-neutral-400 uppercase tracking-wider">
                    Requester
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-neutral-500 dark:text-neutral-400 uppercase tracking-wider">
                    Department
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-neutral-500 dark:text-neutral-400 uppercase tracking-wider">
                    Date
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-neutral-500 dark:text-neutral-400 uppercase tracking-wider">
                    Priority
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-neutral-500 dark:text-neutral-400 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-neutral-200 dark:divide-neutral-700">
                {pendingApprovals.map((approval) => (
                  <tr key={approval.id} className="hover:bg-neutral-50 dark:hover:bg-neutral-700">
                    <td className="px-4 py-3 text-sm font-medium text-neutral-900 dark:text-neutral-100">
                      {approval.type}
                    </td>
                    <td className="px-4 py-3 text-sm text-neutral-600 dark:text-neutral-400">
                      {approval.requester}
                    </td>
                    <td className="px-4 py-3 text-sm text-neutral-600 dark:text-neutral-400">
                      {approval.department}
                    </td>
                    <td className="px-4 py-3 text-sm text-neutral-600 dark:text-neutral-400">
                      {approval.date}
                    </td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                        approval.priority === 'High' ? 'bg-red-100 text-red-800 dark:bg-red-800 dark:text-red-200' :
                        approval.priority === 'Medium' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-800 dark:text-yellow-200' :
                        'bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-200'
                      }`}>
                        {approval.priority}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex gap-2">
                        <button
                          onClick={() => handleReject(approval.id)}
                          className="px-3 py-1 text-xs font-medium text-red-700 bg-red-100 hover:bg-red-200 dark:bg-red-800 dark:text-red-200 dark:hover:bg-red-700 rounded transition-colors"
                        >
                          Reject
                        </button>
                        <button
                          onClick={() => handleApprove(approval.id)}
                          className="px-3 py-1 text-xs font-medium text-green-700 bg-green-100 hover:bg-green-200 dark:bg-green-800 dark:text-green-200 dark:hover:bg-green-700 rounded transition-colors"
                        >
                          Approve
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-white dark:bg-neutral-800 rounded-lg p-4 border border-neutral-200 dark:border-neutral-700">
          <h3 className="text-lg font-semibold text-neutral-900 dark:text-neutral-100 mb-4">
            Quick Actions
          </h3>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <button className="flex flex-col items-center p-3 bg-green-50 dark:bg-green-900/20 rounded-lg hover:bg-green-100 dark:hover:bg-green-900/30 transition-colors">
              <span className="text-lg mb-1">✅</span>
              <span className="text-xs font-medium">Approve All</span>
            </button>
            <button className="flex flex-col items-center p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg hover:bg-blue-100 dark:hover:bg-blue-900/30 transition-colors">
              <span className="text-lg mb-1">📊</span>
              <span className="text-xs font-medium">View Reports</span>
            </button>
            <button className="flex flex-col items-center p-3 bg-purple-50 dark:bg-purple-900/20 rounded-lg hover:bg-purple-100 dark:hover:bg-purple-900/30 transition-colors">
              <span className="text-lg mb-1">⚙️</span>
              <span className="text-xs font-medium">Settings</span>
            </button>
            <button className="flex flex-col items-center p-3 bg-orange-50 dark:bg-orange-900/20 rounded-lg hover:bg-orange-100 dark:hover:bg-orange-900/30 transition-colors">
              <span className="text-lg mb-1">📤</span>
              <span className="text-xs font-medium">Export</span>
            </button>
          </div>
        </div>
      </div>
    </DashboardLayout>
  )
}