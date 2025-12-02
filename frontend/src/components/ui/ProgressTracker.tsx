'use client'

import { useState, useEffect, useRef } from 'react'
import { useRouter } from 'next/navigation'

interface ProgressTrackerProps {
  jobId: string
  onComplete: (timetableId: string) => void
  onCancel?: () => void
}

interface StageInfo {
  name: string
  icon: string
  range: [number, number]
  color: string
}

const STAGES: StageInfo[] = [
  { name: 'Loading Data', icon: '📚', range: [0, 5], color: '#FF0000' },
  { name: 'Assigning Courses', icon: '🎯', range: [5, 10], color: '#FF4500' },
  { name: 'Scheduling Classes', icon: '📅', range: [10, 60], color: '#FFA500' },
  { name: 'Optimizing Schedule', icon: '⚡', range: [60, 85], color: '#FFD700' },
  { name: 'Resolving Conflicts', icon: '🔧', range: [85, 95], color: '#9ACD32' },
  { name: 'Finalizing Timetable', icon: '✅', range: [95, 100], color: '#00A651' },
]

export default function TimetableProgressTracker({ jobId, onComplete, onCancel }: ProgressTrackerProps) {
  // Load cached state immediately (optimistic UI)
  const getCachedState = () => {
    if (typeof window === 'undefined') return null
    const cached = localStorage.getItem(`progress_${jobId}`)
    return cached ? JSON.parse(cached) : null
  }

  const cachedState = getCachedState()
  const [progress, setProgress] = useState(cachedState?.progress ?? 0)
  const [displayProgress, setDisplayProgress] = useState(cachedState?.progress ?? 0) // Smoothly animated progress
  const [targetProgress, setTargetProgress] = useState(cachedState?.progress ?? 0) // Target from server
  const [status, setStatus] = useState(cachedState?.status || 'loading')
  const [phase, setPhase] = useState(cachedState?.phase || 'Initializing...')
  const [timeRemaining, setTimeRemaining] = useState<number | null>(cachedState?.timeRemaining ?? null)
  const [cancelling, setCancelling] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [pulseScale, setPulseScale] = useState(1) // For breathing animation of active stage
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const statusRef = useRef(status) // Keep ref for latest status in animation
  const router = useRouter()

  const API_BASE = process.env.NEXT_PUBLIC_DJANGO_API_URL || 'http://localhost:8000/api'
  const reconnectAttemptsRef = useRef(0)
  const MAX_RECONNECT_ATTEMPTS = 3

  // Keep status ref in sync with status state
  useEffect(() => {
    statusRef.current = status
  }, [status])

  // Breathing animation for active stage icon - smooth zoom in/out effect
  useEffect(() => {
    if (status !== 'running' && status !== 'initializing') {
      setPulseScale(1)
      return
    }

    let increasing = true
    const pulseInterval = setInterval(() => {
      setPulseScale((prev: number) => {
        if (increasing) {
          if (prev >= 1.15) {
            increasing = false
            return prev - 0.01
          }
          return prev + 0.01
        } else {
          if (prev <= 0.95) {
            increasing = true
            return prev + 0.01
          }
          return prev - 0.01
        }
      })
    }, 50) // Update every 50ms for smooth 20fps breathing effect

    return () => clearInterval(pulseInterval)
  }, [status])

  // Smooth progress animation - updates display progress gradually like Google/TensorFlow
  // Runs continuously without restarting, never stops during normal operation
  useEffect(() => {
    const animationInterval = setInterval(() => {
      setDisplayProgress((prev: number) => {
        // Stop animation only for terminal states (use ref to get latest status)
        const currentStatus = statusRef.current
        if (currentStatus === 'completed' || currentStatus === 'failed' || currentStatus === 'cancelled') {
          return targetProgress // Snap to final value
        }
        
        const diff = targetProgress - prev
        
        // If there's a mismatch, smoothly transition with adaptive speed
        if (Math.abs(diff) > 0.05) {
          // Behind server: Speed up (accelerate) to catch up
          if (diff > 0) {
            let speed: number
            
            if (diff > 10) {
              // Large gap (>10%) - move at 2% per update for smooth transition
              speed = 2
            } else if (diff > 5) {
              // Medium gap (5-10%) - move at 1% per update
              speed = 1
            } else if (diff > 1) {
              // Small gap (1-5%) - move at 0.5% per update
              speed = 0.5
            } else {
              // Very close (<1%) - move at 0.2% per update
              speed = 0.2
            }
            
            return Math.min(prev + speed, targetProgress)
          } else {
            // Ahead of server: Slow down (reduce speed) by moving forward very slowly
            // This allows server to catch up without going backward
            // Only do minimal increments (1% per 2 seconds)
            return prev + 0.05
          }
        }
        
        // If we're at target and still running, add tiny incremental progress
        // This creates the illusion of continuous progress even without server updates
        if (prev < 99 && (currentStatus === 'running' || currentStatus === 'initializing' || currentStatus === 'loading') && diff >= 0 && diff < 0.1) {
          // Very slow increment (0.05% per 100ms = 0.5% per second max)
          // This prevents it from reaching 100% before actual completion
          const maxIncrease = Math.min(0.05, (100 - prev) * 0.001)
          return Math.min(prev + maxIncrease, targetProgress + 2, 99)
        }
        
        return prev
      })
    }, 100) // Update every 100ms for smooth animation

    return () => clearInterval(animationInterval)
  }, [targetProgress]) // Only restart when targetProgress changes from server

  useEffect(() => {
    let pollInterval: NodeJS.Timeout | null = null
    let retryCount = 0
    const MAX_RETRIES = 5

    const pollProgress = async () => {
      try {
        const res = await fetch(`${API_BASE}/progress/${jobId}/`, {
          credentials: 'include',
        })

        if (res.ok) {
          retryCount = 0 // Reset retry count on success
          const data = await res.json()
          const newProgress = data.progress || 0
          const newStatus = data.status || 'running'
          const newPhase = data.stage || data.message || 'Processing...'
          const newTimeRemaining = data.time_remaining_seconds || null

          setProgress(newProgress)
          setTargetProgress(newProgress) // Set target for smooth animation
          setStatus(newStatus)
          setPhase(newPhase)
          setTimeRemaining(newTimeRemaining)

          // Cache state for instant load on refresh (enterprise pattern)
          if (typeof window !== 'undefined') {
            localStorage.setItem(`progress_${jobId}`, JSON.stringify({
              progress: newProgress,
              status: newStatus,
              phase: newPhase,
              timeRemaining: newTimeRemaining
            }))
          }

          if (data.status === 'completed') {
            // Clear cache on completion
            if (typeof window !== 'undefined') {
              localStorage.removeItem(`progress_${jobId}`)
            }
            if (pollInterval) clearInterval(pollInterval)
            onComplete(jobId)
          } else if (data.status === 'failed') {
            if (pollInterval) clearInterval(pollInterval)
            setError(data.message || data.error || 'Generation failed')
            // Clear cache on failure
            if (typeof window !== 'undefined') {
              localStorage.removeItem(`progress_${jobId}`)
            }
          } else if (data.status === 'cancelled') {
            if (pollInterval) clearInterval(pollInterval)
            setPhase('Generation cancelled')
            // Clear cache on cancellation
            if (typeof window !== 'undefined') {
              localStorage.removeItem(`progress_${jobId}`)
            }
          }
        } else if (res.status === 404 && retryCount < MAX_RETRIES) {
          // Job not found yet (race condition) - retry with exponential backoff
          retryCount++
          console.log(`Job not found yet (attempt ${retryCount}/${MAX_RETRIES}), retrying...`)
          setPhase('Initializing generation...')
          setStatus('initializing')
          return // Don't set error yet
        } else if (res.status === 404) {
          // After max retries, show error
          setError('Job not found. Please try again.')
        }
      } catch (err) {
        console.error('Failed to poll progress:', err)
        if (retryCount < MAX_RETRIES) {
          retryCount++
          setPhase('Connecting to server...')
        }
      }
    }

    // Poll immediately, then every 1 second for real-time updates
    pollProgress()
    pollInterval = setInterval(pollProgress, 1000)

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

  // Get current stage based on display progress (smooth animated value)
  const getCurrentStage = () => {
    return STAGES.find(stage => displayProgress >= stage.range[0] && displayProgress < stage.range[1]) || STAGES[STAGES.length - 1]
  }

  const currentStage = getCurrentStage()
  const currentStageIndex = STAGES.findIndex(s => s.name === currentStage.name)

  // Get progress color with smooth gradient transition between stages
  const getProgressColor = (prog: number) => {
    // Find current and next stage
    let currentStageForColor = STAGES[0]
    let nextStageForColor = STAGES[1]
    
    for (let i = 0; i < STAGES.length; i++) {
      if (prog >= STAGES[i].range[0] && prog < STAGES[i].range[1]) {
        currentStageForColor = STAGES[i]
        nextStageForColor = STAGES[i + 1] || STAGES[i]
        break
      }
    }
    
    // If at the last stage
    if (prog >= STAGES[STAGES.length - 1].range[0]) {
      return STAGES[STAGES.length - 1].color
    }
    
    // Calculate interpolation factor within current stage
    const stageStart = currentStageForColor.range[0]
    const stageEnd = currentStageForColor.range[1]
    const stageProgress = (prog - stageStart) / (stageEnd - stageStart)
    
    // Interpolate between current and next stage colors
    const fromColor = hexToRgb(currentStageForColor.color)
    const toColor = hexToRgb(nextStageForColor.color)
    
    const r = Math.round(fromColor.r + (toColor.r - fromColor.r) * stageProgress)
    const g = Math.round(fromColor.g + (toColor.g - fromColor.g) * stageProgress)
    const b = Math.round(fromColor.b + (toColor.b - fromColor.b) * stageProgress)
    
    return `rgb(${r}, ${g}, ${b})`
  }
  
  // Helper function to convert hex to RGB
  const hexToRgb = (hex: string) => {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex)
    return result ? {
      r: parseInt(result[1], 16),
      g: parseInt(result[2], 16),
      b: parseInt(result[3], 16)
    } : { r: 0, g: 0, b: 0 }
  }

  // Format time remaining
  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}m ${secs}s`
  }

  return (
    <div className="w-full max-w-5xl mx-auto p-4">
      <style jsx>{`
        @keyframes shimmer {
          0% { transform: translateX(-100%); }
          100% { transform: translateX(100%); }
        }
        @keyframes pulse-ring {
          0% { transform: scale(1); opacity: 0.5; }
          50% { transform: scale(1.15); opacity: 0.2; }
          100% { transform: scale(1); opacity: 0.5; }
        }
        @keyframes slide-up {
          from { opacity: 0; transform: translateY(15px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `}</style>

      {error ? (
        <div className="card">
          <div className="p-6 sm:p-8 text-center space-y-6 animate-[slide-up_0.4s_ease-out]">
            <div className="w-16 h-16 mx-auto rounded-full bg-red-100 dark:bg-red-900/20 flex items-center justify-center">
              <svg className="w-10 h-10 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
            <div>
              <h3 className="text-xl font-semibold text-[#2C2C2C] dark:text-[#FFFFFF] mb-2">Generation Failed</h3>
              <p className="text-sm text-[#606060] dark:text-[#aaaaaa]">{error}</p>
            </div>
            <button onClick={() => router.push('/admin/timetables')} className="btn-primary">
              Back to Timetables
            </button>
          </div>
        </div>
      ) : (
        <div className="card">
          {/* Header Section */}
          <div className="flex items-center justify-between gap-4 mb-6">
            <div className="flex items-center gap-3">
              <div className="relative">
                <div className="w-12 h-12 rounded-xl bg-[#2196F3]/10 dark:bg-[#2196F3]/20 flex items-center justify-center text-2xl">
                  {currentStage.icon}
                </div>
                
              </div>
              <div>
                <h2 className="text-lg font-semibold text-[#2C2C2C] dark:text-[#FFFFFF]">
                  Generating Timetable
                </h2>
                <p className="text-sm text-[#606060] dark:text-[#aaaaaa]">{currentStage.name}</p>
              </div>
            </div>
            <div className="text-right">
              <div className="text-4xl font-bold text-[#2196F3]">{Math.round(displayProgress)}%</div>
              {timeRemaining !== null && timeRemaining > 0 ? (
                <div className="text-xs text-[#606060] dark:text-[#aaaaaa] font-medium mt-1">
                  {formatTime(timeRemaining)} remaining
                </div>
              ) : progress < 100 && (
                <div className="text-xs text-[#606060] dark:text-[#aaaaaa] font-medium mt-1">
                  Calculating...
                </div>
              )}
            </div>
          </div>

          {/* Progress Bar */}
          <div className="mb-6">
            <div className="relative h-2 bg-[#F5F5F5] dark:bg-[#2C2C2C] rounded-full overflow-hidden">
              <div
                className="h-full rounded-full transition-all duration-100 ease-linear relative"
                style={{
                  width: `${displayProgress}%`,
                  backgroundColor: getProgressColor(displayProgress)
                }}
              >
                <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/40 to-transparent animate-[shimmer_2s_infinite]" />
              </div>
            </div>
          </div>

          {/* Horizontal Stage Timeline */}
          <div className="mb-6">
            <div className="flex items-start justify-between gap-2">
              {STAGES.map((stage, idx) => {
                const isActive = displayProgress >= stage.range[0] && displayProgress < stage.range[1]
                const isCompleted = displayProgress >= stage.range[1]
                
                return (
                  <div key={idx} className="flex flex-col items-center flex-1 relative">
                    {/* Connecting Line */}
                    {idx < STAGES.length - 1 && (
                      <div className="absolute top-5 left-1/2 w-full h-0.5 -z-10 transition-colors duration-300" style={{
                        backgroundColor: isCompleted ? '#00A651' : '#E0E0E0'
                      }} />
                    )}
                    
                    {/* Stage Circle */}
                    <div className="relative mb-2">
                      <div className={`w-10 h-10 rounded-full flex items-center justify-center text-sm font-semibold transition-all duration-100`} style={{
                        backgroundColor: isCompleted ? '#00A651' : isActive ? stage.color : '#E0E0E0',
                        color: isCompleted || isActive ? '#FFFFFF' : '#606060',
                        transform: isActive ? `scale(${pulseScale})` : 'scale(1)',
                        boxShadow: isActive ? '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)' : 'none'
                      }}>
                        {isCompleted ? (
                          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                          </svg>
                        ) : (
                          stage.icon
                        )}
                      </div>
                      {isActive && (
                        <div className="absolute inset-0 rounded-full animate-[pulse-ring_2s_ease-in-out_infinite]" style={{
                          border: `2px solid ${stage.color}`,
                          opacity: 0.6
                        }} />
                      )}
                    </div>
                    
                    {/* Stage Name */}
                    <div className={`text-xs text-center font-medium transition-all ${
                      isActive ? 'text-[#2C2C2C] dark:text-[#FFFFFF]' : 
                      isCompleted ? 'text-[#606060] dark:text-[#aaaaaa]' :
                      'text-[#aaaaaa] dark:text-[#606060]'
                    }`}>
                      {stage.name}
                    </div>
                  </div>
                )
              })}
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex justify-between gap-3 pt-4 border-t border-[#E0E0E0] dark:border-[#2C2C2C]">
            <button
              onClick={() => router.push('/admin/timetables')}
              className="btn-secondary"
            >
              <svg className="w-4 h-4 mr-2 inline" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
              Back
            </button>
            
            {status !== 'completed' && status !== 'failed' && status !== 'cancelled' && (
              <button
                onClick={handleCancel}
                disabled={cancelling}
                className="btn-danger"
              >
                {cancelling ? (
                  <span className="flex items-center gap-2">
                    <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                    </svg>
                    Cancelling...
                  </span>
                ) : (
                  <>
                    <svg className="w-4 h-4 mr-2 inline" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                    Cancel
                  </>
                )}
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
