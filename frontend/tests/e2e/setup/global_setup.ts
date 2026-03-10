// Global Playwright setup — runs ONCE before all E2E tests.
//
// Responsibility:
//   1. Wait for the staging Next.js server to be healthy.
//   2. Log in as each role (admin, faculty, student) via the API.
//   3. Persist storageState (browser auth cookies) to:
//         tests/e2e/setup/.auth/admin.json
//         tests/e2e/setup/.auth/faculty.json
//         tests/e2e/setup/.auth/student.json
//   4. These files are reused by all test files via Playwright `storageState`
//      project configuration — no repeated UI login in individual tests.
//
// Teardown:
//   tests/e2e/setup/global_teardown.ts — clears test data created during setup.
//
// Environment variables required:
//   BASE_URL       — staging frontend URL (e.g. http://localhost:3000)
//   ADMIN_EMAIL    — seeded admin email
//   ADMIN_PASSWORD — seeded admin password
//   FACULTY_EMAIL  — seeded faculty email
//   FACULTY_PASSWORD
//   STUDENT_EMAIL
//   STUDENT_PASSWORD
