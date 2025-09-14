'use client'

import { useRef, useEffect, useState } from 'react'
import { useTheme } from 'next-themes'

interface HeaderProps {
  sidebarOpen: boolean
  sidebarCollapsed: boolean
  setSidebarOpen: (open: boolean) => void
  setSidebarCollapsed: (collapsed: boolean) => void
  setShowSignOutDialog: (show: boolean) => void
}

export default function Header({ 
  sidebarOpen, 
  sidebarCollapsed, 
  setSidebarOpen, 
  setSidebarCollapsed,
  setShowSignOutDialog 
}: HeaderProps) {
  const [showSettings, setShowSettings] = useState(false)
  const { theme, setTheme } = useTheme()
  const settingsRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (settingsRef.current && !settingsRef.current.contains(event.target as Node)) {
        setShowSettings(false)
      }
    }

    if (showSettings) {
      document.addEventListener('mousedown', handleClickOutside)
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [showSettings])

  return (
    <header className="fixed top-0 left-0 right-0 bg-white dark:bg-[#2a2a2a] px-2 sm:px-2 lg:px-3 py-2 sm:py-2 md:py-3 z-50">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 sm:gap-4">
          <button
            onClick={() => {
              if (window.innerWidth >= 768) {
                setSidebarCollapsed(!sidebarCollapsed)
              } else {
                setSidebarOpen(!sidebarOpen)
              }
            }}
            className="w-8 h-8 sm:w-10 sm:h-10 rounded-lg hover:bg-[#f5f5f5] dark:hover:bg-[#3c4043] transition-colors duration-300 flex items-center justify-center text-gray-600 dark:text-gray-300"
            title="Toggle menu"
          >
            <span className="text-sm sm:text-lg">☰</span>
          </button>

          <div className="flex items-center gap-2 sm:gap-3">
            <div className="w-8 h-8 sm:w-10 sm:h-10 bg-[#1a73e8] dark:bg-[#1a73e8] rounded-lg flex items-center justify-center text-white font-bold shadow-sm">
              <span className="text-sm sm:text-base">S</span>
            </div>
            <span className="text-lg sm:text-xl font-semibold text-gray-800 dark:text-gray-200">SIH28</span>
          </div>
        </div>
        
        <div className="flex items-center gap-1 sm:gap-2">
          <button className="w-8 h-8 sm:w-10 sm:h-10 rounded-lg hover:bg-[#f5f5f5] dark:hover:bg-[#3c4043] transition-colors duration-300 flex items-center justify-center text-gray-600 dark:text-gray-300">
            <span className="text-sm sm:text-base">🔔</span>
          </button>
          <button 
            onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
            className="w-8 h-8 sm:w-10 sm:h-10 rounded-lg hover:bg-[#f5f5f5] dark:hover:bg-[#3c4043] transition-colors duration-300 flex items-center justify-center text-gray-600 dark:text-gray-300"
          >
            <span className="text-sm sm:text-base">{theme === 'dark' ? '☀️' : '🌙'}</span>
          </button>
          <div className="relative" ref={settingsRef}>
            <button 
              onClick={() => setShowSettings(!showSettings)}
              className="w-8 h-8 sm:w-10 sm:h-10 rounded-lg hover:bg-[#f5f5f5] dark:hover:bg-[#3c4043] transition-colors duration-300 flex items-center justify-center text-gray-600 dark:text-gray-300"
            >
              <span className="text-sm sm:text-base">⚙️</span>
            </button>
            {showSettings && (
              <div className="absolute right-0 mt-2 w-44 sm:w-48 bg-white dark:bg-[#2a2a2a] border border-gray-200 dark:border-gray-700 rounded-xl shadow-lg z-[9999]">
                <div className="py-1">
                  <button className="w-full px-3 sm:px-4 py-2 text-left text-xs sm:text-sm text-gray-800 dark:text-gray-200 hover:bg-[#f5f5f5] dark:hover:bg-[#3c4043] transition-colors duration-300 flex items-center gap-2 rounded-lg">
                    <span className="text-sm">👤</span> My Profile
                  </button>
                  <button 
                    onClick={() => { setShowSignOutDialog(true); setShowSettings(false); }}
                    className="w-full px-3 sm:px-4 py-2 text-left text-xs sm:text-sm text-red-600 dark:text-red-400 hover:bg-[#f5f5f5] dark:hover:bg-red-900/20 transition-colors duration-300 flex items-center gap-2 rounded-lg"
                  >
                    <span className="text-sm">🚪</span> Sign Out
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  )
}