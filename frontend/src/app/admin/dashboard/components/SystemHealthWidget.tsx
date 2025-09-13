export default function SystemHealthWidget() {
  return (
    <div className="card p-4 sm:p-6 hover:shadow-md transition-shadow">
      <div className="flex items-center justify-between">
        <div className="flex-1 min-w-0">
          <p className="text-xs sm:text-sm font-medium text-neutral-600 dark:text-neutral-400">System Health</p>
          <p className="text-xl sm:text-2xl lg:text-3xl font-bold text-green-600 truncate">98%</p>
        </div>
        <div className="w-10 h-10 sm:w-12 sm:h-12 bg-green-100 dark:bg-green-800 rounded-xl flex items-center justify-center flex-shrink-0">
          <span className="text-lg sm:text-xl">❤️</span>
        </div>
      </div>
      <div className="mt-3 sm:mt-4 flex items-center text-xs sm:text-sm">
        <span className="text-green-600">All services online</span>
      </div>
    </div>
  )
}