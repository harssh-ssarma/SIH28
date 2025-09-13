"use client"

import DashboardLayout from '@/components/dashboard-layout'

export default function AdminDashboard() {
  return (
    <DashboardLayout role="admin">
      <div className="space-y-6">
        {/* Stats Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-white dark:bg-neutral-800 rounded-lg p-4 border border-neutral-200 dark:border-neutral-700 hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between">
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-neutral-600 dark:text-neutral-400">Total Users</p>
                <p className="text-2xl font-bold text-blue-600 truncate">1,234</p>
              </div>
              <div className="w-12 h-12 bg-blue-100 dark:bg-blue-800 rounded-xl flex items-center justify-center flex-shrink-0">
                <span className="text-xl">👥</span>
              </div>
            </div>
            <div className="mt-4 flex items-center text-sm">
              <span className="text-green-600">↗ 12%</span>
              <span className="ml-2 text-neutral-600 dark:text-neutral-400">vs last month</span>
            </div>
          </div>

          <div className="bg-white dark:bg-neutral-800 rounded-lg p-4 border border-neutral-200 dark:border-neutral-700 hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between">
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-neutral-600 dark:text-neutral-400">Active Courses</p>
                <p className="text-2xl font-bold text-green-600 truncate">56</p>
              </div>
              <div className="w-12 h-12 bg-green-100 dark:bg-green-800 rounded-xl flex items-center justify-center flex-shrink-0">
                <span className="text-xl">📚</span>
              </div>
            </div>
            <div className="mt-4 flex items-center text-sm">
              <span className="text-green-600">↗ 8%</span>
              <span className="ml-2 text-neutral-600 dark:text-neutral-400">vs last month</span>
            </div>
          </div>

          <div className="bg-white dark:bg-neutral-800 rounded-lg p-4 border border-neutral-200 dark:border-neutral-700 hover:shadow-md transition-shadow cursor-pointer" onClick={() => window.location.href='/admin/approvals'}>
            <div className="flex items-center justify-between">
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-neutral-600 dark:text-neutral-400">Pending Approvals</p>
                <p className="text-2xl font-bold text-yellow-600 truncate">12</p>
              </div>
              <div className="w-12 h-12 bg-yellow-100 dark:bg-yellow-800 rounded-xl flex items-center justify-center flex-shrink-0">
                <span className="text-xl">⏳</span>
              </div>
            </div>
            <div className="mt-4">
              <span className="px-2 py-1 text-xs font-medium bg-yellow-100 text-yellow-800 dark:bg-yellow-800 dark:text-yellow-200 rounded-full">Needs attention</span>
            </div>
          </div>

          <div className="bg-white dark:bg-neutral-800 rounded-lg p-4 border border-neutral-200 dark:border-neutral-700 hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between">
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-neutral-600 dark:text-neutral-400">System Health</p>
                <p className="text-2xl font-bold text-green-600 truncate">98%</p>
              </div>
              <div className="w-12 h-12 bg-green-100 dark:bg-green-800 rounded-xl flex items-center justify-center flex-shrink-0">
                <span className="text-xl">❤️</span>
              </div>
            </div>
            <div className="mt-4 flex items-center text-sm">
              <span className="text-green-600">All services online</span>
            </div>
          </div>
        </div>

        {/* Analytics & Management */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <div className="bg-white dark:bg-neutral-800 rounded-lg p-4 border border-neutral-200 dark:border-neutral-700">
            <div className="pb-4 border-b border-neutral-200 dark:border-neutral-700 mb-4">
              <h3 className="text-lg font-semibold text-neutral-900 dark:text-neutral-100">Utilization Reports</h3>
              <p className="text-sm text-neutral-600 dark:text-neutral-400 mt-1">Resource usage analytics</p>
            </div>
            <div className="space-y-4">
              <div className="flex items-center justify-between text-sm">
                <span className="text-neutral-600 dark:text-neutral-400">Classroom Usage</span>
                <span className="font-medium text-green-600">87%</span>
              </div>
              <div className="w-full bg-neutral-200 dark:bg-neutral-700 rounded-full h-2">
                <div className="bg-green-600 h-2 rounded-full" style={{width: '87%'}}></div>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-neutral-600 dark:text-neutral-400">Faculty Load</span>
                <span className="font-medium text-yellow-600">73%</span>
              </div>
              <div className="w-full bg-neutral-200 dark:bg-neutral-700 rounded-full h-2">
                <div className="bg-yellow-600 h-2 rounded-full" style={{width: '73%'}}></div>
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-neutral-800 rounded-lg p-4 border border-neutral-200 dark:border-neutral-700">
            <div className="pb-4 border-b border-neutral-200 dark:border-neutral-700 mb-4">
              <h3 className="text-lg font-semibold text-neutral-900 dark:text-neutral-100">Conflict Detection</h3>
              <p className="text-sm text-neutral-600 dark:text-neutral-400 mt-1">AI-powered conflict analysis</p>
            </div>
            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-red-500"></div>
                <span className="text-sm text-neutral-900 dark:text-neutral-100">3 Schedule conflicts</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-yellow-500"></div>
                <span className="text-sm text-neutral-900 dark:text-neutral-100">5 Room overlaps</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-green-500"></div>
                <span className="text-sm text-neutral-900 dark:text-neutral-100">12 Resolved today</span>
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-neutral-800 rounded-lg p-4 border border-neutral-200 dark:border-neutral-700">
            <div className="pb-4 border-b border-neutral-200 dark:border-neutral-700 mb-4">
              <h3 className="text-lg font-semibold text-neutral-900 dark:text-neutral-100">System Notifications</h3>
              <p className="text-sm text-neutral-600 dark:text-neutral-400 mt-1">Alerts and announcements</p>
            </div>
            <div className="space-y-3">
              <div className="p-3 bg-yellow-50 dark:bg-yellow-900/20 border-l-4 border-yellow-500 rounded">
                <p className="text-sm font-medium text-yellow-800 dark:text-yellow-200">AI Engine Update</p>
                <p className="text-xs text-yellow-700 dark:text-yellow-300">Optimization algorithm improved by 15%</p>
              </div>
              <div className="p-3 bg-blue-50 dark:bg-blue-900/20 border-l-4 border-blue-500 rounded">
                <p className="text-sm font-medium text-blue-800 dark:text-blue-200">New Faculty Added</p>
                <p className="text-xs text-blue-700 dark:text-blue-300">3 new faculty members registered</p>
              </div>
              <div className="p-3 bg-green-50 dark:bg-green-900/20 border-l-4 border-green-500 rounded">
                <p className="text-sm font-medium text-green-800 dark:text-green-200">Backup Complete</p>
                <p className="text-xs text-green-700 dark:text-green-300">Daily system backup successful</p>
              </div>
            </div>
          </div>
        </div>

        {/* Strategic Control Hub */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <div className="bg-white dark:bg-neutral-800 rounded-lg p-4 border border-neutral-200 dark:border-neutral-700">
            <div className="pb-4 border-b border-neutral-200 dark:border-neutral-700 mb-4">
              <h3 className="text-lg font-semibold text-neutral-900 dark:text-neutral-100">System Health Monitor</h3>
              <p className="text-sm text-neutral-600 dark:text-neutral-400 mt-1">Real-time service status</p>
            </div>
            <div className="space-y-3">
              <div className="flex items-center justify-between p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                  <span className="text-sm font-medium">Django API</span>
                </div>
                <span className="text-sm text-green-600 font-medium">Online</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                  <span className="text-sm font-medium">FastAPI AI Service</span>
                </div>
                <span className="text-sm text-green-600 font-medium">Online</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                  <span className="text-sm font-medium">Database Connection</span>
                </div>
                <span className="text-sm text-green-600 font-medium">Healthy</span>
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-neutral-800 rounded-lg p-4 border border-neutral-200 dark:border-neutral-700">
            <div className="pb-4 border-b border-neutral-200 dark:border-neutral-700 mb-4">
              <h3 className="text-lg font-semibold text-neutral-900 dark:text-neutral-100">Data Management</h3>
              <p className="text-sm text-neutral-600 dark:text-neutral-400 mt-1">Import/Export operations</p>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <button className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg hover:bg-blue-100 dark:hover:bg-blue-900/30 transition-colors text-left">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-sm">📥</span>
                  <span className="text-sm font-medium">Import CSV</span>
                </div>
                <p className="text-xs text-neutral-600 dark:text-neutral-400">Bulk upload data</p>
              </button>
              <button className="p-3 bg-green-50 dark:bg-green-900/20 rounded-lg hover:bg-green-100 dark:hover:bg-green-900/30 transition-colors text-left">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-sm">📤</span>
                  <span className="text-sm font-medium">Export PDF</span>
                </div>
                <p className="text-xs text-neutral-600 dark:text-neutral-400">Generate reports</p>
              </button>
              <button className="p-3 bg-purple-50 dark:bg-purple-900/20 rounded-lg hover:bg-purple-100 dark:hover:bg-purple-900/30 transition-colors text-left">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-sm">💾</span>
                  <span className="text-sm font-medium">Backup DB</span>
                </div>
                <p className="text-xs text-neutral-600 dark:text-neutral-400">Create snapshot</p>
              </button>
              <button className="p-3 bg-orange-50 dark:bg-orange-900/20 rounded-lg hover:bg-orange-100 dark:hover:bg-orange-900/30 transition-colors text-left">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-sm">🔄</span>
                  <span className="text-sm font-medium">Restore</span>
                </div>
                <p className="text-xs text-neutral-600 dark:text-neutral-400">From backup</p>
              </button>
            </div>
          </div>
        </div>

        {/* Audit & Configuration */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <div className="bg-white dark:bg-neutral-800 rounded-lg p-4 border border-neutral-200 dark:border-neutral-700">
            <div className="pb-4 border-b border-neutral-200 dark:border-neutral-700 mb-4">
              <h3 className="text-lg font-semibold text-neutral-900 dark:text-neutral-100">Recent Audit Trail</h3>
              <p className="text-sm text-neutral-600 dark:text-neutral-400 mt-1">Critical system actions</p>
            </div>
            <div className="space-y-2">
              {[
                { action: 'Timetable Approved', user: 'staff@sih28.com', time: '2 min ago', type: 'success' },
                { action: 'User Role Changed', user: 'admin@sih28.com', time: '15 min ago', type: 'warning' },
                { action: 'Course Updated', user: 'faculty@sih28.com', time: '1h ago', type: 'info' },
                { action: 'Login Failed', user: 'unknown', time: '2h ago', type: 'error' }
              ].map((log, index) => (
                <div key={index} className="flex items-center gap-2 p-2 bg-neutral-50 dark:bg-neutral-800 rounded text-sm">
                  <div className={`w-1.5 h-1.5 rounded-full ${
                    log.type === 'success' ? 'bg-green-500' :
                    log.type === 'warning' ? 'bg-yellow-500' :
                    log.type === 'error' ? 'bg-red-500' : 'bg-blue-500'
                  }`}></div>
                  <div className="flex-1 min-w-0">
                    <p className="font-medium truncate">{log.action}</p>
                    <p className="text-neutral-500 dark:text-neutral-400 truncate text-xs">{log.user}</p>
                  </div>
                  <span className="text-neutral-400 text-xs flex-shrink-0">{log.time}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-white dark:bg-neutral-800 rounded-lg p-4 border border-neutral-200 dark:border-neutral-700">
            <div className="pb-4 border-b border-neutral-200 dark:border-neutral-700 mb-4">
              <h3 className="text-lg font-semibold text-neutral-900 dark:text-neutral-100">Role Management</h3>
              <p className="text-sm text-neutral-600 dark:text-neutral-400 mt-1">Permission control</p>
            </div>
            <div className="space-y-2">
              {[
                { role: 'Admin', users: 3, permissions: 'All Access' },
                { role: 'Staff', users: 8, permissions: 'Approvals, Reports' },
                { role: 'Faculty', users: 45, permissions: 'Schedule View' },
                { role: 'HOD', users: 5, permissions: 'Dept. Management' }
              ].map((role, index) => (
                <div key={index} className="flex items-center justify-between p-2 bg-neutral-50 dark:bg-neutral-800 rounded">
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium">{role.role}</p>
                    <p className="text-xs text-neutral-500 dark:text-neutral-400 truncate">{role.permissions}</p>
                  </div>
                  <span className="text-sm font-medium">{role.users}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-white dark:bg-neutral-800 rounded-lg p-4 border border-neutral-200 dark:border-neutral-700">
            <div className="pb-4 border-b border-neutral-200 dark:border-neutral-700 mb-4">
              <h3 className="text-lg font-semibold text-neutral-900 dark:text-neutral-100">System Configuration</h3>
              <p className="text-sm text-neutral-600 dark:text-neutral-400 mt-1">Global settings</p>
            </div>
            <div className="space-y-2">
              <div className="p-3 bg-neutral-50 dark:bg-neutral-800 rounded">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm font-medium">Academic Year</span>
                  <button className="text-xs text-blue-600 hover:underline">Edit</button>
                </div>
                <p className="text-xs text-neutral-600 dark:text-neutral-400">2024-25</p>
              </div>
              <div className="p-3 bg-neutral-50 dark:bg-neutral-800 rounded">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm font-medium">Semester Dates</span>
                  <button className="text-xs text-blue-600 hover:underline">Edit</button>
                </div>
                <p className="text-xs text-neutral-600 dark:text-neutral-400">Jul 1 - Dec 15</p>
              </div>
              <div className="p-3 bg-neutral-50 dark:bg-neutral-800 rounded">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm font-medium">Holiday List</span>
                  <button className="text-xs text-blue-600 hover:underline">Edit</button>
                </div>
                <p className="text-xs text-neutral-600 dark:text-neutral-400">15 holidays configured</p>
              </div>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-white dark:bg-neutral-800 rounded-lg p-4 border border-neutral-200 dark:border-neutral-700">
          <div className="pb-4 border-b border-neutral-200 dark:border-neutral-700 mb-4">
            <h3 className="text-lg font-semibold text-neutral-900 dark:text-neutral-100">Strategic Actions</h3>
            <p className="text-sm text-neutral-600 dark:text-neutral-400 mt-1">Administrative control center</p>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
            <button className="flex flex-col items-center justify-center p-3 h-16 text-xs font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors">
              <span className="text-lg mb-1">👤</span>
              <span>Add User</span>
            </button>
            <button className="flex flex-col items-center justify-center p-3 h-16 text-xs font-medium text-neutral-700 dark:text-neutral-300 bg-white dark:bg-neutral-800 hover:bg-neutral-50 dark:hover:bg-neutral-700 border border-neutral-300 dark:border-neutral-600 rounded-lg transition-colors">
              <span className="text-lg mb-1">🔐</span>
              <span>Roles</span>
            </button>
            <button className="flex flex-col items-center justify-center p-3 h-16 text-xs font-medium text-neutral-700 dark:text-neutral-300 bg-white dark:bg-neutral-800 hover:bg-neutral-50 dark:hover:bg-neutral-700 border border-neutral-300 dark:border-neutral-600 rounded-lg transition-colors">
              <span className="text-lg mb-1">📊</span>
              <span>Audit</span>
            </button>
            <button className="flex flex-col items-center justify-center p-3 h-16 text-xs font-medium text-neutral-700 dark:text-neutral-300 bg-white dark:bg-neutral-800 hover:bg-neutral-50 dark:hover:bg-neutral-700 border border-neutral-300 dark:border-neutral-600 rounded-lg transition-colors">
              <span className="text-lg mb-1">⚙️</span>
              <span>Config</span>
            </button>
            <button className="flex flex-col items-center justify-center p-3 h-16 text-xs font-medium text-neutral-700 dark:text-neutral-300 bg-white dark:bg-neutral-800 hover:bg-neutral-50 dark:hover:bg-neutral-700 border border-neutral-300 dark:border-neutral-600 rounded-lg transition-colors">
              <span className="text-lg mb-1">💾</span>
              <span>Backup</span>
            </button>
            <button className="flex flex-col items-center justify-center p-3 h-16 text-xs font-medium text-neutral-700 dark:text-neutral-300 bg-white dark:bg-neutral-800 hover:bg-neutral-50 dark:hover:bg-neutral-700 border border-neutral-300 dark:border-neutral-600 rounded-lg transition-colors">
              <span className="text-lg mb-1">📈</span>
              <span>Reports</span>
            </button>
          </div>
        </div>
      </div>
    </DashboardLayout>
  )
}