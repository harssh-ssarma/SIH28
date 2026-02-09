"""
Response Models
Pydantic models for API responses
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class GenerationResponse(BaseModel):
    """Timetable generation response"""
    job_id: str = Field(..., description="Unique job identifier for tracking")
    status: str = Field(..., description="Job status: started, running, completed, failed")
    message: str = Field(..., description="Human-readable message")
    estimated_time_minutes: Optional[int] = Field(None, description="Estimated completion time in minutes")


class StatusResponse(BaseModel):
    """Job status response"""
    job_id: str
    status: str
    progress: Optional[int] = None
    stage: Optional[str] = None
    message: Optional[str] = None
    eta: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response"""
    service: str
    status: str
    timestamp: str
    redis: Optional[str] = None
    version: Optional[str] = None


class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    message: str
    error_id: Optional[str] = None
    timestamp: Optional[str] = None
