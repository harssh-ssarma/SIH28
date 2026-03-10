// E2E test: admin login and authentication flow.
//
// User journey tested:
//   An admin navigates to /login, enters credentials, and is redirected
//   to the admin dashboard.  Subsequent navigation to a protected page
//   does not show the login screen again.
//
// Test cases:
//   test_successful_admin_login_redirects_to_admin_dashboard
//     — fills email + password, clicks Sign In, asserts URL is /admin/dashboard
//   test_login_with_wrong_password_shows_error_toast
//     — asserts error toast appears and URL remains /login
//   test_login_with_empty_fields_shows_validation_errors
//     — asserts field-level validation messages without submitting
//   test_authenticated_user_visiting_login_is_redirected_to_dashboard
//     — loads /login with admin storageState, expects redirect to /admin/dashboard
//   test_logout_clears_session_and_redirects_to_login
//     — clicks logout in profile dropdown, asserts redirect to /login
//
// Playwright fixtures used:
//   adminPage (from fixtures.ts) for pre-auth tests
//   Unauthenticated page for login form tests
