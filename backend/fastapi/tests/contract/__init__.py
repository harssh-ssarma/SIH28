# Contract test package for the FastAPI service.
#
# Contract tests verify that the FastAPI service honours the API contract
# that the Django backend and Next.js frontend depend on.  They use
# recorded request/response snapshots (Pact or manual JSON fixtures) and
# assert on schema stability so that breaking changes are caught before
# deployment.
#
# Files in this package:
#   test_generation_api_contract.py  — timetable generation endpoint schema
#   test_websocket_contract.py       — WebSocket progress-event schema
