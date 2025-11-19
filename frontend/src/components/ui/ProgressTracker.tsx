/**
 * WebSocket Progress Tracker Component
 * Real-time progress updates for timetable generation
 */

'use client'

import { useEffect, useState, useRef } from 'react'
import { ProgressTracker } from '@/lib/api/timetable'
import type { ProgressMessage } from '@/types/timetable'

interface ProgressTrackerProps {
  jobId: string
  onComplete?: (message: ProgressMessage) => void
  onError?: (error: string) => void
  className?: string
}

export default function TimetableProgressTracker({
  jobId,
  onComplete,
  onError,
  className = '',
}: ProgressTrackerProps) {
  const [progress, setProgress] = useState<ProgressMessage | null>(null)
  const [isConnected, setIsConnected] = useState(false)
  const trackerRef = useRef<ProgressTracker | null>(null)

  useEffect(() => {
    // Initialize WebSocket connection
    trackerRef.current = new ProgressTracker(jobId, {
      onProgress: message => {
        setProgress(message)
        setIsConnected(true)
      },
      onComplete: message => {
        setProgress(message)
        setIsConnected(false)
        onComplete?.(message)
      },
      onError: error => {
        console.error('Progress tracking error:', error)
        setIsConnected(false)
        onError?.(error)
      },
    })

    trackerRef.current.connect()

    // Cleanup on unmount
    return () => {
      trackerRef.current?.disconnect()
    }
  }, [jobId, onComplete, onError])

  if (!progress) {
    return (
      <div className={`card ${className}`}>
        <div className="flex items-center gap-3">
          <div className="loading-spinner w-5 h-5"></div>
          <span className="text-sm text-[#6B6B6B] dark:text-[#B3B3B3]">
            Connecting to generation server...
          </span>
        </div>
      </div>
    )
  }

  const getPhaseDisplay = (phase: string): string => {
    const phaseMap: Record<string, string> = {
      initializing: 'Initializing',
      clustering: 'Clustering Batches',
      optimization: 'Optimizing Timetable',
      conflict_resolution: 'Resolving Conflicts',
      completed: 'Completed',
      failed: 'Failed',
    }
    return phaseMap[phase] || phase
  }

  const getPhaseIcon = (phase: string): string => {
    const iconMap: Record<string, string> = {
      initializing: '⚙️',
      clustering: '🔄',
      optimization: '🧠',
      conflict_resolution: '🔧',
      completed: '✅',
      failed: '❌',
    }
    return iconMap[phase] || '📊'
  }

  const formatETA = (seconds?: number): string => {
    if (!seconds) return 'Calculating...'

    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = Math.floor(seconds % 60)

    if (minutes > 0) {
      return `${minutes}m ${remainingSeconds}s`
    }
    return `${remainingSeconds}s`
  }

  const getStatusColor = (status: string): string => {
    switch (status) {
      case 'completed':
        return 'bg-[#4CAF50]'
      case 'failed':
        return 'bg-[#F44336]'
      case 'running':
        return 'bg-[#2196F3]'
      default:
        return 'bg-[#FF9800]'
    }
  }

  return (
    <div className={`card ${className}`}>
      <div className="space-y-4">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div
              className={`w-3 h-3 rounded-full ${
                isConnected ? 'bg-[#4CAF50] animate-pulse' : 'bg-[#E0E0E0]'
              }`}
            />
            <span className="text-sm font-medium text-[#2C2C2C] dark:text-[#FFFFFF]">
              {isConnected ? 'Live Updates' : 'Disconnected'}
            </span>
          </div>

          <span className="text-xs text-[#6B6B6B] dark:text-[#B3B3B3]">Job ID: {jobId}</span>
        </div>

        {/* Phase Display */}
        <div className="flex items-center gap-3">
          <span className="text-2xl">{getPhaseIcon(progress.phase)}</span>
          <div className="flex-1">
            <div className="text-sm font-medium text-[#2C2C2C] dark:text-[#FFFFFF]">
              {getPhaseDisplay(progress.phase)}
            </div>
            <div className="text-xs text-[#6B6B6B] dark:text-[#B3B3B3] mt-1">
              {progress.current_step || progress.message}
            </div>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span className="text-[#6B6B6B] dark:text-[#B3B3B3]">Progress</span>
            <span className="font-medium text-[#2C2C2C] dark:text-[#FFFFFF]">
              {progress.progress}%
            </span>
          </div>

          <div className="relative w-full h-2 bg-[#E0E0E0] dark:bg-[#404040] rounded-full overflow-hidden">
            <div
              className={`absolute top-0 left-0 h-full transition-all duration-500 ${getStatusColor(
                progress.status
              )}`}
              style={{ width: `${progress.progress}%` }}
            />
          </div>
        </div>

        {/* ETA Display */}
        {progress.eta_seconds !== undefined && progress.status === 'running' && (
          <div className="flex items-center justify-between p-3 bg-[#2196F3]/5 dark:bg-[#2196F3]/10 rounded">
            <div className="flex items-center gap-2">
              <svg
                className="w-4 h-4 text-[#2196F3]"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              <span className="text-sm font-medium text-[#2196F3]">Estimated Time Remaining</span>
            </div>
            <span className="text-sm font-bold text-[#2196F3]">
              {formatETA(progress.eta_seconds)}
            </span>
          </div>
        )}

        {/* Status Messages */}
        {progress.status === 'completed' && (
          <div className="flex items-center gap-2 p-3 bg-[#4CAF50]/10 dark:bg-[#4CAF50]/20 rounded">
            <svg
              className="w-5 h-5 text-[#4CAF50]"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <span className="text-sm font-medium text-[#4CAF50]">
              Generation completed successfully!
            </span>
          </div>
        )}

        {progress.status === 'failed' && (
          <div className="flex items-center gap-2 p-3 bg-[#F44336]/10 dark:bg-[#F44336]/20 rounded">
            <svg
              className="w-5 h-5 text-[#F44336]"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <span className="text-sm font-medium text-[#F44336]">
              {progress.message || 'Generation failed'}
            </span>
          </div>
        )}
      </div>
    </div>
  )
}
