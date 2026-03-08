'use client'

import { useState, useEffect, useCallback } from 'react'
import apiClient from '@/lib/api'
import { useToast } from '@/components/Toast'
import AddEditDepartmentModal from './components/AddEditDepartmentModal'
import PageHeader from '@/components/shared/PageHeader'
import DataTable, { Column } from '@/components/shared/DataTable'
import { Layers } from 'lucide-react'

interface Department {
  id: number
  dept_id: string
  dept_code: string
  dept_name: string
  school?: { id?: number; school_name: string }
}

const COLUMNS: Column<Record<string, unknown>>[] = [
  { key: 'dept_code', header: 'Code', width: '120px' },
  { key: 'dept_name', header: 'Name' },
  {
    key: 'school',
    header: 'School',
    render: v => (v as Department['school'])?.school_name
      || <span style={{ color: 'var(--color-text-secondary)' }}>—</span>,
  },
]

export default function DepartmentsPage() {
  const { showToast } = useToast()
  const [departments, setDepartments] = useState<Department[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [showModal, setShowModal] = useState(false)
  const [editingDept, setEditingDept] = useState<Department | null>(null)
  const [currentPage, setCurrentPage] = useState(1)
  const [totalCount, setTotalCount] = useState(0)
  const itemsPerPage = 25

  const fetchDepartments = useCallback(async (page = currentPage) => {
    setIsLoading(true)
    try {
      const response = await apiClient.getDepartments(page, itemsPerPage, searchTerm)
      if (response.error) showToast('error', response.error)
      else if (response.data) {
        setDepartments(response.data.results || response.data)
        setTotalCount(response.data.count || 0)
      }
    } catch { showToast('error', 'Failed to load departments') }
    finally { setIsLoading(false) }
  }, [currentPage, itemsPerPage, searchTerm]) // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    const t = setTimeout(() => { setCurrentPage(1); fetchDepartments(1) }, 400)
    return () => clearTimeout(t)
  }, [searchTerm]) // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => { fetchDepartments() }, [currentPage]) // eslint-disable-line react-hooks/exhaustive-deps

  const handleSave = async (data: any) => {
    const res = editingDept
      ? await apiClient.updateDepartment(String(editingDept.id), data)
      : await apiClient.createDepartment(data)
    if (res.error) { showToast('error', res.error); return }
    showToast('success', editingDept ? 'Department updated' : 'Department created')
    setShowModal(false)
    await fetchDepartments()
  }

  const handleBulkDelete = async (ids: string[]) => {
    const results = await Promise.all(ids.map(id => apiClient.deleteDepartment(id)))
    const firstError = results.find(r => r.error)
    if (firstError) { showToast('error', firstError.error!); return }
    showToast('success', `${ids.length} department${ids.length > 1 ? 's' : ''} deleted`)
    await fetchDepartments()
  }

  return (
    <div className="space-y-4">
      <PageHeader
        title="Departments"
        parentLabel="Academic"
        count={totalCount}
        loading={isLoading}
        primaryAction={{ label: 'Add Department', onClick: () => { setEditingDept(null); setShowModal(true) } }}
      />
      <DataTable
        columns={COLUMNS}
        data={departments as unknown as Record<string, unknown>[]}
        loading={isLoading}
        totalCount={totalCount}
        page={currentPage}
        pageSize={itemsPerPage}
        onPageChange={setCurrentPage}
        selectable
        avatarColumn={row => (row as unknown as Department).dept_name}
        onDelete={handleBulkDelete}
        onEdit={row => { setEditingDept(row as unknown as Department); setShowModal(true) }}
        emptyState={{ icon: Layers, title: 'No departments found', description: 'Add your first department to get started.' }}
      />
      <AddEditDepartmentModal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        department={editingDept}
        onSave={handleSave}
      />
    </div>
  )
}
