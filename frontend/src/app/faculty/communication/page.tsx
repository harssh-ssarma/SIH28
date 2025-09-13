import DashboardLayout from '@/components/dashboard-layout'

export default function CommunicationPage() {
  const announcements = [
    { id: 1, title: 'Class Postponed', message: 'Tomorrow\'s Database Systems class is postponed to Friday', date: '2024-03-18', recipients: 'CS Semester 5' },
    { id: 2, title: 'Assignment Deadline', message: 'Data Structures assignment deadline extended to March 25', date: '2024-03-17', recipients: 'CS Semester 3' },
    { id: 3, title: 'Extra Class', message: 'Additional tutorial session on Saturday 10 AM', date: '2024-03-16', recipients: 'All Students' }
  ]

  return (
    <DashboardLayout role="faculty">
      <div className="space-y-4 sm:space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <h1 className="text-2xl sm:text-3xl font-bold text-neutral-900 dark:text-neutral-100">Communication</h1>
          <button className="btn-primary w-full sm:w-auto">
            <span className="mr-2">📢</span>
            New Announcement
          </button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6">
          <div className="card">
            <div className="card-header">
              <h3 className="card-title">Send Announcement</h3>
              <p className="card-description">Communicate with your students</p>
            </div>
            
            <form className="space-y-3 sm:space-y-4">
              <div className="form-group">
                <label className="form-label text-sm sm:text-base">Recipients</label>
                <select className="input-primary text-sm sm:text-base">
                  <option>CS Semester 5</option>
                  <option>CS Semester 3</option>
                  <option>All My Students</option>
                  <option>Specific Course</option>
                </select>
              </div>
              
              <div className="form-group">
                <label className="form-label text-sm sm:text-base">Subject</label>
                <input type="text" className="input-primary text-sm sm:text-base" placeholder="Enter announcement title" />
              </div>
              
              <div className="form-group">
                <label className="form-label text-sm sm:text-base">Message</label>
                <textarea className="input-primary min-h-20 sm:min-h-24 text-sm sm:text-base" placeholder="Enter your message"></textarea>
              </div>
              
              <div className="form-group">
                <label className="flex items-center gap-2">
                  <input type="checkbox" className="rounded w-4 h-4" />
                  <span className="text-xs sm:text-sm">Send email notification</span>
                </label>
              </div>
              
              <div className="flex gap-2 sm:gap-3">
                <button type="button" className="btn-secondary flex-1 text-sm sm:text-base py-2 sm:py-2.5">Save Draft</button>
                <button type="submit" className="btn-primary flex-1 text-sm sm:text-base py-2 sm:py-2.5">Send Now</button>
              </div>
            </form>
          </div>

          <div className="card">
            <div className="card-header">
              <h3 className="card-title">Quick Messages</h3>
              <p className="card-description">Common announcement templates</p>
            </div>
            
            <div className="space-y-3">
              {[
                'Class cancelled due to emergency',
                'Assignment deadline extended',
                'Extra tutorial session scheduled',
                'Exam schedule updated',
                'Course material uploaded'
              ].map((template, index) => (
                <button key={index} className="w-full text-left p-2 sm:p-3 bg-neutral-50 dark:bg-neutral-800 rounded-lg hover:bg-neutral-100 dark:hover:bg-neutral-700 transition-colors">
                  <p className="text-xs sm:text-sm text-neutral-900 dark:text-neutral-100">{template}</p>
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Recent Announcements</h3>
            <p className="card-description">Your sent messages</p>
          </div>
          
          <div className="space-y-3">
            {announcements.map((announcement) => (
              <div key={announcement.id} className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-3 p-3 sm:p-4 bg-neutral-50 dark:bg-neutral-800 rounded-lg">
                <div className="flex-1 min-w-0">
                  <h4 className="font-medium text-sm sm:text-base text-neutral-900 dark:text-neutral-100">{announcement.title}</h4>
                  <p className="text-xs sm:text-sm text-neutral-600 dark:text-neutral-400 mt-1">{announcement.message}</p>
                  <p className="text-xs text-neutral-500 dark:text-neutral-400 mt-2">
                    To: {announcement.recipients} • {announcement.date}
                  </p>
                </div>
                <div className="flex gap-2 w-full sm:w-auto">
                  <button className="btn-ghost text-xs px-2 py-1 flex-1 sm:flex-none">Edit</button>
                  <button className="btn-ghost text-xs px-2 py-1 text-red-600 flex-1 sm:flex-none">Delete</button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </DashboardLayout>
  )
}