// E2E test: role-based page access control.
//
// User journey tested:
//   Every role-restricted route returns the correct page (or redirect to
//   /unauthorized) depending on the authenticated user's role.
//
// Test cases:
//   test_admin_can_access_admin_dashboard
//   test_faculty_accessing_admin_dashboard_is_redirected_to_unauthorized
//   test_student_accessing_admin_dashboard_is_redirected_to_unauthorized
//   test_unauthenticated_user_accessing_admin_dashboard_is_redirected_to_login
//   test_faculty_can_access_faculty_dashboard
//   test_student_can_access_student_dashboard
//   test_admin_cannot_access_student_dashboard_redirects_to_unauthorized
//
// Implementation note:
//   Uses three storageState fixtures (admin, faculty, student) to avoid
//   UI login in each test.  Assertions are URL-only (fast, no rendering wait).
