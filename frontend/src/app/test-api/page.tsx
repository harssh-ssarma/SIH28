'use client'

import { useState } from 'react'

export default function TestApiPage() {
  const [results, setResults] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  const testEndpoint = async (url: string, name: string) => {
    setLoading(true)
    try {
      const response = await fetch(url)
      const data = await response.json()
      setResults({ name, url, status: response.status, data })
    } catch (error: any) {
      setResults({ name, url, error: error.message })
    } finally {
      setLoading(false)
    }
  }

  const endpoints = [
    { name: 'Debug Data', url: 'http://localhost:8000/api/v1/auth/debug/' },
    { name: 'All Users', url: 'http://localhost:8000/api/v1/auth/users/' },
    { name: 'Faculty', url: 'http://localhost:8000/api/v1/auth/faculty/' },
    { name: 'Students', url: 'http://localhost:8000/api/v1/auth/students/' }
  ]

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-6">API Test Page</h1>
      
      <div className="grid grid-cols-2 gap-4 mb-6">
        {endpoints.map((endpoint) => (
          <button
            key={endpoint.name}
            onClick={() => testEndpoint(endpoint.url, endpoint.name)}
            className="p-4 bg-blue-500 text-white rounded hover:bg-blue-600"
            disabled={loading}
          >
            Test {endpoint.name}
          </button>
        ))}
      </div>

      {loading && <div>Loading...</div>}

      {results && (
        <div className="bg-gray-100 p-4 rounded">
          <h2 className="font-bold mb-2">{results.name} Results:</h2>
          <p><strong>URL:</strong> {results.url}</p>
          {results.status && <p><strong>Status:</strong> {results.status}</p>}
          {results.error && <p className="text-red-500"><strong>Error:</strong> {results.error}</p>}
          {results.data && (
            <pre className="mt-4 bg-white p-4 rounded overflow-auto max-h-96">
              {JSON.stringify(results.data, null, 2)}
            </pre>
          )}
        </div>
      )}
    </div>
  )
}