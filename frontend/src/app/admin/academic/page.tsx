'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'

export default function AcademicPage() {
  const router = useRouter()

  useEffect(() => {
    router.replace('/admin/academic/schools')
  }, [router])

  return null
}
