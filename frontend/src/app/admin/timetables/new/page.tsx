'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/context/AuthContext'

export default function CreateTimetablePage() {
  const router = useRouter()
  const { user } = useAuth()
  const API_BASE = process.env.NEXT_PUBLIC_DJANGO_API_URL || 'http://localhost:8000/api'

  const [formData, setFormData] = useState({
    academic_year: '2024-2025',
    semester: 'odd',
    working_days: 6,
    slots_per_day: 9,
    start_time: '08:00',
    end_time: '17:00',
    lunch_break_enabled: true,
    lunch_break_start: '12:00',
    lunch_break_end: '13:00',
    max_classes_per_day: 6,
    faculty_max_continuous: 3,
    optimization_priority: 'balanced',
    minimize_travel: true,
    number_of_variants: 5,
    timeout_seconds: 30,
  })

  const [isGenerating, setIsGenerating] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadLastConfig()
  }, [])

  const loadLastConfig = async () => {
    try {
      const response = await fetch(`${API_BASE}/timetable-configs/last_used/`, {
        credentials: 'include',
      })
      if (response.ok) {
        const config = await response.json()
        setFormData(prev => ({
          ...prev,
          working_days: config.working_days || prev.working_days,
          slots_per_day: config.slots_per_day || prev.slots_per_day,
          start_time: config.start_time || prev.start_time,
          end_time: config.end_time || prev.end_time,
          lunch_break_enabled: config.lunch_break_enabled ?? prev.lunch_break_enabled,
          lunch_break_start: config.lunch_break_start || prev.lunch_break_start,
          lunch_break_end: config.lunch_break_end || prev.lunch_break_end,
          max_classes_per_day: config.max_classes_per_day || prev.max_classes_per_day,
          faculty_max_continuous: config.faculty_max_continuous || prev.faculty_max_continuous,
          optimization_priority: config.optimization_priority || prev.optimization_priority,
          minimize_travel: config.minimize_travel ?? prev.minimize_travel,
          number_of_variants: config.number_of_variants || prev.number_of_variants,
          timeout_seconds: config.timeout_seconds || prev.timeout_seconds,
        }))
      }
    } catch (err) {
      console.error('Failed to load config:', err)
    } finally {
      setIsLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!user?.organization) {
      setError('User organization not found')
      return
    }

    try {
      setIsGenerating(true)
      setError(null)

      // Save configuration - transform to Django format
      const configPayload = {
        config_name: `${formData.academic_year} - ${formData.semester}`,
        academic_year: formData.academic_year,
        semester: formData.semester === 'odd' ? 1 : 2,
        working_days: formData.working_days,
        slots_per_day: formData.slots_per_day,
        start_time: formData.start_time,
        end_time: formData.end_time,
        slot_duration_minutes: 60,
        lunch_break_enabled: formData.lunch_break_enabled,
        lunch_break_start: formData.lunch_break_start,
        lunch_break_end: formData.lunch_break_end,
        max_classes_per_day: formData.max_classes_per_day,
        faculty_max_continuous: formData.faculty_max_continuous,
        optimization_priority: formData.optimization_priority,
        minimize_faculty_travel: formData.minimize_travel,
        number_of_variants: formData.number_of_variants,
        timeout_minutes: Math.ceil(formData.timeout_seconds / 60),
      }
      
      await fetch(`${API_BASE}/timetable-configs/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(configPayload),
      })

      // Start generation
      const response = await fetch(`${API_BASE}/generation-jobs/generate/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          academic_year: formData.academic_year,
          semester: formData.semester,
          org_id: user.organization,
          config: formData,
        }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Failed to start generation')
      }

      if (data.success) {
        router.push(`/admin/timetables/status/${data.job_id}`)
      } else {
        throw new Error(data.error || 'Generation failed')
      }
    } catch (err) {
      console.error('Failed to generate timetable:', err)
      setError(err instanceof Error ? err.message : 'Failed to generate timetable')
    } finally {
      setIsGenerating(false)
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="loading-spinner w-8 h-8 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading configuration...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">Generate University Timetable</h3>
          <p className="card-description">
            Configure and generate timetable for all 127 departments
          </p>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="card bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800">
          <div className="p-4">
            <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
          </div>
        </div>
      )}

      {/* Generation Form */}
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Basic Settings */}
        <div className="card">
          <div className="card-header">
            <h4 className="font-semibold text-gray-900 dark:text-white">Basic Settings</h4>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="form-group">
              <label htmlFor="academic-year" className="form-label">
                Academic Year <span className="text-red-500">*</span>
              </label>
              <select
                id="academic-year"
                className="input-primary"
                value={formData.academic_year}
                onChange={e => setFormData({ ...formData, academic_year: e.target.value })}
                disabled={isGenerating}
                required
              >
                <option value="2024-2025">2024-2025</option>
                <option value="2025-2026">2025-2026</option>
                <option value="2026-2027">2026-2027</option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="semester" className="form-label">
                Semester <span className="text-red-500">*</span>
              </label>
              <select
                id="semester"
                className="input-primary"
                value={formData.semester}
                onChange={e => setFormData({ ...formData, semester: e.target.value })}
                disabled={isGenerating}
                required
              >
                <option value="odd">Odd Semester</option>
                <option value="even">Even Semester</option>
              </select>
            </div>
          </div>
        </div>

        {/* Time Configuration */}
        <div className="card">
          <div className="card-header">
            <h4 className="font-semibold text-gray-900 dark:text-white">Time Configuration</h4>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="form-group">
              <label htmlFor="working-days" className="form-label">Working Days</label>
              <input
                type="number"
                id="working-days"
                className="input-primary"
                value={formData.working_days}
                onChange={e => setFormData({ ...formData, working_days: parseInt(e.target.value) })}
                min="5"
                max="7"
                disabled={isGenerating}
              />
            </div>

            <div className="form-group">
              <label htmlFor="slots-per-day" className="form-label">Slots Per Day</label>
              <input
                type="number"
                id="slots-per-day"
                className="input-primary"
                value={formData.slots_per_day}
                onChange={e => setFormData({ ...formData, slots_per_day: parseInt(e.target.value) })}
                min="6"
                max="12"
                disabled={isGenerating}
              />
            </div>

            <div className="form-group">
              <label htmlFor="start-time" className="form-label">Start Time</label>
              <input
                type="time"
                id="start-time"
                className="input-primary"
                value={formData.start_time}
                onChange={e => setFormData({ ...formData, start_time: e.target.value })}
                disabled={isGenerating}
              />
            </div>

            <div className="form-group">
              <label htmlFor="end-time" className="form-label">End Time</label>
              <input
                type="time"
                id="end-time"
                className="input-primary"
                value={formData.end_time}
                onChange={e => setFormData({ ...formData, end_time: e.target.value })}
                disabled={isGenerating}
              />
            </div>
          </div>

          <div className="mt-4 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
            <label className="flex items-center gap-3">
              <input
                type="checkbox"
                checked={formData.lunch_break_enabled}
                onChange={e => setFormData({ ...formData, lunch_break_enabled: e.target.checked })}
                disabled={isGenerating}
                className="w-4 h-4"
              />
              <span className="text-sm font-medium">Enable Lunch Break</span>
            </label>
            {formData.lunch_break_enabled && (
              <div className="grid grid-cols-2 gap-4 mt-3">
                <div className="form-group">
                  <label htmlFor="lunch-start" className="form-label text-xs">Break Start</label>
                  <input
                    type="time"
                    id="lunch-start"
                    className="input-primary"
                    value={formData.lunch_break_start}
                    onChange={e => setFormData({ ...formData, lunch_break_start: e.target.value })}
                    disabled={isGenerating}
                  />
                </div>
                <div className="form-group">
                  <label htmlFor="lunch-end" className="form-label text-xs">Break End</label>
                  <input
                    type="time"
                    id="lunch-end"
                    className="input-primary"
                    value={formData.lunch_break_end}
                    onChange={e => setFormData({ ...formData, lunch_break_end: e.target.value })}
                    disabled={isGenerating}
                  />
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Constraints */}
        <div className="card">
          <div className="card-header">
            <h4 className="font-semibold text-gray-900 dark:text-white">Constraints</h4>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="form-group">
              <label htmlFor="max-classes" className="form-label">Max Classes Per Day</label>
              <input
                type="number"
                id="max-classes"
                className="input-primary"
                value={formData.max_classes_per_day}
                onChange={e => setFormData({ ...formData, max_classes_per_day: parseInt(e.target.value) })}
                min="4"
                max="8"
                disabled={isGenerating}
              />
            </div>

            <div className="form-group">
              <label htmlFor="max-continuous" className="form-label">Faculty Max Continuous Classes</label>
              <input
                type="number"
                id="max-continuous"
                className="input-primary"
                value={formData.faculty_max_continuous}
                onChange={e => setFormData({ ...formData, faculty_max_continuous: parseInt(e.target.value) })}
                min="2"
                max="5"
                disabled={isGenerating}
              />
            </div>
          </div>
        </div>

        {/* Optimization */}
        <div className="card">
          <div className="card-header">
            <h4 className="font-semibold text-gray-900 dark:text-white">Optimization</h4>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="form-group">
              <label htmlFor="priority" className="form-label">Priority</label>
              <select
                id="priority"
                className="input-primary"
                value={formData.optimization_priority}
                onChange={e => setFormData({ ...formData, optimization_priority: e.target.value })}
                disabled={isGenerating}
              >
                <option value="balanced">Balanced</option>
                <option value="minimize_conflicts">Minimize Conflicts</option>
                <option value="maximize_utilization">Maximize Utilization</option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="variants" className="form-label">Number of Variants</label>
              <input
                type="number"
                id="variants"
                className="input-primary"
                value={formData.number_of_variants}
                onChange={e => setFormData({ ...formData, number_of_variants: parseInt(e.target.value) })}
                min="1"
                max="10"
                disabled={isGenerating}
              />
            </div>

            <div className="form-group">
              <label htmlFor="timeout" className="form-label">Timeout (seconds)</label>
              <input
                type="number"
                id="timeout"
                className="input-primary"
                value={formData.timeout_seconds}
                onChange={e => setFormData({ ...formData, timeout_seconds: parseInt(e.target.value) })}
                min="15"
                max="60"
                disabled={isGenerating}
              />
            </div>
          </div>

          <div className="mt-4">
            <label className="flex items-center gap-3">
              <input
                type="checkbox"
                checked={formData.minimize_travel}
                onChange={e => setFormData({ ...formData, minimize_travel: e.target.checked })}
                disabled={isGenerating}
                className="w-4 h-4"
              />
              <span className="text-sm font-medium">Minimize Faculty Travel Between Buildings</span>
            </label>
          </div>
        </div>

        {/* Submit Button */}
        <div className="flex justify-end gap-3">
          <button
            type="button"
            onClick={() => router.back()}
            disabled={isGenerating}
            className="px-6 py-2 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800"
          >
            Cancel
          </button>
          <button type="submit" disabled={isGenerating} className="btn-primary px-8 py-2">
            {isGenerating ? (
              <>
                <span className="inline-block animate-spin mr-2">⏳</span>
                Generating...
              </>
            ) : (
              'Generate Timetable'
            )}
          </button>
        </div>
      </form>
    </div>
  )
}
