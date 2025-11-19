'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/context/AuthContext'
import TimetableProgressTracker from './ProgressTracker'

// NEP 2020 / Harvard-style Timetable Generation
// NO batch selection - students enroll individually in subjects

interface SubjectEnrollmentSummary {
  subject_id: string
  subject_code: string
  subject_name: string
  subject_type: 'theory' | 'practical' | 'hybrid'
  total_enrolled: number
  core_enrolled: number
  elective_enrolled: number
  cross_dept_enrolled: number
  enrolled_students: string[] // student IDs
  primary_department: string
  cross_departments: string[]
}

interface FixedSlotInput {
  subject_id: string
  faculty_id: string
  day: number
  start_time: string
  end_time: string
}

interface Faculty {
  faculty_id: string
  faculty_name: string
  department_name?: string
}

export default function NEP2020TimetableForm() {
  const router = useRouter()
  const { user } = useAuth()

  const API_BASE = process.env.NEXT_PUBLIC_DJANGO_API_URL || 'http://localhost:8000/api'

  // Form State
  const [formData, setFormData] = useState({
    academic_year: '2024-25',
    semester: 1,
    num_variants: 5,
    include_cross_dept: true, // Include cross-department enrollments
  })

  // NEP 2020 Data
  const [enrollmentSummary, setEnrollmentSummary] = useState<SubjectEnrollmentSummary[]>([])
  const [faculty, setFaculty] = useState<Faculty[]>([])
  const [fixedSlots, setFixedSlots] = useState<FixedSlotInput[]>([])

  // UI State
  const [isGenerating, setIsGenerating] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [jobId, setJobId] = useState<string | null>(null)
  const [cacheKey, setCacheKey] = useState<string | null>(null)

  // Fetch enrollment summary when semester changes
  useEffect(() => {
    if (user?.organization && formData.semester) {
      loadEnrollmentData()
    }
  }, [formData.semester, formData.academic_year, user?.organization])

  const loadEnrollmentData = async () => {
    if (!user?.organization) return

    try {
      setIsLoading(true)
      setError(null)

      // Check Redis cache first
      const generatedCacheKey = `enrollment_${user.organization}_${formData.semester}_${formData.academic_year}`

      let cachedData = null
      try {
        const cacheRes = await fetch(
          `${API_BASE}/timetable/enrollment-cache/?cache_key=${generatedCacheKey}`,
          { credentials: 'include' }
        )
        if (cacheRes.ok) {
          const cacheResponse = await cacheRes.json()
          // Check if cache actually exists
          if (cacheResponse.exists && cacheResponse.data) {
            cachedData = cacheResponse.data
            console.log('✅ Cache HIT - Loading from Redis')
          } else {
            console.log('ℹ️ Cache MISS - Cache does not exist')
          }
        }
      } catch (err) {
        console.log('⚠️ Cache check failed:', err)
      }

      if (cachedData && cachedData.subjects && cachedData.subjects.length > 0) {
        // Load from cache
        setEnrollmentSummary(cachedData.subjects || [])
        setFaculty(cachedData.faculty || [])
        setCacheKey(generatedCacheKey)
        console.log(
          `✅ Loaded from cache: ${cachedData.subjects.length} subjects, ${
            cachedData.faculty?.length || 0
          } faculty`
        )
      } else {
        // Fetch from database
        console.log('📡 Fetching enrollment data...')

        const [enrollmentRes, facultyRes] = await Promise.all([
          fetch(
            `${API_BASE}/timetable/enrollments/?semester=${formData.semester}&academic_year=${formData.academic_year}&include_cross_dept=true`,
            { credentials: 'include' }
          ),
          fetch(`${API_BASE}/enrollment-faculty/?semester=${formData.semester}`, {
            credentials: 'include',
          }),
        ])

        let enrollData, facultyData

        if (enrollmentRes.ok) {
          enrollData = await enrollmentRes.json()
          // Backend returns {summary: [...], enrollments: [...], cross_department_summary: [...]}
          const subjects = enrollData.summary || enrollData.results || enrollData
          setEnrollmentSummary(Array.isArray(subjects) ? subjects : [])
          console.log(`✅ Loaded ${subjects?.length || 0} subjects with enrollments`)
        } else {
          console.error('❌ Failed to fetch enrollments:', enrollmentRes.status)
          setEnrollmentSummary([])
        }

        if (facultyRes.ok) {
          facultyData = await facultyRes.json()
          const faculties = facultyData.results || facultyData
          setFaculty(Array.isArray(faculties) ? faculties : [])
          console.log(`✅ Loaded ${faculties?.length || 0} faculty members`)
        } else {
          console.error('❌ Failed to fetch faculty:', facultyRes.status)
          setFaculty([])
        }

        // Store in Redis cache for future use
        if (enrollmentRes.ok && facultyRes.ok && enrollData && facultyData) {
          try {
            await fetch(`${API_BASE}/timetable/enrollment-cache/`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              credentials: 'include',
              body: JSON.stringify({
                cache_key: generatedCacheKey,
                organization_id: user.organization,
                semester: formData.semester,
                academic_year: formData.academic_year,
                subjects: enrollData.results || enrollData,
                faculty: facultyData.results || facultyData,
                ttl_hours: 24,
              }),
            })
            setCacheKey(generatedCacheKey)
            console.log('✅ Data cached in Redis')
          } catch (cacheErr) {
            console.warn('⚠️ Failed to cache data:', cacheErr)
          }
        }
      }
    } catch (err) {
      console.error('❌ Failed to load enrollment data:', err)
      setError('Failed to load enrollment data')
    } finally {
      setIsLoading(false)
    }
  }

  const addFixedSlot = () => {
    setFixedSlots(prev => [
      ...prev,
      {
        subject_id: '',
        faculty_id: '',
        day: 0,
        start_time: '09:00',
        end_time: '10:00',
      },
    ])
  }

  const updateFixedSlot = (index: number, field: keyof FixedSlotInput, value: any) => {
    setFixedSlots(prev => prev.map((slot, i) => (i === index ? { ...slot, [field]: value } : slot)))
  }

  const removeFixedSlot = (index: number) => {
    setFixedSlots(prev => prev.filter((_, i) => i !== index))
  }

  const handleGenerate = async () => {
    if (enrollmentSummary.length === 0) {
      alert('No subjects with enrollments found. Please ensure students are enrolled in subjects.')
      return
    }

    if (!user?.organization) {
      alert('User organization not found')
      return
    }

    try {
      setIsGenerating(true)
      setError(null)

      // NEP 2020 payload - Organization-wide student enrollments
      const requestPayload = {
        // Selection criteria
        semester: formData.semester,
        academic_year: formData.academic_year,
        organization_id: user.organization,

        // Generation options
        num_variants: formData.num_variants,
        include_cross_dept: formData.include_cross_dept,
        fixed_slots: fixedSlots.filter(slot => slot.subject_id && slot.faculty_id),

        // Enrollment data (or cache key)
        subjects: enrollmentSummary,
        redis_cache_key: cacheKey,
      }

      console.log('🚀 Generating NEP 2020 timetable:', requestPayload)

      const response = await fetch(`${API_BASE}/timetable/generate/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(requestPayload),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Failed to start generation')
      }

      if (data.success) {
        setJobId(data.job_id)
      } else {
        throw new Error(data.error || 'Generation failed')
      }
    } catch (err) {
      console.error('Failed to generate timetable:', err)
      setError(err instanceof Error ? err.message : 'Failed to generate timetable')
      setIsGenerating(false)
    }
  }

  if (isGenerating && jobId) {
    return (
      <TimetableProgressTracker
        jobId={jobId}
        onComplete={generatedTimetableId => {
          router.push(`/admin/timetable/review/${generatedTimetableId}`)
        }}
      />
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div className="space-y-1">
          <h2 className="text-2xl font-bold tracking-tight text-[#2C2C2C] dark:text-[#FFFFFF]">
            Generate Timetable (NEP 2020)
          </h2>
          <p className="text-sm text-[#6B6B6B] dark:text-[#B3B3B3]">
            Student-based flexible course enrollment (Harvard-style)
          </p>
        </div>
      </div>

      {error && (
        <div className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
          <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
        </div>
      )}

      {/* Configuration */}
      <div className="card">
        <div className="p-4 sm:p-6 space-y-4">
          <h3 className="text-base font-semibold text-gray-800 dark:text-gray-200">
            Academic Configuration
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Semester */}
            <div>
              <label className="block text-sm font-medium text-[#2C2C2C] dark:text-[#FFFFFF] mb-2">
                Semester <span className="text-red-500">*</span>
              </label>
              <select
                value={formData.semester}
                onChange={e => setFormData({ ...formData, semester: parseInt(e.target.value) })}
                className="input-field"
                disabled={isGenerating || isLoading}
                aria-label="Select semester"
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
              <label className="block text-sm font-medium text-[#2C2C2C] dark:text-[#FFFFFF] mb-2">
                Academic Year <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={formData.academic_year}
                onChange={e => setFormData({ ...formData, academic_year: e.target.value })}
                placeholder="2024-25"
                className="input-field"
                disabled={isGenerating || isLoading}
                aria-label="Academic year"
              />
            </div>

            {/* Number of Variants */}
            <div>
              <label className="block text-sm font-medium text-[#2C2C2C] dark:text-[#FFFFFF] mb-2">
                Variants
              </label>
              <input
                type="number"
                value={formData.num_variants}
                onChange={e =>
                  setFormData({ ...formData, num_variants: parseInt(e.target.value) || 5 })
                }
                min={3}
                max={10}
                className="input-field"
                disabled={isGenerating || isLoading}
                aria-label="Number of timetable variants"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Enrollment Summary */}
      {isLoading ? (
        <div className="card">
          <div className="p-6 text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-2"></div>
            <p className="text-sm text-gray-600">Loading enrollment data...</p>
          </div>
        </div>
      ) : (
        <div className="card">
          <div className="p-4 sm:p-6 space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-base font-semibold text-gray-800 dark:text-gray-200">
                Subject Enrollments
              </h3>
              <button
                onClick={loadEnrollmentData}
                className="btn-secondary text-xs px-3 py-1.5"
                disabled={isLoading}
              >
                🔄 Refresh
              </button>
            </div>

            {enrollmentSummary.length === 0 ? (
              <p className="text-sm text-gray-500">
                No subjects with enrollments found for selected semester
              </p>
            ) : (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                  <thead className="bg-gray-50 dark:bg-gray-800">
                    <tr>
                      <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                        Subject
                      </th>
                      <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                        Type
                      </th>
                      <th className="px-3 py-2 text-right text-xs font-medium text-gray-500 uppercase">
                        Total
                      </th>
                      <th className="px-3 py-2 text-right text-xs font-medium text-gray-500 uppercase">
                        Core
                      </th>
                      <th className="px-3 py-2 text-right text-xs font-medium text-gray-500 uppercase">
                        Elective
                      </th>
                      <th className="px-3 py-2 text-right text-xs font-medium text-gray-500 uppercase">
                        Cross-Dept
                      </th>
                      <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                        Dept
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
                    {enrollmentSummary.map(subj => (
                      <tr key={subj.subject_id}>
                        <td className="px-3 py-2 text-sm">
                          <div className="font-medium text-gray-900 dark:text-white">
                            {subj.subject_code}
                          </div>
                          <div className="text-xs text-gray-500">{subj.subject_name}</div>
                        </td>
                        <td className="px-3 py-2 text-sm">
                          <span className="badge badge-neutral text-xs">{subj.subject_type}</span>
                        </td>
                        <td className="px-3 py-2 text-sm text-right font-semibold">
                          {subj.total_enrolled}
                        </td>
                        <td className="px-3 py-2 text-sm text-right">{subj.core_enrolled}</td>
                        <td className="px-3 py-2 text-sm text-right">{subj.elective_enrolled}</td>
                        <td className="px-3 py-2 text-sm text-right">
                          {subj.cross_dept_enrolled > 0 && (
                            <span className="text-orange-600 font-medium">
                              {subj.cross_dept_enrolled}
                            </span>
                          )}
                        </td>
                        <td className="px-3 py-2 text-sm text-gray-600">
                          {subj.primary_department}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            <div className="text-xs text-gray-500">
              Total subjects: {enrollmentSummary.length} | Total students:{' '}
              {enrollmentSummary.reduce((sum, s) => sum + s.total_enrolled, 0)}
            </div>
          </div>
        </div>
      )}

      {/* Fixed Slots (Optional) */}
      <div className="card">
        <div className="p-4 sm:p-6 space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-semibold text-gray-800 dark:text-gray-200">
              Fixed Slots <span className="text-xs font-normal text-gray-500">(Optional)</span>
            </h3>
            <button
              onClick={addFixedSlot}
              disabled={isGenerating}
              className="btn-primary text-xs px-3 py-1.5"
            >
              + Add Slot
            </button>
          </div>

          {fixedSlots.length === 0 ? (
            <p className="text-sm text-gray-500">No fixed slots defined</p>
          ) : (
            <div className="space-y-3">
              {fixedSlots.map((slot, index) => (
                <div
                  key={index}
                  className="p-3 border border-gray-200 dark:border-gray-600 rounded-lg bg-gray-50 dark:bg-gray-700/50"
                >
                  <div className="grid grid-cols-1 md:grid-cols-5 gap-2">
                    <select
                      value={slot.subject_id}
                      onChange={e => updateFixedSlot(index, 'subject_id', e.target.value)}
                      className="input-field text-sm"
                      aria-label="Select subject for fixed slot"
                    >
                      <option value="">Select Subject</option>
                      {enrollmentSummary.map(subj => (
                        <option key={subj.subject_id} value={subj.subject_id}>
                          {subj.subject_code}
                        </option>
                      ))}
                    </select>

                    <select
                      value={slot.faculty_id}
                      onChange={e => updateFixedSlot(index, 'faculty_id', e.target.value)}
                      className="input-field text-sm"
                      aria-label="Select faculty for fixed slot"
                    >
                      <option value="">Select Faculty</option>
                      {faculty.map(fac => (
                        <option key={fac.faculty_id} value={fac.faculty_id}>
                          {fac.faculty_name}
                        </option>
                      ))}
                    </select>

                    <select
                      value={slot.day}
                      onChange={e => updateFixedSlot(index, 'day', parseInt(e.target.value))}
                      className="input-field text-sm"
                      aria-label="Select day for fixed slot"
                    >
                      {['Mon', 'Tue', 'Wed', 'Thu', 'Fri'].map((day, i) => (
                        <option key={i} value={i}>
                          {day}
                        </option>
                      ))}
                    </select>

                    <input
                      type="time"
                      value={slot.start_time}
                      onChange={e => updateFixedSlot(index, 'start_time', e.target.value)}
                      className="input-field text-sm"
                      aria-label="Start time for fixed slot"
                    />

                    <div className="flex gap-2">
                      <input
                        type="time"
                        value={slot.end_time}
                        onChange={e => updateFixedSlot(index, 'end_time', e.target.value)}
                        className="input-field text-sm flex-1"
                        aria-label="End time for fixed slot"
                      />
                      <button
                        onClick={() => removeFixedSlot(index)}
                        className="btn-secondary text-xs px-2"
                      >
                        ✕
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Generate Button */}
      <div className="flex justify-end">
        <button
          onClick={handleGenerate}
          disabled={isGenerating || isLoading || enrollmentSummary.length === 0}
          className="btn-primary px-6 py-2"
        >
          {isGenerating ? 'Generating...' : 'Generate Timetable'}
        </button>
      </div>
    </div>
  )
}
