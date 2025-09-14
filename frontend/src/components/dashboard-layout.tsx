"use client"

import { useState } from 'react'
import Header from '@/components/layout/Header'
import Sidebar from '@/components/layout/Sidebar'

interface DashboardLayoutProps {
  children: React.ReactNode
  role: 'admin' | 'staff' | 'faculty' | 'student'
}

export default function DashboardLayout({ children, role }: DashboardLayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
  const [showSignOutDialog, setShowSignOutDialog] = useState(false)

  return (
    <>
      <div className={`min-h-screen bg-white dark:bg-[#2a2a2a] transition-colors duration-300 ${showSignOutDialog ? 'blur-sm' : ''}`}>
        <Header 
          sidebarOpen={sidebarOpen}
          sidebarCollapsed={sidebarCollapsed}
          setSidebarOpen={setSidebarOpen}
          setSidebarCollapsed={setSidebarCollapsed}
          setShowSignOutDialog={setShowSignOutDialog}
        />
        
        <Sidebar 
          sidebarOpen={sidebarOpen}
          sidebarCollapsed={sidebarCollapsed}
          setSidebarOpen={setSidebarOpen}
          role={role}
        />

        {/* Main content */}
        <div className={`transition-all duration-300 ease-in-out ${sidebarCollapsed ? 'md:ml-16' : 'md:ml-56'}`}>
          <main className="min-h-[calc(100vh-20px)] sm:min-h-[calc(100vh-28px)] mt-16 mb-2 mr-2 ml-2 sm:mb-2 sm:mt-15 sm:mr-1 sm:ml-1 pt-[15px] sm:pt-[15px] md:pt-[15px] overflow-y-auto bg-gray-100 dark:bg-[#1f1f1f] scrollbar-hide rounded-2xl">
            <div className="pl-2 pr-2 pb-5 pt-5 sm:p-2 lg:p-4">
              {children}
            </div>
          </main>
        </div>
      </div>
      
      {/* Sign Out Confirmation Dialog */}
      {showSignOutDialog && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="bg-white dark:bg-[#2a2a2a] rounded-xl p-6 w-full max-w-sm border border-gray-200 dark:border-gray-700 shadow-lg">
            <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-2">
              Sign Out
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
              Are you sure you want to sign out?
            </p>
            <div className="flex gap-2 justify-end">
              <button 
                onClick={() => setShowSignOutDialog(false)}
                className="btn-secondary"
              >
                Cancel
              </button>
              <button 
                onClick={() => window.location.href = '/login'}
                className="btn-danger"
              >
                Sign Out
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}