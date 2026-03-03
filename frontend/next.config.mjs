import path from 'path'
import { fileURLToPath } from 'url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',

  // ─── Performance: enable gzip/brotli at Next.js edge ───────────────────────
  compress: true,

  // ─── Security: remove the X-Powered-By: Next.js header ────────────────────
  poweredByHeader: false,

  // ─── React Strict Mode: catches side-effects & double-renders early ────────
  reactStrictMode: true,

  typescript: {
    ignoreBuildErrors: true,
  },
  eslint: {
    ignoreDuringBuilds: true,
  },
  experimental: {
    typedRoutes: false,
    // Optimise CSS delivery: inline critical CSS, defer non-critical
    optimizeCss: false, // set to true if critters package is installed
  },

  // ─── Image optimisation: serve modern formats (avif → webp → original) ─────
  images: {
    formats: ['image/avif', 'image/webp'],
    minimumCacheTTL: 3600, // cache optimised images for 1 hour on the edge
    deviceSizes: [640, 750, 828, 1080, 1200, 1920],
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
  },

  // ─── HTTP headers: long-lived immutable cache for fingerprinted assets ──────
  async headers() {
    return [
      {
        // /_next/static/ files have content hashes in filenames → safe to cache forever
        source: '/_next/static/:path*',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=31536000, immutable',
          },
        ],
      },
      {
        // Public folder assets (fonts, icons, images)
        source: '/fonts/:path*',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=31536000, immutable',
          },
        ],
      },
      {
        // Service worker — must NOT be cached so updates are picked up immediately
        source: '/sw.js',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=0, must-revalidate',
          },
          {
            key: 'Service-Worker-Allowed',
            value: '/',
          },
        ],
      },
      {
        // Security headers for all pages
        source: '/(.*)',
        headers: [
          { key: 'X-Content-Type-Options', value: 'nosniff' },
          { key: 'X-DNS-Prefetch-Control', value: 'on' },
          { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },
        ],
      },
    ]
  },

  // ─── Webpack: production bundle optimisations ───────────────────────────────
  webpack: (config, { dev, isServer }) => {
    // Path alias – keep existing behaviour
    config.resolve.alias = {
      ...config.resolve.alias,
      '@': path.resolve(__dirname, 'src'),
    }

    if (!dev && !isServer) {
      // Enable module ID determinism for better long-term caching
      config.optimization.moduleIds = 'deterministic'
      // Merge small chunks — reduces HTTP requests without ballooning bundle size
      config.optimization.mergeDuplicateChunks = true
      // Keep runtime chunk separate so app chunks can be cached independently
      config.optimization.runtimeChunk = 'single'
    }

    return config
  },

  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/api/:path*',
      },
    ]
  },
}

export default nextConfig