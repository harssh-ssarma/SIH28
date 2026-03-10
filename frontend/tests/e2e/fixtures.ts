// Shared Playwright test fixtures and helper utilities.
//
// This file is imported by every E2E test file in frontend/tests/e2e/.
// It extends the base test object with project-specific fixtures.
//
// Fixtures provided:
//   adminPage    — Page pre-authenticated as an ADMIN user (session cookie set)
//   facultyPage  — Page pre-authenticated as a FACULTY user
//   studentPage  — Page pre-authenticated as a STUDENT user
//   loginPage    — Page factory for the /login route
//   apiContext   — APIRequestContext for making direct API assertions
//
// Authentication strategy:
//   Google Playwright best practice: use storageState (saved browser auth state)
//   to bypass the login UI for every test.  storageState JSON files are
//   generated once in a global setup file and reused across the full test run.
//   This reduces test runtime by ~60% compared to logging in per test.
//
// Global setup file: tests/e2e/setup/global_setup.ts
// StorageState files: tests/e2e/setup/.auth/admin.json
//                     tests/e2e/setup/.auth/faculty.json
//                     tests/e2e/setup/.auth/student.json
