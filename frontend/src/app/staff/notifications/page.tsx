'use client'

import DashboardLayout from '@/components/dashboard-layout'

export default function StaffNotifications() {
  return (
    <DashboardLayout role="staff">
      <div className="space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h2 className="text-xl sm:text-2xl lg:text-3xl font-semibold text-gray-800 dark:text-gray-200">
              Notifications
            </h2>
            <p className="text-sm sm:text-base text-gray-600 dark:text-gray-400 mt-1">
              Department updates and approvals
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
                type: 'approval',
                title: 'Leave Request Pending',
                message: 'Dr. Sharma has requested leave for March 20-22',
                time: '2 hours ago',
                read: false,
              },
              {
                type: 'report',
                title: 'Monthly Report Due',
                message: 'Department performance report due by end of week',
                time: '1 day ago',
                read: false,
              },
              {
                type: 'message',
                title: 'New Message from Admin',
                message: 'Budget allocation meeting scheduled for Friday',
                time: '2 days ago',
                read: true,
              },
            ].map((notification, index) => (
              <div
                key={index}
                className={`p-4 rounded-lg border-l-4 ${
                  notification.type === 'approval'
                    ? 'bg-orange-50 dark:bg-orange-900/10 border-orange-500'
                    : notification.type === 'report'
                      ? 'bg-blue-50 dark:bg-blue-900/10 border-blue-500'
                      : 'bg-green-50 dark:bg-green-900/10 border-green-500'
                } ${!notification.read ? 'ring-2 ring-blue-200' : ''}`}
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex items-start gap-3 flex-1">
                    <div className="text-lg">
                      {notification.type === 'approval'
                        ? '✅'
                        : notification.type === 'report'
                          ? '📊'
                          : '💬'}
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
