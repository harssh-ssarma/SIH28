"use client"

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/context/AuthContext'

export default function LoginPage() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const { login } = useAuth()
  const router = useRouter()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setIsLoading(true)

    try {
      await login(username, password)
      // Redirect based on role after login
      if (username.includes('admin')) {
        router.push('/admin/dashboard')
      } else if (username.includes('staff')) {
        router.push('/staff/dashboard')
      } else if (username.includes('student')) {
        router.push('/student/dashboard')
      } else {
        router.push('/faculty/dashboard')
      }
    } catch (err) {
      setError('Login failed. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4 sm:p-6 lg:p-8 bg-neutral-50 dark:bg-neutral-900">
      <div className="card w-full max-w-sm sm:max-w-md">
        <div className="text-center mb-6">
          <div className="flex items-center justify-center gap-3 mb-6">
            <div className="w-10 h-10 sm:w-12 sm:h-12 bg-primary-600 rounded-xl flex items-center justify-center text-white font-bold text-lg sm:text-xl shadow-lg">
              S
            </div>
            <h1 className="text-2xl sm:text-3xl font-bold text-neutral-900 dark:text-neutral-100">SIH28</h1>
          </div>
          <h2 className="text-lg sm:text-xl lg:text-2xl font-semibold mb-2 text-neutral-900 dark:text-neutral-100">Welcome Back</h2>
          <p className="text-sm sm:text-base text-neutral-600 dark:text-neutral-400">Sign in to your account</p>
        </div>
        
        <form onSubmit={handleSubmit} className="space-y-4 sm:space-y-6">
          {error && (
            <div className="p-3 bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-200 rounded-lg text-xs sm:text-sm">
              {error}
            </div>
          )}
          
          <div className="form-group">
            <label htmlFor="username" className="form-label text-sm sm:text-base">
              Username
            </label>
            <input 
              id="username" 
              type="text" 
              placeholder="Try: admin, staff, faculty, or student"
              className="input-primary text-sm sm:text-base"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="password" className="form-label text-sm sm:text-base">
              Password
            </label>
            <input 
              id="password" 
              type="password" 
              placeholder="Any password"
              className="input-primary text-sm sm:text-base"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          
          <button 
            type="submit" 
            className="btn-primary w-full py-2.5 sm:py-3 text-sm sm:text-base font-medium"
            disabled={isLoading}
          >
            {isLoading ? 'Signing In...' : 'Sign In'}
          </button>
        </form>
        
        <div className="mt-4 sm:mt-6 pt-4 sm:pt-6 border-t border-neutral-200 dark:border-neutral-700">
          <p className="text-center text-xs sm:text-sm text-neutral-500 dark:text-neutral-400 leading-relaxed">
            Mock Auth: Use "admin", "staff", "faculty", or "student" as username
          </p>
        </div>
      </div>
    </div>
  )
}