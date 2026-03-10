// E2E test: timetable review and variant comparison pages.
//
// User journey tested:
//   An admin opens a completed timetable, browses the variant grid,
//   selects two variants to compare side-by-side, and publishes one.
//
// Test cases:
//   test_timetable_list_page_shows_completed_jobs
//     — asserts job rows are visible with StatusChip showing COMPLETED
//   test_clicking_job_row_navigates_to_review_page
//     — clicks row in RunningJobRow list, asserts URL is /admin/timetables/{id}/review
//   test_review_page_variant_grid_renders_variant_cards
//     — asserts at least one VariantCard with a ScoreBar is visible
//   test_department_tree_filters_timetable_grid_on_selection
//     — clicks department in DepartmentTree, asserts grid updates
//   test_compare_page_shows_two_variant_columns
//     — navigates to /admin/timetables/{id}/compare, asserts two columns rendered
//   test_publish_variant_shows_confirmation_and_updates_badge
//     — clicks Publish on a variant, confirms dialog, asserts VariantStatusBadge = PUBLISHED
//
// Playwright fixtures used:
//   adminPage
