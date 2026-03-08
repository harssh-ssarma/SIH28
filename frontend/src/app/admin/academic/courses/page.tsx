'use client'

import { useState, useEffect, useCallback } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import apiClient from '@/lib/api'
import { subjectSchema, type SubjectInput } from '@/lib/validations'
import { FormField } from '@/components/FormFields'
import { useToast } from '@/components/Toast'
import PageHeader from '@/components/shared/PageHeader'
import DataTable, { Column } from '@/components/shared/DataTable'
import { BookMarked } from 'lucide-react'

interface Course {
  course_id: string
  course_code: string
  course_name: string
  department: { dept_id: string; dept_name: string }
  credits: number
  course_type?: string
}

const COLUMNS: Column<Record<string, unknown>>[] = [
  { key: 'course_name', header: 'Name' },
  {
    key: 'course_code',
    header: 'Code',
    width: '110px',
    render: v => <span className="badge badge-neutral">{v as string}</span>,
  },
  { key: 'course_type', header: 'Type', width: '100px', render: v => (v as string) || '—' },
  {
    key: 'department',
    header: 'Department',
    render: v => (v as Course['department'])?.dept_name || '—',
  },
  { key: 'credits', header: 'Credits', width: '80px' },
]

export default function SubjectsPage() {
  const { showSuccessToast, showErrorToast } = useToast()
  const [courses, setCourses] = useState<Course[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [editingId, setEditingId] = useState<string | null>(null)
  const [currentPage, setCurrentPage] = useState(1)
  const [totalCount, setTotalCount] = useState(0)
  const itemsPerPage = 25

  const { register, handleSubmit: handleFormSubmit, formState: { errors, isSubmitting }, reset, setValue } = useForm<SubjectInput>({
    resolver: zodResolver(subjectSchema),
    defaultValues: { subject_name: '', subject_id: '', department_id: '', course_id: '', credits: 3, lecture_hours: 3, lab_hours: 0 },
  })

  const loadSubjects = useCallback(async (page = currentPage) => {
    setIsLoading(true)
    try {
      const response = await apiClient.getCourses(page, itemsPerPage, searchTerm)
      if (response.error) showErrorToast(response.error)
      else if (response.data) {
        setCourses(response.data.results || response.data)
        setTotalCount(response.data.count || 0)
      }
    } catch { showErrorToast('Failed to load courses') }
    finally { setIsLoading(false) }
  }, [currentPage, itemsPerPage, searchTerm]) // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    const t = setTimeout(() => { setCurrentPage(1); loadSubjects(1) }, 400)
    return () => clearTimeout(t)
  }, [searchTerm]) // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => { loadSubjects() }, [currentPage]) // eslint-disable-line react-hooks/exhaustive-deps

  const onSubmit = async (data: SubjectInput) => {
    const payload = {
      course_name: data.subject_name, course_code: data.subject_id,
      department: data.department_id, credits: data.credits,
      lecture_hours_per_week: data.lecture_hours, lab_hours_per_week: data.lab_hours,
    }
    const response = editingId
      ? await apiClient.request<any>(`/courses/${editingId}/`, { method: 'PUT', body: JSON.stringify(payload) })
      : await apiClient.request<any>('/courses/', { method: 'POST', body: JSON.stringify(payload) })
    if (response.error) { showErrorToast(response.error); return }
    showSuccessToast(editingId ? 'Course updated!' : 'Course created!')
    resetForm()
    await loadSubjects()
  }

  const handleEdit = (row: Record<string, unknown>) => {
    const course = row as unknown as Course
    setValue('subject_name', course.course_name)
    setValue('subject_id', course.course_code)
    setValue('department_id', course.department.dept_id)
    setValue('course_id', course.course_id)
    setValue('credits', course.credits)
    setValue('lecture_hours', 3)
    setValue('lab_hours', 0)
    setEditingId(course.course_id)
    setShowForm(true)
  }

  const handleBulkDelete = async (ids: string[]) => {
    const results = await Promise.all(ids.map(id => apiClient.request<any>(`/courses/${id}/`, { method: 'DELETE' })))
    const firstError = results.find(r => r.error)
    if (firstError) { showErrorToast(firstError.error!); return }
    showSuccessToast(`${ids.length} course${ids.length > 1 ? 's' : ''} deleted`)
    await loadSubjects()
  }

  const resetForm = () => { reset(); setEditingId(null); setShowForm(false) }

  return (
    <div className="space-y-4">
      <PageHeader
        title="Courses"
        parentLabel="Academic"
        count={totalCount}
        loading={isLoading}
        primaryAction={{ label: 'Add Course', onClick: () => setShowForm(true) }}
      />

      {showForm && (
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">{editingId ? 'Edit' : 'Add'} Course</h3>
          </div>
          <form onSubmit={handleFormSubmit(onSubmit)} className="p-4 sm:p-6 space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <FormField label="Course Name" name="subject_name" register={register} error={errors.subject_name} placeholder="e.g., Data Structures" required />
              <FormField label="Course Code" name="subject_id" register={register} error={errors.subject_id} placeholder="e.g., CS101" required helpText="Uppercase letters and numbers only" />
              <FormField label="Course ID" name="course_id" register={register} error={errors.course_id} placeholder="e.g., BTECH-CS" required />
              <FormField label="Department ID" name="department_id" register={register} error={errors.department_id} placeholder="e.g., CS" required />
              <FormField label="Credits" name="credits" type="number" register={register} error={errors.credits} placeholder="1-10" required helpText="Number of credits (1-10)" />
              <FormField label="Lecture Hours" name="lecture_hours" type="number" register={register} error={errors.lecture_hours} placeholder="0-20" helpText="Lecture hours per week" />
              <FormField label="Lab Hours" name="lab_hours" type="number" register={register} error={errors.lab_hours} placeholder="0-20" helpText="Lab hours per week" />
            </div>
            <div className="flex gap-2">
              <button type="submit" className="btn-primary" disabled={isSubmitting}>{isSubmitting ? 'Saving...' : editingId ? 'Update Course' : 'Create Course'}</button>
              <button type="button" onClick={resetForm} className="btn-secondary" disabled={isSubmitting}>Cancel</button>
            </div>
          </form>
        </div>
      )}

      <DataTable
        columns={COLUMNS}
        data={courses as unknown as Record<string, unknown>[]}
        loading={isLoading}
        totalCount={totalCount}
        page={currentPage}
        pageSize={itemsPerPage}
        onPageChange={setCurrentPage}
        selectable
        idField="course_id"
        avatarColumn={row => (row as unknown as Course).course_name}
        onDelete={handleBulkDelete}
        onEdit={handleEdit}
        emptyState={{ icon: BookMarked, title: 'No courses found', description: 'Add courses to get started.' }}
      />
    </div>
  )
}