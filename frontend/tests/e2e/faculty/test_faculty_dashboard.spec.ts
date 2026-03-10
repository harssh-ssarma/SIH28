// E2E test: faculty dashboard and schedule view.
//
// User journey tested:
//   A faculty member logs in, views their weekly schedule, updates time
//   preferences, and verifies that their assigned subjects are displayed.
//
// Test cases:
//   test_faculty_dashboard_shows_welcome_card_with_name
//   test_weekly_schedule_card_renders_correct_day_columns
//   test_faculty_quick_stats_show_assigned_subject_count
//   test_assigned_subjects_card_lists_course_names
//   test_faculty_preferences_page_loads_availability_grid
//   test_updating_availability_preference_shows_success_toast
//   test_faculty_schedule_page_shows_published_timetable
//
// Playwright fixtures used:
//   facultyPage (storageState pre-authenticated as faculty)
