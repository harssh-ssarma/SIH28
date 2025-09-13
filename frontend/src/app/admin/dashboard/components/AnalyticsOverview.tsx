export default function AnalyticsOverview() {
  return (
    <div className="card">
      <div className="card-header">
        <h3 className="card-title text-sm sm:text-base">Utilization Reports</h3>
        <p className="card-description text-xs sm:text-sm">Resource usage analytics</p>
      </div>
      <div className="space-y-3">
        <div className="flex items-center justify-between text-xs sm:text-sm">
          <span className="text-neutral-600 dark:text-neutral-400">Classroom Usage</span>
          <span className="font-medium text-green-600">87%</span>
        </div>
        <div className="w-full bg-neutral-200 dark:bg-neutral-700 rounded-full h-2">
          <div className="bg-green-600 h-2 rounded-full" style={{width: '87%'}}></div>
        </div>
        <div className="flex items-center justify-between text-xs sm:text-sm">
          <span className="text-neutral-600 dark:text-neutral-400">Faculty Load</span>
          <span className="font-medium text-yellow-600">73%</span>
        </div>
        <div className="w-full bg-neutral-200 dark:bg-neutral-700 rounded-full h-2">
          <div className="bg-yellow-600 h-2 rounded-full" style={{width: '73%'}}></div>
        </div>
      </div>
    </div>
  )
}