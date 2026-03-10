// Unit tests (Vitest) for src/lib/api/client.ts
//
// Module under test: frontend/src/lib/api/client.ts
//
// Responsibility of source module:
//   Configures an axios/fetch client with base URL, JWT cookie forwarding,
//   401 interceptor (redirect to /login), and CSRF token header injection.
//
// What these tests verify:
//   - client.get() attaches the correct Authorization header when cookie present
//   - client.post() includes X-CSRFToken header from the csrf cookie
//   - a 401 response triggers window.location redirect to /login
//   - a 403 response does NOT trigger redirect (stays on current page)
//   - a 500 response rejects the promise with an ApiError containing status=500
//   - base URL is read from NEXT_PUBLIC_API_URL environment variable
//
// Test data strategy:
//   Use vi.spyOn(global, 'fetch') to mock the underlying fetch calls.
//   Use vi.stubEnv for environment variable injection.
//
// Dependencies to mock:
//   global fetch — vi.spyOn
//   window.location — vi.stubGlobal
