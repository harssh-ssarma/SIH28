// Playwright configuration for E2E tests.
//
// Target environment: Docker-Compose staging stack running in GitHub Actions.
// Why staging over localhost dev mode (Google practice):
//   - Production-identical Next.js build (no HMR artifacts, no dev-only warnings)
//   - Real JWT cookie behaviour (Next.js dev mode handles cookies differently)
//   - Stable test execution — dev mode hot-reload can cause flakiness
//
// Base URL:  set via PLAYWRIGHT_BASE_URL env var (default: http://localhost:3000)
// Reports:   HTML report + GitHub Actions artifact upload
// Retries:   2 retries in CI (network flakiness), 0 locally
//
// How it works:
//   1. GitHub Actions starts docker-compose.test.yml (Next.js + Django + FastAPI + Redis + PG)
//   2. wait-on waits for all services to be healthy
//   3. playwright runs E2E suite against BASE_URL
//
// Project structure (separate browser contexts per role):
//   admin-chromium  — Chrome + admin storageState
//   faculty-firefox — Firefox + faculty storageState
//   student-webkit  — Safari/WebKit + student storageState
//   unauthenticated — Chrome, no storageState (login page tests)
//
// Run locally:
//   npx playwright test
// Run with headed browser:
//   npx playwright test --headed
// Run single file:
//   npx playwright test tests/e2e/admin/test_admin_dashboard.spec.ts

import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  // PLACEHOLDER — implement after reading playwright.config.ts docs
  // See: https://playwright.dev/docs/test-configuration
  testDir: "./tests/e2e",
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: process.env.CI ? "github" : "html",
  globalSetup: "./tests/e2e/setup/global_setup.ts",
  globalTeardown: "./tests/e2e/setup/global_teardown.ts",
  use: {
    baseURL: process.env.PLAYWRIGHT_BASE_URL ?? "http://localhost:3000",
    trace: "on-first-retry",
    screenshot: "only-on-failure",
  },
  projects: [
    // Setup project: logs in and saves storageState files
    { name: "setup", testMatch: /global_setup\.ts/ },

    // Admin tests run on Chromium with admin auth state
    {
      name: "admin-chromium",
      use: {
        ...devices["Desktop Chrome"],
        storageState: "./tests/e2e/setup/.auth/admin.json",
      },
      dependencies: ["setup"],
    },

    // Faculty tests run on Firefox
    {
      name: "faculty-firefox",
      use: {
        ...devices["Desktop Firefox"],
        storageState: "./tests/e2e/setup/.auth/faculty.json",
      },
      dependencies: ["setup"],
    },

    // Student tests run on WebKit (Safari engine)
    {
      name: "student-webkit",
      use: {
        ...devices["Desktop Safari"],
        storageState: "./tests/e2e/setup/.auth/student.json",
      },
      dependencies: ["setup"],
    },

    // Unauthenticated tests (login page, access control)
    {
      name: "unauthenticated",
      use: { ...devices["Desktop Chrome"] },
      dependencies: ["setup"],
    },
  ],
});
