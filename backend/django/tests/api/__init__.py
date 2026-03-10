# Django API (end-to-end HTTP) test package.
#
# API tests treat Django as a black box and assert only on HTTP status codes,
# response schemas, and side effects visible via the DB — similar to how the
# Next.js frontend and FastAPI service consume the API.
#
# Files in this package:
#   test_authentication_api.py        — login/logout/token-refresh endpoints
#   test_academic_resources_api.py    — CRUD for departments, courses, rooms
#   test_faculty_management_api.py    — faculty create/read/update/delete
#   test_student_management_api.py    — student enrolment and profile endpoints
#   test_timetable_generation_api.py  — job submission and status polling
#   test_conflict_report_api.py       — conflict endpoint schema and access control
#   test_rbac_access_control_api.py   — role-based access matrix (403/401 checks)
