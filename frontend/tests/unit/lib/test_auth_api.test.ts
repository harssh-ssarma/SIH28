// Vitest unit tests for src/lib/api/auth.ts
//
// Module under test: frontend/src/lib/api/auth.ts
//
// Responsibility of source module:
//   Typed API functions for authentication: login, logout, token refresh,
//   and fetching the current user profile — all of which set or clear
//   HttpOnly cookies managed by the Django backend.
//
// What these tests verify:
//   - login() calls POST /api/auth/login with email and password in body
//   - login() returns a typed User object on success
//   - login() throws AuthError with error_code on 401 response
//   - logout() calls POST /api/auth/logout
//   - getCurrentUser() calls GET /api/auth/me
//   - getCurrentUser() returns null (gracefully) on 401 (not logged in)
//   - refreshToken() calls POST /api/auth/refresh
//
// Key functions to test:
//   login(email, password) -> Promise<User>
//   logout() -> Promise<void>
//   getCurrentUser() -> Promise<User | null>
//   refreshToken() -> Promise<void>
//
// Dependencies to mock:
//   global fetch — MSW server
