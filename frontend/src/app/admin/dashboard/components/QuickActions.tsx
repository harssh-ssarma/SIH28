export default function QuickActions() {
  return (
    <div className="card">
      <div className="card-header">
        <h3 className="card-title">Quick Actions</h3>
        <p className="card-description">Common administrative tasks</p>
      </div>
      <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 gap-3 sm:gap-4">
        <button className="btn-primary justify-center flex-col h-16 sm:h-20">
          <span className="text-lg sm:text-xl mb-1">👤</span>
          <span className="text-xs sm:text-sm">Add User</span>
        </button>
        <button className="btn-secondary justify-center flex-col h-16 sm:h-20">
          <span className="text-lg sm:text-xl mb-1">📚</span>
          <span className="text-xs sm:text-sm">New Course</span>
        </button>
        <button className="btn-secondary justify-center flex-col h-16 sm:h-20">
          <span className="text-lg sm:text-xl mb-1">🏫</span>
          <span className="text-xs sm:text-sm">Add Room</span>
        </button>
        <button className="btn-secondary justify-center flex-col h-16 sm:h-20">
          <span className="text-lg sm:text-xl mb-1">📅</span>
          <span className="text-xs sm:text-sm">Generate</span>
        </button>
        <button className="btn-secondary justify-center flex-col h-16 sm:h-20">
          <span className="text-lg sm:text-xl mb-1">⚙️</span>
          <span className="text-xs sm:text-sm">Settings</span>
        </button>
        <button className="btn-secondary justify-center flex-col h-16 sm:h-20">
          <span className="text-lg sm:text-xl mb-1">📊</span>
          <span className="text-xs sm:text-sm">Reports</span>
        </button>
      </div>
    </div>
  )
}