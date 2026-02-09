"""
Request Models
Pydantic models for API requests
"""
from pydantic import BaseModel, Field
from typing import Optional


class TimeConfig(BaseModel):
    """Time configuration for timetable generation"""
    working_days: int = Field(default=6, ge=1, le=7, description="Number of working days per week")
    slots_per_day: int = Field(default=9, ge=1, le=15, description="Number of time slots per day")
    start_time: str = Field(default="09:00", description="Start time in HH:MM format")
    slot_duration_minutes: int = Field(default=60, ge=30, le=180, description="Duration of each slot in minutes")


class GenerationRequest(BaseModel):
    """Timetable generation request"""
    organization_id: str = Field(..., description="Organization ID or name")
    semester: int = Field(..., ge=1, le=12, description="Semester number")
    time_config: Optional[TimeConfig] = Field(None, description="Optional time configuration")


class CacheInvalidationRequest(BaseModel):
    """Cache invalidation request"""
    organization_id: str = Field(..., description="Organization ID")
    resource_type: str = Field(default="all", description="Resource type to invalidate")
    semester: Optional[int] = Field(None, description="Semester for course cache")
