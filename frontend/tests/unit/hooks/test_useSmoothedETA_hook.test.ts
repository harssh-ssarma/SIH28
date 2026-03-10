// Unit tests (Vitest) for src/hooks/useSmoothedETA.ts
//
// Module under test: frontend/src/hooks/useSmoothedETA.ts
//
// Responsibility of source module:
//   Smooths the estimated time-to-completion received from WebSocket events
//   to avoid the ETA display jumping erratically — applies an exponential
//   moving average over recent ETA samples.
//
// What these tests verify:
//   - initial ETA is null before first WebSocket event
//   - first ETA event sets the smoothed value to the received eta_seconds
//   - subsequent events apply EMA smoothing (value changes incrementally)
//   - ETA is set to null when status transitions to COMPLETED or FAILED
//   - hook does not leak timers after unmount
//
// Test data strategy:
//   renderHook() with controlled eta input values.
//   Assert smoothedEta values after each re-render with act().
