"""
Django Settings for Celery Configuration
Enterprise-Scale Multi-Tenant Task Queue
"""

# Add to your settings.py

# ============================================================================
# CELERY CONFIGURATION
# ============================================================================

import os

from celery.schedules import crontab

# Celery broker (Redis)
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")

# Celery task settings
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TIMEZONE = "UTC"
CELERY_ENABLE_UTC = True

# Task execution settings
CELERY_TASK_ACKS_LATE = True  # Acknowledge after task completes
CELERY_TASK_REJECT_ON_WORKER_LOST = True  # Requeue if worker crashes
CELERY_WORKER_PREFETCH_MULTIPLIER = 1  # Only 1 task per worker (long-running)
CELERY_WORKER_MAX_TASKS_PER_CHILD = 10  # Restart after 10 tasks (prevent leaks)

# Task time limits
CELERY_TASK_TIME_LIMIT = 1800  # 30 minutes hard limit
CELERY_TASK_SOFT_TIME_LIMIT = 1500  # 25 minutes soft limit

# Result backend settings
CELERY_RESULT_EXPIRES = 3600  # Results expire after 1 hour
CELERY_RESULT_PERSISTENT = True  # Persist results to disk

# Monitoring
CELERY_WORKER_SEND_TASK_EVENTS = True  # Enable events for Flower
CELERY_TASK_SEND_SENT_EVENT = True

# ============================================================================
# FASTAPI INTEGRATION
# ============================================================================

FASTAPI_URL = os.getenv("FASTAPI_URL", "http://localhost:8001")

# ============================================================================
# MULTI-TENANT CONFIGURATION
# ============================================================================

# Organization tiers (for priority routing)
ORG_TIERS = {
    "free": {"queue": "timetable.low", "priority": 1, "rate_limit": 5},
    "standard": {"queue": "timetable.normal", "priority": 5, "rate_limit": 10},
    "premium": {"queue": "timetable.high", "priority": 8, "rate_limit": 50},
    "enterprise": {"queue": "timetable.high", "priority": 10, "rate_limit": 100},
}

# Rate limiting
GENERATION_RATE_LIMIT_WINDOW = 60  # seconds
GENERATION_MAX_CONCURRENT_PER_ORG = 10  # max concurrent generations per org
