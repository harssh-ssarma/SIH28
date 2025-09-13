"use client"

import DashboardLayout from '@/components/dashboard-layout'
import { useState } from 'react'

export default function FacultyLeaveRequests() {
  const [showForm, setShowForm] = useState(false)
  
  const leaveRequests = [
    { id: 1, type: 'Sick Leave', startDate: '2024-01-20', endDate: '2024-01-22', status: 'Pending', reason: 'Medical appointment' },
    { id: 2, type: 'Personal Leave', startDate: '2024-01-15', endDate: '2024-01-15', status: 'Approved', reason: 'Family function' },
    { id: 3, type: 'Conference', startDate: '2024-01-10', endDate: '2024-01-12', status: 'Rejected', reason: 'Academic conference' },
  ]

  return (
    <DashboardLayout role="faculty">
      <div className="space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-xl sm:text-2xl font-bold text-neutral-900 dark:text-neutral-100">Leave Requests</h1>
            <p className="text-sm text-neutral-600 dark:text-neutral-400 mt-1">Manage your leave applications</p>
          </div>
          <button 
            onClick={() => setShowForm(true)}
            className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors"
          >
            New Request
          </button>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="bg-white dark:bg-neutral-800 rounded-lg p-4 border border-neutral-200 dark:border-neutral-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-neutral-600 dark:text-neutral-400">Pending</p>
                <p className="text-2xl font-bold text-yellow-600">1</p>
              </div>
              <div className="w-10 h-10 bg-yellow-100 dark:bg-yellow-800 rounded-lg flex items-center justify-center">
                <span className="text-lg">⏳</span>
              </div>
            </div>
          </div>
          
          <div className="bg-white dark:bg-neutral-800 rounded-lg p-4 border border-neutral-200 dark:border-neutral-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-neutral-600 dark:text-neutral-400">Approved</p>
                <p className="text-2xl font-bold text-green-600">1</p>
              </div>
              <div className="w-10 h-10 bg-green-100 dark:bg-green-800 rounded-lg flex items-center justify-center">
                <span className="text-lg">✅</span>
              </div>
            </div>
          </div>
          
          <div className="bg-white dark:bg-neutral-800 rounded-lg p-4 border border-neutral-200 dark:border-neutral-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-neutral-600 dark:text-neutral-400">Rejected</p>
                <p className="text-2xl font-bold text-red-600">1</p>
              </div>
              <div className="w-10 h-10 bg-red-100 dark:bg-red-800 rounded-lg flex items-center justify-center">
                <span className="text-lg">❌</span>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-neutral-800 rounded-lg border border-neutral-200 dark:border-neutral-700 overflow-hidden">
          <div className="px-4 py-3 border-b border-neutral-200 dark:border-neutral-700">
            <h3 className="text-lg font-semibold text-neutral-900 dark:text-neutral-100">Recent Requests</h3>
          </div>
          
          <div className="block sm:hidden">
            {leaveRequests.map((request) => (
              <div key={request.id} className="p-4 border-b border-neutral-200 dark:border-neutral-700 last:border-b-0">
                <div className="flex items-start justify-between mb-2">
                  <div>
                    <h4 className="font-medium text-neutral-900 dark:text-neutral-100">{request.type}</h4>
                    <p className="text-sm text-neutral-600 dark:text-neutral-400">{request.startDate} - {request.endDate}</p>
                  </div>
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                    request.status === 'Approved' ? 'bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-200' :
                    request.status === 'Pending' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-800 dark:text-yellow-200' :
                    'bg-red-100 text-red-800 dark:bg-red-800 dark:text-red-200'
                  }`}>
                    {request.status}
                  </span>
                </div>
                <p className="text-xs text-neutral-500 dark:text-neutral-500">{request.reason}</p>
              </div>
            ))}
          </div>

          <div className="hidden sm:block overflow-x-auto">
            <table className="w-full">
              <thead className="bg-neutral-50 dark:bg-neutral-700">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-neutral-500 dark:text-neutral-400 uppercase">Type</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-neutral-500 dark:text-neutral-400 uppercase">Start Date</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-neutral-500 dark:text-neutral-400 uppercase">End Date</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-neutral-500 dark:text-neutral-400 uppercase">Status</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-neutral-500 dark:text-neutral-400 uppercase">Reason</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-neutral-200 dark:divide-neutral-700">
                {leaveRequests.map((request) => (
                  <tr key={request.id} className="hover:bg-neutral-50 dark:hover:bg-neutral-700">
                    <td className="px-4 py-3 text-sm font-medium text-neutral-900 dark:text-neutral-100">{request.type}</td>
                    <td className="px-4 py-3 text-sm text-neutral-600 dark:text-neutral-400">{request.startDate}</td>
                    <td className="px-4 py-3 text-sm text-neutral-600 dark:text-neutral-400">{request.endDate}</td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                        request.status === 'Approved' ? 'bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-200' :
                        request.status === 'Pending' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-800 dark:text-yellow-200' :
                        'bg-red-100 text-red-800 dark:bg-red-800 dark:text-red-200'
                      }`}>
                        {request.status}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm text-neutral-600 dark:text-neutral-400">{request.reason}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {showForm && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
            <div className="bg-white dark:bg-neutral-800 rounded-lg p-6 w-full max-w-md border border-neutral-200 dark:border-neutral-700">
              <h3 className="text-lg font-semibold text-neutral-900 dark:text-neutral-100 mb-4">New Leave Request</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-1">Leave Type</label>
                  <select className="w-full px-3 py-2 text-sm border border-neutral-300 dark:border-neutral-600 rounded-lg bg-white dark:bg-neutral-800">
                    <option>Sick Leave</option>
                    <option>Personal Leave</option>
                    <option>Conference</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-1">Start Date</label>
                  <input type="date" className="w-full px-3 py-2 text-sm border border-neutral-300 dark:border-neutral-600 rounded-lg bg-white dark:bg-neutral-800" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-1">End Date</label>
                  <input type="date" className="w-full px-3 py-2 text-sm border border-neutral-300 dark:border-neutral-600 rounded-lg bg-white dark:bg-neutral-800" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-1">Reason</label>
                  <textarea className="w-full px-3 py-2 text-sm border border-neutral-300 dark:border-neutral-600 rounded-lg bg-white dark:bg-neutral-800" rows={3}></textarea>
                </div>
              </div>
              <div className="flex gap-2 justify-end mt-6">
                <button 
                  onClick={() => setShowForm(false)}
                  className="px-4 py-2 text-sm font-medium text-neutral-700 dark:text-neutral-300 bg-white dark:bg-neutral-800 hover:bg-neutral-50 dark:hover:bg-neutral-700 border border-neutral-300 dark:border-neutral-600 rounded-lg transition-colors"
                >
                  Cancel
                </button>
                <button 
                  onClick={() => setShowForm(false)}
                  className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors"
                >
                  Submit
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  )
}