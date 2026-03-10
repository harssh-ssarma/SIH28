// E2E test: timetable generation workflow (critical path).
//
// User journey tested:
//   An admin navigates to /admin/timetables/new, fills the generation form,
//   submits the job, watches the status page update in real time via WebSocket,
//   and finally views the generated timetable grid.
//
// Test cases:
//   test_new_timetable_form_renders_all_required_fields
//     — asserts department selector, semester selector, and submit button are visible
//   test_submitting_generation_form_redirects_to_status_page
//     — fills form, clicks Generate, asserts URL changes to /admin/timetables/{id}/status
//   test_status_page_shows_running_progress_bar
//     — asserts progress bar is visible and percentage increases
//   test_status_page_shows_completed_state_with_view_button
//     — waits for COMPLETED status (mocked WebSocket) and asserts View Timetable button
//   test_completed_timetable_grid_renders_all_departments
//     — navigates to /admin/timetables/{id}/review, asserts DepartmentTree is populated
//   test_cancelling_running_job_shows_cancelled_status
//     — clicks Cancel on the status page, asserts status badge = CANCELLED
//
// Playwright fixtures used:
//   adminPage, apiContext
// Mock strategy:
//   WebSocket messages mocked via page.routeWebSocket()
