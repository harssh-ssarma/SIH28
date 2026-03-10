# Integration test package for the FastAPI service.
#
# Integration tests spin up a real TestClient (httpx + ASGI) and verify
# that HTTP routes, middleware, dependency injection, and service wiring
# all cooperate correctly.  Redis and Django are replaced with fakes or
# docker-compose services during CI.
#
# Sub-packages:
#   integration/routers/   — end-to-end HTTP route tests per router module
#   integration/services/  — service-layer integration with in-process fakes
