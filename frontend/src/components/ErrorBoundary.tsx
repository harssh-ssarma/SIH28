'use client'

import React, { Component, ReactNode } from 'react'
import { AlertTriangle, RefreshCw, Home } from 'lucide-react'

interface Props {
  children: ReactNode
  fallback?: ReactNode
}

interface State {
  hasError: boolean
  error: Error | null
  errorInfo: React.ErrorInfo | null
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    }
  }

  static getDerivedStateFromError(error: Error): State {
    return {
      hasError: true,
      error,
      errorInfo: null,
    }
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo)

    this.setState({
      error,
      errorInfo,
    })

    // Send to Sentry or logging service
    if (typeof window !== 'undefined' && (window as any).Sentry) {
      ;(window as any).Sentry.captureException(error, {
        contexts: {
          react: {
            componentStack: errorInfo.componentStack,
          },
        },
      })
    }
  }

  handleReset = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    })
  }

  handleGoHome = () => {
    if (typeof window !== 'undefined') {
      window.history.pushState({}, '', '/')
      window.location.reload()
    }
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback
      }

      return (
        <div className="min-h-screen flex items-center justify-center px-4" style={{ background: 'var(--color-bg-page)' }}>
          <div className="card max-w-md w-full" style={{ padding: '32px' }}>
            <div
              className="flex items-center justify-center w-16 h-16 mx-auto rounded-full mb-4"
              style={{ background: 'var(--color-danger-subtle)' }}
            >
              <AlertTriangle className="w-8 h-8" style={{ color: 'var(--color-danger)' }} />
            </div>

            <h1 className="text-2xl font-bold text-center mb-2" style={{ color: 'var(--color-text-primary)' }}>
              Something went wrong
            </h1>

            <p className="text-center mb-6" style={{ color: 'var(--color-text-secondary)' }}>
              We&apos;re sorry, but something unexpected happened. Please try again.
            </p>

            {process.env.NODE_ENV === 'development' && this.state.error && (
              <div
                className="mb-6 p-4 rounded-lg border"
                style={{ background: 'var(--color-bg-surface-2)', borderColor: 'var(--color-border)' }}
              >
                <p className="text-sm font-semibold mb-2" style={{ color: 'var(--color-text-primary)' }}>Error Details:</p>
                <p className="text-xs font-mono mb-2" style={{ color: 'var(--color-danger-text)' }}>{this.state.error.toString()}</p>
                {this.state.errorInfo && (
                  <details className="text-xs" style={{ color: 'var(--color-text-muted)' }}>
                    <summary className="cursor-pointer hover:underline">
                      Component Stack
                    </summary>
                    <pre
                      className="mt-2 overflow-auto max-h-40 p-2 rounded border"
                      style={{ background: 'var(--color-bg-surface)', borderColor: 'var(--color-border)' }}
                    >
                      {this.state.errorInfo.componentStack}
                    </pre>
                  </details>
                )}
              </div>
            )}

            <div className="flex gap-3">
              <button
                onClick={this.handleReset}
                className="btn-primary flex-1 flex items-center justify-center gap-2"
              >
                <RefreshCw className="w-4 h-4" />
                Try Again
              </button>

              <button
                onClick={this.handleGoHome}
                className="btn-secondary flex-1 flex items-center justify-center gap-2"
              >
                <Home className="w-4 h-4" />
                Go Home
              </button>
            </div>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}

// Hook for functional components to trigger error boundary
export function useErrorHandler() {
  const [, setError] = React.useState()

  return React.useCallback(
    (error: Error) => {
      setError(() => {
        throw error
      })
    },
    [setError]
  )
}
