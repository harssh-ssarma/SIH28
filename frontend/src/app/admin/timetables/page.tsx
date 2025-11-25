'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '@/context/AuthContext'
import {
  fetchTimetableWorkflows,
  transformWorkflowsToListItems,
  fetchFacultyAvailability,
  updateFacultyAvailability,
} from '@/lib/api/timetable'
import type { TimetableListItem, FacultyAvailability } from '@/types/timetable'

export default function AdminTimetablesPage() {
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')
  const [timetables, setTimetables] = useState<TimetableListItem[]>([])
  const [facultyAvailability, setFacultyAvailability] = useState<FacultyAvailability[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const { user } = useAuth()

  useEffect(() => {
    loadTimetableData()
    loadFacultyData()
  }, [])

  const loadTimetableData = async () => {
    try {
      setLoading(true)
      setError(null)

      // Fetch generation jobs (no filters to avoid backend errors)
      const workflows = await fetchTimetableWorkflows({})

      const listItems = transformWorkflowsToListItems(workflows)
      setTimetables(listItems)
    } catch (err) {
      console.error('Failed to load timetables:', err)
      // Don't show error - just show empty state
      // This is more user-friendly for new installations
      setTimetables([])
    } finally {
      setLoading(false)
    }
  }

  const loadFacultyData = async () => {
    try {
      // Get department_id and organization_id from authenticated user
      const faculty = await fetchFacultyAvailability({
        department_id: user?.department,
        organization_id: user?.organization,
      })
      setFacultyAvailability(faculty)
    } catch (err) {
      console.error('Failed to load faculty:', err)
      // Don't set error state for faculty - it's not critical
      setFacultyAvailability([])
    }
  }

  const toggleFacultyAvailability = async (facultyId: string) => {
    // Optimistically update UI
    setFacultyAvailability(prev =>
      prev.map(faculty =>
        faculty.id === facultyId ? { ...faculty, available: !faculty.available } : faculty
      )
    )

    // Update backend
    try {
      const faculty = facultyAvailability.find(f => f.id === facultyId)
      if (faculty) {
        await updateFacultyAvailability(facultyId, !faculty.available)
      }
    } catch (err) {
      console.error('Failed to update faculty availability:', err)
      // Revert optimistic update on error
      setFacultyAvailability(prev =>
        prev.map(faculty =>
          faculty.id === facultyId ? { ...faculty, available: !faculty.available } : faculty
        )
      )
      alert('Failed to update faculty availability. Please try again.')
    }
  }

  const getGroupedBySemester = () => {
    const grouped: { [key: string]: TimetableListItem[] } = {}

    timetables.forEach(timetable => {
      const key = `${timetable.academic_year}-${timetable.semester}`
      if (!grouped[key]) {
        grouped[key] = []
      }
      grouped[key].push(timetable)
    })

    return grouped
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'approved':
        return 'text-[#4CAF50] bg-[#4CAF50]/10 dark:bg-[#4CAF50]/20'
      case 'pending':
        return 'text-[#FF9800] bg-[#FF9800]/10 dark:bg-[#FF9800]/20'
      case 'draft':
        return 'text-[#6B6B6B] dark:text-[#B3B3B3] bg-[#E0E0E0] dark:bg-[#404040]'
      case 'rejected':
        return 'text-[#F44336] bg-[#F44336]/10 dark:bg-[#F44336]/20'
      default:
        return 'text-[#6B6B6B] dark:text-[#B3B3B3] bg-[#E0E0E0] dark:bg-[#404040]'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'approved':
        return '✅'
      case 'pending':
        return '⏳'
      case 'draft':
        return '📝'
      case 'rejected':
        return '❌'
      default:
        return '📄'
    }
  }

  const groupedTimetables = getGroupedBySemester()

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="loading-spinner w-8 h-8 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading timetables...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="space-y-6">
        <div className="card border-[#F44336] bg-[#F44336]/5">
          <div className="card-header">
            <div className="flex items-center gap-3">
              <svg
                className="w-6 h-6 text-[#F44336]"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              <h3 className="text-lg font-semibold text-[#F44336]">Error Loading Timetables</h3>
            </div>
          </div>
          <p className="text-sm text-[#2C2C2C] dark:text-[#FFFFFF]">{error}</p>
          <button onClick={loadTimetableData} className="btn-primary mt-4">
            Retry
          </button>
        </div>
      </div>
    )
  }

  return (
      <div className="space-y-6">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-end">
          <div className="flex flex-col sm:flex-row gap-3 ml-auto">
            <a
              href="/admin/timetables/new"
              className="btn-primary flex items-center justify-center gap-2"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a9 9 0 117.072 0l-.548.547A3.374 3.374 0 0014.846 21H9.154a3.374 3.374 0 00-2.879-1.453l-.548-.547z"
                />
              </svg>
              <span className="hidden sm:inline">Generate New Timetable</span>
              <span className="sm:hidden">Generate</span>
            </a>
          </div>
        </div>

        {/* Two Column Layout: Timetables (Left) + Faculty (Right) */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column: Timetables (2/3 width) */}
          <div className="lg:col-span-2 space-y-6">

            {/* View Mode Toggle */}
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Department Timetables</h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">Course-centric schedules for all semesters</p>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => setViewMode('grid')}
                  className={`px-4 py-2 text-sm rounded-lg transition-colors ${
                    viewMode === 'grid'
                      ? 'bg-[#2196F3] text-white'
                      : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700'
                  }`}
                >
                  Grid View
                </button>
                <button
                  onClick={() => setViewMode('list')}
                  className={`px-4 py-2 text-sm rounded-lg transition-colors ${
                    viewMode === 'list'
                      ? 'bg-[#2196F3] text-white'
                      : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700'
                  }`}
                >
                  List View
                </button>
              </div>
            </div>

            {/* Timetables by Semester */}
            <div className="space-y-4">
          {Object.keys(groupedTimetables).length === 0 ? (
            <div className="card">
              <div className="text-center py-8 sm:py-12">
                <div className="text-4xl sm:text-6xl mb-4">📅</div>
                <h3 className="text-base sm:text-lg font-medium text-[#0f0f0f] dark:text-white mb-2">
                  No Timetables Found
                </h3>
                <p className="text-sm text-[#606060] dark:text-[#aaaaaa] mb-4 sm:mb-6 px-4">
                  No timetables have been created yet.
                </p>
                <a href="/admin/timetables/new" className="btn-primary">
                  Create First Timetable
                </a>
              </div>
            </div>
          ) : (
            Object.entries(groupedTimetables)
              .sort(([a], [b]) => b.localeCompare(a))
              .map(([semesterKey, semesterTimetables]) => {
                const [academicYear, semester] = semesterKey.split('-')
                return (
                  <div key={semesterKey} className="card">
                    <div className="card-header">
                      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
                        <div>
                          <h3 className="card-title">
                            {academicYear} - Semester {semester}
                          </h3>
                          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                            {semesterTimetables.length} course{semesterTimetables.length !== 1 ? 's' : ''} scheduled
                          </p>
                        </div>
                        <span className="badge badge-info">
                          {semesterTimetables.filter(t => t.status === 'approved').length} approved
                        </span>
                      </div>
                    </div>

                    <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3 sm:gap-4">
                      {semesterTimetables
                        .sort((a, b) => a.department.localeCompare(b.department))
                        .map(timetable => (
                          <a
                            key={timetable.id}
                            href={`/admin/timetables/${timetable.id}/review`}
                            className="block p-3 sm:p-4 bg-white dark:bg-[#1E1E1E] border border-[#E0E0E0] dark:border-[#2A2A2A] rounded-lg hover:border-[#2196F3] dark:hover:border-[#2196F3] transition-colors"
                          >
                            <div className="flex items-start justify-between mb-3">
                              <div className="flex-1 min-w-0">
                                <h4 className="font-medium text-[#2C2C2C] dark:text-[#FFFFFF] truncate">
                                  {timetable.department}
                                </h4>
                                <p className="text-sm text-[#6B6B6B] dark:text-[#B3B3B3]">
                                  {timetable.batch || 'All Students'}
                                </p>
                              </div>
                              <span
                                className={`px-2 py-1 text-xs font-medium flex-shrink-0 ml-2 rounded ${getStatusColor(
                                  timetable.status
                                )}`}
                              >
                                {getStatusIcon(timetable.status)} {timetable.status.charAt(0).toUpperCase() + timetable.status.slice(1)}
                              </span>
                            </div>

                            <div className="space-y-2">
                              <div className="flex items-center justify-between text-sm">
                                <span className="text-[#606060] dark:text-[#aaaaaa]">
                                  Last Updated:
                                </span>
                                <span className="text-[#0f0f0f] dark:text-white">
                                  {timetable.lastUpdated}
                                </span>
                              </div>

                              {timetable.score && (
                                <div className="flex items-center justify-between text-sm">
                                  <span className="text-[#606060] dark:text-[#aaaaaa]">Score:</span>
                                  <span className="font-medium text-[#00ba7c]">
                                    {timetable.score}/10
                                  </span>
                                </div>
                              )}

                              <div className="flex items-center justify-between text-sm">
                                <span className="text-[#606060] dark:text-[#aaaaaa]">Conflicts:</span>
                                <span
                                  className={`font-medium ${
                                    timetable.conflicts > 0 ? 'text-[#ff4444]' : 'text-[#00ba7c]'
                                  }`}
                                >
                                  {timetable.conflicts}
                                </span>
                              </div>
                            </div>

                            <div className="mt-3 pt-3 border-t border-[#e5e5e5] dark:border-[#3d3d3d]">
                              <span className="text-xs text-[#065fd4] font-medium group-hover:text-[#0856c1] transition-colors duration-200">
                                👁️ View Details →
                              </span>
                            </div>
                          </a>
                        ))}
                    </div>
                  </div>
                )
              })
            </div>
          </div>

          {/* Right Column: Faculty Availability (1/3 width) */}
          <div className="lg:col-span-1">
            <div className="card sticky top-6">
              <div className="card-header">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-[#2196F3]/10 dark:bg-[#2196F3]/20 flex items-center justify-center rounded-lg">
                    <svg
                      className="w-5 h-5 text-[#2196F3]"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth="2"
                        d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z"
                      />
                    </svg>
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900 dark:text-white">Faculty</h3>
                    <p className="text-xs text-[#6B6B6B] dark:text-[#B3B3B3]">
                      {facultyAvailability.filter(f => f.available).length} available
                    </p>
                  </div>
                </div>
              </div>

              <div className="max-h-[calc(100vh-200px)] overflow-y-auto space-y-2">
                {facultyAvailability.filter(f => f.name).map(faculty => (
                  <div key={faculty.id} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors">
                    <div className="flex items-center gap-3 flex-1 min-w-0">
                      <div className="w-8 h-8 bg-[#2196F3]/10 dark:bg-[#2196F3]/20 rounded-full flex items-center justify-center flex-shrink-0">
                        <span className="text-xs font-medium text-[#2196F3]">
                          {faculty.name
                            .split(' ')
                            .map(n => n[0])
                            .join('')
                            .slice(0, 2)}
                        </span>
                      </div>
                      <span className="text-sm font-medium text-[#2C2C2C] dark:text-[#FFFFFF] truncate">
                        {faculty.name}
                      </span>
                    </div>
                    <button
                      type="button"
                      onClick={() => toggleFacultyAvailability(faculty.id)}
                      aria-label={`Toggle availability for ${faculty.name}`}
                      className={`relative inline-flex h-5 w-9 flex-shrink-0 items-center rounded-full transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-[#2196F3] focus:ring-offset-2 ${
                        faculty.available ? 'bg-[#2196F3]' : 'bg-[#E0E0E0] dark:bg-[#404040]'
                      }`}
                    >
                      <span
                        className={`inline-block h-3 w-3 transform rounded-full bg-white transition-transform duration-300 shadow-md ${
                          faculty.available ? 'translate-x-5' : 'translate-x-1'
                        }`}
                      />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-4 sm:gap-4">
          <div className="card text-center p-3 sm:p-4">
            <div className="text-xl sm:text-2xl lg:text-3xl font-bold text-[#00ba7c]">
              {timetables.filter(t => t.status === 'approved').length}
            </div>
            <div className="text-xs sm:text-sm text-[#606060] dark:text-[#aaaaaa] mt-1">
              Approved
            </div>
          </div>
          <div className="card text-center p-3 sm:p-4">
            <div className="text-xl sm:text-2xl lg:text-3xl font-bold text-[#f9ab00]">
              {timetables.filter(t => t.status === 'pending').length}
            </div>
            <div className="text-xs sm:text-sm text-[#606060] dark:text-[#aaaaaa] mt-1">
              Pending
            </div>
          </div>
          <div className="card text-center p-3 sm:p-4">
            <div className="text-xl sm:text-2xl lg:text-3xl font-bold text-[#606060] dark:text-[#aaaaaa]">
              {timetables.filter(t => t.status === 'draft').length}
            </div>
            <div className="text-xs sm:text-sm text-[#606060] dark:text-[#aaaaaa] mt-1">Draft</div>
          </div>
          <div className="card text-center p-3 sm:p-4">
            <div className="text-xl sm:text-2xl lg:text-3xl font-bold text-[#ff4444]">
              {timetables.filter(t => t.status === 'rejected').length}
            </div>
            <div className="text-xs sm:text-sm text-[#606060] dark:text-[#aaaaaa] mt-1">
              Rejected
            </div>
          </div>
        </div>
      </div>
  )
}
