# Django test package root.
#
# This package contains all tests for the Django ERP backend service.
#
# Test layers (Google Testing Pyramid):
#   Unit tests     — backend/django/tests/unit/
#   Integration    — backend/django/tests/integration/
#   API tests      — backend/django/tests/api/
#
# Database strategy:
#   pytest-django with --reuse-db uses a real PostgreSQL database in CI
#   (industry standard at Google / Stripe / Shopify scale).
#   The test DB is provisioned from DATABASE_URL_TEST environment variable.
#
#   WHY PostgreSQL and not SQLite for Django tests:
#   - PostgreSQL-specific features (JSON fields, array ops, ILIKE, advisory locks)
#     behave differently in SQLite and produce false-test-passes.
#   - Google SWE guidance: test against the same engine used in production.
#   - GitHub Actions spins up a postgres:16 service container in < 15 s.
#
# Run with:
#   pytest backend/django/tests/ -v --cov=backend/django
