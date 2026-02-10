"""
Conflict Resolution Router
Handles timetable conflict detection and resolution
"""
from fastapi import APIRouter, HTTPException, Depends
import logging

from api.deps import get_django_client

router = APIRouter(prefix="/api/conflicts", tags=["conflicts"])
logger = logging.getLogger(__name__)


@router.get("/detect")
async def detect_conflicts(timetable_id: str, client = Depends(get_django_client)):
    """
    Detect all conflicts in timetable.
    
    Args:
        timetable_id: Timetable identifier
        
    Returns:
        List of detected conflicts with details
    """
    try:
        from services.conflict_resolution_service import ConflictResolutionService
        
        # Fetch timetable data
        timetable = await client.fetch_timetable(timetable_id)
        courses = await client.fetch_all_courses(timetable_id)
        rooms = await client.fetch_all_rooms(timetable_id)
        time_slots = await client.fetch_all_time_slots(timetable_id)
        faculty = await client.fetch_all_faculty(timetable_id)
        
        # Detect conflicts
        service = ConflictResolutionService(timetable, courses, rooms, time_slots, faculty)
        conflicts = service.detect_all_conflicts()
        
        await client.close()
        
        return {
            "conflicts": [c.dict() for c in conflicts],
            "total": len(conflicts),
            "timetable_id": timetable_id
        }
        
    except Exception as e:
        logger.error(f"Conflict detection error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/resolve")
async def resolve_conflicts(
    timetable_id: str,
    auto_resolve: bool = True,
    client = Depends(get_django_client)
):
    """
    Resolve conflicts automatically with hierarchical approach.
    
    Args:
        timetable_id: Timetable identifier
        auto_resolve: Whether to automatically resolve conflicts
        
    Returns:
        Resolution results with statistics
    """
    try:
        from services.conflict_resolution_service import ConflictResolutionService
        
        # Fetch timetable data
        timetable = await client.fetch_timetable(timetable_id)
        courses = await client.fetch_all_courses(timetable_id)
        rooms = await client.fetch_all_rooms(timetable_id)
        time_slots = await client.fetch_all_time_slots(timetable_id)
        faculty = await client.fetch_all_faculty(timetable_id)
        
        service = ConflictResolutionService(timetable, courses, rooms, time_slots, faculty)
        
        if auto_resolve:
            results = service.resolve_all_conflicts()
        else:
            conflicts = service.detect_all_conflicts()
            results = {
                'total': len(conflicts),
                'resolved': 0,
                'manual_review': len(conflicts)
            }
        
        await client.close()
        
        return results
        
    except Exception as e:
        logger.error(f"Conflict resolution error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/resolve/{conflict_id}")
async def resolve_single_conflict(
    conflict_id: str,
    timetable_id: str,
    client = Depends(get_django_client)
):
    """
    Resolve single conflict with hierarchical approach.
    
    Args:
        conflict_id: Conflict identifier
        timetable_id: Timetable identifier
        
    Returns:
        Resolution result for specific conflict
    """
    try:
        from services.conflict_resolution_service import ConflictResolutionService
        
        # Fetch timetable data
        timetable = await client.fetch_timetable(timetable_id)
        courses = await client.fetch_all_courses(timetable_id)
        rooms = await client.fetch_all_rooms(timetable_id)
        time_slots = await client.fetch_all_time_slots(timetable_id)
        faculty = await client.fetch_all_faculty(timetable_id)
        
        service = ConflictResolutionService(timetable, courses, rooms, time_slots, faculty)
        conflicts = service.detect_all_conflicts()
        
        # Find specific conflict
        conflict = next((c for c in conflicts if c.conflict_id == conflict_id), None)
        if not conflict:
            raise HTTPException(status_code=404, detail="Conflict not found")
        
        result = service.resolve_conflict(conflict)
        
        await client.close()
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Single conflict resolution error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
