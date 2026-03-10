// E2E test: timetable grid rendering and interaction.
//
// User journey tested:
//   An admin views the TimetableGrid component on the review page, filters
//   by department, clicks a slot to see the SlotDetailPanel, and exports
//   the timetable to PDF and Excel.
//
// Test cases:
//   test_timetable_grid_renders_all_day_columns
//   test_timetable_grid_renders_all_configured_time_slots
//   test_clicking_slot_opens_slot_detail_panel
//   test_slot_detail_panel_displays_faculty_name_and_room
//   test_department_tree_filter_hides_non_selected_departments
//   test_export_pdf_button_triggers_download
//   test_export_excel_button_triggers_download
//   test_variant_selector_switches_displayed_timetable
//
// Playwright fixtures used:
//   adminPage
// Component under test:
//   components/shared/TimetableGrid.tsx
//   components/timetables/TimetableGridFiltered.tsx
