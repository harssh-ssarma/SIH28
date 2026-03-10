# Shared pytest-django fixtures for the Django test suite.
#
# This conftest.py is automatically loaded by pytest for all tests under
# backend/django/tests/.  It provides:
#
# Fixtures:
#   django_db_setup        — one-time PostgreSQL test DB creation (session scope)
#   api_client             — DRF APIClient with helper auth methods
#   authenticated_client   — APIClient pre-authenticated as a regular user
#   admin_client           — APIClient pre-authenticated as an admin user
#   faculty_client         — APIClient pre-authenticated as a faculty user
#   student_client         — APIClient pre-authenticated as a student user
#   sample_department      — a persisted Department model fixture
#   sample_course          — a persisted Course model fixture
#   sample_faculty         — a persisted Faculty model fixture
#   sample_room            — a persisted Room model fixture
#   sample_timetable_job   — a persisted GenerationJob model fixture
#   mock_redis             — fakeredis.FakeRedis replacing django-redis cache
#   mock_fastapi_client    — httpx mock for calls to the FastAPI service
#
# Scope strategy:
#   session scope: DB setup, superuser creation
#   function scope: stateful model instances (auto-rolled back via transaction)
#
# Django settings override:
#   Uses pytest-django @pytest.mark.django_db(databases=["default"]) on each test.
#   CACHES setting is overridden to use fakeredis in all test runs.
