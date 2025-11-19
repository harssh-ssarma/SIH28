"""
Celery Tasks for Enterprise-Scale Timetable Generation
Supports 1000+ Universities with Multi-Tenant Isolation
"""
import json
import logging
from datetime import datetime, timedelta

import httpx
from celery import Task, shared_task
from celery.exceptions import SoftTimeLimitExceeded
from django.core.cache import cache
from django.db import transaction

logger = logging.getLogger(__name__)


# ============================================================================
# ENTERPRISE PATTERN: Base Task with Retry Logic
# ============================================================================


class BaseGenerationTask(Task):
    """
    Base task class with automatic retry and error handling.

    ENTERPRISE PATTERN: Resilient task execution
    - Automatic retries on failure
    - Exponential backoff
    - Dead letter queue for failed tasks
    """

    autoretry_for = (Exception,)
    retry_kwargs = {"max_retries": 3}
    retry_backoff = True  # Exponential backoff: 1s, 2s, 4s
    retry_backoff_max = 600  # Max 10 minutes
    retry_jitter = True  # Add randomness to prevent thundering herd


# ============================================================================
# TASK 1: Generate Timetable Variants (High Priority)
# ============================================================================


@shared_task(
    bind=True,
    base=BaseGenerationTask,
    name="tasks.generate_timetable_high",
    time_limit=1800,  # 30 minutes
    soft_time_limit=1500,  # 25 minutes
    queue="timetable.high",
    priority=10,
)
def generate_timetable_high(
    self, job_id: str, request_data: dict, organization_id: str
):
    """
    HIGH PRIORITY: VIP universities, urgent requests.

    ENTERPRISE PATTERN: Priority queue
    - Executes before normal/low priority tasks
    - Guaranteed resource allocation
    - SLA: 95% complete within 10 minutes
    """
    return _execute_generation(
        self, job_id, request_data, organization_id, priority="high"
    )


# ============================================================================
# TASK 2: Generate Timetable Variants (Normal Priority)
# ============================================================================


@shared_task(
    bind=True,
    base=BaseGenerationTask,
    name="tasks.generate_timetable_normal",
    time_limit=1800,
    soft_time_limit=1500,
    queue="timetable.normal",
    priority=5,
)
def generate_timetable_normal(
    self, job_id: str, request_data: dict, organization_id: str
):
    """
    NORMAL PRIORITY: Regular universities, standard requests.

    ENTERPRISE PATTERN: Best-effort execution
    - Executes after high priority tasks
    - Fair scheduling among organizations
    - SLA: 95% complete within 15 minutes
    """
    return _execute_generation(
        self, job_id, request_data, organization_id, priority="normal"
    )


# ============================================================================
# TASK 3: Generate Timetable Variants (Low Priority)
# ============================================================================


@shared_task(
    bind=True,
    base=BaseGenerationTask,
    name="tasks.generate_timetable_batch",
    time_limit=3600,  # 1 hour (can take longer)
    soft_time_limit=3300,  # 55 minutes
    queue="timetable.low",
    priority=1,
)
def generate_timetable_batch(
    self, job_id: str, request_data: dict, organization_id: str
):
    """
    LOW PRIORITY: Batch operations, scheduled generations.

    ENTERPRISE PATTERN: Background processing
    - Executes during off-peak hours
    - Lower resource priority
    - No SLA guarantee
    """
    return _execute_generation(
        self, job_id, request_data, organization_id, priority="low"
    )


# ============================================================================
# CORE GENERATION LOGIC (Shared)
# ============================================================================


def _execute_generation(
    task_self, job_id: str, request_data: dict, organization_id: str, priority: str
):
    """
    Core timetable generation logic.

    ENTERPRISE PATTERN: Distributed task execution
    - Calls FastAPI generation engine
    - Updates progress in real-time
    - Handles failures gracefully
    - Calls Django callback on completion
    """
    from academics.models import GenerationJob, TimetableWorkflow

    logger.info(
        f"[CELERY:{priority.upper()}] Starting generation for job {job_id}, org {organization_id}"
    )

    try:
        # Update job status to 'processing'
        GenerationJob.objects.filter(job_id=job_id).update(
            status="processing", progress=0.0, started_at=datetime.utcnow()
        )

        # Call FastAPI generation engine
        FASTAPI_URL = settings.FASTAPI_URL or "http://localhost:8001"

        response = httpx.post(
            f"{FASTAPI_URL}/api/generate_variants",
            json={
                **request_data,
                "job_id": job_id,  # Pass Django's job_id
                "celery_task_id": task_self.request.id,  # Track Celery task
                "priority": priority,
            },
            timeout=30.0,  # FastAPI responds immediately
        )

        if response.status_code != 200:
            raise Exception(f"FastAPI returned {response.status_code}: {response.text}")

        logger.info(f"[CELERY:{priority.upper()}] FastAPI accepted job {job_id}")

        # FastAPI will run generation in background and call Django callback
        # This Celery task is just for queue management and retry logic

        return {
            "job_id": job_id,
            "status": "processing",
            "organization_id": organization_id,
            "priority": priority,
            "celery_task_id": task_self.request.id,
        }

    except SoftTimeLimitExceeded:
        # Soft time limit reached (25 minutes)
        logger.warning(f"[CELERY:{priority.upper()}] Soft time limit for job {job_id}")

        # Update job status
        GenerationJob.objects.filter(job_id=job_id).update(
            status="timeout", progress=task_self.request.get("progress", 0.0)
        )

        # Notify user via callback
        _notify_timeout(job_id, organization_id)

        raise

    except Exception as e:
        logger.error(
            f"[CELERY:{priority.upper()}] Generation failed for job {job_id}: {e}",
            exc_info=True,
        )

        # Update job status
        GenerationJob.objects.filter(job_id=job_id).update(
            status="failed", error_message=str(e)
        )

        # Retry with exponential backoff (handled by BaseGenerationTask)
        raise task_self.retry(exc=e)


# ============================================================================
# TASK 4: Django Callback Handler
# ============================================================================


@shared_task(
    bind=True,
    name="tasks.django_callback",
    queue="callbacks",
    priority=10,
    time_limit=300,  # 5 minutes
)
def django_callback(
    self, job_id: str, status: str, variants: list = None, error: str = None
):
    """
    Handle FastAPI callbacks asynchronously.

    ENTERPRISE PATTERN: Async callback processing
    - Decouples FastAPI from Django database writes
    - Prevents blocking FastAPI workers
    - Automatic retry on database failures
    """
    from academics.models import GenerationJob, TimetableVariant, TimetableWorkflow
    from django.db import transaction

    logger.info(
        f"[CELERY:CALLBACK] Processing callback for job {job_id}, status: {status}"
    )

    try:
        with transaction.atomic():
            # Update GenerationJob
            job = GenerationJob.objects.select_for_update().get(job_id=job_id)
            job.status = status
            job.progress = 100.0 if status == "completed" else job.progress
            job.completed_at = datetime.utcnow()
            if error:
                job.error_message = error
            job.save()

            # Update TimetableWorkflow
            workflow = TimetableWorkflow.objects.select_for_update().get(job_id=job_id)
            workflow.status = "draft" if status == "completed" else "failed"
            workflow.save()

            # Save variants (if completed)
            if status == "completed" and variants:
                for variant_data in variants:
                    TimetableVariant.objects.create(
                        job_id=job_id,
                        variant_number=variant_data["variant_number"],
                        optimization_priority=variant_data["optimization_priority"],
                        optimization_name=variant_data["optimization_name"],
                        organization_id=workflow.organization_id,
                        department_id=workflow.department_id,
                        semester=workflow.semester,
                        academic_year=workflow.academic_year,
                        timetable_entries=variant_data["timetable_entries"],
                        statistics=variant_data.get("statistics", {}),
                        quality_metrics=variant_data.get("quality_metrics", {}),
                        generation_time=variant_data.get("generation_time", 0.0),
                    )

                logger.info(
                    f"[CELERY:CALLBACK] Saved {len(variants)} variants for job {job_id}"
                )

            # Clear rate limit counter
            cache.delete(f"rate_limit:{workflow.organization_id}")

        return {"job_id": job_id, "status": "callback_processed"}

    except Exception as e:
        logger.error(
            f"[CELERY:CALLBACK] Callback failed for job {job_id}: {e}", exc_info=True
        )
        raise self.retry(exc=e, countdown=30)  # Retry after 30 seconds


# ============================================================================
# TASK 5: Cleanup Expired Jobs (Scheduled)
# ============================================================================


@shared_task(name="tasks.cleanup_expired_jobs")
def cleanup_expired_jobs():
    """
    Cleanup expired jobs and results.

    ENTERPRISE PATTERN: Housekeeping
    - Runs hourly via Celery Beat
    - Removes old jobs (> 7 days)
    - Frees up database space
    """
    from academics.models import GenerationJob

    expiry_date = datetime.utcnow() - timedelta(days=7)

    deleted_count = GenerationJob.objects.filter(
        created_at__lt=expiry_date, status__in=["completed", "failed", "cancelled"]
    ).delete()[0]

    logger.info(f"[CELERY:CLEANUP] Deleted {deleted_count} expired jobs")

    return {"deleted_count": deleted_count}


# ============================================================================
# TASK 6: Generate Usage Reports (Scheduled)
# ============================================================================


@shared_task(name="tasks.generate_usage_reports")
def generate_usage_reports():
    """
    Generate daily usage reports for each organization.

    ENTERPRISE PATTERN: Analytics
    - Runs daily via Celery Beat
    - Tracks usage per organization
    - Sends reports to admins
    """
    from academics.models import GenerationJob
    from django.db.models import Avg, Count, Sum

    yesterday = datetime.utcnow() - timedelta(days=1)

    # Aggregate usage by organization
    usage = (
        GenerationJob.objects.filter(created_at__gte=yesterday)
        .values("organization_id")
        .annotate(
            total_jobs=Count("id"),
            avg_generation_time=Avg("generation_time"),
            failed_jobs=Count("id", filter=Q(status="failed")),
        )
    )

    logger.info(
        f"[CELERY:REPORTS] Generated usage reports for {len(usage)} organizations"
    )

    return {
        "organizations": len(usage),
        "total_jobs": sum(u["total_jobs"] for u in usage),
    }


# ============================================================================
# TASK 7: Health Check (Scheduled)
# ============================================================================


@shared_task(name="tasks.health_check")
def health_check():
    """
    Periodic health check for workers and queues.

    ENTERPRISE PATTERN: Monitoring
    - Runs every 5 minutes
    - Checks queue depths
    - Alerts if system unhealthy
    """
    from celery.task.control import inspect

    i = inspect()

    # Check active workers
    active_workers = i.active()
    worker_count = len(active_workers) if active_workers else 0

    # Check queue lengths
    reserved = i.reserved()
    total_tasks = sum(len(tasks) for tasks in (reserved or {}).values())

    # Alert if unhealthy
    if worker_count == 0:
        logger.error("[CELERY:HEALTH] NO ACTIVE WORKERS! System down.")
        # Send alert (email, Slack, PagerDuty)

    if total_tasks > 500:
        logger.warning(f"[CELERY:HEALTH] High queue depth: {total_tasks} tasks pending")
        # Send alert

    return {
        "worker_count": worker_count,
        "pending_tasks": total_tasks,
        "healthy": worker_count > 0 and total_tasks < 500,
    }


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def _notify_timeout(job_id: str, organization_id: str):
    """Notify organization of timeout via email/webhook"""
    logger.warning(f"[CELERY] Job {job_id} timed out for org {organization_id}")
    # TODO: Send email/webhook notification


def _notify_failure(job_id: str, organization_id: str, error: str):
    """Notify organization of failure via email/webhook"""
    logger.error(f"[CELERY] Job {job_id} failed for org {organization_id}: {error}")
    # TODO: Send email/webhook notification


# Import Django settings
from django.conf import settings
from django.db.models import Q
