"""
Data Models Package
Contains all Pydantic models for the application
"""
from .timetable_models import (
    Course,
    Faculty,
    Room,
    TimeSlot,
    Student,
    Batch,
    CourseType
)
from .request_models import (
    TimeConfig,
    GenerationRequest,
    CacheInvalidationRequest
)
from .response_models import (
    GenerationResponse,
    StatusResponse,
    HealthResponse,
    ErrorResponse
)

__all__ = [
    # Domain models
    'Course',
    'Faculty',
    'Room',
    'TimeSlot',
    'Student',
    'Batch',
    'CourseType',
    # Request models
    'TimeConfig',
    'GenerationRequest',
    'CacheInvalidationRequest',
    # Response models
    'GenerationResponse',
    'StatusResponse',
    'HealthResponse',
    'ErrorResponse'
]
