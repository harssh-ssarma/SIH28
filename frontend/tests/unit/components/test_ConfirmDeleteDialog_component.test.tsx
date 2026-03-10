// Unit tests (Vitest + React Testing Library) for components/shared/ConfirmDeleteDialog.tsx
//
// Component under test: frontend/src/components/shared/ConfirmDeleteDialog.tsx
//
// Responsibility of source component:
//   Modal dialog that asks the user to confirm deletion of a resource,
//   showing the resource name and handling confirm/cancel callbacks.
//
// What these tests verify:
//   - dialog is NOT rendered when isOpen=false
//   - dialog IS rendered when isOpen=true
//   - resource name appears in the dialog body text
//   - clicking "Confirm" calls the onConfirm callback exactly once
//   - clicking "Cancel" calls the onCancel callback and closes dialog
//   - pressing Escape key calls onCancel
//   - confirm button shows a loading spinner while isPending=true
//   - confirm button is disabled while isPending=true
//
// Test data strategy:
//   Render with isOpen=true and onConfirm/onCancel as vi.fn() spies.
//
// Dependencies to mock:
//   None — pure presentational component.
