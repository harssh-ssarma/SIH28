// src/components/shared/Avatar.tsx
// Google Contacts–style seeded avatar — proportional letter scaling, Google Sans.

import { useRef, useEffect } from 'react'

const PALETTE = [
  '#d32f2f','#c2185b','#7b1fa2','#512da8',
  '#1976d2','#0288d1','#00796b','#388e3c',
  '#f57c00','#5d4037',
]

function seedColor(name: string): string {
  let hash = 0
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash)
  }
  return PALETTE[Math.abs(hash) % PALETTE.length]
}

function initial(name: string): string {
  return (name.trim()[0] ?? '?').toUpperCase()
}

type AvatarSize = 'sm' | 'md' | 'lg'

/** Named preset → pixel diameter */
const SIZE_PX: Record<AvatarSize, number> = {
  sm: 32,
  md: 36,
  lg: 40,
}

interface AvatarProps {
  name: string
  /** Named preset or any pixel number — letter scales proportionally (×0.42, Google's ratio). */
  size?: AvatarSize | number
  imageUrl?: string
  className?: string
}

export default function Avatar({ name, size = 'md', imageUrl, className = '' }: AvatarProps) {
  const px = typeof size === 'number' ? size : SIZE_PX[size]
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const el = ref.current
    if (!el) return
    el.style.setProperty('--av-sz', `${px}px`)
    el.style.setProperty('--av-fs', `${Math.round(px * 0.42)}px`)
    el.style.setProperty('--av-bg', seedColor(name))
  }, [px, name])

  if (imageUrl) {
    return (
      <div
        ref={ref}
        className={`rounded-full shrink-0 overflow-hidden [width:var(--av-sz)] [height:var(--av-sz)] ${className}`}
      >
        <img src={imageUrl} alt={name} className="w-full h-full object-cover" />
      </div>
    )
  }

  return (
    <div
      ref={ref}
      aria-label={name}
      className={`avatar-font rounded-full shrink-0 flex items-center justify-center select-none text-white font-medium [width:var(--av-sz)] [height:var(--av-sz)] [font-size:var(--av-fs)] [background:var(--av-bg)] ${className}`}
    >
      {initial(name)}
    </div>
  )
}
