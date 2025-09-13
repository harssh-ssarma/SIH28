import ProfileDropdown from '../shared/ProfileDropdown'

interface HeaderProps {
  title: string
  onMenuClick: () => void
  user: {
    name: string
    email: string
    role: string
  }
}

export default function Header({ title, onMenuClick, user }: HeaderProps) {
  return (
    <header className="bg-white dark:bg-neutral-800 border-b border-neutral-200 dark:border-neutral-700 px-3 py-2 sm:px-4 sm:py-3 lg:px-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 sm:gap-4 flex-1 min-w-0">
          <button
            onClick={onMenuClick}
            className="btn-ghost p-2 lg:hidden flex-shrink-0 hover:bg-neutral-100 dark:hover:bg-neutral-700"
            title="Toggle menu"
          >
            <span className="text-lg">☰</span>
          </button>
          <h1 className="text-base sm:text-lg lg:text-xl font-semibold text-neutral-900 dark:text-neutral-100 capitalize truncate">
            {title}
          </h1>
        </div>
        
        <div className="flex items-center gap-1 sm:gap-3 flex-shrink-0">
          <button className="btn-ghost p-1.5 sm:p-2 text-sm sm:text-base">
            🔔
          </button>
          <button className="btn-ghost p-1.5 sm:p-2 text-sm sm:text-base">
            🌙
          </button>
          <ProfileDropdown user={user} />
        </div>
      </div>
    </header>
  )
}