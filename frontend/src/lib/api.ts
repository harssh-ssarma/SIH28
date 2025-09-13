const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

class ApiClient {
  private baseURL: string
  private token: string | null = null

  constructor(baseURL: string) {
    this.baseURL = baseURL
    if (typeof window !== 'undefined') {
      this.token = localStorage.getItem('access_token')
    }
  }

  setToken(token: string) {
    this.token = token
    if (typeof window !== 'undefined') {
      localStorage.setItem('access_token', token)
    }
  }

  clearToken() {
    this.token = null
    if (typeof window !== 'undefined') {
      localStorage.removeItem('access_token')
    }
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    }

    if (this.token) {
      headers.Authorization = `Bearer ${this.token}`
    }

    const response = await fetch(url, {
      ...options,
      headers,
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    return response.json()
  }

  // Auth endpoints
  async login(username: string, password: string) {
    return this.request<{
      access: string
      refresh: string
      user: any
    }>('/api/v1/auth/login/', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    })
  }

  async getProfile() {
    return this.request<any>('/api/v1/auth/profile/')
  }

  // Users endpoints
  async getUsers() {
    return this.request<any[]>('/api/v1/auth/users/')
  }

  async createUser(userData: any) {
    return this.request<any>('/api/v1/auth/users/', {
      method: 'POST',
      body: JSON.stringify(userData),
    })
  }

  // Courses endpoints
  async getCourses() {
    return this.request<any[]>('/api/v1/courses/')
  }

  async createCourse(courseData: any) {
    return this.request<any>('/api/v1/courses/', {
      method: 'POST',
      body: JSON.stringify(courseData),
    })
  }

  // Classrooms endpoints
  async getClassrooms() {
    return this.request<any[]>('/api/v1/classrooms/')
  }

  async createClassroom(classroomData: any) {
    return this.request<any>('/api/v1/classrooms/', {
      method: 'POST',
      body: JSON.stringify(classroomData),
    })
  }

  // Timetables endpoints
  async getTimetables() {
    return this.request<any[]>('/api/v1/timetables/')
  }

  async generateTimetable(constraints: any) {
    return this.request<any>('/api/v1/timetables/generate/', {
      method: 'POST',
      body: JSON.stringify(constraints),
    })
  }
}

export const apiClient = new ApiClient(API_BASE_URL)