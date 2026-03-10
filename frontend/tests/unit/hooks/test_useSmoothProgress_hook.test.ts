// Unit tests (Vitest) for src/hooks/useSmoothProgress.ts
//
// Module under test: frontend/src/hooks/useSmoothProgress.ts
//
// Responsibility of source module:
//   Interpolates between sparse WebSocket progress updates using
//   requestAnimationFrame to produce a smooth animated percentage
//   for the progress bar — avoiding jarring jumps on large updates.
//
// What these tests verify:
//   - smoothedPercentage starts at 0 and increases toward target
//   - smoothedPercentage never decreases (progress never goes backwards)
//   - smoothedPercentage reaches exactly 100 when target=100
//   - hook does not call requestAnimationFrame after unmount (no memory leak)
//   - smoothed value converges within the configured SMOOTH_DURATION_MS
//
// Test data strategy:
//   renderHook() with vi.useFakeTimers() to advance RAF.
//   Assert on result.current.smoothedPercentage after timer ticks.
//
// Dependencies to mock:
//   requestAnimationFrame — vi.useFakeTimers() handles this.
