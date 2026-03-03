import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { Providers } from '@/components/Providers'
import { ServiceWorkerRegister } from '@/components/ServiceWorkerRegister'

// display:'swap' prevents invisible text during font load (FOIT → FOUT)
// preload:true (default) injects <link rel="preload"> for the font file
const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-inter',
})

export const metadata: Metadata = {
  title: 'Cadence - Timetable Optimization Platform',
  description: 'AI-powered timetable optimization for educational institutions',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        {/* DNS prefetch for API servers — resolves DNS before the first fetch */}
        <link rel="dns-prefetch" href="//localhost:8000" />
        <link rel="dns-prefetch" href="//localhost:8001" />
        {/* Preconnect cuts TCP + TLS handshake time for the Django API */}
        <link rel="preconnect" href="http://localhost:8000" crossOrigin="anonymous" />
      </head>
      <body className={inter.className} suppressHydrationWarning>
        <Providers>{children}</Providers>
        {/* Progressive enhancement: cache static assets on repeat visits */}
        <ServiceWorkerRegister />
      </body>
    </html>
  )
}
