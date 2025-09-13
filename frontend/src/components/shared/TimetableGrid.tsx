interface TimetableSlot {
  time: string
  monday?: string
  tuesday?: string
  wednesday?: string
  thursday?: string
  friday?: string
  saturday?: string
}

interface TimetableGridProps {
  slots: TimetableSlot[]
  className?: string
}

export default function TimetableGrid({ slots, className = '' }: TimetableGridProps) {
  const days = ['Time', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']

  return (
    <div className={`overflow-x-auto ${className}`}>
      <table className="w-full border-collapse bg-white dark:bg-neutral-800 rounded-lg overflow-hidden shadow-sm">
        <thead>
          <tr className="bg-neutral-50 dark:bg-neutral-700">
            {days.map((day) => (
              <th key={day} className="p-3 text-left text-xs font-medium text-neutral-500 dark:text-neutral-400 uppercase tracking-wider border-b border-neutral-200 dark:border-neutral-600">
                {day}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {slots.map((slot, index) => (
            <tr key={index} className="border-b border-neutral-200 dark:border-neutral-700 hover:bg-neutral-50 dark:hover:bg-neutral-800">
              <td className="p-3 font-medium text-neutral-900 dark:text-neutral-100 text-sm">{slot.time}</td>
              <td className="p-3 text-sm text-neutral-700 dark:text-neutral-300">{slot.monday || '-'}</td>
              <td className="p-3 text-sm text-neutral-700 dark:text-neutral-300">{slot.tuesday || '-'}</td>
              <td className="p-3 text-sm text-neutral-700 dark:text-neutral-300">{slot.wednesday || '-'}</td>
              <td className="p-3 text-sm text-neutral-700 dark:text-neutral-300">{slot.thursday || '-'}</td>
              <td className="p-3 text-sm text-neutral-700 dark:text-neutral-300">{slot.friday || '-'}</td>
              <td className="p-3 text-sm text-neutral-700 dark:text-neutral-300">{slot.saturday || '-'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}