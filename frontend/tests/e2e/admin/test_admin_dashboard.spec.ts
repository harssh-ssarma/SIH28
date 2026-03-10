// E2E test: admin dashboard rendering and data display.
//
// User journey tested:
//   An admin visits /admin/dashboard and sees live stats, system monitor
//   cards, and faculty availability information fetched from the API.
//
// Test cases:
//   test_admin_dashboard_loads_without_errors
//     — waits for loading skeletons to resolve, asserts no error toast
//   test_admin_stats_grid_displays_faculty_count
//     — asserts AdminStatsGrid card displays a numeric value > 0
//   test_system_monitor_grid_shows_online_status
//     — asserts system health card shows "Online" badge
//   test_strategic_actions_panel_render_buttons
//     — asserts at least one action button is visible
//   test_audit_panel_displays_recent_activity_entries
//     — asserts audit log list has at least one entry
//
// Playwright fixtures used:
//   adminPage (storageState pre-authenticated)
