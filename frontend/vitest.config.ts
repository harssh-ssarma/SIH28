// Vitest configuration for frontend unit tests.
//
// Covers: src/lib/, src/hooks/, src/components/
// Does NOT cover E2E tests (those use playwright.config.ts).
//
// Environment: jsdom (browser-like DOM for React component rendering)
// Coverage provider: v8 (fastest, no babel needed)
// Coverage minimum: 80% lines/functions/branches for all source files
//
// Aliases mirror the @/* path aliases from tsconfig.json so imports work.
//
// Run:
//   npx vitest run          (single run, CI mode)
//   npx vitest              (watch mode, local development)
//   npx vitest --coverage   (generate coverage report)
//
// See: https://vitest.dev/config/

import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";
import path from "path";

export default defineConfig({
  // PLACEHOLDER — implement fully once vitest is installed
  plugins: [react()],
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: ["./tests/unit/setup.ts"],
    include: ["tests/unit/**/*.test.{ts,tsx}"],
    coverage: {
      provider: "v8",
      reporter: ["text", "lcov", "html"],
      include: ["src/lib/**", "src/hooks/**", "src/components/**"],
      thresholds: {
        lines: 80,
        functions: 80,
        branches: 80,
      },
    },
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
});
