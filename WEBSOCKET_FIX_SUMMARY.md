# WebSocket Infinite Loop Fix - Summary

## Problem
Frontend was stuck in infinite WebSocket reconnection loop when timetable generation failed:
- WebSocket tried connecting to wrong URL (FastAPI instead of Django Channels)
- No maximum reconnection attempts - infinite retries
- Backend didn't update Redis when FastAPI failed - frontend never knew it failed
- "Cannot cancel completed process" error when trying to cancel

## Root Causes

### 1. Wrong WebSocket URL
```typescript
// BEFORE (WRONG)
const WS_BASE = 'ws://localhost:8001'  // FastAPI doesn't have WebSocket
const ws = new WebSocket(`${WS_BASE}/ws/progress/${jobId}`)
```

**Issue**: FastAPI doesn't have WebSocket endpoint. Django Channels does, but it's not configured yet.

### 2. No Reconnection Limit
```typescript
// BEFORE (WRONG)
ws.onclose = () => {
  // Always reconnects - infinite loop!
  if (status !== 'completed' && status !== 'failed') {
    setTimeout(() => connectWebSocket(), 3000)
  }
}
```

**Issue**: WebSocket fails immediately, triggers reconnect, fails again → infinite loop

### 3. Backend Doesn't Update Redis on Failure
```python
# BEFORE (WRONG)
except Exception as e:
    job.status = 'failed'
    job.save()
    # Redis NOT updated - frontend keeps polling forever!
```

**Issue**: Frontend polls Redis for progress, but Redis never gets "failed" status

### 4. Cancel Button Doesn't Check Status
```typescript
// BEFORE (WRONG)
const handleCancel = async () => {
  // No status check - tries to cancel completed jobs!
  const res = await fetch(`${API_BASE}/generation-jobs/${jobId}/cancel/`)
}
```

## Solutions Applied

### ✅ Fix 1: Remove WebSocket, Use HTTP Polling Only
**File**: `frontend/src/components/ui/ProgressTracker.tsx`

```typescript
// AFTER (FIXED)
// Removed all WebSocket code
// Use HTTP polling only - simpler and works
useEffect(() => {
  let pollInterval: NodeJS.Timeout | null = null
  
  const pollProgress = async () => {
    const res = await fetch(`${API_BASE}/progress/${jobId}/`)
    const data = await res.json()
    
    if (data.status === 'completed') {
      clearInterval(pollInterval!)
      onComplete(jobId)
    } else if (data.status === 'failed') {
      clearInterval(pollInterval!)
      setError(data.message || 'Generation failed')
    }
  }
  
  pollInterval = setInterval(pollProgress, 2000)
  return () => clearInterval(pollInterval!)
}, [jobId])
```

**Why**: WebSocket adds complexity without benefit. HTTP polling is simpler and works perfectly.

### ✅ Fix 2: Update Redis When Backend Fails
**File**: `backend/django/academics/celery_tasks.py`

```python
# AFTER (FIXED)
except Exception as e:
    job.status = 'failed'
    job.completed_at = timezone.now()
    job.save()
    
    # UPDATE REDIS so frontend knows it failed!
    from django.core.cache import cache
    cache.set(
        f"progress:job:{job_id}",
        {
            'job_id': str(job_id),
            'status': 'failed',
            'progress': 0,
            'message': str(e),
            'error': str(e)
        },
        timeout=3600
    )
    
    # Don't retry - just fail
    return {'status': 'failed', 'error': str(e)}
```

**Why**: Frontend polls Redis. If Redis doesn't have "failed" status, frontend keeps polling forever.

### ✅ Fix 3: Check Status Before Cancel
**File**: `frontend/src/components/ui/ProgressTracker.tsx`

```typescript
// AFTER (FIXED)
const handleCancel = async () => {
  // Check status FIRST
  if (status === 'completed' || status === 'failed' || status === 'cancelled') {
    alert(`Cannot cancel ${status} process`)
    return
  }
  
  if (!confirm('Are you sure?')) return
  
  const res = await fetch(`${API_BASE}/generation-jobs/${jobId}/cancel/`)
  // ...
}
```

**Why**: Prevents "Cannot cancel completed process" error by checking status first.

### ✅ Fix 4: Fixed FastAPI Indentation
**File**: `backend/fastapi/main.py`

```python
# BEFORE (WRONG)
if len(courses) < 5:
    return
    
    # This code was unreachable due to wrong indentation!
    await update_progress(...)
    variants = await generate_real_variants(...)

# AFTER (FIXED)
if len(courses) < 5:
    await update_progress(redis_client, job_id, 0, 'failed', 'failed', error_msg)
    await call_django_callback(job_id, 'failed', error=error_msg)
    return

# Now this code runs when data is sufficient
await update_progress(redis_client, job_id, 30, 'running', 'Generating', 'Creating schedule')
variants = await generate_real_variants(...)
```

## Testing Steps

1. **Start all services**:
   ```bash
   # Terminal 1: Django
   cd backend/django
   python manage.py runserver
   
   # Terminal 2: FastAPI
   cd backend/fastapi
   uvicorn main:app --reload --port 8001
   
   # Terminal 3: Frontend
   cd frontend
   npm run dev
   ```

2. **Test failure scenario**:
   - Go to `/admin/timetables/new`
   - Click "Generate Timetable"
   - If insufficient data, should show error message immediately
   - Should NOT see infinite WebSocket reconnection loop
   - Should NOT see "Cannot cancel completed process" error

3. **Test success scenario**:
   - Ensure database has sufficient data (5+ courses, 3+ faculty, 3+ rooms)
   - Generate timetable
   - Should see progress updates every 2 seconds
   - Should complete successfully

## Architecture Flow (Fixed)

```
User clicks "Generate"
    ↓
Django creates GenerationJob
    ↓
Celery task starts
    ↓
Celery calls FastAPI /api/generate_variants
    ↓
FastAPI responds immediately (200 OK)
    ↓
FastAPI runs generation in background
    ↓
FastAPI updates Redis every second
    ↓
Frontend polls Django /api/progress/{job_id}/ every 2 seconds
    ↓
Django reads from Redis and returns to frontend
    ↓
If success: FastAPI calls Django callback → Job status = completed
If failure: FastAPI updates Redis with error → Frontend shows error
```

## Key Insights

1. **WebSocket is overkill** - HTTP polling every 2 seconds is simpler and works perfectly
2. **Always update Redis** - Frontend depends on Redis for progress, must update on failure
3. **Check status before actions** - Prevents "Cannot cancel completed process" errors
4. **Fail fast** - Don't retry indefinitely, show clear error messages
5. **Indentation matters** - Python indentation errors can make code unreachable

## Files Modified

1. `frontend/src/components/ui/ProgressTracker.tsx` - Removed WebSocket, use HTTP polling only
2. `backend/django/academics/celery_tasks.py` - Update Redis on failure
3. `backend/fastapi/main.py` - Fixed indentation bug

## Result

✅ No more infinite WebSocket reconnection loop
✅ Frontend shows clear error messages when generation fails
✅ Cancel button properly checks status before attempting cancel
✅ HTTP polling works reliably without WebSocket complexity
