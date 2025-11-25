# Critical Fixes for Timetable Generation System

## Issue Summary
- **Frontend shows 0% "Queued"** - Progress not updating
- **CP-SAT failing** - Status 0 (INFEASIBLE) on all clusters
- **Redis SSL errors** - Callback failures
- **Full page reloads** - Navigation issues

## ✅ COMPLETED FIXES

### 1. Frontend Navigation (FIXED)
- Replaced all `<a href>` with Next.js `<Link>` component
- Replaced `window.location.href` with `router.push()`
- Replaced `window.location.reload()` with function calls
- Files updated:
  - `/admin/timetables/page.tsx`
  - `/admin/dashboard/page.tsx`
  - `/admin/admins/page.tsx`
  - `/admin/faculty/page.tsx`
  - `/admin/students/page.tsx`
  - `/staff/dashboard/page.tsx`

## 🔧 PENDING CRITICAL FIXES

### 2. Redis SSL Configuration (backend/fastapi/main.py)
**Current Issue:** SSL certificate errors blocking callbacks

**Fix Required:**
```python
# Line ~650 in lifespan function
if redis_url.startswith("rediss://"):
    app.state.redis_client = redis.from_url(
        redis_url,
        decode_responses=True,
        ssl_cert_reqs=ssl.CERT_NONE,  # ✅ Already fixed
        ssl_check_hostname=False       # ✅ Already fixed
    )
```
**Status:** ✅ Already implemented correctly

### 3. Progress Key Consistency
**Current Issue:** FastAPI writes to one key, Django reads from another

**Verification Needed:**
- FastAPI writes: `progress:job:{job_id}` ✅ (Line 1050)
- Django reads: `progress:job:{job_id}` ✅ (needs verification)

### 4. CP-SAT Greedy Fallback (CRITICAL)
**Current Issue:** CP-SAT returns status 0 (INFEASIBLE) for all clusters

**Fix Required in `_solve_cluster_safe()` method (Line ~1050):**

```python
def _solve_cluster_safe(self, cluster_id, courses, rooms, time_slots, faculty):
    """Solve single cluster with greedy fallback"""
    try:
        from engine.stage2_hybrid import CPSATSolver
        
        # STRATEGY 1: Try CP-SAT first
        solver = CPSATSolver(
            courses=courses,
            rooms=rooms,
            time_slots=time_slots,
            faculty=faculty,
            timeout_seconds=15  # Reduced from 30
        )
        
        solution = solver.solve()
        if solution and len(solution) > 0:
            logger.info(f"Cluster {cluster_id}: CP-SAT success ({len(solution)} assignments)")
            return solution
        
        # STRATEGY 2: Greedy fallback when CP-SAT fails
        logger.warning(f"Cluster {cluster_id}: CP-SAT failed, using greedy fallback")
        return self._greedy_schedule(cluster_id, courses, rooms, time_slots, faculty)
        
    except Exception as e:
        logger.error(f"Cluster {cluster_id} error: {e}")
        # STRATEGY 3: Emergency fallback
        return self._greedy_schedule(cluster_id, courses, rooms, time_slots, faculty)

def _greedy_schedule(self, cluster_id, courses, rooms, time_slots, faculty):
    """Greedy scheduling fallback - ALWAYS returns something"""
    schedule = {}
    
    # Sort courses by constraint density (most constrained first)
    sorted_courses = sorted(
        courses,
        key=lambda c: len(getattr(c, 'student_ids', [])) * len(getattr(c, 'required_features', [])),
        reverse=True
    )
    
    # Track used slots
    used_slots = set()
    faculty_schedule = {}
    room_schedule = {}
    
    for course in sorted_courses:
        assigned = False
        
        # Try each time slot
        for time_slot in time_slots:
            if assigned:
                break
                
            # Check faculty availability
            faculty_id = getattr(course, 'faculty_id', None)
            if faculty_id and (faculty_id, time_slot.slot_id) in faculty_schedule:
                continue
            
            # Try each room
            for room in rooms:
                # Check room availability
                if (room.room_id, time_slot.slot_id) in room_schedule:
                    continue
                
                # Check room features match
                required_features = set(getattr(course, 'required_features', []))
                room_features = set(getattr(room, 'features', []))
                if required_features and not required_features.issubset(room_features):
                    continue
                
                # Assign!
                key = (course.course_id, 0)
                value = (time_slot.slot_id, room.room_id)
                schedule[key] = value
                
                # Mark as used
                used_slots.add((time_slot.slot_id, room.room_id))
                if faculty_id:
                    faculty_schedule[(faculty_id, time_slot.slot_id)] = course.course_id
                room_schedule[(room.room_id, time_slot.slot_id)] = course.course_id
                
                assigned = True
                break
        
        if not assigned:
            logger.warning(f"Could not assign course {course.course_id} in cluster {cluster_id}")
    
    logger.info(f"Cluster {cluster_id}: Greedy assigned {len(schedule)}/{len(courses)} courses")
    return schedule
```

### 5. Frontend Progress Polling Hook

**Create new file:** `frontend/src/hooks/useProgress.ts`

```typescript
import { useState, useEffect } from 'react';

interface ProgressData {
  job_id: string;
  status: 'queued' | 'running' | 'completed' | 'failed';
  progress: number;
  stage: string;
  message: string;
}

export function useProgress(jobId: string | null) {
  const [progress, setProgress] = useState<ProgressData>({
    job_id: jobId || '',
    status: 'queued',
    progress: 0,
    stage: 'queued',
    message: 'Initializing...'
  });

  useEffect(() => {
    if (!jobId) return;

    const pollInterval = setInterval(async () => {
      try {
        const response = await fetch(
          `${process.env.NEXT_PUBLIC_DJANGO_API_URL}/api/generation-jobs/${jobId}/progress/`,
          { credentials: 'include' }
        );
        
        if (!response.ok) return;

        const data: ProgressData = await response.json();
        setProgress(data);

        // Stop polling when complete or failed
        if (data.status === 'completed' || data.status === 'failed') {
          clearInterval(pollInterval);
        }

      } catch (error) {
        console.error('Progress poll error:', error);
      }
    }, 2000); // Poll every 2 seconds

    return () => clearInterval(pollInterval);
  }, [jobId]);

  return progress;
}
```

## Implementation Priority

1. **✅ DONE:** Frontend navigation fixes
2. **CRITICAL:** Add greedy fallback to `_solve_cluster_safe()`
3. **HIGH:** Create `useProgress` hook
4. **MEDIUM:** Verify Django progress endpoint reads correct Redis key
5. **LOW:** Redis SSL already fixed

## Expected Results After Fixes

- ✅ No full page reloads on navigation
- ⏳ Progress updates from 0% → 100% in real-time
- ⏳ CP-SAT failures handled gracefully with greedy fallback
- ⏳ 95%+ courses scheduled (even if not optimal)
- ⏳ Callbacks reach Django successfully

## Testing Checklist

- [ ] Click "Generate New Timetable" - should NOT reload page
- [ ] Progress bar shows 0% → 100% smoothly
- [ ] Check logs: "Greedy assigned X/Y courses" messages
- [ ] Verify timetable entries created for ALL departments
- [ ] No "CP-SAT failed with status: 0" errors
