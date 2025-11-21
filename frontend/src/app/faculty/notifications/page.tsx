'use client'

import DashboardLayout from '@/components/dashboard-layout'

export default function FacultyNotifications() {
  return (
    <DashboardLayout role="faculty">
      <div className="space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h2 className="text-xl sm:text-2xl lg:text-3xl font-semibold text-gray-800 dark:text-gray-200">
              Notifications
            </h2>
            <p className="text-sm sm:text-base text-gray-600 dark:text-gray-400 mt-1">
              Schedule updates and messages
            </p>
          </div>
          <button className="btn-secondary">
            <span className="mr-2">✅</span>Mark All Read
          </button>
        </div>

        <div className="card">
          <div className="space-y-3">
            {[
              {
                type: 'schedule',
                title: 'Schedule Change',
                message: 'Your Monday 10 AM class has been moved to Room 305',
                time: '30 minutes ago',
                read: false,
              },
              {
                type: 'leave',
                title: 'Leave Request Approved',
                message: 'Your leave request for March 25-27 has been approved',
                time: '4 hours ago',
                read: false,
              },
              {
                type: 'student',
                title: 'Student Query',
                message: 'Student Rahul Kumar has sent you a message',
                time: '1 day ago',
                read: true,
              },
            ].map((notification, index) => (
              <div
                key={index}
                className={`p-4 rounded-lg border-l-4 ${
                  notification.type === 'schedule'
                    ? 'bg-blue-50 dark:bg-blue-900/10 border-blue-500'
                    : notification.type === 'leave'
                      ? 'bg-green-50 dark:bg-green-900/10 border-green-500'
                      : 'bg-purple-50 dark:bg-purple-900/10 border-purple-500'
                } ${!notification.read ? 'ring-2 ring-blue-200' : ''}`}
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex items-start gap-3 flex-1">
                    <div className="text-lg">
                      {notification.type === 'schedule'
                        ? '📅'
                        : notification.type === 'leave'
                          ? '✅'
                          : '🎓'}
                    </div>
                    <div className="flex-1">
                      <h4 className="font-medium text-sm text-gray-800 dark:text-gray-200">
                        {notification.title}
                      </h4>
                      <p className="text-xs text-gray-600 dark:text-gray-400 mb-2">
                        {notification.message}
                      </p>
                      <span className="text-xs text-gray-500">{notification.time}</span>
                    </div>
                  </div>
                  {!notification.read && (
                    <button className="btn-ghost text-xs px-2 py-1">Mark Read</button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </DashboardLayout>
  )
}
