// Vitest global test setup — runs before every test file.
//
// Responsibility:
//   1. Import @testing-library/jest-dom matchers (toBeInTheDocument, etc.)
//   2. Clean up React component renders after each test (cleanup())
//   3. Reset all vi.fn() / vi.spyOn() mocks between tests
//
// This file is registered in vitest.config.ts under test.setupFiles.
