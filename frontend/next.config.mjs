import path from 'path'
import { fileURLToPath } from 'url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

const isProd = process.env.NODE_ENV === 'production'

// ╔══════════════════════════════════════════════════════════════════════════════╗
// ║                     DEV vs PRODUCTION CHEAT-SHEET                          ║
// ║                                                                              ║
// ║  Everything in this file is safe to leave as-is during development.         ║
// ║  The conditional logic (isProd) handles the dangerous settings              ║
// ║  automatically. However, if you ever need to manually switch, here is       ║
// ║  exactly what each prod-only setting does and how to revert it:             ║
// ║                                                                              ║
// ║  1. output: 'standalone'  [currently: only active when NODE_ENV=production] ║
// ║     ► WHAT IT DOES: bundles the app + only the required node_modules into   ║
// ║       a self-contained .next/standalone folder for Docker deployments.      ║
// ║     ► WHY IT BREAKS DEV: disables the webpack build worker → HMR (hot       ║
// ║       module replacement) stops working → browser serves stale JS.          ║
// ║     ► TO REVERT FOR DEV: already handled by isProd. If you hardcode it,     ║
// ║       remove `output: 'standalone'` entirely or comment it out.             ║
// ║                                                                              ║
// ║  2. webpackBuildWorker: true  [always on]                                   ║
// ║     ► WHAT IT DOES: forces the webpack worker on even when a custom         ║
// ║       webpack() function is present. Required for HMR in dev.               ║
// ║     ► KEEP THIS in dev. Only remove it if you see worker-related crashes.   ║
// ║                                                                              ║
// ║  3. Cache-Control headers  [always sent, even in dev]                       ║
// ║     ► WHAT THEY DO: tell browsers to cache /_next/static/* for 1 year.      ║
// ║       Safe in prod (filenames are content-hashed). In dev Next.js           ║
// ║       ignores these headers for its own HMR WebSocket traffic, so they      ║
// ║       don't cause stale-cache issues during development.                    ║
// ║     ► TO REVERT FOR DEV: not needed, but you can wrap the static header     ║
// ║       entry in `if (isProd)` inside the headers() function if you ever      ║
// ║       want the browser Network tab to show no caching during debugging.     ║
// ║                                                                              ║
// ║  4. webpack optimizations (moduleIds, mergeDuplicateChunks, runtimeChunk)   ║
// ║     ► Already gated behind `if (!dev && !isServer)` — safe in dev as-is.   ║
// ║                                                                              ║
// ║  5. images.minimumCacheTTL: 3600                                            ║
// ║     ► Only affects the Next.js Image Optimisation API cache on the server.  ║
// ║       Has no effect on browser HMR. Safe in dev.                            ║
// ╚══════════════════════════════════════════════════════════════════════════════╝

/** @type {import('next').NextConfig} */
const nextConfig = {
  // [PROD ONLY] — standalone bundles app for Docker. Breaks HMR in dev.
  // Handled automatically by isProd. Do NOT hardcode `output: 'standalone'`.
  ...(isProd ? { output: 'standalone' } : {}),

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
    // [DEV CRITICAL] — forces webpack build worker on even with a custom webpack()
    // function. Without this, HMR breaks and the browser serves stale bundles.
    // Keep this ON in dev. Only remove if you see worker crash errors in the terminal.
    webpackBuildWorker: true,
    // Optimise CSS delivery: inline critical CSS, defer non-critical
    optimizeCss: false, // set to true if critters package is installed
  },

  // ─── Image optimisation: serve modern formats (avif → webp → original) ─────
  images: {
    formats: ['image/avif', 'image/webp'],
    minimumCacheTTL: 3600, // cache optimised images for 1 hour on the edge — safe in dev
    deviceSizes: [640, 750, 828, 1080, 1200, 1920],
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
  },

  // ─── HTTP headers ───────────────────────────────────────────────────────────
  // [NOTE FOR DEV] The long Cache-Control on /_next/static/* is safe in dev
  // because Next.js HMR uses a WebSocket, not HTTP cache. You won't see stale
  // pages. If you want zero caching visible in DevTools, wrap the first entry
  // in `...(isProd ? [{ source: '/_next/static/:path*', ... }] : [])`.
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

  // ─── Webpack ────────────────────────────────────────────────────────────────
  // [NOTE FOR DEV] The optimization block inside is already gated by
  // `if (!dev && !isServer)` so it never runs during `npm run dev`.
  // The @alias block always runs — that is required in both dev and prod.
  webpack: (config, { dev, isServer }) => {
    // Path alias – required in both dev and prod
    config.resolve.alias = {
      ...config.resolve.alias,
      '@': path.resolve(__dirname, 'src'),
    }

    if (!dev && !isServer) {
      // [PROD ONLY] — these three lines only execute during `next build`
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