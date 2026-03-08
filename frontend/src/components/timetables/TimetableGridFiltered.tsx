'use client'

/**
 * TimetableGridFiltered — extracted timetable grid component.
 *
 * Preserves the exact Google Calendar 12-colour subject palette already used
 * on the variant review page (SUBJECT_PALETTES below), so tiles look identical
 * whether rendered here or in the original review page.
 *
 * Parent owns: departmentFilter + activeDay (DepartmentTree and
 * loadVariantEntries need to reset them on variant switch).
 */

import { useMemo } from 'react'
import { TimetableGridSkeleton } from '@/components/LoadingSkeletons'
import type { BackendTimetableEntry, TimetableSlotDetailed } from '@/types/timetable'

// ─── Day labels ────────────────────────────────────────────────────────────────
const DAYS      = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
const DAY_SHORT = ['Mon',    'Tue',     'Wed',       'Thu',      'Fri']

// ─── Google Calendar 12-colour subject palette ─────────────────────────────────
// 12 perceptually-distinct accent colours — Google Calendar style.
// Each entry is just one saturated colour; the card itself stays neutral
// (surface background + 3 px left border) so text is always legible.
// *** Preserved exactly from review/page.tsx — do not change order or values ***
const SUBJECT_PALETTES: { accent: string }[] = [
  { accent: '#4285f4' }, // blue
  { accent: '#0f9d58' }, // green
  { accent: '#9334e6' }, // purple
  { accent: '#ea4335' }, // red
  { accent: '#fa7b17' }, // orange
  { accent: '#00897b' }, // teal
  { accent: '#1e88e5' }, // indigo-blue
  { accent: '#e91e63' }, // pink
  { accent: '#7cb342' }, // lime-green
  { accent: '#f9ab00' }, // amber
  { accent: '#00acc1' }, // cyan
  { accent: '#8d6e63' }, // warm brown
]

// Deterministic palette index from a string key — same hash as review page
function subjectPaletteIndex(key: string): number {
  let h = 0
  for (let i = 0; i < key.length; i++) {
    h = (Math.imul(31, h) + key.charCodeAt(i)) | 0
  }
  return Math.abs(h) % SUBJECT_PALETTES.length
}

// ─── Time formatters ──────────────────────────────────────────────────────────

function formatTime12Hour(time24: string): string {
  if (!time24) return time24
  const match = time24.match(/(\d{1,2}):(\d{2})/)
  if (!match) return time24
  let hours = parseInt(match[1], 10)
  const minutes = match[2]
  const ampm = hours >= 12 ? 'PM' : 'AM'
  hours = hours % 12 || 12
  return `${hours}:${minutes} ${ampm}`
}

function formatTimeRange(start?: string, end?: string): string {
  if (!start || !end) return start || end || ''
  return `${formatTime12Hour(start)} - ${formatTime12Hour(end)}`
}

// ─── Adapter: BackendTimetableEntry → TimetableSlotDetailed ───────────────────

function toSlotDetailed(
  e: BackendTimetableEntry,
  day: number,
): TimetableSlotDetailed {
  const timeKey =
    e.start_time && e.end_time
      ? `${e.start_time}-${e.end_time}`
      : e.time_slot
  return {
    day,
    time_slot:            timeKey,
    subject_code:         e.subject_code  ?? '',
    subject_name:         e.subject_name  ?? e.subject_code ?? '',
    faculty_id:           e.faculty_id    ?? '',
    faculty_name:         e.faculty_name  ?? 'Unknown',
    room_number:          e.room_number   ?? '',
    batch_name:           e.batch_name    ?? '',
    department_id:        e.department_id ?? '',
    year:                 undefined,
    section:              undefined,
    has_conflict:         false,
    conflict_description: undefined,
    enrolled_count:       undefined,
    room_capacity:        undefined,
  } as unknown as TimetableSlotDetailed
}

// ─── Props ─────────────────────────────────────────────────────────────────────

interface TimetableGridFilteredProps {
  /** Raw timetable entries for the active variant */
  entries: BackendTimetableEntry[]
  /** 'all' or a department UUID—applied as a filter on entries */
  departmentFilter: string
  /** 0-4 (Mon-Fri) or 'all' */
  activeDay: number | 'all'
  onDayChange: (day: number | 'all') => void
  /** True while entries are still loading (shows skeleton) */
  isLoading: boolean
  /** Called when the user clicks a timetable cell */
  onSlotClick: (slot: TimetableSlotDetailed) => void
  /** Called when the user clicks "Retry" on the empty state */
  onRetry: () => void
}

// ─── Component ─────────────────────────────────────────────────────────────────

export function TimetableGridFiltered({
  entries,
  departmentFilter,
  activeDay,
  onDayChange,
  isLoading,
  onSlotClick,
  onRetry,
}: TimetableGridFilteredProps) {
  // Build stable subject → accent colour mapping (same logic as review page)
  const subjectPaletteMap = useMemo(() => {
    const map = new Map<string, string>()
    entries.forEach(e => {
      const key = e.subject_id ?? e.subject_code ?? ''
      if (key && !map.has(key)) {
        map.set(key, SUBJECT_PALETTES[subjectPaletteIndex(key)].accent)
      }
    })
    return map
  }, [entries])

  // ── Guard states ─────────────────────────────────────────────────────────────

  if (isLoading) return <TimetableGridSkeleton days={5} slots={8} />

  if (entries.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16" style={{ color: 'var(--color-text-muted)' }}>
        <svg className="w-12 h-12 mb-3 opacity-40" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
            d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
        </svg>
        <p className="text-sm font-medium">No timetable entries loaded.</p>
        <p className="text-xs mt-1 opacity-70">The server may be slow. Click retry to try again.</p>
        <button onClick={onRetry} className="mt-4 btn-primary text-xs">Retry</button>
      </div>
    )
  }

  // ── Filtering ────────────────────────────────────────────────────────────────

  const deptFiltered =
    departmentFilter === 'all'
      ? entries
      : entries.filter(e => e.department_id === departmentFilter)

  const dayFiltered =
    activeDay === 'all'
      ? deptFiltered
      : deptFiltered.filter(e => e.day === activeDay)

  // ── Grid data ────────────────────────────────────────────────────────────────

  const grid: Record<string, BackendTimetableEntry[]> = {}
  dayFiltered.forEach(entry => {
    const timeKey =
      entry.start_time && entry.end_time
        ? `${entry.start_time}-${entry.end_time}`
        : entry.time_slot
    const key = `${entry.day}-${timeKey}`
    if (!grid[key]) grid[key] = []
    grid[key].push(entry)
  })

  const timeSlots = Array.from(
    new Set(
      deptFiltered
        .map(e => (e.start_time && e.end_time ? `${e.start_time}-${e.end_time}` : e.time_slot))
        .filter(Boolean),
    ),
  ).sort()

  const daysToShow = activeDay === 'all' ? DAYS.map((_, i) => i) : [activeDay as number]

  // ── Subject legend ────────────────────────────────────────────────────────────

  const legendItems: Array<{ key: string; label: string; name: string; accent: string }> = []
  const seenKeys = new Set<string>()
  deptFiltered.forEach(e => {
    const key = e.subject_id ?? e.subject_code ?? ''
    if (key && !seenKeys.has(key)) {
      seenKeys.add(key)
      const accent = subjectPaletteMap.get(key) ?? SUBJECT_PALETTES[0].accent
      legendItems.push({
        key,
        label: e.subject_code ?? key,
        name:  e.subject_name ?? e.subject_code ?? key,
        accent,
      })
    }
  })

  // ── Render ───────────────────────────────────────────────────────────────────

  return (
    <div className="space-y-4">

      {/* Day filter tabs */}
      <div className="flex flex-wrap gap-1.5">
        {(['all', 0, 1, 2, 3, 4] as const).map((d, i) => (
          <button
            key={i}
            onClick={() => onDayChange(d)}
            className="px-3 py-1 rounded-full text-xs font-medium transition-colors"
            style={
              activeDay === d
                ? { background: 'var(--color-primary)', color: '#fff' }
                : { background: 'var(--color-bg-surface-2)', color: 'var(--color-text-secondary)' }
            }
          >
            {d === 'all' ? 'All Days' : DAY_SHORT[d as number]}
          </button>
        ))}
      </div>

      {/* Grid table */}
      <div className="overflow-x-auto rounded-xl shadow-sm print:shadow-none" style={{ border: '1px solid var(--color-border)' }}>
        <table className="min-w-full text-xs border-collapse">
          <thead>
            <tr style={{ background: 'var(--color-bg-surface-2)' }}>
              <th
                className="sticky left-0 z-10 px-3 py-3 text-left font-semibold uppercase tracking-wider border-b border-r w-24 min-w-[6rem]"
                style={{ background: 'var(--color-bg-surface-2)', color: 'var(--color-text-muted)', borderColor: 'var(--color-border)' }}
              >
                Time
              </th>
              {daysToShow.map(di => (
                <th
                  key={di}
                  className="px-3 py-3 text-center font-semibold uppercase tracking-wider border-b border-r min-w-[8rem]"
                  style={{ color: 'var(--color-text-secondary)', borderColor: 'var(--color-border)' }}
                >
                  {DAYS[di]}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {timeSlots.length === 0 ? (
              <tr>
                <td colSpan={daysToShow.length + 1} className="py-10 text-center text-sm" style={{ color: 'var(--color-text-muted)' }}>
                  No classes scheduled for this filter
                </td>
              </tr>
            ) : (
              timeSlots.map(time => (
                <tr key={time} className="group transition-colors" style={{ borderBottom: '1px solid var(--color-border)' }}>
                  <td
                    className="sticky left-0 z-10 px-3 py-3 font-medium border-r whitespace-nowrap align-top"
                    style={{ background: 'var(--color-bg-surface)', color: 'var(--color-text-secondary)', borderColor: 'var(--color-border)' }}
                  >
                    {time.includes('-') ? formatTimeRange(...(time.split('-') as [string, string])) : time}
                  </td>
                  {daysToShow.map(di => {
                    const cellEntries = grid[`${di}-${time}`] ?? []
                    return (
                      <td key={di} className="px-2 py-2 align-top border-r" style={{ borderColor: 'var(--color-border)' }}>
                        {cellEntries.length > 0 ? (
                          <div className="space-y-1.5">
                            {cellEntries.map((entry, idx) => {
                              const key    = entry.subject_id ?? entry.subject_code ?? ''
                              const accent = subjectPaletteMap.get(key) ?? SUBJECT_PALETTES[0].accent
                              // Hex alpha: 18 = ~10% tint — same as review page
                              const bgTint = `${accent}18`
                              const slotDetailed = toSlotDetailed(entry, di)
                              return (
                                <div
                                  key={idx}
                                  className="rounded-md overflow-hidden"
                                  style={{ borderLeft: `3px solid ${accent}`, background: bgTint, cursor: 'pointer' }}
                                  onClick={() => onSlotClick(slotDetailed)}
                                  title="Click for details"
                                >
                                  <div className="px-2 pt-1.5 pb-1.5 space-y-0.5">
                                    {/* Subject code — accent coloured, tight */}
                                    <div className="text-[10px] font-bold leading-none tracking-wide uppercase truncate" style={{ color: accent }}>
                                      {entry.subject_code ?? '—'}
                                    </div>
                                    {/* Subject name */}
                                    <div className="font-semibold text-[11px] leading-tight truncate" style={{ color: 'var(--color-text-primary)' }}>
                                      {entry.subject_name ?? entry.subject_code ?? '—'}
                                    </div>
                                    {/* Faculty */}
                                    {entry.faculty_name && (
                                      <div className="text-[10px] leading-tight truncate" style={{ color: 'var(--color-text-secondary)' }}>
                                        {entry.faculty_name}
                                      </div>
                                    )}
                                    {/* Room · Batch · Duration */}
                                    {(entry.room_number || entry.batch_name || entry.duration_minutes) && (
                                      <div className="flex items-center gap-1.5 flex-wrap pt-0.5">
                                        {entry.room_number && (
                                          <span className="inline-flex items-center gap-0.5 text-[9px] font-medium" style={{ color: 'var(--color-text-muted)' }}>
                                            <svg className="w-2.5 h-2.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0H5" />
                                            </svg>
                                            {entry.room_number}
                                          </span>
                                        )}
                                        {entry.batch_name && (
                                          <span className="inline-flex items-center gap-0.5 text-[9px] font-medium" style={{ color: 'var(--color-text-muted)' }}>
                                            <svg className="w-2.5 h-2.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0" />
                                            </svg>
                                            {entry.batch_name}
                                          </span>
                                        )}
                                        {entry.duration_minutes && (
                                          <span className="text-[9px] font-medium" style={{ color: 'var(--color-text-muted)' }}>
                                            {entry.duration_minutes}m
                                          </span>
                                        )}
                                      </div>
                                    )}
                                  </div>
                                </div>
                              )
                            })}
                          </div>
                        ) : (
                          <div className="h-full min-h-[2rem] flex items-center justify-center">
                            <span className="w-1 h-1 rounded-full" style={{ background: 'var(--color-border)' }} />
                          </div>
                        )}
                      </td>
                    )
                  })}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Subject legend */}
      {legendItems.length > 0 && (
        <div className="pt-2 print:pt-4">
          <p className="text-xs font-semibold uppercase tracking-wider mb-2" style={{ color: 'var(--color-text-muted)' }}>
            Subject Legend
          </p>
          <div className="flex flex-wrap gap-2">
            {legendItems.map(({ key, label, name, accent }) => (
              <div
                key={key}
                className="inline-flex items-center gap-1.5 px-2 py-1 rounded-md text-xs"
                style={{ background: `${accent}18`, borderLeft: `3px solid ${accent}` }}
              >
                <span className="font-bold text-[10px] uppercase tracking-wide leading-none" style={{ color: accent }}>
                  {label}
                </span>
                <span className="font-medium" style={{ color: 'var(--color-text-secondary)' }}>{name}</span>
              </div>
            ))}
          </div>
        </div>
      )}

    </div>
  )
}
