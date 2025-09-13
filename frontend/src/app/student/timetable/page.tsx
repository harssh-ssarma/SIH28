"use client"

import DashboardLayout from '@/components/dashboard-layout'

export default function StudentTimetable() {
  return (
    <DashboardLayout role="student">
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h2 className="text-xl font-semibold text-neutral-900 dark:text-neutral-100">My Timetable</h2>
            <p className="text-sm text-neutral-600 dark:text-neutral-400 mt-1">View your weekly schedule</p>
          </div>
          <div className="flex gap-2">
            <button className="btn-secondary">
              📤 Export
            </button>
            <button className="btn-primary">
              📅 Sync Calendar
            </button>
          </div>
        </div>

        {/* Timetable */}
        <div className="card">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-neutral-200 dark:border-neutral-700">
                  <th className="text-left py-3 px-4 font-medium text-neutral-900 dark:text-neutral-100">Time</th>
                  <th className="text-left py-3 px-4 font-medium text-neutral-900 dark:text-neutral-100">Monday</th>
                  <th className="text-left py-3 px-4 font-medium text-neutral-900 dark:text-neutral-100">Tuesday</th>
                  <th className="text-left py-3 px-4 font-medium text-neutral-900 dark:text-neutral-100">Wednesday</th>
                  <th className="text-left py-3 px-4 font-medium text-neutral-900 dark:text-neutral-100">Thursday</th>
                  <th className="text-left py-3 px-4 font-medium text-neutral-900 dark:text-neutral-100">Friday</th>
                </tr>
              </thead>
              <tbody>
                {[
                  { time: '09:00 - 10:30', mon: 'Data Structures\nDr. Rajesh Kumar\nLab 1', tue: '', wed: 'Database Systems\nProf. Meera Sharma\nRoom 205', thu: '', fri: 'Software Engineering\nDr. Vikram Gupta\nRoom 301' },
                  { time: '11:00 - 12:30', mon: '', tue: 'Machine Learning\nDr. Anita Verma\nLab 2', wed: '', thu: 'Web Development\nProf. Suresh Reddy\nLab 3', fri: '' },
                  { time: '14:00 - 15:30', mon: 'Technical Writing\nDr. Kavita Joshi\nRoom 101', tue: '', wed: 'Data Structures\nDr. Rajesh Kumar\nRoom 205', thu: '', fri: 'Database Systems\nProf. Meera Sharma\nLab 1' },
                ].map((row, index) => (
                  <tr key={index} className="border-b border-neutral-100 dark:border-neutral-800">
                    <td className="py-3 px-4 font-medium text-neutral-900 dark:text-neutral-100">{row.time}</td>
                    <td className="py-3 px-4">{row.mon && <div className="p-2 bg-blue-50 dark:bg-blue-900/20 rounded text-xs">{row.mon}</div>}</td>
                    <td className="py-3 px-4">{row.tue && <div className="p-2 bg-green-50 dark:bg-green-900/20 rounded text-xs">{row.tue}</div>}</td>
                    <td className="py-3 px-4">{row.wed && <div className="p-2 bg-purple-50 dark:bg-purple-900/20 rounded text-xs">{row.wed}</div>}</td>
                    <td className="py-3 px-4">{row.thu && <div className="p-2 bg-orange-50 dark:bg-orange-900/20 rounded text-xs">{row.thu}</div>}</td>
                    <td className="py-3 px-4">{row.fri && <div className="p-2 bg-red-50 dark:bg-red-900/20 rounded text-xs">{row.fri}</div>}</td>
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