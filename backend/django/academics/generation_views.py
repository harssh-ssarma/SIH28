"""
Timetable Generation API Views
Handles timetable generation, progress tracking, and approval workflow
"""
import logging
import os
from datetime import datetime

import requests
from django.core.cache import cache
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Batch, Department, GenerationJob, Timetable
from .serializers import (
    GenerationJobCreateSerializer,
    GenerationJobSerializer,
    TimetableSerializer,
)

logger = logging.getLogger(__name__)


class GenerationJobViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing timetable generation jobs
    """

    queryset = GenerationJob.objects.all()
    serializer_class = GenerationJobSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter jobs based on user role"""
        user = self.request.user
        if user.role == "admin":
            return GenerationJob.objects.all()
        elif user.role in ["staff", "faculty"]:
            return GenerationJob.objects.filter(
                department__department_id=user.department
            )
        return GenerationJob.objects.filter(created_by=user)

    @action(detail=False, methods=["post"], url_path="generate")
    def generate_timetable(self, request):
        """
        ENTERPRISE PATTERN: Django-First Architecture

        Start a new timetable generation job with workflow tracking.
        This is the MAIN ENTRY POINT for all timetable generation requests.

        POST /api/timetable/generate/
        Body: {
            "department_id": "CSE",
            "batch_ids": ["2024-CSE-A", "2024-CSE-B"],  # Multiple batches supported
            "semester": 3,
            "academic_year": "2024-25",
            "organization_id": "org_123",
            "num_variants": 5  # Optional, default 5
        }

        FLOW:
        1. Django creates TimetableWorkflow record (source of truth)
        2. Django creates GenerationJob record (detailed tracking)
        3. Django calls FastAPI asynchronously (compute engine)
        4. Returns job_id immediately (non-blocking)
        5. Frontend polls /status/ or connects via WebSocket

        WHY DJANGO-FIRST:
        - Single source of truth (PostgreSQL)
        - Transaction safety (rollback on failure)
        - Permissions & auditing in one place
        - Easy retry/recovery if FastAPI fails
        - Scalable: Django scales horizontally
        """
        import uuid

        from django.db import transaction

        from .timetable_models import TimetableWorkflow

        # Validate request data
        serializer = GenerationJobCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # STEP 1: Create workflow + job in SINGLE TRANSACTION (atomic)
        try:
            with transaction.atomic():
                # Generate unique job_id
                job_id = f"tt_{uuid.uuid4().hex[:12]}"

                # Get department (validate existence)
                department = Department.objects.get(
                    department_id=serializer.validated_data["department_id"]
                )

                # Get batches (support multiple batches)
                batch_ids = serializer.validated_data.get("batch_ids", [])
                if not batch_ids:
                    # Fallback: single batch_id (backward compatibility)
                    batch_ids = [serializer.validated_data.get("batch_id")]

                batches = Batch.objects.filter(batch_id__in=batch_ids)
                if not batches.exists():
                    return Response(
                        {"success": False, "error": "No valid batches found"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                # Create TimetableWorkflow (source of truth for approval process)
                workflow = TimetableWorkflow.objects.create(
                    job_id=job_id,
                    organization_id=serializer.validated_data.get("organization_id"),
                    department_id=department.department_id,
                    semester=serializer.validated_data["semester"],
                    academic_year=serializer.validated_data["academic_year"],
                    status="draft",  # Initial status (not submitted yet)
                    created_by=request.user,
                    parameters={  # Store ALL parameters for audit/retry
                        "batch_ids": batch_ids,
                        "num_variants": serializer.validated_data.get(
                            "num_variants", 5
                        ),
                        "fixed_slots": serializer.validated_data.get("fixed_slots", []),
                        "shifts": serializer.validated_data.get("shifts", []),
                    },
                )

                # Create GenerationJob (detailed progress tracking)
                job = GenerationJob.objects.create(
                    job_id=job_id,
                    department=department,
                    batch=batches.first(),  # Primary batch
                    semester=serializer.validated_data["semester"],
                    academic_year=serializer.validated_data["academic_year"],
                    status="queued",
                    progress=0.0,
                    created_by=request.user,
                    workflow=workflow,  # Link to workflow
                )

                logger.info(f"[DJANGO] Created workflow {workflow.id} and job {job_id}")

            # STEP 2: Call FastAPI asynchronously (AFTER transaction commits)
            # This ensures database records exist even if FastAPI call fails
            self._call_fastapi_async(job_id, serializer.validated_data)

            # STEP 3: Return job details immediately (non-blocking)
            return Response(
                {
                    "success": True,
                    "message": "Timetable generation started",
                    "job_id": job_id,
                    "workflow_id": workflow.id,
                    "status": "queued",
                    "estimated_time": "5-10 minutes",
                    "websocket_url": f"ws://localhost:8001/ws/progress/{job_id}",
                    "status_url": f"/api/timetable/status/{job_id}/",
                },
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            logger.error(
                f"[DJANGO] Error creating generation job: {str(e)}", exc_info=True
            )
            return Response(
                {"success": False, "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _call_fastapi_async(self, job_id: str, validated_data: dict):
        """
        ENTERPRISE PATTERN: Celery Task Queue (Multi-Tenant)

        Queue generation task using Celery for enterprise-scale processing.

        WHY CELERY:
        - Multi-tenant isolation (1000+ universities)
        - Priority queues (VIP customers first)
        - Automatic retries (resilience)
        - Distributed workers (horizontal scaling)
        - Rate limiting (prevent abuse)
        - Monitoring (Flower dashboard)

        ARCHITECTURE:
        Django → Celery Queue → Celery Worker → FastAPI Engine
        """
        from academics.tasks import (
            generate_timetable_batch,
            generate_timetable_high,
            generate_timetable_normal,
        )
        from django.conf import settings

        organization_id = validated_data.get("organization_id")

        # Determine organization tier (for priority routing)
        org_tier = self._get_organization_tier(organization_id)

        # Prepare task data (NEP 2020 compatible)
        request_data = {
            "department_id": validated_data["department_id"],
            "batch_ids": validated_data.get("batch_ids", []),  # Legacy
            "semester": validated_data["semester"],
            "academic_year": validated_data["academic_year"],
            "organization_id": organization_id,
            "num_variants": validated_data.get("num_variants", 5),
            # NEP 2020: Student enrollment data
            "student_enrollments": validated_data.get("student_enrollments", []),
            "subjects": validated_data.get("subjects", []),
            "redis_cache_key": validated_data.get("redis_cache_key"),
            # Constraints
            "fixed_slots": validated_data.get("fixed_slots", []),
            "shifts": validated_data.get("shifts", []),
        }

        # Route to appropriate queue based on tier
        if org_tier in ["enterprise", "premium"]:
            # VIP customers → High priority queue
            task = generate_timetable_high.apply_async(
                args=[job_id, request_data, organization_id],
                queue="timetable.high",
                priority=10,
            )
            logger.info(
                f"[DJANGO] Queued HIGH priority task {task.id} for job {job_id}"
            )

        elif org_tier == "standard":
            # Regular customers → Normal priority queue
            task = generate_timetable_normal.apply_async(
                args=[job_id, request_data, organization_id],
                queue="timetable.normal",
                priority=5,
            )
            logger.info(
                f"[DJANGO] Queued NORMAL priority task {task.id} for job {job_id}"
            )

        else:
            # Free tier → Low priority queue
            task = generate_timetable_batch.apply_async(
                args=[job_id, request_data, organization_id],
                queue="timetable.low",
                priority=1,
            )
            logger.info(f"[DJANGO] Queued LOW priority task {task.id} for job {job_id}")

        # Store Celery task ID for tracking
        GenerationJob.objects.filter(job_id=job_id).update(celery_task_id=task.id)

        return task.id

    def _get_organization_tier(self, organization_id: str) -> str:
        """
        Get organization tier from database or cache.

        ENTERPRISE PATTERN: Multi-tenant tier management
        - Cache tier for fast lookup (Redis)
        - Fallback to database if not cached
        """
        from core.models import Organization  # Assuming you have this model
        from django.core.cache import cache

        # Check cache first
        cache_key = f"org_tier:{organization_id}"
        tier = cache.get(cache_key)

        if tier:
            return tier

        # Fallback to database
        try:
            org = Organization.objects.get(id=organization_id)
            tier = org.subscription_tier or "free"

            # Cache for 1 hour
            cache.set(cache_key, tier, timeout=3600)

            return tier
        except Organization.DoesNotExist:
            return "free"  # Default to free tier

    @action(detail=False, methods=["post"], url_path="fastapi_callback")
    def fastapi_callback(self, request):
        """
        ENTERPRISE PATTERN: FastAPI Callback Endpoint

        FastAPI calls this endpoint when generation completes.
        This updates Django's database with final results.

        POST /api/timetable/fastapi_callback/
        Body: {
            "job_id": "tt_abc123",
            "status": "completed" | "failed",
            "variants": [...],  # Generated variants
            "generation_time": 487.3,
            "error": "..."  # If failed
        }

        WHY CALLBACK:
        - FastAPI pushes results (no polling needed)
        - Django updates workflow + job immediately
        - Clean separation: FastAPI = compute, Django = data
        """
        from django.db import transaction

        from .timetable_models import TimetableVariant, TimetableWorkflow

        try:
            job_id = request.data.get("job_id")
            status_value = request.data.get("status")
            variants_data = request.data.get("variants", [])
            generation_time = request.data.get("generation_time", 0.0)
            error_message = request.data.get("error")

            if not job_id:
                return Response(
                    {"success": False, "error": "job_id is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            logger.info(
                f"[DJANGO] FastAPI callback for job {job_id}, status: {status_value}"
            )

            with transaction.atomic():
                # Update GenerationJob
                job = GenerationJob.objects.filter(job_id=job_id).first()
                if not job:
                    logger.error(f"[DJANGO] Job {job_id} not found")
                    return Response(
                        {"success": False, "error": "Job not found"},
                        status=status.HTTP_404_NOT_FOUND,
                    )

                job.status = status_value
                job.progress = 100.0 if status_value == "completed" else job.progress
                job.completed_at = timezone.now()
                job.save()

                # Update TimetableWorkflow
                workflow = TimetableWorkflow.objects.filter(job_id=job_id).first()
                if workflow:
                    workflow.status = (
                        "draft" if status_value == "completed" else "failed"
                    )
                    workflow.save()

                # Save variants (if completed)
                if status_value == "completed" and variants_data:
                    for variant_data in variants_data:
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
                        f"[DJANGO] Saved {len(variants_data)} variants for job {job_id}"
                    )

            return Response(
                {"success": True, "message": f"Job {job_id} updated successfully"}
            )

        except Exception as e:
            logger.error(f"[DJANGO] FastAPI callback error: {e}", exc_info=True)
            return Response(
                {"success": False, "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["get"], url_path="status")
    def get_status(self, request, pk=None):
        """
        Get current status and progress of a generation job
        GET /api/timetable/status/{job_id}/
        """
        try:
            job = self.get_object()

            # Check Redis for real-time progress
            cache_key = f"generation_progress:{job.job_id}"
            redis_progress = cache.get(cache_key)

            if redis_progress is not None:
                job.progress = redis_progress
                job.save(update_fields=["progress"])

            serializer = GenerationJobSerializer(job)
            return Response({"success": True, "job": serializer.data})

        except Exception as e:
            logger.error(f"Error fetching job status: {str(e)}")
            return Response(
                {"success": False, "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["get"], url_path="progress")
    def get_progress(self, request, pk=None):
        """
        Get real-time progress from Redis
        GET /api/timetable/progress/{job_id}/
        """
        try:
            job = self.get_object()
            cache_key = f"generation_progress:{job.job_id}"

            # Get progress from Redis
            progress = cache.get(cache_key)
            if progress is None:
                progress = job.progress

            return Response(
                {
                    "success": True,
                    "job_id": str(job.job_id),
                    "status": job.status,
                    "progress": progress,
                    "updated_at": job.updated_at.isoformat()
                    if job.updated_at
                    else None,
                }
            )

        except Exception as e:
            logger.error(f"Error fetching progress: {str(e)}")
            return Response(
                {"success": False, "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["post"], url_path="approve")
    def approve(self, request, pk=None):
        """
        Approve a completed generation job and publish timetable
        POST /api/timetable/approve/{job_id}/
        Body: { "action": "approve" | "reject", "comments": "..." }
        """
        if request.user.role not in ["admin", "staff"]:
            return Response(
                {
                    "success": False,
                    "error": "Only admin and staff can approve timetables",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            job = self.get_object()
            action_type = request.data.get("action", "approve")
            comments = request.data.get("comments", "")

            if job.status != "completed":
                return Response(
                    {
                        "success": False,
                        "error": "Can only approve/reject completed jobs",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if action_type == "approve":
                job.status = "approved"
                # Update associated timetable status
                Timetable.objects.filter(generation_job=job).update(
                    status="published", updated_at=timezone.now()
                )
                message = "Timetable approved and published"
            else:
                job.status = "rejected"
                message = "Timetable rejected"

            job.completed_at = timezone.now()
            job.save()

            serializer = GenerationJobSerializer(job)
            return Response(
                {"success": True, "message": message, "job": serializer.data}
            )

        except Exception as e:
            logger.error(f"Error approving job: {str(e)}")
            return Response(
                {"success": False, "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["get"], url_path="result")
    def get_result(self, request, pk=None):
        """
        Get generated timetable for a job
        GET /api/timetable/result/{job_id}/
        """
        try:
            job = self.get_object()

            if job.status not in ["completed", "approved"]:
                return Response(
                    {
                        "success": False,
                        "error": "Timetable generation not completed yet",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Get timetables for this job
            timetables = Timetable.objects.filter(generation_job=job).prefetch_related(
                "slots"
            )
            serializer = TimetableSerializer(timetables, many=True)

            return Response(
                {
                    "success": True,
                    "job_id": str(job.job_id),
                    "status": job.status,
                    "timetables": serializer.data,
                }
            )

        except Exception as e:
            logger.error(f"Error fetching timetable result: {str(e)}")
            return Response(
                {"success": False, "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _queue_generation_job(self, job):
        """
        Queue job in Redis for FastAPI worker to pick up
        """
        try:
            # Store job data in Redis queue
            cache_key = f"generation_queue:{job.job_id}"
            job_data = {
                "job_id": str(job.job_id),
                "department_id": job.department.department_id,
                "batch_id": job.batch.batch_id,
                "semester": job.semester,
                "academic_year": job.academic_year,
                "created_at": job.created_at.isoformat(),
            }
            cache.set(cache_key, job_data, timeout=3600)  # 1 hour

            # Trigger FastAPI service
            fastapi_url = os.getenv("FASTAPI_AI_SERVICE_URL", "http://localhost:8001")
            try:
                requests.post(
                    f"{fastapi_url}/api/generate/{job.job_id}", json=job_data, timeout=5
                )
                logger.info(f"Triggered FastAPI generation for job {job.job_id}")
            except requests.exceptions.RequestException as e:
                logger.warning(
                    f"Could not trigger FastAPI service: {e}. Job queued in Redis."
                )

        except Exception as e:
            logger.error(f"Error queuing job: {str(e)}")
            job.status = "failed"
            job.error_message = str(e)
            job.save()
