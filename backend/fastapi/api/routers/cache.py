"""
Cache Management Router
Handles cache operations, invalidation, and statistics
"""
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timezone
from typing import Optional
import logging

from api.deps import get_redis_client, get_django_client
from pydantic import BaseModel

router = APIRouter(prefix="/api/cache", tags=["cache"])
logger = logging.getLogger(__name__)


class CacheInvalidationRequest(BaseModel):
    """Request model for cache invalidation"""
    organization_id: str
    resource_type: str = "all"  # courses|faculty|rooms|students|time_slots|config|all
    semester: Optional[int] = None


@router.post("/invalidate")
async def invalidate_cache(
    request: CacheInvalidationRequest,
    redis = Depends(get_redis_client),
    client = Depends(get_django_client)
):
    """
    Invalidate cache when frontend updates data.
    
    Request body:
    {
        "organization_id": "uuid",
        "resource_type": "courses|faculty|rooms|students|time_slots|config|all",
        "semester": 1  // optional, for courses
    }
    """
    try:
        org_id = request.organization_id
        resource_type = request.resource_type
        
        if not org_id:
            raise HTTPException(status_code=400, detail="organization_id is required")
        
        if resource_type == 'all':
            # Invalidate all resources for this org
            await client.cache_manager.invalidate_pattern(f"*:{org_id}:*")
            logger.info(f"[CACHE] Invalidated ALL cache for org {org_id}")
            return {
                "status": "success",
                "message": f"All cache invalidated for org {org_id}"
            }
        
        # Invalidate specific resource
        if resource_type == 'courses':
            await client.cache_manager.invalidate('courses', org_id, semester=request.semester)
        else:
            await client.cache_manager.invalidate(resource_type, org_id)
        
        logger.info(f"[CACHE] Invalidated {resource_type} cache for org {org_id}")
        return {
            "status": "success",
            "message": f"{resource_type} cache invalidated",
            "organization_id": org_id
        }
        
    except Exception as e:
        logger.error(f"[CACHE] Invalidation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_cache_stats(
    organization_id: Optional[str] = None,
    client = Depends(get_django_client)
):
    """
    Get cache statistics.
    
    Returns:
        Cache hit/miss rates, size, and performance metrics
    """
    try:
        stats = client.cache_manager.get_stats()
        
        return {
            "status": "success",
            "stats": stats,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"[CACHE] Stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/warm")
async def warm_cache(
    request: CacheInvalidationRequest,
    client = Depends(get_django_client)
):
    """
    Pre-load cache with frequently accessed data.
    
    Warms cache for specified organization to improve response times.
    """
    try:
        org_id = request.organization_id
        
        if not org_id:
            raise HTTPException(status_code=400, detail="organization_id is required")
        
        result = await client.cache_manager.warm_cache(org_id, client)
        
        return {
            "status": "success",
            "message": "Cache warmed successfully",
            "result": result
        }
        
    except Exception as e:
        logger.error(f"[CACHE] Warming error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
