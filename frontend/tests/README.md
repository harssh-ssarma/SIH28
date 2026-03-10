# Frontend test package — Playwright E2E + Vitest unit tests.
#
# Google uses a staging-deploy target for E2E tests to match production
# behaviour more accurately than localhost dev mode.  Playwright is configured
# to run against a Docker-Compose staging environment (Next.js + Django + FastAPI)
# started by GitHub Actions before the test suite.
#
# Test layers:
#   e2e/           — Playwright E2E tests (user journeys, critical paths)
#   unit/          — Vitest unit tests for lib/, hooks/, components/
#
# Playwright configuration: playwright.config.ts (project root level)
# Vitest configuration:     vitest.config.ts (project root level)
#
# Run E2E tests:
#   npx playwright test
# Run unit tests:
#   npx vitest run
