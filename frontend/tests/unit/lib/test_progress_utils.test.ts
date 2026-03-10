// Unit tests (Vitest) for src/lib/progressUtils.ts
//
// Module under test: frontend/src/lib/progressUtils.ts
//
// Responsibility of source module:
//   Pure utility functions for progress calculation: formats ETA as a
//   human-readable string, interpolates smooth percentage values, and
//   determines whether a job is in a terminal state.
//
// What these tests verify:
//   - formatEtaSeconds(90) returns "1 min 30 sec"
//   - formatEtaSeconds(0) returns "Almost done"
//   - formatEtaSeconds(3700) returns "> 1 hour"
//   - interpolateProgressPercentage(from, to, t) returns correct lerp value
//   - interpolateProgressPercentage clamps output to [0, 100]
//   - isTerminalJobStatus("COMPLETED") returns true
//   - isTerminalJobStatus("FAILED") returns true
//   - isTerminalJobStatus("RUNNING") returns false
//
// Test data strategy:
//   test.each for (seconds, expected_string) pairs.
//   Pure assertions — no React, no DOM.
