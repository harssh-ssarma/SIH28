"use client"

import { create } from 'zustand'
import { apiClient } from '@/lib/api'

interface User {
  id: number
  username: string
  email: string
  role: 'admin' | 'staff' | 'faculty' | 'student'
  first_name: string
  last_name: string
}

interface AuthState {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (username: string, password: string) => Promise<void>
  logout: () => void
  checkAuth: () => Promise<void>
}

export const useAuth = create<AuthState>((set, get) => ({
  user: null,
  isAuthenticated: false,
  isLoading: true,

  login: async (username: string, password: string) => {
    try {
      const response = await apiClient.login(username, password)
      apiClient.setToken(response.access)
      set({ 
        user: response.user, 
        isAuthenticated: true, 
        isLoading: false 
      })
    } catch (error) {
      console.error('Login failed:', error)
      throw error
    }
  },

  logout: () => {
    apiClient.clearToken()
    set({ 
      user: null, 
      isAuthenticated: false, 
      isLoading: false 
    })
  },

  checkAuth: async () => {
    try {
      const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null
      if (!token) {
        set({ isLoading: false })
        return
      }

      apiClient.setToken(token)
      const user = await apiClient.getProfile()
      set({ 
        user, 
        isAuthenticated: true, 
        isLoading: false 
      })
    } catch (error) {
      console.error('Auth check failed:', error)
      apiClient.clearToken()
      set({ 
        user: null, 
        isAuthenticated: false, 
        isLoading: false 
      })
    }
  },
}))