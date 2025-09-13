"use client"

import DashboardLayout from '@/components/dashboard-layout'

export default function StaffReports() {
  return (
    <DashboardLayout role="staff">
      <div className="space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-xl sm:text-2xl font-bold text-neutral-900 dark:text-neutral-100">Reports</h1>
            <p className="text-sm text-neutral-600 dark:text-neutral-400 mt-1">Generate and view system reports</p>
          </div>
          <button className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors">
            Generate Report
          </button>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <div className="bg-white dark:bg-neutral-800 rounded-lg p-4 border border-neutral-200 dark:border-neutral-700">
            <h3 className="font-semibold text-neutral-900 dark:text-neutral-100 mb-2">Faculty Utilization</h3>
            <p className="text-sm text-neutral-600 dark:text-neutral-400 mb-4">Teaching load analysis</p>
            <button className="w-full px-3 py-2 text-sm font-medium text-blue-600 bg-blue-50 hover:bg-blue-100 dark:bg-blue-900/20 dark:hover:bg-blue-900/30 rounded-lg transition-colors">
              View Report
            </button>
          </div>
          
          <div className="bg-white dark:bg-neutral-800 rounded-lg p-4 border border-neutral-200 dark:border-neutral-700">
            <h3 className="font-semibold text-neutral-900 dark:text-neutral-100 mb-2">Room Usage</h3>
            <p className="text-sm text-neutral-600 dark:text-neutral-400 mb-4">Classroom occupancy stats</p>
            <button className="w-full px-3 py-2 text-sm font-medium text-blue-600 bg-blue-50 hover:bg-blue-100 dark:bg-blue-900/20 dark:hover:bg-blue-900/30 rounded-lg transition-colors">
              View Report
            </button>
          </div>
          
          <div className="bg-white dark:bg-neutral-800 rounded-lg p-4 border border-neutral-200 dark:border-neutral-700">
            <h3 className="font-semibold text-neutral-900 dark:text-neutral-100 mb-2">Attendance</h3>
            <p className="text-sm text-neutral-600 dark:text-neutral-400 mb-4">Student attendance summary</p>
            <button className="w-full px-3 py-2 text-sm font-medium text-blue-600 bg-blue-50 hover:bg-blue-100 dark:bg-blue-900/20 dark:hover:bg-blue-900/30 rounded-lg transition-colors">
              View Report
            </button>
          </div>
        </div>
      </div>
    </DashboardLayout>
  )
}