# Unit tests for Celery tasks defined in academics/celery_tasks.py.
#
# Each file in this package tests one Celery task module in eager mode
# (CELERY_TASK_ALWAYS_EAGER=True in test settings — industry standard for
# unit-testing Celery tasks without a broker).
