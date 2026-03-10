# Shared pytest fixtures for all FastAPI tests.
#
# This module is automatically discovered by pytest (conftest.py convention)
# and its fixtures are available to every test in the fastapi/tests/ tree
# without any explicit import.
#
# Fixtures provided here:
#   fastapi_test_client    — httpx AsyncClient wrapping the ASGI app
#   override_settings      — factory for temporarily patching app config values
#   mock_redis_client      — in-memory fake for redis.asyncio.Redis
#   mock_django_client     — httpx mock for outbound calls to the Django ERP API
#   sample_generation_request  — minimal valid TimetableGenerationRequest DTO
#   sample_timetable_response  — minimal valid TimetableResponse fixture
#
# Scope strategy (Google SWE Book §12):
#   function scope  — stateful fakes (redis, http mocks)
#   session scope   — expensive app startup (ASGI lifespan)
