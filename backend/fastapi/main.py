"""
FastAPI Timetable Generation Service
Three-Stage Hybrid Architecture for NEP 2020-Compliant Timetabling
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import redis
import json
import asyncio
import logging
import uuid
from datetime import datetime
from typing import Dict

from models.timetable_models import GenerationRequest, GenerationResponse, TimetableResult
from models.progress_models import JobStatus, ProgressUpdate
from engine.orchestrator import TimetableOrchestrator
from utils.progress_tracker import ProgressTracker
from config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Sentry (if DSN configured)
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.redis import RedisIntegration

if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.SENTRY_ENVIRONMENT,
        integrations=[
            FastApiIntegration(),
            RedisIntegration(),
        ],
        traces_sample_rate=0.1,  # 10% of transactions for performance monitoring
        profiles_sample_rate=0.1,  # 10% for profiling
        before_send=lambda event, hint: event if settings.SENTRY_ENVIRONMENT != "development" else None,
    )
    logger.info(f"Sentry initialized for environment: {settings.SENTRY_ENVIRONMENT}")
else:
    logger.info("Sentry DSN not configured, exception tracking disabled")


# WebSocket connection manager
class ConnectionManager:
    """
    ENTERPRISE PATTERN: WebSocket connection pooling
    Manages real-time connections for progress streaming
    """
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, job_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[job_id] = websocket
        logger.info(f"WebSocket connected for job {job_id}")

    def disconnect(self, job_id: str):
        if job_id in self.active_connections:
            del self.active_connections[job_id]
            logger.info(f"WebSocket disconnected for job {job_id}")

    async def send_progress(self, job_id: str, progress: dict):
        if job_id in self.active_connections:
            try:
                await self.active_connections[job_id].send_json(progress)
            except Exception as e:
                logger.error(f"Failed to send progress to {job_id}: {e}")
                self.disconnect(job_id)


manager = ConnectionManager()


# Redis Pub/Sub for progress streaming
from utils.redis_pubsub import RedisPublisher, RedisSubscriber

# Prometheus metrics
from utils.metrics import setup_metrics, record_generation_request, record_generation_success, record_generation_failure


# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Timetable Generation Service...")
    logger.info(f"Redis URL: {settings.REDIS_URL}")
    logger.info(f"Django API URL: {settings.DJANGO_API_BASE_URL}")

    # Test Redis connection
    try:
        app.state.redis_client.ping()
        logger.info("Redis connection successful")
    except Exception as e:
        logger.error(f"Redis connection failed: {e}")

    yield

    # Shutdown
    logger.info("Shutting down Timetable Generation Service...")


# Initialize FastAPI app
app = FastAPI(
    title="Timetable Generation Engine",
    description="Three-Stage Hybrid NEP 2020-Compliant Timetabling System",
    version="2.0.0",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redis connection
app.state.redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

# Setup Prometheus metrics
setup_metrics(app)


# =============================================================================
# BACKGROUND TASK: Timetable Generation
# =============================================================================

async def run_timetable_generation(request: GenerationRequest, job_id: str):
    """Background task to run timetable generation"""
    orchestrator = TimetableOrchestrator(job_id, app.state.redis_client)

    try:
        result = await orchestrator.generate_timetable(
            department_id=request.department_id,
            batch_ids=request.batch_ids,
            semester=request.semester
        )

        # Cache result in Redis
        result_key = f"timetable:result:{job_id}"
        app.state.redis_client.setex(
            result_key,
            settings.RESULT_EXPIRE_SECONDS,
            json.dumps(result)
        )

    except Exception as e:
        logger.error(f"Timetable generation failed: {str(e)}")
        raise


async def run_variant_generation(request: GenerationRequest, job_id: str, num_variants: int = 5):
    """
    ENTERPRISE PATTERN: Background task with Django callback

    Generate multiple timetable variants and notify Django when complete.

    **Flow:**
    1. Generate variants (5-10 min with adaptive parallelism)
    2. Update progress to Redis every 5 seconds
    3. Call Django callback endpoint with results
    4. Django saves variants to PostgreSQL
    5. Django updates workflow status
    """
    from engine.variant_generator import VariantGenerator
    import httpx

    # Store original settings
    original_settings = {
        'soft_constraint_weights': {
            'faculty_preference': settings.WEIGHT_FACULTY_PREFERENCE,
            'compactness': settings.WEIGHT_COMPACTNESS,
            'room_utilization': settings.WEIGHT_ROOM_UTILIZATION,
            'workload_balance': settings.WEIGHT_WORKLOAD_BALANCE,
            'peak_spreading': settings.WEIGHT_PEAK_SPREADING,
            'continuity': settings.WEIGHT_CONTINUITY
        }
    }

    generator = VariantGenerator(job_id, app.state.redis_client, original_settings)
    start_time = datetime.utcnow()

    try:
        logger.info(f"[FASTAPI] Starting variant generation for job {job_id}")

        # STEP 1: Generate variants (5-10 minutes)
        variants = await generator.generate_variants(
            department_id=request.department_id,
            batch_ids=request.batch_ids,
            semester=request.semester,
            academic_year=request.academic_year,
            organization_id=request.organization_id,
            num_variants=num_variants
        )

        generation_time = (datetime.utcnow() - start_time).total_seconds()

        # STEP 2: Cache variants in Redis (temporary, 1 hour)
        result_key = f"timetable:variants:{job_id}"
        app.state.redis_client.setex(
            result_key,
            settings.RESULT_EXPIRE_SECONDS,
            json.dumps({
                'variants': variants,
                'comparison': generator.compare_variants(),
                'generation_time': generation_time
            })
        )

        logger.info(f"[FASTAPI] Generation complete for job {job_id} in {generation_time:.1f}s")

        # STEP 3: Call Django callback (save to PostgreSQL)
        await _call_django_callback(
            job_id=job_id,
            status='completed',
            variants=variants,
            generation_time=generation_time
        )

    except Exception as e:
        logger.error(f"[FASTAPI] Generation failed for job {job_id}: {e}", exc_info=True)

        # Notify Django of failure
        await _call_django_callback(
            job_id=job_id,
            status='failed',
            error=str(e)
        )


async def _call_django_callback(job_id: str, status: str, variants: list = None, generation_time: float = 0.0, error: str = None):
    """
    ENTERPRISE PATTERN: Celery Callback Task

    Queue callback task to Django via Celery (not direct HTTP call).

    **Why Celery Callback:**
    - Decouples FastAPI from Django database writes
    - Automatic retries if Django/database is down
    - Non-blocking (FastAPI worker freed immediately)
    - Task queue prevents thundering herd
    - Better fault tolerance

    **Architecture:**
    FastAPI → Celery Queue → Celery Worker → Django Database
    """
    try:
        # Connect to Celery broker
        from celery import Celery

        celery_app = Celery(
            'timetable',
            broker=settings.CELERY_BROKER_URL or 'redis://localhost:6379/0'
        )

        payload = {
            'job_id': job_id,
            'status': status,
            'generation_time': generation_time
        }

        if status == 'completed' and variants:
            payload['variants'] = variants

        if status == 'failed' and error:
            payload['error'] = error

        logger.info(f"[FASTAPI] Queueing Django callback for job {job_id}, status: {status}")

        # Queue callback task (async, non-blocking)
        task = celery_app.send_task(
            'tasks.django_callback',
            args=[job_id, status],
            kwargs={'variants': variants, 'error': error},
            queue='callbacks',
            priority=10,
        )

        logger.info(f"[FASTAPI] Callback task {task.id} queued for job {job_id}")

    except Exception as e:
        logger.error(f"[FASTAPI] Failed to queue callback for job {job_id}: {e}", exc_info=True)

        # Fallback to direct HTTP call (if Celery is down)
        await _call_django_callback_http(job_id, status, variants, generation_time, error)


async def _call_django_callback_http(job_id: str, status: str, variants: list = None, generation_time: float = 0.0, error: str = None):
    """
    Fallback: Direct HTTP callback (if Celery is unavailable).
    """
    import httpx

    try:
        DJANGO_URL = settings.DJANGO_API_BASE_URL
        callback_url = f"{DJANGO_URL}/api/academics/timetable/fastapi_callback/"

        payload = {
            'job_id': job_id,
            'status': status,
            'generation_time': generation_time
        }

        if status == 'completed' and variants:
            payload['variants'] = variants

        if status == 'failed' and error:
            payload['error'] = error

        logger.warning(f"[FASTAPI] Using fallback HTTP callback for job {job_id}")

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(callback_url, json=payload)

            if response.status_code == 200:
                logger.info(f"[FASTAPI] Fallback callback successful for job {job_id}")
            else:
                logger.error(f"[FASTAPI] Fallback callback failed: {response.status_code} - {response.text}")

    except Exception as e:
        logger.error(f"[FASTAPI] Fallback callback error for job {job_id}: {e}", exc_info=True)


# =============================================================================
# API ENDPOINTS
# =============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        app.state.redis_client.ping()
        return {
            "service": "Timetable Generation Engine",
            "status": "healthy",
            "redis": "connected",
            "version": "2.0.0",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "service": "Timetable Generation Engine",
            "status": "unhealthy",
            "redis": f"disconnected: {str(e)}",
            "version": "2.0.0",
            "timestamp": datetime.utcnow().isoformat()
        }


@app.post("/api/generate", response_model=GenerationResponse)
async def generate_timetable(request: GenerationRequest, background_tasks: BackgroundTasks):
    """
    **Main Endpoint: Generate Timetable**

    Initiates three-stage hybrid timetable generation:
    - Stage 1: Constraint Graph Clustering (Louvain)
    - Stage 2: Parallel Hybrid Micro-Scheduling (CP-SAT + GA)
    - Stage 3: RL-Based Global Conflict Resolution

    **Flow:**
    1. User clicks "Generate Timetable" in frontend
    2. Frontend calls this endpoint with form data
    3. Returns job_id immediately
    4. Generation runs in background
    5. Frontend polls /api/status/{job_id} or connects via WebSocket
    6. Progress bar updates in real-time

    **Returns:**
    - job_id: Unique identifier to track generation
    - estimated_time_seconds: Expected completion time (5-10 minutes)
    """
    try:
        # Generate unique job ID
        job_id = f"timetable_{uuid.uuid4().hex[:12]}"

        logger.info(f"=" * 80)
        logger.info(f"NEW GENERATION REQUEST - Job ID: {job_id}")
        logger.info(f"Organization: {request.organization_id}")
        logger.info(f"Department: {request.department_id}")
        logger.info(f"Batches: {request.batch_ids}")
        logger.info(f"Semester: {request.semester} | Year: {request.academic_year}")
        logger.info(f"=" * 80)

        # Start background generation
        background_tasks.add_task(run_timetable_generation, request, job_id)

        # Estimate time based on number of batches (simplified)
        estimated_seconds = 300 + (len(request.batch_ids) * 60)  # Base 5min + 1min per batch

        return GenerationResponse(
            job_id=job_id,
            status="queued",
            message="Timetable generation started. Connect via WebSocket for real-time updates.",
            estimated_time_seconds=estimated_seconds
        )

    except Exception as e:
        logger.error(f"Failed to start generation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to start generation: {str(e)}")


@app.post("/api/generate_variants", response_model=GenerationResponse)
async def generate_timetable_variants(
    request: GenerationRequest,
    background_tasks: BackgroundTasks,
    num_variants: int = 5
):
    """
    ENTERPRISE PATTERN: FastAPI as Compute Engine

    **Generate Multiple Timetable Variants**

    This endpoint is called BY DJANGO (not directly by frontend).
    Django creates the job_id and workflow record FIRST, then calls this endpoint.

    Generates 3-5 optimized timetables with different optimization priorities:
    - Variant 1: Balanced (all constraints equally weighted)
    - Variant 2: Faculty-focused (maximize faculty preferences)
    - Variant 3: Compactness-focused (minimize student travel)
    - Variant 4: Room-efficient (maximize room utilization)
    - Variant 5: Workload-balanced (minimize faculty variance)

    **Flow:**
    1. Django calls this endpoint with job_id
    2. FastAPI accepts request immediately (returns 200)
    3. FastAPI runs generation in background (5-10 min)
    4. FastAPI updates progress to Redis (real-time)
    5. FastAPI calls Django callback with results

    **Returns:**
    - job_id: Django's job_id (passed in request, NOT generated here)
    - status: "queued" (immediately)
    - estimated_time_seconds: Expected completion time (5-10 minutes with parallelism)
    """
    try:
        # ENTERPRISE: Use Django's job_id (passed in request)
        # If not provided, generate one (backward compatibility)
        job_id = request.job_id if hasattr(request, 'job_id') and request.job_id else f"variants_{uuid.uuid4().hex[:12]}"

        logger.info(f"=" * 80)
        logger.info(f"[FASTAPI] RECEIVED GENERATION REQUEST - Job ID: {job_id}")
        logger.info(f"Organization: {request.organization_id}")
        logger.info(f"Department: {request.department_id}")
        logger.info(f"Num Variants: {num_variants}")
        logger.info(f"Batches: {request.batch_ids}")
        logger.info(f"=" * 80)

        # Start background variant generation
        background_tasks.add_task(run_variant_generation, request, job_id, num_variants)

        # Estimate time based on hardware (adaptive parallelism)
        # Render free tier: 10-15 min, Laptop: 5-7 min, Workstation: 5-6 min
        estimated_seconds = 600  # Conservative estimate (10 min)

        return GenerationResponse(
            job_id=job_id,
            status="queued",
            message=f"Generating {num_variants} timetable variants with resource-aware parallelism.",
            estimated_time_seconds=estimated_seconds
        )

    except Exception as e:
        logger.error(f"[FASTAPI] Failed to start variant generation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to start variant generation: {str(e)}")


@app.get("/api/variants/{job_id}")
async def get_variants(job_id: str):
    """
    **Get Generated Variants**

    Retrieve all generated timetable variants with comparison data.
    Call this after variant generation is complete.
    """
    try:
        result_key = f"timetable:variants:{job_id}"
        result_json = app.state.redis_client.get(result_key)

        if not result_json:
            raise HTTPException(
                status_code=404,
                detail=f"Variants for job {job_id} not found. Generation may still be running or results expired."
            )

        return json.loads(result_json)

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse variants: {e}")
        raise HTTPException(status_code=500, detail="Failed to parse variant data")
    except Exception as e:
        logger.error(f"Failed to retrieve variants: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/status/{job_id}", response_model=JobStatus)
async def get_job_status(job_id: str):
    """
    **Get Job Status**

    Poll this endpoint to check generation progress.
    Frontend should call this every 2-3 seconds to update progress bar.

    **Alternative:** Use WebSocket `/ws/{job_id}` for push-based updates.
    """
    try:
        tracker = ProgressTracker(job_id, app.state.redis_client)
        progress = tracker.get_progress()

        if not progress:
            raise HTTPException(
                status_code=404,
                detail=f"Job {job_id} not found. It may have expired or never existed."
            )

        return JobStatus(
            job_id=job_id,
            status=progress.stage,
            progress=progress,
            error=None
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/result/{job_id}")
async def get_timetable_result(job_id: str):
    """
    Get Generated Timetable

    Call this after status shows completed to retrieve the final timetable.
    Result is cached in Redis for 24 hours.
    """
    try:
        # Get result from Redis
        result_key = f"timetable:result:{job_id}"
        result_data = app.state.redis_client.get(result_key)

        if not result_data:
            raise HTTPException(
                status_code=404,
                detail=f"Result for job {job_id} not found or expired."
            )

        result = json.loads(result_data)
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting result: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# WEBSOCKET ENDPOINT - Real-time Progress Updates
# =============================================================================

@app.websocket("/ws/progress/{job_id}")
async def websocket_progress(websocket: WebSocket, job_id: str):
    """
    ENTERPRISE PATTERN: WebSocket + Redis Pub/Sub for Real-Time Progress

    **Architecture:**
    ```
    Algorithm → Redis Pub/Sub → WebSocket → Frontend
    ```

    **Frontend Usage:**
    ```javascript
    const ws = new WebSocket(`ws://localhost:8001/ws/progress/${jobId}`);

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      updateProgressBar(data.progress);  // 0-100
      updateStatusText(data.status);     // Human-readable message
      updateETA(data.eta_seconds);       // Seconds remaining
      updatePhase(data.phase);           // Current algorithm phase
    };

    ws.onclose = () => {
      console.log("Generation complete or connection lost");
    };
    ```

    **Benefits:**
    - Push-based updates (instant, no polling)
    - Percentage + ETA from instrumented algorithm
    - Phase transitions (clustering → solving → optimizing)
    - Automatic reconnection on disconnect
    """
    await manager.connect(job_id, websocket)

    # Create Redis subscriber for this job
    subscriber = RedisSubscriber(app.state.redis_client)

    try:
        # Subscribe to job's progress channel
        subscriber.subscribe(job_id)
        logger.info(f"WebSocket subscribed to progress:{job_id}")

        # Send current progress immediately (if available)
        progress_key = f"progress:job:{job_id}"
        current_progress = app.state.redis_client.hget(f"job:{job_id}:progress", 'data')
        if current_progress:
            await websocket.send_text(current_progress)

        # Listen for progress updates from Redis Pub/Sub
        for message in subscriber.listen():
            try:
                await websocket.send_json(message)

                # Close connection if generation completed/failed
                if message.get('status') in ['completed', 'failed']:
                    logger.info(f"Job {job_id} finished: {message.get('status')}")
                    break

            except WebSocketDisconnect:
                logger.info(f"WebSocket disconnected for job {job_id}")
                break
            except Exception as e:
                logger.error(f"Error sending progress update: {e}")
                break

    except WebSocketDisconnect:
        logger.info(f"Client disconnected from job {job_id}")
    except Exception as e:
        logger.error(f"WebSocket error for job {job_id}: {e}", exc_info=True)
    finally:
        # Cleanup
        subscriber.unsubscribe(job_id)
        subscriber.close()
        manager.disconnect(job_id)


# =============================================================================
# DEVELOPMENT/DEBUG ENDPOINTS
# =============================================================================

@app.get("/api/config")
async def get_config():
    """Get current configuration (for debugging)"""
    return {
        "cpsat_timeout": settings.CPSAT_TIMEOUT_SECONDS,
        "ga_population": settings.GA_POPULATION_SIZE,
        "ga_generations": settings.GA_GENERATIONS,
        "weights": {
            "faculty_preference": settings.WEIGHT_FACULTY_PREFERENCE,
            "compactness": settings.WEIGHT_COMPACTNESS,
            "room_utilization": settings.WEIGHT_ROOM_UTILIZATION,
            "workload_balance": settings.WEIGHT_WORKLOAD_BALANCE,
            "peak_spreading": settings.WEIGHT_PEAK_SPREADING,
            "continuity": settings.WEIGHT_CONTINUITY
        }
    }


@app.delete("/api/job/{job_id}")
async def cancel_job(job_id: str):
    """Cancel a running job (best effort)"""
    try:
        # Remove progress and result from Redis
        progress_key = f"timetable:progress:{job_id}"
        result_key = f"timetable:result:{job_id}"

        app.state.redis_client.delete(progress_key)
        app.state.redis_client.delete(result_key)

        return {"message": f"Job {job_id} cancelled", "success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# SERVER STARTUP
# =============================================================================

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info",
        ws_ping_interval=20,
        ws_ping_timeout=20
    )
