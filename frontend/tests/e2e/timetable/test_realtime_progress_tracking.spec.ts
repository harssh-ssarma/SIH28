// E2E test: real-time progress tracking via WebSocket.
//
// User journey tested:
//   An admin submits a timetable generation job and watches the status page
//   update in real time as the WebSocket pushes progress events.
//
// Test cases:
//   test_status_page_initial_state_shows_pending
//   test_websocket_progress_events_update_progress_bar_percentage
//   test_websocket_completed_event_shows_view_timetable_button
//   test_websocket_failed_event_shows_error_message
//   test_eta_countdown_decrements_correctly
//   test_reconnection_banner_appears_after_websocket_disconnect
//
// Mock strategy:
//   Playwright page.routeWebSocket() intercepts the ws://host/ws/progress/{job_id}
//   connection and injects synthetic ProgressEvent messages from a fixture file
//   tests/e2e/timetable/fixtures/progress_events.json
//
// Component under test:
//   app/admin/timetables/[id]/status/page.tsx
//   hooks/useProgress.ts
//   hooks/useSmoothProgress.ts
