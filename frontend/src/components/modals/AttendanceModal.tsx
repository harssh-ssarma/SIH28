'use client'

import { useState, useEffect } from 'react'

interface Student {
  id: number
  student_id: string
  name: string
  email: string
}

interface AttendanceModalProps {
  isOpen: boolean
  onClose: () => void
  classData: {
    id: number
    course_id: number
    course_name: string
    batch: string
    time_slot: string
    classroom: string
  }
  facultyId: number
}

export default function AttendanceModal({ isOpen, onClose, classData, facultyId }: AttendanceModalProps) {
  const [students, setStudents] = useState<Student[]>([])
  const [attendance, setAttendance] = useState<{ [key: number]: string }>({})
  const [loading, setLoading] = useState(false)
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    if (isOpen && classData) {
      loadStudents()
    }
  }, [isOpen, classData])

  const loadStudents = async () => {
    setLoading(true)
    try {
      const response = await fetch(`http://localhost:8000/api/v1/attendance/batch/${classData.batch}/students/`)
      const data = await response.json()
      setStudents(data)
      
      // Initialize all students as present
      const initialAttendance: { [key: number]: string } = {}
      data.forEach((student: Student) => {
        initialAttendance[student.id] = 'present'
      })
      setAttendance(initialAttendance)
    } catch (error) {
      console.error('Failed to load students:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleAttendanceChange = (studentId: number, status: string) => {
    setAttendance(prev => ({
      ...prev,
      [studentId]: status
    }))
  }

  const handleSubmit = async () => {
    setSubmitting(true)
    try {
      const attendanceRecords = students.map(student => ({
        student_id: student.id,
        status: attendance[student.id] || 'present'
      }))

      const response = await fetch('http://localhost:8000/api/v1/attendance/mark/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          course_id: classData.course_id,
          faculty_id: facultyId,
          batch: classData.batch,
          date: new Date().toISOString().split('T')[0],
          time_slot: classData.time_slot,
          classroom: classData.classroom,
          attendance_records: attendanceRecords
        })
      })

      const result = await response.json()
      if (result.success) {
        alert('Attendance marked successfully!')
        onClose()
      } else {
        alert(`Failed to mark attendance: ${result.error}`)
      }
    } catch (error) {
      alert(`Error: ${error}`)
    } finally {
      setSubmitting(false)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'present': return 'bg-green-500 text-white'
      case 'absent': return 'bg-red-500 text-white'
      case 'late': return 'bg-yellow-500 text-white'
      default: return 'bg-gray-300 text-gray-700'
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-2 sm:p-4">
      <div className="bg-white dark:bg-gray-800 rounded-xl w-full max-w-4xl max-h-[90vh] overflow-hidden border border-gray-200 dark:border-gray-700 shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between p-4 sm:p-6 border-b border-gray-200 dark:border-gray-700">
          <div>
            <h2 className="text-xl sm:text-2xl font-semibold text-gray-900 dark:text-white">
              Mark Attendance
            </h2>
            <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
              {classData.course_name} - {classData.batch} - {classData.time_slot}
            </p>
          </div>
          <button
            onClick={onClose}
            className="w-8 h-8 sm:w-10 sm:h-10 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors flex items-center justify-center text-gray-600 dark:text-gray-300"
          >
            ✕
          </button>
        </div>

        {/* Content */}
        <div className="p-4 sm:p-6 overflow-y-auto max-h-[calc(90vh-200px)]">
          {loading ? (
            <div className="text-center py-8">
              <div className="loading-spinner w-8 h-8 mx-auto mb-4"></div>
              <p className="text-gray-600 dark:text-gray-400">Loading students...</p>
            </div>
          ) : (
            <div className="space-y-3">
              {students.map((student) => (
                <div key={student.id} className="flex flex-col sm:flex-row sm:items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg gap-3">
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-900 dark:text-white">
                      {student.name}
                    </h4>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {student.student_id} • {student.email}
                    </p>
                  </div>
                  
                  <div className="flex gap-2">
                    {['present', 'absent', 'late'].map((status) => (
                      <button
                        key={status}
                        onClick={() => handleAttendanceChange(student.id, status)}
                        className={`px-3 py-1 text-sm font-medium rounded-lg transition-colors ${
                          attendance[student.id] === status
                            ? getStatusColor(status)
                            : 'bg-gray-200 text-gray-700 hover:bg-gray-300 dark:bg-gray-600 dark:text-gray-300 dark:hover:bg-gray-500'
                        }`}
                      >
                        {status.charAt(0).toUpperCase() + status.slice(1)}
                      </button>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex flex-col sm:flex-row justify-end gap-2 sm:gap-3 p-4 sm:p-6 border-t border-gray-200 dark:border-gray-700">
          <button
            onClick={onClose}
            className="btn-secondary w-full sm:w-auto"
          >
            Cancel
          </button>
          <button
            onClick={handleSubmit}
            disabled={submitting || loading}
            className="btn-primary w-full sm:w-auto disabled:opacity-50"
          >
            {submitting ? (
              <>
                <div className="loading-spinner w-4 h-4 mr-2"></div>
                Submitting...
              </>
            ) : (
              <>✅ Submit Attendance</>
            )}
          </button>
        </div>
      </div>
    </div>
  )
}