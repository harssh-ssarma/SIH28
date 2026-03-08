'use client'

import { useState, useEffect, useCallback } from 'react'
import apiClient from '@/lib/api'
import { useToast } from '@/components/Toast'
import PageHeader from '@/components/shared/PageHeader'
import DataTable, { Column } from '@/components/shared/DataTable'
import { DoorOpen } from 'lucide-react'

interface Room {
  room_id: string
  room_code: string
  room_number: string
  room_name?: string
  seating_capacity: number
  room_type: string
  building_name?: string
  building?: { building_id: string; building_name: string }
  department?: { dept_id: string; dept_name: string }
}

const ROOM_TYPE_LABELS: Record<string, string> = {
  lecture_hall: 'Lecture Hall',
  laboratory: 'Laboratory',
  tutorial_room: 'Tutorial Room',
  seminar_hall: 'Seminar Hall',
}

const COLUMNS: Column<Record<string, unknown>>[] = [
  { key: 'room_code', header: 'Code', width: '100px' },
  { key: 'room_number', header: 'Number', width: '90px' },
  { key: 'room_name', header: 'Name', render: v => (v as string) || '—' },
  {
    key: 'building',
    header: 'Building',
    render: (v, row) =>
      (row['building_name'] as string) ||
      (v as Room['building'])?.building_name ||
      '—',
  },
  { key: 'seating_capacity', header: 'Capacity', width: '90px' },
  {
    key: 'room_type',
    header: 'Type',
    render: v => (
      <span className="badge badge-neutral">
        {ROOM_TYPE_LABELS[v as string] || (v as string)}
      </span>
    ),
  },
]

export default function ClassroomsPage() {
  const { showToast } = useToast()
  const [rooms, setRooms] = useState<Room[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [editingId, setEditingId] = useState<string | null>(null)
  const [formData, setFormData] = useState({
    room_code: '', room_number: '', room_name: '',
    seating_capacity: '', room_type: 'lecture_hall',
    building_id: '', dept_id: '',
  })
  const [currentPage, setCurrentPage] = useState(1)
  const [totalCount, setTotalCount] = useState(0)
  const itemsPerPage = 25

  const fetchRooms = useCallback(async (page = currentPage) => {
    setIsLoading(true)
    try {
      const response = await apiClient.getRooms(page, itemsPerPage, searchTerm)
      if (response.error) showToast('error', response.error)
      else if (response.data) {
        setRooms(response.data.results || response.data)
        setTotalCount(response.data.count || 0)
      }
    } catch { showToast('error', 'Failed to load rooms') }
    finally { setIsLoading(false) }
  }, [currentPage, itemsPerPage, searchTerm]) // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    const t = setTimeout(() => { setCurrentPage(1); fetchRooms(1) }, 400)
    return () => clearTimeout(t)
  }, [searchTerm]) // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => { fetchRooms() }, [currentPage]) // eslint-disable-line react-hooks/exhaustive-deps

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    const response = editingId
      ? await apiClient.updateRoom(editingId, formData)
      : await apiClient.createRoom(formData)
    if (response.error) { showToast('error', 'Failed to save room: ' + response.error); return }
    showToast('success', editingId ? 'Room updated' : 'Room created')
    resetForm()
    await fetchRooms()
  }

  const handleEdit = (row: Record<string, unknown>) => {
    const room = row as unknown as Room
    setFormData({
      room_code: room.room_code, room_number: room.room_number,
      room_name: room.room_name || '', seating_capacity: String(room.seating_capacity),
      room_type: room.room_type, building_id: room.building?.building_id || '',
      dept_id: room.department?.dept_id || '',
    })
    setEditingId(room.room_id)
    setShowForm(true)
  }

  const handleBulkDelete = async (ids: string[]) => {
    const results = await Promise.all(ids.map(id => apiClient.deleteRoom(id)))
    const firstError = results.find(r => r.error)
    if (firstError) { showToast('error', firstError.error!); return }
    showToast('success', `${ids.length} room${ids.length > 1 ? 's' : ''} deleted`)
    await fetchRooms()
  }

  const resetForm = () => {
    setFormData({ room_code: '', room_number: '', room_name: '', seating_capacity: '', room_type: 'lecture_hall', building_id: '', dept_id: '' })
    setEditingId(null)
    setShowForm(false)
  }

  return (
    <div className="space-y-4">
      <PageHeader
        title="Rooms"
        parentLabel="Academic"
        count={totalCount}
        loading={isLoading}
        primaryAction={{ label: 'Add Room', onClick: () => setShowForm(true) }}
      />

      {showForm && (
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">{editingId ? 'Edit' : 'Add'} Room</h3>
          </div>
          <form onSubmit={handleSubmit} className="p-4 sm:p-6 space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">Room Code</label>
                <input type="text" value={formData.room_code} onChange={e => setFormData({ ...formData, room_code: e.target.value })} className="input-primary" placeholder="Room Code" title="Room Code" required />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Room Number</label>
                <input type="text" value={formData.room_number} onChange={e => setFormData({ ...formData, room_number: e.target.value })} className="input-primary" placeholder="Room Number" title="Room Number" required />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Room Name</label>
                <input type="text" value={formData.room_name} onChange={e => setFormData({ ...formData, room_name: e.target.value })} className="input-primary" placeholder="Room Name" title="Room Name" />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Capacity</label>
                <input type="number" value={formData.seating_capacity} onChange={e => setFormData({ ...formData, seating_capacity: e.target.value })} className="input-primary" placeholder="Seating Capacity" title="Seating Capacity" required />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Type</label>
                <select value={formData.room_type} onChange={e => setFormData({ ...formData, room_type: e.target.value })} className="input-primary" title="Room Type">
                  <option value="lecture_hall">Lecture Hall</option>
                  <option value="laboratory">Laboratory</option>
                  <option value="tutorial_room">Tutorial Room</option>
                  <option value="seminar_hall">Seminar Hall</option>
                </select>
              </div>
            </div>
            <div className="flex gap-2">
              <button type="submit" className="btn-primary">{editingId ? 'Update' : 'Create'}</button>
              <button type="button" onClick={resetForm} className="btn-secondary">Cancel</button>
            </div>
          </form>
        </div>
      )}

      <DataTable
        columns={COLUMNS}
        data={rooms as unknown as Record<string, unknown>[]}
        loading={isLoading}
        totalCount={totalCount}
        page={currentPage}
        pageSize={itemsPerPage}
        onPageChange={setCurrentPage}
        selectable
        idField="room_id"
        avatarColumn={row => (row as unknown as Room).room_name || (row as unknown as Room).room_number}
        onDelete={handleBulkDelete}
        onEdit={handleEdit}
        emptyState={{ icon: DoorOpen, title: 'No rooms found', description: 'Add your first room to get started.' }}
      />
    </div>
  )
}