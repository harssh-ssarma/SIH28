'use client'

import { useState, useEffect, useCallback } from 'react'
import apiClient from '@/lib/api'
import { useToast } from '@/components/Toast'
import AddEditBuildingModal from './components/AddEditBuildingModal'
import PageHeader from '@/components/shared/PageHeader'
import DataTable, { Column } from '@/components/shared/DataTable'
import { Building2 } from 'lucide-react'

interface Building {
  id: number
  building_id: string
  building_code: string
  building_name: string
  address?: string
  total_floors?: number
}

const COLUMNS: Column<Record<string, unknown>>[] = [
  { key: 'building_code', header: 'Code', width: '120px' },
  { key: 'building_name', header: 'Name' },
  { key: 'address', header: 'Address', render: v => (v as string) || '—' },
  { key: 'total_floors', header: 'Floors', width: '80px', render: v => (v as number) || '—' },
]

export default function BuildingsPage() {
  const { showToast } = useToast()
  const [buildings, setBuildings] = useState<Building[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [showModal, setShowModal] = useState(false)
  const [editingBuilding, setEditingBuilding] = useState<Building | null>(null)
  const [currentPage, setCurrentPage] = useState(1)
  const [totalCount, setTotalCount] = useState(0)
  const itemsPerPage = 25

  const fetchBuildings = useCallback(async (page = currentPage) => {
    setIsLoading(true)
    try {
      const response = await apiClient.getBuildings(page, itemsPerPage, searchTerm)
      if (response.error) showToast('error', response.error)
      else if (response.data) {
        setBuildings(response.data.results || response.data)
        setTotalCount(response.data.count || 0)
      }
    } catch { showToast('error', 'Failed to load buildings') }
    finally { setIsLoading(false) }
  }, [currentPage, itemsPerPage, searchTerm]) // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    const t = setTimeout(() => { setCurrentPage(1); fetchBuildings(1) }, 400)
    return () => clearTimeout(t)
  }, [searchTerm]) // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => { fetchBuildings() }, [currentPage]) // eslint-disable-line react-hooks/exhaustive-deps

  const handleSave = async (data: any) => {
    const res = editingBuilding
      ? await apiClient.updateBuilding(String(editingBuilding.id), data)
      : await apiClient.createBuilding(data)
    if (res.error) { showToast('error', res.error); return }
    showToast('success', editingBuilding ? 'Building updated' : 'Building created')
    setShowModal(false)
    await fetchBuildings()
  }

  const handleBulkDelete = async (ids: string[]) => {
    const results = await Promise.all(ids.map(id => apiClient.deleteBuilding(id)))
    const firstError = results.find(r => r.error)
    if (firstError) { showToast('error', firstError.error!); return }
    showToast('success', `${ids.length} building${ids.length > 1 ? 's' : ''} deleted`)
    await fetchBuildings()
  }

  return (
    <div className="space-y-4">
      <PageHeader
        title="Buildings"
        parentLabel="Academic"
        count={totalCount}
        loading={isLoading}
        primaryAction={{ label: 'Add Building', onClick: () => { setEditingBuilding(null); setShowModal(true) } }}
      />
      <DataTable
        columns={COLUMNS}
        data={buildings as unknown as Record<string, unknown>[]}
        loading={isLoading}
        totalCount={totalCount}
        page={currentPage}
        pageSize={itemsPerPage}
        onPageChange={setCurrentPage}
        selectable
        avatarColumn={row => (row as unknown as Building).building_name}
        onDelete={handleBulkDelete}
        onEdit={row => { setEditingBuilding(row as unknown as Building); setShowModal(true) }}
        emptyState={{ icon: Building2, title: 'No buildings found', description: 'Add your first building to get started.' }}
      />
      <AddEditBuildingModal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        building={editingBuilding}
        onSave={handleSave}
      />
    </div>
  )
}