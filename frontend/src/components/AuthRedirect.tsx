'use client'

/**
 * AuthRedirect - Google-style authentication redirect
 * 
 * PURPOSE:
 *   Redirects already-authenticated users away from auth pages (login/signup)
 *   to their role-based dashboard.
 * 
 * USAGE:
 *   ✅ Use ONLY on authentication pages (/login, /signup, /forgot-password)
 *   ❌ Do NOT use on marketing pages (/, /pricing, /contact, /blog)
 * 
 * BEHAVIOR:
 *   - If user is logged in → redirect to dashboard
 *   - If user is NOT logged in → do nothing (stay on page)
 * 
 * GOOGLE EXAMPLE:
 *   - google.com (marketing) → accessible to everyone, no redirect
 *   - accounts.google.com/signin → redirects if already logged in
 */
import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/context/AuthContext'

export function AuthRedirect() {
  const { user, isLoading } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (isLoading) return          // wait for the auth check to finish
    if (!user) return              // not logged in — stay on this page

    const role = user.role?.toLowerCase() ?? ''
    if (role === 'admin' || role === 'org_admin') {
      router.replace('/admin/dashboard')
    } else if (role === 'faculty') {
      router.replace('/faculty/dashboard')
    } else if (role === 'student') {
      router.replace('/student/dashboard')
    }
  }, [user, isLoading, router])

  return null  // renders nothing
}
