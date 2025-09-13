"use client"

import DashboardLayout from '@/components/dashboard-layout'

export default function StudentEnrollments() {
  const courses = [
    { code: 'MATH101', name: 'Calculus I', credits: 3, status: 'Enrolled', grade: 'A-' },
    { code: 'PHYS201', name: 'Physics II', credits: 4, status: 'Enrolled', grade: 'B+' },
    { code: 'CHEM101', name: 'General Chemistry', credits: 3, status: 'Enrolled', grade: 'A' },
    { code: 'ENG102', name: 'English Literature', credits: 2, status: 'Completed', grade: 'A-' },
  ]

  return (
    <DashboardLayout role="student">
      <div className="space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-xl sm:text-2xl font-bold text-neutral-900 dark:text-neutral-100">Course Enrollments</h1>
            <p className="text-sm text-neutral-600 dark:text-neutral-400 mt-1">Manage your course registrations</p>
          </div>
          <button className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors">
            Add Course
          </button>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="bg-white dark:bg-neutral-800 rounded-lg p-4 border border-neutral-200 dark:border-neutral-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-neutral-600 dark:text-neutral-400">Total Credits</p>
                <p className="text-2xl font-bold text-blue-600">12</p>
              </div>
              <div className="w-10 h-10 bg-blue-100 dark:bg-blue-800 rounded-lg flex items-center justify-center">
                <span className="text-lg">📚</span>
              </div>
            </div>
          </div>
          
          <div className="bg-white dark:bg-neutral-800 rounded-lg p-4 border border-neutral-200 dark:border-neutral-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-neutral-600 dark:text-neutral-400">Current GPA</p>
                <p className="text-2xl font-bold text-green-600">3.7</p>
              </div>
              <div className="w-10 h-10 bg-green-100 dark:bg-green-800 rounded-lg flex items-center justify-center">
                <span className="text-lg">⭐</span>
              </div>
            </div>
          </div>
          
          <div className="bg-white dark:bg-neutral-800 rounded-lg p-4 border border-neutral-200 dark:border-neutral-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-neutral-600 dark:text-neutral-400">Completed</p>
                <p className="text-2xl font-bold text-purple-600">1</p>
              </div>
              <div className="w-10 h-10 bg-purple-100 dark:bg-purple-800 rounded-lg flex items-center justify-center">
                <span className="text-lg">✅</span>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-neutral-800 rounded-lg border border-neutral-200 dark:border-neutral-700 overflow-hidden">
          <div className="px-4 py-3 border-b border-neutral-200 dark:border-neutral-700">
            <h3 className="text-lg font-semibold text-neutral-900 dark:text-neutral-100">Enrolled Courses</h3>
          </div>
          
          <div className="block sm:hidden">
            {courses.map((course, index) => (
              <div key={index} className="p-4 border-b border-neutral-200 dark:border-neutral-700 last:border-b-0">
                <div className="flex items-start justify-between mb-2">
                  <div>
                    <h4 className="font-medium text-neutral-900 dark:text-neutral-100">{course.code}</h4>
                    <p className="text-sm text-neutral-600 dark:text-neutral-400">{course.name}</p>
                    <p className="text-xs text-neutral-500 dark:text-neutral-500">{course.credits} credits</p>
                  </div>
                  <div className="text-right">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                      course.status === 'Enrolled' ? 'bg-blue-100 text-blue-800 dark:bg-blue-800 dark:text-blue-200' :
                      'bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-200'
                    }`}>
                      {course.status}
                    </span>
                    <p className="text-sm font-medium mt-1">{course.grade}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="hidden sm:block overflow-x-auto">
            <table className="w-full">
              <thead className="bg-neutral-50 dark:bg-neutral-700">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-neutral-500 dark:text-neutral-400 uppercase">Course Code</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-neutral-500 dark:text-neutral-400 uppercase">Course Name</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-neutral-500 dark:text-neutral-400 uppercase">Credits</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-neutral-500 dark:text-neutral-400 uppercase">Status</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-neutral-500 dark:text-neutral-400 uppercase">Grade</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-neutral-200 dark:divide-neutral-700">
                {courses.map((course, index) => (
                  <tr key={index} className="hover:bg-neutral-50 dark:hover:bg-neutral-700">
                    <td className="px-4 py-3 text-sm font-medium text-neutral-900 dark:text-neutral-100">{course.code}</td>
                    <td className="px-4 py-3 text-sm text-neutral-600 dark:text-neutral-400">{course.name}</td>
                    <td className="px-4 py-3 text-sm text-neutral-600 dark:text-neutral-400">{course.credits}</td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                        course.status === 'Enrolled' ? 'bg-blue-100 text-blue-800 dark:bg-blue-800 dark:text-blue-200' :
                        'bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-200'
                      }`}>
                        {course.status}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm font-medium text-neutral-900 dark:text-neutral-100">{course.grade}</td>
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