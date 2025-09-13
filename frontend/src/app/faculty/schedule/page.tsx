"use client"

import DashboardLayout from '@/components/dashboard-layout'

export default function FacultySchedule() {
  const schedule = [
    { time: '9:00 AM', monday: 'Math 101', tuesday: 'Physics 201', wednesday: 'Math 101', thursday: 'Physics 201', friday: 'Free' },
    { time: '10:00 AM', monday: 'Free', tuesday: 'Math 101', wednesday: 'Free', thursday: 'Math 101', friday: 'Physics 201' },
    { time: '11:00 AM', monday: 'Physics 201', tuesday: 'Free', wednesday: 'Physics 201', thursday: 'Free', friday: 'Math 101' },
    { time: '2:00 PM', monday: 'Lab Session', tuesday: 'Lab Session', wednesday: 'Free', thursday: 'Lab Session', friday: 'Free' },
  ]

  return (
    <DashboardLayout role="faculty">
      <div className="space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-xl sm:text-2xl font-bold text-neutral-900 dark:text-neutral-100">My Schedule</h1>
            <p className="text-sm text-neutral-600 dark:text-neutral-400 mt-1">View your weekly teaching schedule</p>
          </div>
          <div className="flex gap-2">
            <button className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors">
              Export PDF
            </button>
            <button className="px-4 py-2 text-sm font-medium text-neutral-700 dark:text-neutral-300 bg-white dark:bg-neutral-800 hover:bg-neutral-50 dark:hover:bg-neutral-700 border border-neutral-300 dark:border-neutral-600 rounded-lg transition-colors">
              Print
            </button>
          </div>
        </div>

        <div className="bg-white dark:bg-neutral-800 rounded-lg border border-neutral-200 dark:border-neutral-700 overflow-hidden">
          <div className="hidden sm:block overflow-x-auto">
            <table className="w-full">
              <thead className="bg-neutral-50 dark:bg-neutral-700">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-neutral-500 dark:text-neutral-400 uppercase">Time</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-neutral-500 dark:text-neutral-400 uppercase">Monday</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-neutral-500 dark:text-neutral-400 uppercase">Tuesday</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-neutral-500 dark:text-neutral-400 uppercase">Wednesday</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-neutral-500 dark:text-neutral-400 uppercase">Thursday</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-neutral-500 dark:text-neutral-400 uppercase">Friday</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-neutral-200 dark:divide-neutral-700">
                {schedule.map((slot, index) => (
                  <tr key={index} className="hover:bg-neutral-50 dark:hover:bg-neutral-700">
                    <td className="px-4 py-3 text-sm font-medium text-neutral-900 dark:text-neutral-100">{slot.time}</td>
                    <td className="px-4 py-3 text-sm text-neutral-600 dark:text-neutral-400">{slot.monday}</td>
                    <td className="px-4 py-3 text-sm text-neutral-600 dark:text-neutral-400">{slot.tuesday}</td>
                    <td className="px-4 py-3 text-sm text-neutral-600 dark:text-neutral-400">{slot.wednesday}</td>
                    <td className="px-4 py-3 text-sm text-neutral-600 dark:text-neutral-400">{slot.thursday}</td>
                    <td className="px-4 py-3 text-sm text-neutral-600 dark:text-neutral-400">{slot.friday}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="block sm:hidden">
            {schedule.map((slot, index) => (
              <div key={index} className="p-4 border-b border-neutral-200 dark:border-neutral-700 last:border-b-0">
                <h3 className="font-medium text-neutral-900 dark:text-neutral-100 mb-3">{slot.time}</h3>
                <div className="grid grid-cols-1 gap-2">
                  <div className="flex justify-between"><span className="text-xs text-neutral-500">Mon:</span><span className="text-sm">{slot.monday}</span></div>
                  <div className="flex justify-between"><span className="text-xs text-neutral-500">Tue:</span><span className="text-sm">{slot.tuesday}</span></div>
                  <div className="flex justify-between"><span className="text-xs text-neutral-500">Wed:</span><span className="text-sm">{slot.wednesday}</span></div>
                  <div className="flex justify-between"><span className="text-xs text-neutral-500">Thu:</span><span className="text-sm">{slot.thursday}</span></div>
                  <div className="flex justify-between"><span className="text-xs text-neutral-500">Fri:</span><span className="text-sm">{slot.friday}</span></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </DashboardLayout>
  )
}