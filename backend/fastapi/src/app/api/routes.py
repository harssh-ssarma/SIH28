from fastapi import APIRouter, HTTPException
from ..schemas.timetable import OptimizationRequest, OptimizationResponse
from ..ai_engine.optimizer import TimetableOptimizer

router = APIRouter()

@router.post("/optimize", response_model=OptimizationResponse)
async def optimize_timetable(request: OptimizationRequest):
    """
    Optimize timetable based on given constraints and requirements
    """
    try:
        optimizer = TimetableOptimizer()
        result = optimizer.optimize(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")

@router.get("/status")
async def get_status():
    """
    Get the status of the AI optimization service
    """
    return {
        "service": "AI Optimization Engine",
        "status": "running",
        "version": "1.0.0"
    }