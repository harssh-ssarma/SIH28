'use client'

import { useState, useEffect, useCallback } from 'react'
import apiClient from '@/lib/api'
import { useToast } from '@/components/Toast'
import AddEditProgramModal from './components/AddEditProgramModal'
import PageHeader from '@/components/shared/PageHeader'
import DataTable, { Column } from '@/components/shared/DataTable'
import { BookOpen } from 'lucide-react'

interface Program {
  id: number
  program_id: string
  program_code: string
  program_name: string
  department?: { id?: number; dept_name: string }
  duration_years?: number
}

const COLUMNS: Column<Record<string, unknown>>[] = [
  { key: 'program_code', header: 'Code', width: '120px' },
  { key: 'program_name', header: 'Name' },
  { key: 'department', header: 'Department', render: v => (v as Program['department'])?.dept_name ?? '—' },
  { key: 'duration_years', header: 'Duration', width: '100px', render: v => v ? `${v} yrs` : '—' },
]

export default function ProgramsPage() {
  const { showToast } = useToast()
  const [programs, setPrograms] = useState<Program[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [showModal, setShowModal] = useState(false)
  const [editingProgram, setEditingProgram] = useState<Program | null>(null)
  const [currentPage, setCurrentPage] = useState(1)
  const [totalCount, setTotalCount] = useState(0)
  const itemsPerPage = 25

  const fetchPrograms = useCallback(async (page = currentPage) => {
    setIsLoading(true)
    try {
      const response = await apiClient.getPrograms(page, itemsPerPage, searchTerm)
      if (response.error) showToast('error', response.error)
      else if (response.data) {
        setPrograms(response.data.results || response.data)
        setTotalCount(response.data.count || 0)
      }
    } catch { showToast('error', 'Failed to load programs') }
    finally { setIsLoading(false) }
  }, [currentPage, itemsPerPage, searchTerm]) // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    const t = setTimeout(() => { setCurrentPage(1); fetchPrograms(1) }, 400)
    return () => clearTimeout(t)
  }, [searchTerm]) // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => { fetchPrograms() }, [currentPage]) // eslint-disable-line react-hooks/exhaustive-deps

  const handleSave = async (data: any) => {
    const res = editingProgram
      ? await apiClient.updateProgram(String(editingProgram.id), data)
      : await apiClient.createProgram(data)
    if (res.error) { showToast('error', res.error); return }
    showToast('success', editingProgram ? 'Program updated' : 'Program created')
    setShowModal(false)
    await fetchPrograms()
  }

  const handleBulkDelete = async (ids: string[]) => {
    const results = await Promise.all(ids.map(id => apiClient.deleteProgram(id)))
    const firstError = results.find(r => r.error)
    if (firstError) { showToast('error', firstError.error!); return }
    showToast('success', `${ids.length} program${ids.length > 1 ? 's' : ''} deleted`)
    await fetchPrograms()
  }

  return (
    <div className="space-y-4">
      <PageHeader
        title="Programs"
        parentLabel="Academic"
        count={totalCount}
        loading={isLoading}
        primaryAction={{ label: 'Add Program', onClick: () => { setEditingProgram(null); setShowModal(true) } }}
      />
      <DataTable
        columns={COLUMNS}
        data={programs as unknown as Record<string, unknown>[]}
        loading={isLoading}
        totalCount={totalCount}
        page={currentPage}
        pageSize={itemsPerPage}
        onPageChange={setCurrentPage}
        selectable
        avatarColumn={row => (row as unknown as Program).program_name}
        onDelete={handleBulkDelete}
        onEdit={row => { setEditingProgram(row as unknown as Program); setShowModal(true) }}
        emptyState={{ icon: BookOpen, title: 'No programs found', description: 'Add your first program to get started.' }}
      />
      <AddEditProgramModal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        program={editingProgram}
        onSave={handleSave}
      />
    </div>
  )
}