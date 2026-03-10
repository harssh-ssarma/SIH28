// E2E test: student dashboard and timetable view.
//
// User journey tested:
//   A student logs in, views their today's classes, checks their timetable
//   grid, and verifies that clash detection highlights are shown when applicable.
//
// Test cases:
//   test_student_dashboard_shows_welcome_card_with_student_name
//   test_todays_classes_card_lists_correct_subjects
//   test_enrollment_card_displays_active_course_count
//   test_clash_detection_card_shows_no_clashes_for_clean_schedule
//   test_clash_detection_card_highlights_clashing_slots
//   test_student_timetable_page_renders_timetable_grid
//   test_student_cannot_navigate_to_admin_routes
//
// Playwright fixtures used:
//   studentPage (storageState pre-authenticated as student)
