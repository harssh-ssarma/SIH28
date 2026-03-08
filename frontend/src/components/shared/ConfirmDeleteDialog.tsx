// src/components/shared/ConfirmDeleteDialog.tsx
// Reusable delete confirmation dialog — matches AppShell sign-out dialog style.
'use client'

import { Trash2 } from 'lucide-react'

interface ConfirmDeleteDialogProps {
  open: boolean
  onClose: () => void
  onConfirm: () => void
  title?: string
  description?: string
  count?: number
  loading?: boolean
}

export default function ConfirmDeleteDialog({
  open,
  onClose,
  onConfirm,
  title,
  description,
  count,
  loading = false,
}: ConfirmDeleteDialogProps) {
  if (!open) return null

  const heading = title ?? (count && count > 1 ? `Delete ${count} items?` : 'Delete item?')
  const body =
    description ??
    (count && count > 1
      ? `This will permanently delete ${count} items. This action cannot be undone.`
      : 'This will permanently delete this item. This action cannot be undone.')

  return (
    <div className="fixed inset-0 z-[70] flex items-center justify-center p-4">
      <div
        className="absolute inset-0 bg-black/40 backdrop-blur-sm"
        onClick={onClose}
        aria-hidden="true"
      />
      <div
        className="relative w-full max-w-sm rounded-2xl p-6 flex flex-col gap-4"
        style={{
          background: 'var(--color-bg-surface)',
          boxShadow: 'var(--shadow-modal)',
          border: '1px solid var(--color-border)',
        }}
      >
        {/* Icon + text */}
        <div className="flex items-start gap-3">
          <span
            className="w-10 h-10 rounded-full flex items-center justify-center shrink-0 mt-0.5"
            style={{
              background: 'var(--color-danger-subtle)',
              color: 'var(--color-danger)',
            }}
          >
            <Trash2 size={18} />
          </span>
          <div>
            <h2
              className="font-medium"
              style={{ fontSize: '16px', color: 'var(--color-text-primary)' }}
            >
              {heading}
            </h2>
            <p
              className="mt-1"
              style={{ fontSize: '14px', color: 'var(--color-text-secondary)' }}
            >
              {body}
            </p>
          </div>
        </div>

        {/* Buttons */}
        <div className="flex gap-2 justify-end">
          <button onClick={onClose} className="btn-ghost" disabled={loading}>
            Cancel
          </button>
          <button onClick={onConfirm} className="btn-danger" disabled={loading}>
            {loading ? 'Deleting…' : 'Delete'}
          </button>
        </div>
      </div>
    </div>
  )
}
