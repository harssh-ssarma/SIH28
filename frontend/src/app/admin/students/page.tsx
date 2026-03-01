'use client'

import { useState, useEffect, useCallback } from 'react'
import AddEditStudentModal from './components/AddEditStudentModal'
import StudentDetailPanel from './components/StudentDetailPanel'
import { SimpleStudentInput } from '@/lib/validations'
import apiClient from '@/lib/api'
import { useToast } from '@/components/Toast'
import PageHeader from '@/components/shared/PageHeader'
import DataTable, { Column } from '@/components/shared/DataTable'
import { GraduationCap } from 'lucide-react'

interface Student {
  id: number
  student_id: string
  name: string
  email?: string
  phone?: string
  department: { department_id: string; department_name: string }
  course: { course_id: string; course_name: string }
  electives: string
  year: number
  semester: number
  faculty_advisor: { faculty_id: string; faculty_name: string } | null
}

const COLUMNS: Column<Record<string, unknown>>[] = [
  {
    key: 'name',
    header: 'Student',
    render: (v, row) => (
      <div>
        <div className="font-medium text-sm text-[var(--color-text-primary)]">{v as string}</div>
        <div className="text-xs text-[var(--color-text-secondary)] font-mono">{row['student_id'] as string}</div>
      </div>
    ),
  },
  { key: 'department', header: 'Department', render: v => <span className="badge badge-neutral">{(v as Student['department'])?.department_name || '—'}</span> },
  { key: 'course', header: 'Course', render: v => (v as Student['course'])?.course_name || '—' },
  { key: 'year', header: 'Year', width: '70px', render: v => <span className="badge badge-info">Year {v as number}</span> },
  { key: 'semester', header: 'Sem', width: '70px', render: v => <span className="badge badge-success">Sem {v as number}</span> },
  { key: 'faculty_advisor', header: 'Advisor', render: v => (v as Student['faculty_advisor'])?.faculty_name || <span className="text-[var(--color-text-secondary)]">Unassigned</span> },
]

export default function StudentsPage() {
  const { showToast } = useToast()
  const [students, setStudents] = useState<Student[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [currentPage, setCurrentPage] = useState(1)
  const [totalCount, setTotalCount] = useState(0)
  const itemsPerPage = 25
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [selectedStudent, setSelectedStudent] = useState<Student | null>(null)
  const [detailStudent, setDetailStudent] = useState<Student | null>(null)

  const fetchStudents = useCallback(async (page = currentPage) => {
    setIsLoading(true)
    try {
      const response = await apiClient.getStudents(page, itemsPerPage, searchTerm)
      if (response.error) showToast('error', response.error)
      else if (response.data) {
        setStudents(response.data.results || response.data)
        setTotalCount(response.data.count || 0)
      }
    } catch { showToast('error', 'Failed to fetch students') }
    finally { setIsLoading(false) }
  }, [currentPage, itemsPerPage, searchTerm]) // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    const t = setTimeout(() => { setCurrentPage(1); fetchStudents(1) }, 400)
    return () => clearTimeout(t)
  }, [searchTerm]) // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => { fetchStudents() }, [currentPage]) // eslint-disable-line react-hooks/exhaustive-deps

  const handleSaveStudent = async (data: SimpleStudentInput) => {
    const payload = { ...data, email: data.email || '', phone: data.phone || '', electives: data.electives || '' }
    const response = selectedStudent
      ? await apiClient.updateStudent(String(selectedStudent.id), payload)
      : await apiClient.createStudent(payload)
    if (response.error) { showToast('error', response.error); return }
    showToast('success', selectedStudent ? 'Student updated!' : 'Student created!')
    setIsModalOpen(false)
    setSelectedStudent(null)
    await fetchStudents()
  }

  const handleBulkDelete = async (ids: string[]) => {
    for (const id of ids) {
      const res = await apiClient.deleteStudent(id)
      if (res.error) { showToast('error', res.error); break }
    }
    showToast('success', `${ids.length} student${ids.length > 1 ? 's' : ''} deleted`)
    await fetchStudents()
  }

  return (
    <div className="space-y-4">
      <PageHeader
        title="Students"
        count={totalCount}
        loading={isLoading}
        primaryAction={{ label: 'Add Student', onClick: () => { setSelectedStudent(null); setIsModalOpen(true) } }}
      />
      <DataTable
        columns={COLUMNS}
        data={students as unknown as Record<string, unknown>[]}
        loading={isLoading}
        totalCount={totalCount}
        page={currentPage}
        pageSize={itemsPerPage}
        onPageChange={setCurrentPage}
        selectable
        avatarColumn={row => (row as unknown as Student).name}
        onDelete={handleBulkDelete}
        onEdit={row => { setSelectedStudent(row as unknown as Student); setIsModalOpen(true) }}
        onRowClick={row => setDetailStudent(row as unknown as Student)}
        emptyState={{ icon: GraduationCap, title: 'No students found', description: 'Add students to get started.' }}
      />
      <AddEditStudentModal
        isOpen={isModalOpen}
        onClose={() => { setIsModalOpen(false); setSelectedStudent(null) }}
        onSave={handleSaveStudent}
        student={selectedStudent}
      />
      {detailStudent && (
        <StudentDetailPanel
          student={detailStudent}
          onClose={() => setDetailStudent(null)}
          onEdit={() => { setSelectedStudent(detailStudent); setDetailStudent(null); setIsModalOpen(true) }}
          onDelete={() => { handleBulkDelete([String(detailStudent.id)]); setDetailStudent(null) }}
        />
      )}
    </div>
  )
}