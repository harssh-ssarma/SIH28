'use client'

import { useEffect, useState } from 'react'
import { AppShellSkeleton } from '@/components/shell/AppShellSkeleton'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/context/AuthContext'
import AppShell from '@/components/shell/AppShell'

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const { user, isLoading } = useAuth()
  const router = useRouter()
  const [mounted, setMounted] = useState(false)

  useEffect(() => { setMounted(true) }, [])

  useEffect(() => {
    if (!isLoading) {
      if (!user) {
        router.push('/login')
      } else {
        const role = user.role.toLowerCase()
        if (role !== 'admin' && role !== 'org_admin' && role !== 'super_admin') {
          router.push('/unauthorized')
        }
      }
    }
  }, [user, isLoading, router])

  if (!mounted || isLoading) {
    return <AppShellSkeleton />
  }

  if (!user) {
    return null
  }

  const role = user.role.toLowerCase()
  if (role !== 'admin' && role !== 'org_admin' && role !== 'super_admin') {
    return null
  }

  return <AppShell>{children}</AppShell>
}
