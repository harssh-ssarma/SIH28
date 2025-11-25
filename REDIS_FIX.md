# Redis Progress Update Fix

## Problem
FastAPI was logging progress updates but they weren't reaching Redis. Django showed progress = 0 while FastAPI terminal showed progress updates.

## Root Cause
The `_update_progress()` method in `TimetableGenerationSaga` class was trying to access `app.state.redis_client`, but this caused issues because:
1. Circular import when trying to import `app` inside the class
2. The Redis client wasn't accessible from within the Saga class methods

## Solution
Created a global `redis_client_global` variable that's set during app startup and accessible from anywhere.

### Changes Made

#### 1. Added Global Variable (Line ~48)
```python
# Global hardware profile and executor
hardware_profile: Optional[HardwareProfile] = None
adaptive_executor: Optional[AdaptiveExecutor] = None
redis_client_global = None  # ✅ NEW
```

#### 2. Set Global in Lifespan (Line ~660)
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    global redis_client_global  # ✅ NEW
    
    # ... Redis initialization code ...
    
    redis_client_global = app.state.redis_client  # ✅ NEW
    app.state.redis_client.ping()
    logger.info("✅ Redis connection successful")
```

#### 3. Updated _update_progress() Method (Line ~621)
```python
async def _update_progress(self, job_id: str, progress: int, message: str):
    """Update job progress with better error handling"""
    global redis_client_global  # ✅ NEW
    try:
        if redis_client_global:  # ✅ Changed from app.state.redis_client
            progress_data = {
                'job_id': job_id,
                'progress': progress,
                'status': 'running',
                'stage': message,
                'message': message,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            redis_client_global.setex(  # ✅ Changed
                f"progress:job:{job_id}",
                3600,
                json.dumps(progress_data)
            )
            logger.info(f"[PROGRESS] ✅ Redis updated: {job_id} -> {progress}% - {message}")
        else:
            logger.error(f"[PROGRESS] ❌ Redis client not available")
    except Exception as e:
        logger.error(f"[PROGRESS] ❌ Failed to update Redis: {e}")
        import traceback
        logger.error(traceback.format_exc())
```

#### 4. Updated generate_variants_enterprise() (Line ~932)
```python
@app.post("/api/generate_variants", response_model=GenerationResponse)
async def generate_variants_enterprise(request: GenerationRequest, background_tasks: BackgroundTasks):
    global redis_client_global  # ✅ NEW
    
    if redis_client_global:  # ✅ Changed
        progress_data = { ... }
        redis_client_global.setex(...)  # ✅ Changed
        logger.info(f"✅ Initial progress set in Redis for job {job_id}")
```

#### 5. Updated run_enterprise_generation() (Line ~796, ~815, ~830)
All three progress updates (completion, timeout, error) now use `redis_client_global` instead of `app.state.redis_client`.

## Testing

### 1. Test Redis Connection
```bash
cd backend/fastapi
python test_redis.py
```

Expected output:
```
✅ Redis connection successful
✅ Wrote test data to Redis
✅ Read test data from Redis: 50%
✅ Cleaned up test data
```

### 2. Test Progress Updates
Start generation and watch FastAPI logs:
```
2025-11-25 18:26:09,366 - __main__ - INFO - [PROGRESS] ✅ Redis updated: job-id -> 30%
2025-11-25 18:26:10,178 - __main__ - INFO - [PROGRESS] ✅ Redis updated: job-id -> 31%
```

### 3. Verify Django Reads Progress
Check Django endpoint:
```bash
curl http://localhost:8000/api/generation-jobs/{job_id}/progress/
```

Expected response:
```json
{
  "job_id": "...",
  "progress": 30,
  "status": "running",
  "stage": "Solved 1/100 clusters",
  "message": "Solved 1/100 clusters"
}
```

## Expected Behavior After Fix

### FastAPI Logs
```
✅ Initial progress set in Redis for job abc-123
[PROGRESS] ✅ Redis updated: abc-123 -> 20% - Completed load_data
[PROGRESS] ✅ Redis updated: abc-123 -> 40% - Completed stage1_louvain_clustering
[PROGRESS] ✅ Redis updated: abc-123 -> 30% - Starting 1 workers
[PROGRESS] ✅ Redis updated: abc-123 -> 31% - Solved 1/100 clusters
[PROGRESS] ✅ Redis updated: abc-123 -> 32% - Solved 2/100 clusters
...
✅ Final progress (100%) set in Redis for job abc-123
```

### Frontend
- Progress bar updates from 0% → 100%
- Status messages change in real-time
- No more stuck at "Queued 0%"

## Rollback
If issues occur:
```bash
git diff backend/fastapi/main.py  # Review changes
git checkout backend/fastapi/main.py  # Revert
```

## Files Modified
- `backend/fastapi/main.py` - 5 sections updated
- `backend/fastapi/test_redis.py` - New test script

## Status
✅ Fix applied
⏳ Awaiting testing with real generation job
