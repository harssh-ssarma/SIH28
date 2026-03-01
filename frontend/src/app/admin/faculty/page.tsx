'use client'

import { useState, useEffect, useCallback } from 'react'
import AddEditFacultyModal from './components/AddEditFacultyModal'
import FacultyDetailPanel from './components/FacultyDetailPanel'
import { SimpleFacultyInput } from '@/lib/validations'
import apiClient from '@/lib/api'
import { useToast } from '@/components/Toast'
import PageHeader from '@/components/shared/PageHeader'
import DataTable, { Column } from '@/components/shared/DataTable'
import { Users } from 'lucide-react'

interface Faculty {
  id: number
  faculty_id: string
  faculty_code: string
  first_name: string
  middle_name?: string
  last_name: string
  designation: string
  specialization: string
  department: { dept_id: string; dept_name: string }
  max_workload: number
  status: string
  email?: string
  phone?: string
}

const COLUMNS: Column<Record<string, unknown>>[] = [
  {
    key: 'first_name',
    header: 'Name',
    render: (_, row) => {
      const name = [row['first_name'], row['middle_name'], row['last_name']].filter(Boolean).join(' ')
      return (
        <div>
          <div className="font-medium text-sm text-[var(--color-text-primary)]">{name}</div>
          <div className="text-xs text-[var(--color-text-secondary)]">{row['faculty_code'] as string}</div>
        </div>
      )
    },
  },
  { key: 'designation', header: 'Designation', render: v => <span className="badge badge-neutral">{v as string}</span> },
  { key: 'department', header: 'Department', render: v => (v as Faculty['department'])?.dept_name || '—' },
  { key: 'specialization', header: 'Specialization' },
  { key: 'max_workload', header: 'Workload', width: '90px', render: v => `${v}h/wk` },
  { key: 'status', header: 'Status', width: '90px', render: v => <span className="badge badge-success">{v as string}</span> },
]

export default function FacultyManagePage() {
  const { showToast } = useToast()
  const [faculty, setFaculty] = useState<Faculty[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [currentPage, setCurrentPage] = useState(1)
  const [totalCount, setTotalCount] = useState(0)
  const itemsPerPage = 25
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [selectedFaculty, setSelectedFaculty] = useState<Faculty | null>(null)
  const [detailFaculty, setDetailFaculty] = useState<Faculty | null>(null)

  const fetchFaculty = useCallback(async (page = currentPage) => {
    setIsLoading(true)
    try {
      const response = await apiClient.getFaculty(page, itemsPerPage, searchTerm)
      if (response.error) showToast('error', response.error)
      else if (response.data) {
        setFaculty(response.data.results || response.data)
        setTotalCount(response.data.count || 0)
      }
    } catch { showToast('error', 'Failed to fetch faculty') }
    finally { setIsLoading(false) }
  }, [currentPage, itemsPerPage, searchTerm]) // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    const t = setTimeout(() => { setCurrentPage(1); fetchFaculty(1) }, 400)
    return () => clearTimeout(t)
  }, [searchTerm]) // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => { fetchFaculty() }, [currentPage]) // eslint-disable-line react-hooks/exhaustive-deps

  const handleSaveFaculty = async (data: SimpleFacultyInput) => {
    const payload = {
      faculty_id: data.faculty_id, first_name: data.first_name,
      middle_name: data.middle_name || '', last_name: data.last_name,
      designation: data.designation, specialization: data.specialization,
      max_workload_per_week: data.max_workload_per_week,
      email: data.email, phone: data.phone || '',
      department: data.department, status: data.status,
    }
    const response = selectedFaculty
      ? await apiClient.updateFaculty(String(selectedFaculty.id), payload)
      : await apiClient.createFaculty(payload)
    if (response.error) { showToast('error', response.error); return }
    showToast('success', selectedFaculty ? 'Faculty updated' : 'Faculty created. User account also created.')
    setIsModalOpen(false)
    await fetchFaculty()
  }

  const handleBulkDelete = async (ids: string[]) => {
    for (const id of ids) {
      const res = await apiClient.deleteFaculty(id)
      if (res.error) { showToast('error', res.error); break }
    }
    showToast('success', `${ids.length} faculty member${ids.length > 1 ? 's' : ''} deleted`)
    await fetchFaculty()
  }

  return (
    <div className="space-y-4">
      <PageHeader
        title="Faculty"
        count={totalCount}
        loading={isLoading}
        primaryAction={{ label: 'Add Faculty', onClick: () => { setSelectedFaculty(null); setIsModalOpen(true) } }}
      />
      <DataTable
        columns={COLUMNS}
        data={faculty as unknown as Record<string, unknown>[]}
        loading={isLoading}
        totalCount={totalCount}
        page={currentPage}
        pageSize={itemsPerPage}
        onPageChange={setCurrentPage}
        selectable
        avatarColumn={row => {
          const r = row as unknown as Faculty
          return [r.first_name, r.middle_name, r.last_name].filter(Boolean).join(' ')
        }}
        onDelete={handleBulkDelete}
        onEdit={row => { setSelectedFaculty(row as unknown as Faculty); setIsModalOpen(true) }}
        onRowClick={row => setDetailFaculty(row as unknown as Faculty)}
        emptyState={{ icon: Users, title: 'No faculty found', description: 'Add faculty members to get started.' }}
      />
      <AddEditFacultyModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        faculty={selectedFaculty}
        onSave={handleSaveFaculty}
      />
      {detailFaculty && (
        <FacultyDetailPanel
          faculty={detailFaculty}
          onClose={() => setDetailFaculty(null)}
          onEdit={() => { setSelectedFaculty(detailFaculty); setDetailFaculty(null); setIsModalOpen(true) }}
          onDelete={() => { handleBulkDelete([String(detailFaculty.id)]); setDetailFaculty(null) }}
        />
      )}
    </div>
  )
}