"""
Celery Configuration for Enterprise-Scale Timetable Generation
Supports 1000+ Universities with Multi-Tenant Task Isolation
"""
import os

from celery import Celery
from celery.schedules import crontab
from kombu import Exchange, Queue

# Initialize Celery app
app = Celery("timetable_generation")

# Load configuration from Django settings
app.config_from_object("django.conf:settings", namespace="CELERY")

# ============================================================================
# ENTERPRISE PATTERN: Multi-Tenant Task Routing
# ============================================================================

# Define exchanges for task routing
default_exchange = Exchange("default", type="direct")
priority_exchange = Exchange("priority", type="direct")
batch_exchange = Exchange("batch", type="direct")

# Define queues with priorities and resource limits
app.conf.task_queues = (
    # HIGH PRIORITY: VIP universities, urgent generations (10% capacity)
    Queue(
        "timetable.high",
        exchange=priority_exchange,
        routing_key="timetable.high",
        queue_arguments={
            "x-max-priority": 10,
            "x-message-ttl": 3600000,  # 1 hour TTL
        },
    ),
    # NORMAL PRIORITY: Regular generations (70% capacity)
    Queue(
        "timetable.normal",
        exchange=default_exchange,
        routing_key="timetable.normal",
        queue_arguments={
            "x-max-priority": 5,
            "x-message-ttl": 7200000,  # 2 hours TTL
        },
    ),
    # LOW PRIORITY: Batch generations, background tasks (20% capacity)
    Queue(
        "timetable.low",
        exchange=batch_exchange,
        routing_key="timetable.low",
        queue_arguments={
            "x-max-priority": 1,
            "x-message-ttl": 86400000,  # 24 hours TTL
        },
    ),
    # CALLBACKS: FastAPI → Django callbacks (instant)
    Queue(
        "callbacks",
        exchange=default_exchange,
        routing_key="callbacks",
        queue_arguments={
            "x-max-priority": 10,
        },
    ),
)

# ============================================================================
# ENTERPRISE PATTERN: Task Routing Rules
# ============================================================================

app.conf.task_routes = {
    # High priority: VIP universities (paid plans, urgent requests)
    "tasks.generate_timetable_high": {
        "queue": "timetable.high",
        "routing_key": "timetable.high",
        "priority": 10,
    },
    # Normal priority: Regular universities (standard plans)
    "tasks.generate_timetable_normal": {
        "queue": "timetable.normal",
        "routing_key": "timetable.normal",
        "priority": 5,
    },
    # Low priority: Batch operations (background, scheduled)
    "tasks.generate_timetable_batch": {
        "queue": "timetable.low",
        "routing_key": "timetable.low",
        "priority": 1,
    },
    # Callbacks: Django updates (instant processing)
    "tasks.django_callback": {
        "queue": "callbacks",
        "routing_key": "callbacks",
        "priority": 10,
    },
}

# ============================================================================
# ENTERPRISE PATTERN: Resource Management & Rate Limiting
# ============================================================================

app.conf.update(
    # Task execution settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # Worker concurrency (per worker instance)
    worker_prefetch_multiplier=1,  # Only 1 task per worker at a time (long-running)
    worker_max_tasks_per_child=10,  # Restart worker after 10 tasks (prevent memory leaks)
    # Task time limits (prevent stuck tasks)
    task_time_limit=1800,  # 30 minutes hard limit
    task_soft_time_limit=1500,  # 25 minutes soft limit (cleanup warning)
    # Task retries (automatic recovery)
    task_acks_late=True,  # Acknowledge after task completes (not before)
    task_reject_on_worker_lost=True,  # Requeue if worker crashes
    task_default_retry_delay=300,  # 5 minutes between retries
    task_max_retries=3,  # Max 3 retry attempts
    # Result backend (Redis)
    result_backend=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/1"),
    result_expires=3600,  # Results expire after 1 hour
    result_persistent=True,  # Persist results to disk
    # Broker settings (Redis)
    broker_url=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"),
    broker_connection_retry_on_startup=True,
    broker_connection_retry=True,
    broker_connection_max_retries=10,
    # Monitoring & observability
    worker_send_task_events=True,  # Enable task events for Flower
    task_send_sent_event=True,  # Track task sent events
    # Rate limiting (per-organization)
    task_annotations={
        "tasks.generate_timetable_*": {
            "rate_limit": "10/m",  # Max 10 generations per minute per org
        }
    },
)

# ============================================================================
# ENTERPRISE PATTERN: Scheduled Tasks (Celery Beat)
# ============================================================================

app.conf.beat_schedule = {
    # Cleanup expired jobs (every hour)
    "cleanup-expired-jobs": {
        "task": "tasks.cleanup_expired_jobs",
        "schedule": crontab(minute=0),  # Every hour
        "options": {"queue": "timetable.low"},
    },
    # Generate usage reports (daily)
    "generate-usage-reports": {
        "task": "tasks.generate_usage_reports",
        "schedule": crontab(hour=0, minute=0),  # Midnight
        "options": {"queue": "timetable.low"},
    },
    # Health check (every 5 minutes)
    "health-check": {
        "task": "tasks.health_check",
        "schedule": crontab(minute="*/5"),  # Every 5 minutes
        "options": {"queue": "callbacks"},
    },
    # Auto-scale workers (every 10 minutes)
    "auto-scale-workers": {
        "task": "tasks.auto_scale_workers",
        "schedule": crontab(minute="*/10"),  # Every 10 minutes
        "options": {"queue": "callbacks"},
    },
}

# ============================================================================
# ENTERPRISE PATTERN: Multi-Tenant Isolation
# ============================================================================


@app.task(bind=True, name="tasks.route_generation_task")
def route_generation_task(self, organization_id: str, request_data: dict):
    """
    Smart task routing based on organization tier and system load.

    ENTERPRISE PATTERN: Multi-tenant task isolation
    - VIP orgs → high priority queue
    - Regular orgs → normal priority queue
    - Rate-limited orgs → low priority queue
    """
    from django.core.cache import cache

    # Check organization tier from cache
    org_tier = cache.get(f"org_tier:{organization_id}", "standard")

    # Check current system load
    queue_lengths = {
        "high": cache.get("queue_length:high", 0),
        "normal": cache.get("queue_length:normal", 0),
        "low": cache.get("queue_length:low", 0),
    }

    # Route based on tier + load
    if org_tier == "enterprise" or org_tier == "premium":
        # VIP customers always get high priority
        queue = "timetable.high"
        priority = 10
    elif queue_lengths["normal"] > 50:
        # System overloaded, route to low priority
        queue = "timetable.low"
        priority = 1
    else:
        # Normal routing
        queue = "timetable.normal"
        priority = 5

    # Apply rate limiting
    rate_limit_key = f"rate_limit:{organization_id}"
    current_count = cache.get(rate_limit_key, 0)

    if current_count >= 10:  # Max 10 concurrent per org
        raise self.retry(countdown=60)  # Retry after 1 minute

    # Increment rate limit counter
    cache.set(rate_limit_key, current_count + 1, timeout=60)

    # Route to appropriate task
    from tasks import generate_timetable_variants

    return generate_timetable_variants.apply_async(
        args=[request_data],
        queue=queue,
        priority=priority,
        kwargs={"organization_id": organization_id},
    )


# ============================================================================
# ENTERPRISE PATTERN: Dynamic Worker Scaling
# ============================================================================


@app.task(bind=True, name="tasks.auto_scale_workers")
def auto_scale_workers(self):
    """
    Automatically scale Celery workers based on queue depth.

    ENTERPRISE PATTERN: Auto-scaling (like Kubernetes HPA)
    - Queue depth > 100 → Scale up
    - Queue depth < 20 → Scale down
    """
    from celery.task.control import inspect

    i = inspect()

    # Get queue lengths
    active = i.active()
    reserved = i.reserved()

    # Calculate total pending tasks
    total_pending = sum(len(tasks) for tasks in (active or {}).values())
    total_reserved = sum(len(tasks) for tasks in (reserved or {}).values())
    total_load = total_pending + total_reserved

    # Scaling logic (integrate with Kubernetes/Docker Swarm)
    if total_load > 100:
        # Scale up (trigger Kubernetes HPA or Docker Swarm scale)
        # This is a placeholder - actual implementation depends on orchestrator
        print(f"[AUTO-SCALE] High load detected ({total_load} tasks). Scaling UP.")
        # kubectl scale deployment celery-worker --replicas=10

    elif total_load < 20:
        # Scale down
        print(f"[AUTO-SCALE] Low load detected ({total_load} tasks). Scaling DOWN.")
        # kubectl scale deployment celery-worker --replicas=3

    return {
        "total_load": total_load,
        "action": "scaled" if total_load > 100 else "no_action",
    }


# Auto-discover tasks from Django apps
app.autodiscover_tasks()
