# Unit test package for the FastAPI service.
#
# Unit tests validate individual functions and classes in complete isolation.
# All external dependencies (Redis, Django client, databases) are mocked.
#
# Sub-packages mirror the source tree:
#   unit/engine/   — scheduling algorithms (CP-SAT, GA, RL)
#   unit/core/     — resilience patterns, lifespan, memory monitor
#   unit/models/   — Pydantic model validators and DTO contracts
#   unit/utils/    — cache manager, progress tracker, metrics, django_client
#   unit/api/      — request routing, dependency injection, middleware logic
