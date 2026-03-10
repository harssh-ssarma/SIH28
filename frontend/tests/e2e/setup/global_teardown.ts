// Global Playwright teardown — runs ONCE after all E2E tests complete.
//
// Responsibility:
//   Cleans up any test data created by global_setup.ts and individual tests:
//   - Deletes test users created during setup via the Django admin API.
//   - Removes any timetable generation jobs started during tests.
//   - Clears Redis test keys.
//
// Why teardown matters (Google SWE guideline):
//   Tests must leave shared environments in the same state they found them.
//   This file ensures the staging DB is always clean for the next test run.
