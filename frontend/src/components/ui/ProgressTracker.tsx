'use client'

import { useState, useEffect, useRef } from 'react'

interface ProgressTrackerProps {
  jobId: string
  onComplete: (timetableId: string) => void
  onCancel?: () => void
}

export default function TimetableProgressTracker({ jobId, onComplete, onCancel }: ProgressTrackerProps) {
  const [progress, setProgress] = useState(0)
  const [status, setStatus] = useState('queued')
  const [phase, setPhase] = useState('Initializing...')
  const [eta, setEta] = useState<number | null>(null)
  const [cancelling, setCancelling] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null)

  const API_BASE = process.env.NEXT_PUBLIC_DJANGO_API_URL || 'http://localhost:8000/api'
  const reconnectAttemptsRef = useRef(0)
  const MAX_RECONNECT_ATTEMPTS = 3

  useEffect(() => {
    let pollInterval: NodeJS.Timeout | null = null

    const pollProgress = async () => {
      try {
        const res = await fetch(`${API_BASE}/progress/${jobId}/`, {
          credentials: 'include',
        })

        if (res.ok) {
          const data = await res.json()
          setProgress(data.progress || 0)
          setStatus(data.status || 'running')
          setPhase(data.stage || data.message || 'Processing...')

          if (data.status === 'completed') {
            if (pollInterval) clearInterval(pollInterval)
            onComplete(jobId)
          } else if (data.status === 'failed') {
            if (pollInterval) clearInterval(pollInterval)
            setError(data.message || data.error || 'Generation failed')
          } else if (data.status === 'cancelled') {
            if (pollInterval) clearInterval(pollInterval)
            setPhase('Generation cancelled')
          }
        }
      } catch (err) {
        console.error('Failed to poll progress:', err)
      }
    }

    // Use HTTP polling only (WebSocket not working)
    pollInterval = setInterval(pollProgress, 2000)
    pollProgress()

    return () => {
      if (pollInterval) clearInterval(pollInterval)
    }
  }, [jobId, onComplete])

  const handleCancel = async () => {
    if (status === 'completed' || status === 'failed' || status === 'cancelled') {
      alert(`Cannot cancel ${status} process`)
      return
    }

    if (!confirm('Are you sure you want to cancel this generation? This cannot be undone.')) {
      return
    }

    setCancelling(true)
    try {
      const res = await fetch(`${API_BASE}/generation-jobs/${jobId}/cancel/`, {
        method: 'POST',
        credentials: 'include',
      })

      if (res.ok) {
        setStatus('cancelled')
        setPhase('Generation cancelled by user')
        if (onCancel) onCancel()
      } else {
        const data = await res.json()
        alert(`Failed to cancel: ${data.error || 'Unknown error'}`)
      }
    } catch (err) {
      console.error('Failed to cancel generation:', err)
      alert('Failed to cancel generation')
    } finally {
      setCancelling(false)
    }
  }

  return (
    <div className="card max-w-2xl mx-auto">
      <div className="p-6 space-y-6">
        {error ? (
          <div className="text-center space-y-4">
            <div className="text-red-600 text-6xl">⚠️</div>
            <h3 className="text-xl font-semibold text-red-600">Generation Failed</h3>
            <p className="text-sm text-gray-700 bg-red-50 p-4 rounded border border-red-200">{error}</p>
            <a
              href="/admin/timetables"
              className="inline-block px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              Back to Timetables
            </a>
          </div>
        ) : (
          <>
            <div className="text-center">
              <h3 className="text-xl font-semibold mb-2">Generating Timetable</h3>
              <p className="text-sm text-gray-600">{phase}</p>
            </div>

        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="font-medium">{status}</span>
            <span className="text-gray-600">{progress}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
            <div
              className="bg-blue-600 h-full transition-all duration-500 ease-out"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        {eta && (
          <p className="text-center text-sm text-gray-500">
            Estimated time remaining: {Math.ceil(eta / 60)} minutes
          </p>
        )}

        <div className="flex justify-center gap-4">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
        </div>

            <div className="flex justify-center gap-4">
              <a
                href="/admin/timetables"
                className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
              >
                Back to Timetables
              </a>
              
              {status !== 'completed' && status !== 'failed' && status !== 'cancelled' && (
                <button
                  onClick={handleCancel}
                  disabled={cancelling}
                  className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {cancelling ? 'Cancelling...' : 'Cancel Generation'}
                </button>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  )
}
