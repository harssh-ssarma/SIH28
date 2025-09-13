"use client"

import { useState } from 'react'

interface DashboardLayoutProps {
  children: React.ReactNode
  role: 'admin' | 'staff' | 'faculty' | 'student'
}

const navigationItems = {
  admin: [
    { name: 'Dashboard', href: '/admin/dashboard', icon: '📊' },
    { name: 'Users', href: '/admin/users', icon: '👥' },
    { name: 'Courses', href: '/admin/courses', icon: '📚' },
    { name: 'Classrooms', href: '/admin/classrooms', icon: '🏫' },
    { name: 'Timetables', href: '/admin/timetables', icon: '📅' },
    { name: 'Approvals', href: '/admin/approvals', icon: '✅' },
  ],
  staff: [
    { name: 'Dashboard', href: '/staff/dashboard', icon: '📊' },
    { name: 'Approvals', href: '/staff/approvals', icon: '✅' },
    { name: 'Reports', href: '/staff/reports', icon: '📊' },
    { name: 'Analytics', href: '/staff/analytics', icon: '📊' },
  ],
  faculty: [
    { name: 'Dashboard', href: '/faculty/dashboard', icon: '📊' },
    { name: 'My Schedule', href: '/faculty/schedule', icon: '📅' },
    { name: 'Preferences', href: '/faculty/preferences', icon: '⚙️' },
    { name: 'Leave Requests', href: '/faculty/leave-requests', icon: '📝' },
  ],
  student: [
    { name: 'Dashboard', href: '/student/dashboard', icon: '📊' },
    { name: 'My Timetable', href: '/student/timetable', icon: '📅' },
    { name: 'Enrollments', href: '/student/enrollments', icon: '📚' },
    { name: 'Notifications', href: '/student/notifications', icon: '🔔' },
  ],
}

export default function DashboardLayout({ children, role }: DashboardLayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
  const [showSettings, setShowSettings] = useState(false)
  const [showSignOutDialog, setShowSignOutDialog] = useState(false)
  const items = navigationItems[role] || []

  return (
    <div className="min-h-screen">
      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 z-40 bg-black/50 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}
      
      {/* Settings dropdown overlay */}
      {showSettings && (
        <div 
          className="fixed inset-0 z-30"
          onClick={() => setShowSettings(false)}
        />
      )}

      {/* Sidebar */}
      <div className={`fixed inset-y-0 left-0 z-50 bg-white dark:bg-neutral-800 transform transition-all duration-300 ease-in-out ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'} lg:translate-x-0 ${sidebarCollapsed ? 'lg:w-16' : 'lg:w-56'} w-56`}>
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="flex items-center justify-between px-4 py-3 min-h-[60px]">
            {sidebarCollapsed ? (
              <button
                onClick={() => setSidebarCollapsed(false)}
                className="min-w-[2.5rem] w-10 h-10 rounded-lg hover:bg-neutral-100 dark:hover:bg-neutral-700 active:bg-neutral-200 dark:active:bg-neutral-600 active:scale-95 transition-all duration-100 mx-auto flex items-center justify-center"
                title="Open menu"
              >
                <span className="text-lg">☰</span>
              </button>
            ) : (
              <>
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center text-white font-bold">
                    S
                  </div>
                  <span className="text-xl font-bold text-neutral-900 dark:text-neutral-100">SIH28</span>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => setSidebarCollapsed(true)}
                    className="hidden lg:block w-10 h-10 rounded-lg hover:bg-neutral-100 dark:hover:bg-neutral-700 active:bg-neutral-200 dark:active:bg-neutral-600 active:scale-95 transition-all duration-100 flex items-center justify-center"
                  >
                    <span className="text-lg leading-none">←</span>
                  </button>
                  <button
                    onClick={() => setSidebarOpen(false)}
                    className="lg:hidden w-10 h-10 rounded-lg hover:bg-neutral-100 dark:hover:bg-neutral-700 active:bg-neutral-200 dark:active:bg-neutral-600 active:scale-95 transition-all duration-100 flex items-center justify-center"
                  >
                    <span className="text-lg leading-none">←</span>
                  </button>
                </div>
              </>
            )}
          </div>

          {/* Navigation */}
          <nav className="flex-1 p-4 space-y-2 overflow-y-auto overflow-x-hidden scrollbar-hide" style={{overscrollBehavior: 'contain'}}>
            {items.map((item) => (
              <a
                key={item.name}
                href={item.href}
                className={`flex items-center text-sm font-medium text-neutral-700 dark:text-neutral-300 hover:bg-neutral-100 dark:hover:bg-neutral-700 hover:text-neutral-900 dark:hover:text-neutral-100 rounded-md transition-colors duration-200 ${sidebarCollapsed ? 'lg:justify-center lg:w-10 lg:h-10 lg:p-0' : 'px-3 py-2'}`}
                title={sidebarCollapsed ? item.name : ''}
                onClick={() => setSidebarOpen(false)}
              >
                <span className={`text-lg ${sidebarCollapsed ? '' : 'mr-3'}`}>{item.icon}</span>
                <span className={`${sidebarCollapsed ? 'lg:hidden' : ''}`}>{item.name}</span>
              </a>
            ))}
          </nav>

          {/* User info */}
          <div className="p-4">
            <div className={`flex items-center gap-3 ${sidebarCollapsed ? 'lg:justify-center' : ''}`}>
              <div className="w-8 h-8 bg-neutral-300 dark:bg-neutral-600 rounded-full flex items-center justify-center">
                👤
              </div>
              <div className={`flex-1 min-w-0 ${sidebarCollapsed ? 'lg:hidden' : ''}`}>
                <p className="text-sm font-medium text-neutral-900 dark:text-neutral-100 truncate">
                  {role === 'admin' ? 'Harsh Sharma' : 
                   role === 'staff' ? 'Priya Patel' :
                   role === 'faculty' ? 'Dr. Rajesh Kumar' : 'Arjun Singh'}
                </p>
                <p className="text-xs text-neutral-500 dark:text-neutral-400 truncate">
                  {role === 'admin' ? 'harsh.sharma@sih28.edu' : 
                   role === 'staff' ? 'priya.patel@sih28.edu' :
                   role === 'faculty' ? 'rajesh.kumar@sih28.edu' : 'arjun.singh@sih28.edu'}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className={`transition-all duration-300 ease-in-out ${sidebarCollapsed ? 'lg:ml-16' : 'lg:ml-56'}`}>
        {/* Header */}
        <header className="bg-white dark:bg-neutral-800 px-4 py-3 lg:px-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button
                onClick={() => {
                  setSidebarOpen(true)
                  setSidebarCollapsed(false)
                }}
                className={`w-10 h-10 rounded-lg hover:bg-neutral-100 dark:hover:bg-neutral-700 active:bg-neutral-200 dark:active:bg-neutral-600 active:scale-95 transition-all duration-100 lg:hidden flex items-center justify-center`}
                title="Open menu"
              >
                <span className="text-lg">☰</span>
              </button>

              <h1 className="text-lg lg:text-xl font-semibold text-neutral-900 dark:text-neutral-100 capitalize">
                {role}
              </h1>
            </div>
            
            <div className="flex items-center gap-2">
              <button className="w-10 h-10 rounded-lg hover:bg-neutral-100 dark:hover:bg-neutral-700 active:bg-neutral-200 dark:active:bg-neutral-600 active:scale-95 transition-all duration-100 flex items-center justify-center">
                🔔
              </button>
              <button className="w-10 h-10 rounded-lg hover:bg-neutral-100 dark:hover:bg-neutral-700 active:bg-neutral-200 dark:active:bg-neutral-600 active:scale-95 transition-all duration-100 flex items-center justify-center">
                🌙
              </button>
              <div className="relative">
                <button 
                  onClick={() => setShowSettings(!showSettings)}
                  className="w-10 h-10 rounded-lg hover:bg-neutral-100 dark:hover:bg-neutral-700 active:bg-neutral-200 dark:active:bg-neutral-600 active:scale-95 transition-all duration-100 flex items-center justify-center"
                >
                  ⚙️
                </button>
                {showSettings && (
                  <div className="absolute right-0 mt-2 w-48 bg-white dark:bg-neutral-800 border border-neutral-200 dark:border-neutral-700 rounded-lg shadow-lg z-50">
                    <div className="py-1">
                      <button className="w-full px-4 py-2 text-left text-sm hover:bg-neutral-100 dark:hover:bg-neutral-700 active:bg-neutral-200 dark:active:bg-neutral-600 transition-all duration-100 flex items-center gap-2">
                        👤 My Profile
                      </button>
                      <button 
                        onClick={() => { setShowSignOutDialog(true); setShowSettings(false); }}
                        className="w-full px-4 py-2 text-left text-sm hover:bg-neutral-100 dark:hover:bg-neutral-700 active:bg-neutral-200 dark:active:bg-neutral-600 transition-all duration-100 flex items-center gap-2 text-red-600"
                      >
                        🚪 Sign Out
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </header>

        {/* Content */}
        <main className="p-4 lg:p-6 bg-neutral-50 dark:bg-neutral-900 rounded-xl m-2 h-[calc(100vh-76px)] overflow-y-auto scrollbar-hide" style={{overscrollBehavior: 'contain'}}>
          {children}
        </main>
      </div>
      
      {/* Sign Out Confirmation Dialog */}
      {showSignOutDialog && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="bg-white dark:bg-neutral-800 rounded-lg p-6 w-full max-w-sm border border-neutral-200 dark:border-neutral-700">
            <h3 className="text-lg font-semibold text-neutral-900 dark:text-neutral-100 mb-2">
              Sign Out
            </h3>
            <p className="text-sm text-neutral-600 dark:text-neutral-400 mb-4">
              Are you sure you want to sign out?
            </p>
            <div className="flex gap-2 justify-end">
              <button 
                onClick={() => setShowSignOutDialog(false)}
                className="px-4 py-2 text-sm font-medium text-neutral-700 dark:text-neutral-300 bg-white dark:bg-neutral-800 hover:bg-neutral-50 dark:hover:bg-neutral-700 active:bg-neutral-100 dark:active:bg-neutral-600 active:scale-98 rounded-lg transition-all duration-100"
              >
                Cancel
              </button>
              <button 
                onClick={() => window.location.href = '/login'}
                className="px-4 py-2 text-sm font-medium text-white bg-red-600 hover:bg-red-700 active:bg-red-800 active:scale-98 rounded-lg transition-all duration-100"
              >
                Sign Out
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}