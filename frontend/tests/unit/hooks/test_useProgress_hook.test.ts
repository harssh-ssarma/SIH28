// Unit tests (Vitest + React Testing Library) for src/hooks/useProgress.ts
//
// Module under test: frontend/src/hooks/useProgress.ts
//
// Responsibility of source module:
//   React hook that opens a WebSocket connection to the FastAPI progress
//   endpoint and returns { percentage, stage, eta, status, error } state
//   that updates as events arrive.
//
// What these tests verify:
//   - hook initialises with percentage=0, status="PENDING"
//   - receiving a PROGRESS event updates percentage and stage
//   - receiving a COMPLETED event sets status="COMPLETED" and closes socket
//   - receiving a FAILED event sets status="FAILED" and sets error message
//   - hook retries connection on socket close with exponential back-off
//   - hook cleans up the WebSocket on component unmount
//
// Test data strategy:
//   Use renderHook() from @testing-library/react.
//   Mock WebSocket via vi.stubGlobal("WebSocket", MockWebSocket).
//   Drive events by calling mockSocket.triggerMessage(eventPayload).
//
// Dependencies to mock:
//   WebSocket constructor — vi.stubGlobal
