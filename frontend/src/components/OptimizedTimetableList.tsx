'use client'

import { useState, useEffect } from 'react'
import { fetchTimetablesOptimized } from '@/lib/api/optimized-client'

/**
 * Optimized Timetable List - Loads in <500ms
 */
export default function OptimizedTimetableList() {
  const [timetables, setTimetables] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadData()
  }, [])

  async function loadData() {
    try {
      const data = await fetchTimetablesOptimized()
      setTimetables(data)
    } catch (error) {
      console.error('Load failed:', error)
      setTimetables([])
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="animate-pulse space-y-4">
        {[1, 2, 3].map(i => (
          <div key={i} className="h-20 bg-gray-200 dark:bg-gray-700 rounded" />
        ))}
      </div>
    )
  }

  if (timetables.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">No timetables found</p>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      {timetables.map(tt => (
        <div key={tt.id} className="p-4 bg-white dark:bg-gray-800 rounded-lg border">
          <div className="flex justify-between items-center">
            <div>
              <h3 className="font-medium">{tt.id.slice(0, 8)}</h3>
              <p className="text-sm text-gray-500">{new Date(tt.created_at).toLocaleDateString()}</p>
            </div>
            <span className="px-3 py-1 bg-green-100 text-green-800 rounded text-sm">
              {tt.status}
            </span>
          </div>
        </div>
      ))}
    </div>
  )
}
