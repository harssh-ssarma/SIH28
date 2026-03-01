'use client'

import { useState, useEffect, useCallback } from 'react'
import apiClient from '@/lib/api'
import AddEditUserModal from './components/AddEditUserModal'
import UserDetailPanel from './components/UserDetailPanel'
import { useToast } from '@/components/Toast'
import PageHeader from '@/components/shared/PageHeader'
import DataTable, { Column } from '@/components/shared/DataTable'
import { UserCog } from 'lucide-react'

interface User {
  id: number
  username: string
  first_name: string
  last_name: string
  email: string
  role: string
  department: string
  is_active: boolean
}

interface PaginatedResponse<T> {
  results: T[]
  count: number
}

const COLUMNS: Column<Record<string, unknown>>[] = [
  { key: 'username', header: 'Username', width: '140px' },
  {
    key: 'first_name',
    header: 'Name',
    render: (_, row) => `${row['first_name'] || ''} ${row['last_name'] || ''}`.trim() || '—',
  },
  { key: 'email', header: 'Email' },
  { key: 'role', header: 'Role', width: '120px', render: v => <span className="badge badge-neutral">{v as string}</span> },
  { key: 'department', header: 'Department', render: v => (v as string) || '—' },
  {
    key: 'is_active',
    header: 'Status',
    width: '80px',
    render: v => v
      ? <span className="badge badge-success">Active</span>
      : <span className="badge badge-neutral">Inactive</span>,
  },
]

export default function AdminUsersPage() {
  const { showToast } = useToast()
  const [users, setUsers] = useState<User[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [currentPage, setCurrentPage] = useState(1)
  const [totalCount, setTotalCount] = useState(0)
  const [showModal, setShowModal] = useState(false)
  const [editingUser, setEditingUser] = useState<User | null>(null)
  const [detailUser, setDetailUser] = useState<User | null>(null)

  const fetchUsers = useCallback(async (page = currentPage, search = searchTerm) => {
    setIsLoading(true)
    try {
      const params = new URLSearchParams({ role: 'ADMIN', page: String(page), page_size: '100', ordering: 'username' })
      if (search) params.set('search', search)
      const response = await apiClient.request<PaginatedResponse<User>>(`/users/?${params}`)
      if (response.error) showToast('error', response.error)
      else if (response.data) {
        setUsers(response.data.results || [])
        setTotalCount(response.data.count ?? 0)
      }
    } catch { showToast('error', 'Failed to fetch admin users') }
    finally { setIsLoading(false) }
  }, [currentPage, searchTerm]) // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    const t = setTimeout(() => { setCurrentPage(1); fetchUsers(1, searchTerm) }, 400)
    return () => clearTimeout(t)
  }, [searchTerm]) // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => { fetchUsers() }, [currentPage]) // eslint-disable-line react-hooks/exhaustive-deps

  const handleSaveUser = async (userData: any) => {
    if (userData.role !== 'admin') { showToast('error', 'Only admin users can be created here'); return }
    const response = editingUser
      ? await apiClient.updateUser(String(editingUser.id), userData)
      : await apiClient.createUser(userData)
    if (response.error) { showToast('error', response.error); return }
    showToast('success', editingUser ? 'Admin updated' : 'Admin created')
    setShowModal(false)
    setEditingUser(null)
    setTimeout(() => fetchUsers(), 500)
  }

  const handleBulkDelete = async (ids: string[]) => {
    for (const id of ids) {
      const res = await apiClient.deleteUser(id)
      if (res.error) { showToast('error', res.error); break }
    }
    showToast('success', `${ids.length} user${ids.length > 1 ? 's' : ''} deleted`)
    setTimeout(() => fetchUsers(), 500)
  }

  return (
    <div className="space-y-4">
      <PageHeader
        title="Admin Users"
        count={totalCount}
        loading={isLoading}
        primaryAction={{ label: 'Add Admin User', onClick: () => { setEditingUser(null); setShowModal(true) } }}
      />
      <DataTable
        columns={COLUMNS}
        data={users as unknown as Record<string, unknown>[]}
        loading={isLoading}
        totalCount={totalCount}
        page={currentPage}
        pageSize={100}
        onPageChange={setCurrentPage}
        selectable
        avatarColumn={row => {
          const u = row as unknown as User
          return (`${u.first_name || ''} ${u.last_name || ''}`).trim() || u.username
        }}
        onDelete={handleBulkDelete}
        onEdit={row => { setEditingUser(row as unknown as User); setShowModal(true) }}
        onRowClick={row => setDetailUser(row as unknown as User)}
        emptyState={{ icon: UserCog, title: 'No admin users found', description: 'Create an admin account to get started.' }}
      />
      <AddEditUserModal
        isOpen={showModal}
        onClose={() => { setShowModal(false); setEditingUser(null) }}
        user={editingUser}
        onSave={handleSaveUser}
      />
      {detailUser && (
        <UserDetailPanel
          user={detailUser}
          onClose={() => setDetailUser(null)}
          onEdit={() => { setEditingUser(detailUser); setDetailUser(null); setShowModal(true) }}
          onDelete={() => { handleBulkDelete([String(detailUser.id)]); setDetailUser(null) }}
        />
      )}
    </div>
  )
}