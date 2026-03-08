/**
 * API Service for Timetable Management
 * Handles all backend API calls for timetable generation, workflow, and approval
 */

import type { GenerationJob } from '@/types/timetable'

const DJANGO_API_BASE = process.env.NEXT_PUBLIC_DJANGO_API_URL || 'http://localhost:8000/api'

// ============================================
// HELPER FUNCTIONS
// ============================================

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: response.statusText }))
    throw new Error(
      error.error || error.detail || `HTTP ${response.status}: ${response.statusText}`
    )
  }
  return response.json()
}

function getAuthHeaders(): HeadersInit {
  // Using HttpOnly cookies for authentication (like rest of the app)
  // No need for Authorization header - cookies sent automatically
  return {
    'Content-Type': 'application/json',
  }
}

function getFetchOptions(): RequestInit {
  return {
    headers: getAuthHeaders(),
    credentials: 'include', // Send HttpOnly cookies with request
  }
}

// ============================================
// GENERATION JOB API
// ============================================

export async function fetchGenerationJobStatus(jobId: string): Promise<GenerationJob> {
  const response = await fetch(`${DJANGO_API_BASE}/generation-jobs/${jobId}/`, getFetchOptions())
  return handleResponse<GenerationJob>(response)
}
