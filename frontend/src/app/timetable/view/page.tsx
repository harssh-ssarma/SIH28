'use client'

import { useState, useEffect } from 'react'
import TimetableGrid from '@/components/shared/TimetableGrid'

interface TimeSlot {
  day: string
  time: string
  subject: string
  faculty: string
  classroom: string
  batch: string
}

export default function PublicTimetableView() {
  const [department, setDepartment] = useState('')
  const [year, setYear] = useState('')
  const [batch, setBatch] = useState('')
  const [schedule, setSchedule] = useState<TimeSlot[]>([])
  const [loading, setLoading] = useState(false)

  const loadTimetable = async () => {
    if (!department || !year || !batch) return

    setLoading(true)
    try {
      // Mock data - replace with actual API call
      const mockSchedule: TimeSlot[] = [
        { day: 'Monday', time: '9:00-10:00', subject: 'Data Structures', faculty: 'Dr. Smith', classroom: 'Room 101', batch: `${department}-${batch}` },
        { day: 'Monday', time: '10:00-11:00', subject: 'Mathematics', faculty: 'Dr. Johnson', classroom: 'Room 102', batch: `${department}-${batch}` },
        { day: 'Tuesday', time: '9:00-10:00', subject: 'Programming', faculty: 'Dr. Brown', classroom: 'Lab 1', batch: `${department}-${batch}` },
      ]
      setSchedule(mockSchedule)
    } catch (error) {
      console.error('Failed to load timetable:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadTimetable()
  }, [department, year, batch])

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-4 sm:py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="space-y-4 sm:space-y-6">
          {/* Header */}
          <div className="text-center">
            <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold text-gray-900 dark:text-white">
              📅 Timetable Viewer
            </h1>
            <p className="mt-2 text-sm sm:text-base text-gray-600 dark:text-gray-400">
              View approved timetables for all departments and batches
            </p>
          </div>

          {/* Filters */}
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-4 sm:p-6">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div className="form-group">
                <label className="form-label">Department</label>
                <select 
                  className="input-primary"
                  value={department}
                  onChange={(e) => setDepartment(e.target.value)}
                >
                  <option value="">Select Department</option>
                  <option value="CSE">Computer Science</option>
                  <option value="ECE">Electronics</option>
                  <option value="ME">Mechanical</option>
                  <option value="CE">Civil</option>
                </select>
              </div>
              
              <div className="form-group">
                <label className="form-label">Year</label>
                <select 
                  className="input-primary"
                  value={year}
                  onChange={(e) => setYear(e.target.value)}
                >
                  <option value="">Select Year</option>
                  <option value="1">1st Year</option>
                  <option value="2">2nd Year</option>
                  <option value="3">3rd Year</option>
                  <option value="4">4th Year</option>
                </select>
              </div>
              
              <div className="form-group">
                <label className="form-label">Batch/Section</label>
                <select 
                  className="input-primary"
                  value={batch}
                  onChange={(e) => setBatch(e.target.value)}
                >
                  <option value="">Select Batch</option>
                  <option value="A">Section A</option>
                  <option value="B">Section B</option>
                  <option value="C">Section C</option>
                </select>
              </div>
            </div>
          </div>

          {/* Timetable Display */}
          {loading ? (
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-8 sm:p-12">
              <div className="text-center">
                <div className="loading-spinner w-8 h-8 mx-auto mb-4"></div>
                <p className="text-gray-600 dark:text-gray-400">Loading timetable...</p>
              </div>
            </div>
          ) : schedule.length > 0 ? (
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-4 sm:p-6">
              <div className="mb-4">
                <h2 className="text-lg sm:text-xl font-semibold text-gray-900 dark:text-white">
                  {department} - {year === '1' ? '1st' : year === '2' ? '2nd' : year === '3' ? '3rd' : '4th'} Year - Section {batch}
                </h2>
                <p className="text-sm text-gray-600 dark:text-gray-400">Current Semester Timetable</p>
              </div>
              <div className="overflow-x-auto">
                <TimetableGrid schedule={schedule} />
              </div>
            </div>
          ) : department && year && batch ? (
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-8 sm:p-12">
              <div className="text-center">
                <div className="text-4xl sm:text-6xl mb-4">📋</div>
                <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                  No Timetable Available
                </h3>
                <p className="text-gray-600 dark:text-gray-400">
                  No approved timetable found for {department} - {year === '1' ? '1st' : year === '2' ? '2nd' : year === '3' ? '3rd' : '4th'} Year - Section {batch}
                </p>
              </div>
            </div>
          ) : (
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-8 sm:p-12">
              <div className="text-center">
                <div className="text-4xl sm:text-6xl mb-4">🎯</div>
                <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                  Select Filters
                </h3>
                <p className="text-gray-600 dark:text-gray-400">
                  Please select department, year, and batch to view the timetable
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}