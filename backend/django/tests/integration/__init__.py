# Django integration test package.
#
# Integration tests exercise full request/response cycles through the DRF
# router → view → service → database chain using pytest-django + APIClient.
# Redis is replaced with fakeredis; FastAPI calls are intercepted with respx.
#
# Sub-packages:
#   integration/academics/  — full CRUD flows for academic resource endpoints
#   integration/auth/       — login, token refresh, logout, session management
#   integration/generation/ — timetable job lifecycle (create, poll, cancel)
