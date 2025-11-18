'use client'

import { useState } from 'react'
import { useAuth } from '@/context/AuthContext'

interface EnrollmentStats {
  students_enrolled: number
  subjects_count: number
  total_enrollments_created: number
  core_enrollments: number
  elective_enrollments: number
  cross_dept_enrollments: number
  already_existed: number
}

export default function BulkEnrollmentTool() {
  const { user } = useAuth()
  const API_BASE = process.env.NEXT_PUBLIC_DJANGO_API_URL || 'http://localhost:8000/api'

  const [formData, setFormData] = useState({
    academic_year: '2024-25',
    semester: 1,
    enrollment_type: 'core_and_electives',
    max_electives_per_student: 2,
  })

  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<{
    success: boolean
    message: string
    stats?: EnrollmentStats
  } | null>(null)
  const [summary, setSummary] = useState<any>(null)

  const handleAutoEnroll = async () => {
    if (!user?.organization) {
      alert('User organization not found')
      return
    }

    if (
      !confirm(
        `This will create enrollments for ALL students in Semester ${formData.semester}. Continue?`
      )
    ) {
      return
    }

    try {
      setLoading(true)
      setResult(null)

      const response = await fetch(`${API_BASE}/enrollments/bulk/auto-enroll/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(formData),
      })

      const data = await response.json()

      if (response.ok) {
        setResult({ success: true, message: data.message, stats: data.stats })
        // Refresh summary
        loadSummary()
      } else {
        setResult({ success: false, message: data.error || 'Failed to create enrollments' })
      }
    } catch (err) {
      console.error('Enrollment failed:', err)
      setResult({ success: false, message: 'Network error' })
    } finally {
      setLoading(false)
    }
  }

  const loadSummary = async () => {
    try {
      const response = await fetch(
        `${API_BASE}/enrollments/bulk/enrollment-summary/?academic_year=${formData.academic_year}&semester=${formData.semester}`,
        { credentials: 'include' }
      )
      if (response.ok) {
        const data = await response.json()
        setSummary(data.summary)
      }
    } catch (err) {
      console.error('Failed to load summary:', err)
    }
  }

  const handleClearEnrollments = async () => {
    if (
      !confirm(
        `⚠️ WARNING: This will DELETE all enrollments for Semester ${formData.semester}. This cannot be undone! Continue?`
      )
    ) {
      return
    }

    if (!confirm('Are you ABSOLUTELY SURE? Type YES in the next prompt.')) {
      return
    }

    try {
      setLoading(true)
      const response = await fetch(
        `${API_BASE}/enrollments/bulk/clear-enrollments/?academic_year=${formData.academic_year}&semester=${formData.semester}&confirm=true`,
        {
          method: 'DELETE',
          credentials: 'include',
        }
      )

      const data = await response.json()

      if (response.ok) {
        alert(`✅ Deleted ${data.deleted_count} enrollments`)
        setSummary(null)
        setResult(null)
      } else {
        alert(`❌ Failed: ${data.error}`)
      }
    } catch (err) {
      alert('❌ Network error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="card">
        <div className="p-4 sm:p-6">
          <h2 className="text-xl font-bold text-gray-800 dark:text-gray-200 mb-2">
            Bulk Student Enrollment
          </h2>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Automatically enroll students in subjects based on their semester and department
          </p>
        </div>
      </div>

      {/* Configuration */}
      <div className="card">
        <div className="p-4 sm:p-6 space-y-4">
          <h3 className="text-base font-semibold text-gray-800 dark:text-gray-200">
            Enrollment Configuration
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Semester */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Semester
              </label>
              <select
                value={formData.semester}
                onChange={e => setFormData({ ...formData, semester: parseInt(e.target.value) })}
                className="input-field"
                disabled={loading}
              >
                {[1, 2, 3, 4, 5, 6, 7, 8].map(sem => (
                  <option key={sem} value={sem}>
                    Semester {sem}
                  </option>
                ))}
              </select>
            </div>

            {/* Academic Year */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Academic Year
              </label>
              <input
                type="text"
                value={formData.academic_year}
                onChange={e => setFormData({ ...formData, academic_year: e.target.value })}
                className="input-field"
                disabled={loading}
              />
            </div>

            {/* Enrollment Type */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Enrollment Type
              </label>
              <select
                value={formData.enrollment_type}
                onChange={e => setFormData({ ...formData, enrollment_type: e.target.value })}
                className="input-field"
                disabled={loading}
              >
                <option value="core_only">Core Subjects Only</option>
                <option value="core_and_electives">Core + Electives (Recommended)</option>
                <option value="all">All Subjects</option>
              </select>
            </div>

            {/* Max Electives */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Max Electives Per Student
              </label>
              <input
                type="number"
                value={formData.max_electives_per_student}
                onChange={e =>
                  setFormData({ ...formData, max_electives_per_student: parseInt(e.target.value) })
                }
                min={0}
                max={5}
                className="input-field"
                disabled={loading}
              />
            </div>
          </div>

          {/* Actions */}
          <div className="flex gap-3 pt-4">
            <button onClick={handleAutoEnroll} disabled={loading} className="btn-primary">
              {loading ? 'Processing...' : '🚀 Auto Enroll Students'}
            </button>

            <button onClick={loadSummary} disabled={loading} className="btn-secondary">
              📊 Load Summary
            </button>

            <button
              onClick={handleClearEnrollments}
              disabled={loading}
              className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50"
            >
              🗑️ Clear Enrollments
            </button>
          </div>
        </div>
      </div>

      {/* Result */}
      {result && (
        <div className={`card ${result.success ? 'border-green-500' : 'border-red-500'} border-2`}>
          <div className="p-4 sm:p-6">
            <h3
              className={`text-base font-semibold mb-3 ${
                result.success ? 'text-green-700' : 'text-red-700'
              }`}
            >
              {result.success ? '✅ Success' : '❌ Error'}
            </h3>
            <p className="text-sm text-gray-700 dark:text-gray-300 mb-4">{result.message}</p>

            {result.stats && (
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                <div className="bg-blue-50 dark:bg-blue-900/20 p-3 rounded">
                  <div className="text-2xl font-bold text-blue-600">
                    {result.stats.students_enrolled}
                  </div>
                  <div className="text-xs text-gray-600 dark:text-gray-400">Students Enrolled</div>
                </div>
                <div className="bg-green-50 dark:bg-green-900/20 p-3 rounded">
                  <div className="text-2xl font-bold text-green-600">
                    {result.stats.total_enrollments_created}
                  </div>
                  <div className="text-xs text-gray-600 dark:text-gray-400">
                    Enrollments Created
                  </div>
                </div>
                <div className="bg-purple-50 dark:bg-purple-900/20 p-3 rounded">
                  <div className="text-2xl font-bold text-purple-600">
                    {result.stats.core_enrollments}
                  </div>
                  <div className="text-xs text-gray-600 dark:text-gray-400">Core Subjects</div>
                </div>
                <div className="bg-orange-50 dark:bg-orange-900/20 p-3 rounded">
                  <div className="text-2xl font-bold text-orange-600">
                    {result.stats.elective_enrollments}
                  </div>
                  <div className="text-xs text-gray-600 dark:text-gray-400">Electives</div>
                </div>
                <div className="bg-pink-50 dark:bg-pink-900/20 p-3 rounded">
                  <div className="text-2xl font-bold text-pink-600">
                    {result.stats.cross_dept_enrollments}
                  </div>
                  <div className="text-xs text-gray-600 dark:text-gray-400">Cross-Department</div>
                </div>
                <div className="bg-gray-50 dark:bg-gray-700 p-3 rounded">
                  <div className="text-2xl font-bold text-gray-600">
                    {result.stats.already_existed}
                  </div>
                  <div className="text-xs text-gray-600 dark:text-gray-400">Already Existed</div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Summary */}
      {summary && (
        <div className="card">
          <div className="p-4 sm:p-6">
            <h3 className="text-base font-semibold text-gray-800 dark:text-gray-200 mb-4">
              Current Enrollment Summary
            </h3>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              <div className="bg-gray-50 dark:bg-gray-700 p-3 rounded">
                <div className="text-2xl font-bold text-gray-800 dark:text-gray-200">
                  {summary.total_enrollments}
                </div>
                <div className="text-xs text-gray-600 dark:text-gray-400">Total Enrollments</div>
              </div>
              <div className="bg-gray-50 dark:bg-gray-700 p-3 rounded">
                <div className="text-2xl font-bold text-gray-800 dark:text-gray-200">
                  {summary.unique_students}
                </div>
                <div className="text-xs text-gray-600 dark:text-gray-400">Unique Students</div>
              </div>
              <div className="bg-gray-50 dark:bg-gray-700 p-3 rounded">
                <div className="text-2xl font-bold text-gray-800 dark:text-gray-200">
                  {summary.unique_subjects}
                </div>
                <div className="text-xs text-gray-600 dark:text-gray-400">Unique Subjects</div>
              </div>
              <div className="bg-gray-50 dark:bg-gray-700 p-3 rounded">
                <div className="text-2xl font-bold text-gray-800 dark:text-gray-200">
                  {summary.core_enrollments}
                </div>
                <div className="text-xs text-gray-600 dark:text-gray-400">Core Enrollments</div>
              </div>
              <div className="bg-gray-50 dark:bg-gray-700 p-3 rounded">
                <div className="text-2xl font-bold text-gray-800 dark:text-gray-200">
                  {summary.elective_enrollments}
                </div>
                <div className="text-xs text-gray-600 dark:text-gray-400">Elective Enrollments</div>
              </div>
              <div className="bg-gray-50 dark:bg-gray-700 p-3 rounded">
                <div className="text-2xl font-bold text-gray-800 dark:text-gray-200">
                  {summary.cross_department_enrollments}
                </div>
                <div className="text-xs text-gray-600 dark:text-gray-400">Cross-Department</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Info */}
      <div className="card bg-blue-50 dark:bg-blue-900/20 border border-blue-200">
        <div className="p-4 sm:p-6">
          <h4 className="text-sm font-semibold text-blue-900 dark:text-blue-200 mb-2">
            ℹ️ How It Works
          </h4>
          <ul className="text-xs text-blue-800 dark:text-blue-300 space-y-1">
            <li>
              • <strong>Core Only:</strong> Enrolls students only in their department's core
              subjects
            </li>
            <li>
              • <strong>Core + Electives:</strong> Enrolls in core subjects + randomly selects
              electives (can be from other departments)
            </li>
            <li>
              • <strong>All:</strong> Enrolls in all available subjects for the semester
            </li>
            <li>• Cross-department enrollments simulate NEP 2020 flexible credit system</li>
            <li>• Already existing enrollments are skipped (idempotent operation)</li>
          </ul>
        </div>
      </div>
    </div>
  )
}
