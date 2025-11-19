"""
Progress Tracking Models
"""
from pydantic import BaseModel
from typing import Optional, Dict
from enum import Enum


class GenerationStage(str, Enum):
    INITIALIZING = "initializing"
    FETCHING_DATA = "fetching_data"
    BUILDING_GRAPH = "building_graph"
    CLUSTERING = "clustering"
    CPSAT_SOLVING = "cpsat_solving"
    GA_OPTIMIZATION = "ga_optimization"
    RL_RESOLUTION = "rl_resolution"
    FINALIZING = "finalizing"
    COMPLETED = "completed"
    FAILED = "failed"


class ProgressUpdate(BaseModel):
    """Real-time progress update"""
    job_id: str
    stage: GenerationStage
    progress_percent: float  # 0.0 to 100.0
    current_step: str
    time_elapsed_seconds: float
    estimated_time_remaining_seconds: Optional[float] = None
    details: Optional[Dict] = None

    class Config:
        json_schema_extra = {
            "example": {
                "job_id": "job_123",
                "stage": "ga_optimization",
                "progress_percent": 45.5,
                "current_step": "Optimizing cluster 3 of 8",
                "time_elapsed_seconds": 120.5,
                "estimated_time_remaining_seconds": 143.2,
                "details": {
                    "clusters_completed": 2,
                    "total_clusters": 8,
                    "current_fitness": 0.78
                }
            }
        }


class JobStatus(BaseModel):
    """Job status query response"""
    job_id: str
    status: GenerationStage
    progress: ProgressUpdate
    error: Optional[str] = None
