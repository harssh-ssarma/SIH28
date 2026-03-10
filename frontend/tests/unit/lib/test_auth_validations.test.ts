// Vitest unit tests for src/lib/validations/auth.ts
//
// Module under test: frontend/src/lib/validations/auth.ts
//
// Responsibility of source module:
//   Zod schemas for authentication form validation: LoginFormSchema,
//   PasswordChangeSchema — used by react-hook-form on the login page
//   and password-change dialog.
//
// What these tests verify:
//   - valid LoginFormSchema with email + password passes .parse()
//   - empty email fails with path=["email"] error
//   - invalid email format fails with email validation error
//   - password shorter than MIN_PASSWORD_LENGTH fails
//   - PasswordChangeSchema rejects when new_password !== confirm_password
//   - PasswordChangeSchema accepts when new_password === confirm_password
//
// Key schemas to test:
//   LoginFormSchema
//   PasswordChangeSchema
//
// Dependencies to mock:
//   None.
