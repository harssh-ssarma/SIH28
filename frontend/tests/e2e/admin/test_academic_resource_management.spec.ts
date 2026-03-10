// E2E test: academic resource management (faculty, students, courses, rooms).
//
// User journey tested:
//   An admin creates, edits, and deletes academic resources through the CRUD
//   tables and modal dialogs, verifying that the data table updates after each
//   operation.
//
// Test cases:
//   test_faculty_table_loads_with_search_and_pagination
//   test_opening_add_faculty_modal_shows_all_required_fields
//   test_submitting_add_faculty_form_adds_row_to_table
//   test_editing_faculty_prepopulates_modal_with_existing_data
//   test_deleting_faculty_removes_row_after_confirmation_dialog
//   test_course_table_loads_and_filters_by_department
//   test_rooms_table_filters_by_room_type
//   test_student_table_shows_enrolment_count_column
//
// Playwright fixtures used:
//   adminPage
// API mock strategy:
//   Use page.route() to intercept API calls and return fixture JSON
//   so tests do not depend on live database state.
