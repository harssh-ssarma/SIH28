# Django unit test package.
#
# Unit tests validate models, services, serializers, and utility functions
# in isolation.  Database state is managed per-test via pytest-django
# transaction rollback (@pytest.mark.django_db).
#
# Sub-packages:
#   unit/models/       — model method, property, and constraint tests
#   unit/services/     — service-layer business logic tests
#   unit/serializers/  — DRF serializer validation and representation tests
#   unit/tasks/        — Celery task unit tests (eager mode)
#   unit/core/         — authentication, permissions, RBAC, throttling tests
