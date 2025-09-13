"use client"

import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { User } from '@/types'

interface AuthContextType {
  user: User | null
  login: (username: string, password: string) => Promise<void>
  logout: () => void
  isLoading: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const savedUser = localStorage.getItem('user')
    if (savedUser) {
      setUser(JSON.parse(savedUser))
    }
    setIsLoading(false)
  }, [])

  const login = async (username: string, password: string) => {
    if (process.env.NEXT_PUBLIC_MOCK_AUTH === 'true') {
      // Mock authentication
      let mockUser: User
      
      if (username.includes('admin')) {
        mockUser = { id: 1, username, email: `${username}@sih28.com`, role: 'admin' }
      } else if (username.includes('staff')) {
        mockUser = { id: 2, username, email: `${username}@sih28.com`, role: 'staff' }
      } else if (username.includes('student')) {
        mockUser = { id: 4, username, email: `${username}@sih28.com`, role: 'student' }
      } else {
        mockUser = { id: 3, username, email: `${username}@sih28.com`, role: 'faculty' }
      }
      
      setUser(mockUser)
      localStorage.setItem('user', JSON.stringify(mockUser))
    } else {
      // Real API call placeholder
      throw new Error('Real authentication not implemented')
    }
  }

  const logout = () => {
    setUser(null)
    localStorage.removeItem('user')
  }

  return (
    <AuthContext.Provider value={{ user, login, logout, isLoading }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}