// Unit tests (Vitest) for src/lib/validations/auth.ts
//
// Module under test: frontend/src/lib/validations/auth.ts
//
// Responsibility of source module:
//   Defines Zod schemas for login and password-change forms,
//   with cross-field validators (e.g., new password != old password).
//
// What these tests verify:
//   - loginSchema accepts a valid {email, password} object
//   - loginSchema rejects missing email with "Email is required"
//   - loginSchema rejects invalid email format
//   - loginSchema rejects empty password
//   - passwordChangeSchema rejects when newPassword === currentPassword
//   - passwordChangeSchema rejects when confirmPassword !== newPassword
//   - passwordChangeSchema accepts a valid payload
//
// Test data strategy:
//   Use schema.safeParse() for all assertions — no React rendering.
//   Use test.each for invalid value matrices.
//
// Dependencies:
//   Zod (installed) — no mocking needed.
