"""
Dependency Injection Layer - Industry Standard
Provides reusable dependencies for FastAPI endpoints
"""
import redis
from fastapi import Depends, HTTPException, Request
from typing import Optional
import logging

logger = logging.getLogger(__name__)


# ==================== Redis Dependencies ====================

async def get_redis_client(request: Request) -> redis.Redis:
    """
    Get Redis client from app state.
    Used for caching, progress tracking, and message queuing.
    
    Usage:
        @app.get("/endpoint")
        async def endpoint(redis: Redis = Depends(get_redis_client)):
            ...
    """
    if not hasattr(request.app.state, "redis_client") or request.app.state.redis_client is None:
        raise HTTPException(status_code=503, detail="Redis not available")
    return request.app.state.redis_client


# ==================== Hardware Profile Dependencies ====================

async def get_hardware_profile(request: Request):
    """
    Get hardware profile from app state.
    Contains detected CPU, GPU, RAM information for adaptive execution.
    
    Usage:
        @app.get("/endpoint")
        async def endpoint(hw: HardwareProfile = Depends(get_hardware_profile)):
            ...
    """
    if not hasattr(request.app.state, "hardware_profile"):
        from engine.hardware import get_hardware_profile as detect_hardware
        request.app.state.hardware_profile = detect_hardware()
    return request.app.state.hardware_profile


async def get_adaptive_executor(request: Request):
    """
    Get adaptive executor from app state.
    Handles hardware-adaptive algorithm selection.
    """
    if not hasattr(request.app.state, "adaptive_executor"):
        from engine.adaptive_executor import get_adaptive_executor as create_executor
        request.app.state.adaptive_executor = create_executor()
    return request.app.state.adaptive_executor


# ==================== Service Dependencies ====================

async def get_generation_service(
    redis: redis.Redis = Depends(get_redis_client),
    hardware_profile = Depends(get_hardware_profile)
):
    """
    Get timetable generation service.
    
    Usage:
        @app.post("/generate")
        async def generate(service = Depends(get_generation_service)):
            ...
    """
    from core.services.generation_service import GenerationService
    return GenerationService(redis, hardware_profile)


# ==================== Database Client Dependencies ====================

async def get_django_client(redis: redis.Redis = Depends(get_redis_client)):
    """
    Get Django API client for database access.
    
    Usage:
        @app.get("/data")
        async def get_data(client = Depends(get_django_client)):
            ...
    """
    from utils.django_client import DjangoAPIClient
    return DjangoAPIClient(redis_client=redis)


# ==================== Resource Isolation Dependencies ====================

async def get_resource_isolation(request: Request):
    """Get resource isolation context (Bulkhead pattern)"""
    if not hasattr(request.app.state, "resource_isolation"):
        from core.patterns.bulkhead import ResourceIsolation
        request.app.state.resource_isolation = ResourceIsolation()
    return request.app.state.resource_isolation


# ==================== Rate Limiting Dependencies ====================

async def get_rate_limiter():
    """
    Get rate limiter instance.
    Note: Rate limiting is also applied at middleware level.
    Use this dependency for custom rate limit checks in specific endpoints.
    
    Usage:
        @app.post("/expensive-operation")
        async def operation(limiter = Depends(get_rate_limiter)):
            limiter.check_rate_limit("custom-key")
            ...
    """
    from engine.rate_limiter import rate_limiter
    return rate_limiter
