"use client"

import DashboardLayout from '@/components/dashboard-layout'

export default function StaffAnalytics() {
  return (
    <DashboardLayout role="staff">
      <div className="space-y-6">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold text-neutral-900 dark:text-neutral-100">Analytics</h1>
          <p className="text-sm text-neutral-600 dark:text-neutral-400 mt-1">Performance metrics and insights</p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-white dark:bg-neutral-800 rounded-lg p-4 border border-neutral-200 dark:border-neutral-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-neutral-600 dark:text-neutral-400">Total Classes</p>
                <p className="text-2xl font-bold text-blue-600">156</p>
              </div>
              <div className="w-10 h-10 bg-blue-100 dark:bg-blue-800 rounded-lg flex items-center justify-center">
                <span className="text-lg">📚</span>
              </div>
            </div>
          </div>
          
          <div className="bg-white dark:bg-neutral-800 rounded-lg p-4 border border-neutral-200 dark:border-neutral-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-neutral-600 dark:text-neutral-400">Efficiency Rate</p>
                <p className="text-2xl font-bold text-green-600">94%</p>
              </div>
              <div className="w-10 h-10 bg-green-100 dark:bg-green-800 rounded-lg flex items-center justify-center">
                <span className="text-lg">📈</span>
              </div>
            </div>
          </div>
          
          <div className="bg-white dark:bg-neutral-800 rounded-lg p-4 border border-neutral-200 dark:border-neutral-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-neutral-600 dark:text-neutral-400">Conflicts Resolved</p>
                <p className="text-2xl font-bold text-yellow-600">23</p>
              </div>
              <div className="w-10 h-10 bg-yellow-100 dark:bg-yellow-800 rounded-lg flex items-center justify-center">
                <span className="text-lg">⚡</span>
              </div>
            </div>
          </div>
          
          <div className="bg-white dark:bg-neutral-800 rounded-lg p-4 border border-neutral-200 dark:border-neutral-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-neutral-600 dark:text-neutral-400">Satisfaction</p>
                <p className="text-2xl font-bold text-purple-600">4.8</p>
              </div>
              <div className="w-10 h-10 bg-purple-100 dark:bg-purple-800 rounded-lg flex items-center justify-center">
                <span className="text-lg">⭐</span>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-neutral-800 rounded-lg p-4 border border-neutral-200 dark:border-neutral-700">
          <h3 className="text-lg font-semibold text-neutral-900 dark:text-neutral-100 mb-4">Performance Trends</h3>
          <div className="h-64 flex items-center justify-center text-neutral-500 dark:text-neutral-400">
            Chart placeholder - Analytics visualization would go here
          </div>
        </div>
      </div>
    </DashboardLayout>
  )
}