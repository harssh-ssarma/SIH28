"""
Timetable Generation Router
Handles main timetable generation requests
"""
from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict
import logging
import uuid

from api.deps import get_redis_client, get_hardware_profile

router = APIRouter(prefix="/api", tags=["generation"])
logger = logging.getLogger(__name__)


class TimeConfig(BaseModel):
    """Time configuration model"""
    working_days: int = 6
    slots_per_day: int = 9
    start_time: str = "09:00"
    slot_duration_minutes: int = 60


class GenerationRequest(BaseModel):
    """Timetable generation request model"""
    organization_id: str
    semester: int
    time_config: Optional[TimeConfig] = None


class GenerationResponse(BaseModel):
    """Timetable generation response model"""
    job_id: str
    status: str
    message: str
    estimated_time_minutes: Optional[int] = None


@router.post("/generate", response_model=GenerationResponse)
async def generate_timetable(
    request: GenerationRequest,
    background_tasks: BackgroundTasks,
    redis = Depends(get_redis_client),
    hardware_profile = Depends(get_hardware_profile)
):
    """
    Generate timetable using adaptive multi-stage algorithm.
    
    This endpoint starts an asynchronous timetable generation job.
    Progress can be tracked via WebSocket at /ws/progress/{job_id}
    
    Args:
        request: Generation request with organization_id and semester
        background_tasks: FastAPI background tasks
        redis: Redis client for job tracking
        hardware_profile: Detected hardware profile
        
    Returns:
        Job ID and estimated completion time
    """
    try:
        # Generate unique job ID
        job_id = str(uuid.uuid4())
        
        logger.info(f"[GENERATION] New job {job_id} for org {request.organization_id}, semester {request.semester}")
        
        # Get estimated time based on hardware
        from engine.hardware import get_optimal_config
        optimal_config = get_optimal_config(hardware_profile)
        estimated_minutes = optimal_config.get('expected_time_minutes', 10)
        
        # Import generation service
        from core.services.generation_service import GenerationService
        
        service = GenerationService(redis, hardware_profile)
        
        # Start generation in background
        background_tasks.add_task(
            service.generate_timetable,
            job_id=job_id,
            organization_id=request.organization_id,
            semester=request.semester,
            time_config=request.time_config.dict() if request.time_config else None
        )
        
        return GenerationResponse(
            job_id=job_id,
            status="started",
            message="Timetable generation started",
            estimated_time_minutes=estimated_minutes
        )
        
    except Exception as e:
        logger.error(f"[GENERATION] Failed to start: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/preview")
async def preview_generation(
    organization_id: str,
    semester: int,
    redis = Depends(get_redis_client)
):
    """
    Preview generation parameters before starting.
    
    Returns data counts and estimated time without starting generation.
    """
    try:
        from utils.django_client import DjangoAPIClient
        from engine.hardware import get_hardware_profile, get_optimal_config
        
        django_client = DjangoAPIClient(redis_client=redis)
        
        # Resolve org_id
        org_id = django_client.resolve_org_id(organization_id)
        
        # Fetch data counts
        courses = await django_client.fetch_courses(org_id, semester)
        faculty = await django_client.fetch_faculty(org_id)
        rooms = await django_client.fetch_rooms(org_id)
        time_slots = await django_client.fetch_time_slots(org_id, None)
        students = await django_client.fetch_students(org_id)
        
        # Get hardware estimates
        hardware = get_hardware_profile()
        config = get_optimal_config(hardware)
        
        await django_client.close()
        
        return {
            "organization_id": org_id,
            "semester": semester,
            "data": {
                "courses": len(courses),
                "faculty": len(faculty),
                "rooms": len(rooms),
                "time_slots": len(time_slots),
                "students": len(students)
            },
            "estimation": {
                "time_minutes": config.get('expected_time_minutes', 10),
                "strategy": hardware.optimal_strategy.value,
                "hardware_tier": config.get('tier', 'unknown')
            }
        }
        
    except Exception as e:
        logger.error(f"[PREVIEW] Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
