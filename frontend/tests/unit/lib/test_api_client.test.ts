// Vitest unit tests for src/lib/api/client.ts
//
// Module under test: frontend/src/lib/api/client.ts
//
// Responsibility of source module:
//   Configures the base fetch/axios client with base URL, default headers,
//   HttpOnly cookie credentials, request/response interceptors for auth errors,
//   and automatic redirect to /login on 401 responses.
//
// What these tests verify:
//   - client sends requests with credentials: "include" by default
//   - client includes the correct Content-Type: application/json header
//   - a 401 response triggers a redirect to /login via router.push
//   - a 403 response does NOT trigger a redirect (handled at call site)
//   - a 500 response throws an ApiError with status=500
//   - request base URL is read from NEXT_PUBLIC_DJANGO_API_URL env var
//
// Key exports to test:
//   apiClient (fetch wrapper / axios instance)
//   handleApiError(response) -> never
//
// Test data strategy:
//   Use vitest's vi.stubGlobal("fetch", vi.fn()) to intercept requests.
//   Use vi.stubEnv for environment variables.
//
// Dependencies to mock:
//   next/navigation useRouter — vi.mock("next/navigation")
//   global fetch              — vi.stubGlobal
