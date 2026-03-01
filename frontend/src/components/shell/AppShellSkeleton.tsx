/**
 * AppShellSkeleton
 * ─────────────────────────────────────────────────────────────────────────────
 * Renders a shimmer placeholder that matches the exact visual structure of
 * AppShell: header bar + sidebar + content card.
 *
 * Used during auth-guard checks in layout files so the screen never flashes a
 * blank page or an out-of-context spinning indicator.
 */

const Shimmer = ({ className = '', style }: { className?: string; style?: React.CSSProperties }) => (
  <div className={`animate-pulse rounded-md bg-gray-200 dark:bg-[#333537] ${className}`} style={style} />
)

export function AppShellSkeleton() {
  return (
    <div className="min-h-screen bg-[#f9f9f9] dark:bg-[#212121] flex">
      {/* ── Sidebar ──────────────────────────────────────────────────────── */}
      <aside className="hidden md:flex flex-col w-[256px] shrink-0 min-h-screen p-3 gap-3">
        {/* Logo row */}
        <div className="flex items-center gap-3 px-2 py-3">
          <Shimmer className="w-9 h-9 rounded-xl shrink-0" />
          <Shimmer className="h-5 w-28" />
        </div>

        {/* Nav items */}
        <div className="flex flex-col gap-1 mt-1">
          {Array.from({ length: 7 }).map((_, i) => (
            <div key={i} className="flex items-center gap-3 px-3 py-2.5">
              <Shimmer className="w-5 h-5 rounded shrink-0" />
              <Shimmer className="h-4 flex-1" style={{ opacity: 1 - i * 0.08 }} />
            </div>
          ))}
        </div>

        {/* Bottom avatar row */}
        <div className="mt-auto flex items-center gap-3 px-3 py-2">
          <Shimmer className="w-8 h-8 rounded-full shrink-0" />
          <div className="flex-1 space-y-1.5">
            <Shimmer className="h-3 w-24" />
            <Shimmer className="h-2.5 w-16" />
          </div>
        </div>
      </aside>

      {/* ── Main column ──────────────────────────────────────────────────── */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <header className="h-16 flex items-center gap-4 px-4 shrink-0">
          {/* Hamburger */}
          <Shimmer className="w-8 h-8 rounded-full shrink-0" />
          {/* Search bar */}
          <Shimmer className="h-10 rounded-full flex-1 max-w-md mx-auto" />
          {/* Right icons */}
          <div className="flex items-center gap-2 ml-auto shrink-0">
            <Shimmer className="w-8 h-8 rounded-full" />
            <Shimmer className="w-8 h-8 rounded-full" />
            <Shimmer className="w-9 h-9 rounded-full" />
          </div>
        </header>

        {/* Content card */}
        <main className="flex-1 mx-2 md:mx-3 mb-2 md:mb-3 rounded-2xl bg-white dark:bg-[#1e1e1e] p-4 md:p-6 space-y-5">
          {/* Breadcrumb / title */}
          <Shimmer className="h-7 w-48" />

          {/* Stat tiles row */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="rounded-xl border border-gray-100 dark:border-[#2e2e2e] p-4 space-y-2">
                <Shimmer className="h-3 w-20" />
                <Shimmer className="h-7 w-12" />
              </div>
            ))}
          </div>

          {/* Content rows */}
          <div className="space-y-3">
            {Array.from({ length: 5 }).map((_, i) => (
              <div key={i} className="flex items-center gap-4 py-2">
                <Shimmer className="w-10 h-10 rounded-lg shrink-0" />
                <div className="flex-1 space-y-1.5">
                  <Shimmer className="h-4 w-1/3" />
                  <Shimmer className="h-3 w-1/2" />
                </div>
                <Shimmer className="h-6 w-16 rounded-full shrink-0" />
              </div>
            ))}
          </div>
        </main>
      </div>
    </div>
  )
}
