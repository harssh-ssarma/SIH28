'use client'

import { useState, useEffect, useCallback } from 'react'
import apiClient from '@/lib/api'
import { useToast } from '@/components/Toast'
import AddEditSchoolModal from './components/AddEditSchoolModal'
import PageHeader from '@/components/shared/PageHeader'
import DataTable, { Column } from '@/components/shared/DataTable'
import { Building2 } from 'lucide-react'

interface School {
  id: number
  school_id: string
  school_code: string
  school_name: string
  description?: string
}

const COLUMNS: Column<Record<string, unknown>>[] = [
  { key: 'school_code', header: 'Code', width: '120px' },
  { key: 'school_name', header: 'Name' },
  {
    key: 'description',
    header: 'Description',
    render: v => (v as string) || <span style={{ color: 'var(--color-text-secondary)' }}>—</span>,
  },
]

export default function SchoolsPage() {
  const { showToast } = useToast()
  const [schools, setSchools] = useState<School[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [showModal, setShowModal] = useState(false)
  const [editingSchool, setEditingSchool] = useState<School | null>(null)
  const [currentPage, setCurrentPage] = useState(1)
  const [totalCount, setTotalCount] = useState(0)
  const itemsPerPage = 25

  const fetchSchools = useCallback(async (page = currentPage) => {
    setIsLoading(true)
    try {
      const response = await apiClient.getSchools(page, itemsPerPage, searchTerm)
      if (response.error) showToast('error', response.error)
      else if (response.data) {
        setSchools(response.data.results || response.data)
        setTotalCount(response.data.count || 0)
      }
    } catch { showToast('error', 'Failed to load schools') }
    finally { setIsLoading(false) }
  }, [currentPage, itemsPerPage, searchTerm]) // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    const t = setTimeout(() => { setCurrentPage(1); fetchSchools(1) }, 400)
    return () => clearTimeout(t)
  }, [searchTerm]) // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => { fetchSchools() }, [currentPage]) // eslint-disable-line react-hooks/exhaustive-deps

  const handleSave = async (data: any) => {
    const res = editingSchool
      ? await apiClient.updateSchool(String(editingSchool.id), data)
      : await apiClient.createSchool(data)
    if (res.error) { showToast('error', res.error); return }
    showToast('success', editingSchool ? 'School updated' : 'School created')
    setShowModal(false)
    await fetchSchools()
  }

  const handleBulkDelete = async (ids: string[]) => {
    const results = await Promise.all(ids.map(id => apiClient.deleteSchool(id)))
    const firstError = results.find(r => r.error)
    if (firstError) { showToast('error', firstError.error!); return }
    showToast('success', `${ids.length} school${ids.length > 1 ? 's' : ''} deleted`)
    await fetchSchools()
  }

  return (
    <div className="space-y-4">
      <PageHeader
        title="Schools"
        parentLabel="Academic"
        count={totalCount}
        loading={isLoading}
        primaryAction={{ label: 'Add School', onClick: () => { setEditingSchool(null); setShowModal(true) } }}
      />
      <DataTable
        columns={COLUMNS}
        data={schools as unknown as Record<string, unknown>[]}
        loading={isLoading}
        totalCount={totalCount}
        page={currentPage}
        pageSize={itemsPerPage}
        onPageChange={setCurrentPage}
        selectable
        avatarColumn={row => (row as unknown as School).school_name}
        onDelete={handleBulkDelete}
        onEdit={row => { setEditingSchool(row as unknown as School); setShowModal(true) }}
        emptyState={{ icon: Building2, title: 'No schools found', description: 'Add your first school to get started.' }}
      />
      <AddEditSchoolModal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        school={editingSchool}
        onSave={handleSave}
      />
    </div>
  )
}
