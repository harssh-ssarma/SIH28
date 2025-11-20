'use client'

import { useState } from 'react'
import Sidebar from '@/components/layout/Sidebar'

interface DashboardLayoutProps {
  children: React.ReactNode
  role: 'admin' | 'staff' | 'faculty' | 'student'
  pageTitle?: string
  pageDescription?: string
}

export default function DashboardLayout({
  children,
  role,
  pageTitle,
  pageDescription,
}: DashboardLayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
  const [showSignOutDialog, setShowSignOutDialog] = useState(false)

  return (
    <>
      <div
        className={`min-h-screen bg-[#FFFFFF] dark:bg-[#121212] transition-colors duration-300 ${
          showSignOutDialog ? 'blur-sm' : ''
        }`}
      >
        <Sidebar
          sidebarOpen={sidebarOpen}
          sidebarCollapsed={sidebarCollapsed}
          setSidebarOpen={setSidebarOpen}
          setSidebarCollapsed={setSidebarCollapsed}
          role={role}
          setShowSignOutDialog={setShowSignOutDialog}
        />

        {/* Main content */}
        <div
          className={`transition-all duration-300 ease-out ${
            sidebarCollapsed ? 'md:ml-16' : 'md:ml-56'
          }`}
        >
          <main className="min-h-screen p-4 lg:p-6">{children}</main>
        </div>
      </div>

      {/* Sign Out Confirmation Dialog */}
      {showSignOutDialog && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-sm">
          <div className="bg-white dark:bg-[#1E1E1E] rounded-xl p-6 w-full max-w-sm border border-[#E0E0E0] dark:border-[#2A2A2A] shadow-2xl">
            <h3 className="text-lg font-semibold text-[#2C2C2C] dark:text-[#FFFFFF] mb-2">
              Sign Out
            </h3>
            <p className="text-sm text-[#6B6B6B] dark:text-[#B3B3B3] mb-6">
              Are you sure you want to sign out?
            </p>
            <div className="flex gap-3 justify-end">
              <button onClick={() => setShowSignOutDialog(false)} className="btn-secondary">
                Cancel
              </button>
              <button onClick={() => (window.location.href = '/login')} className="btn-danger">
                Sign Out
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}
