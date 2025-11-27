# 🔧 CP-SAT Quality Fix - Root Cause Analysis

## 🐛 PROBLEM IDENTIFIED

### Current Issues
```
❌ 84,338 conflicts (target: <100)
❌ 25% quality score (target: 90%+)
❌ 5% room utilization (target: 80%+)
```

### Root Cause
**CP-SAT solver is NOT being used!** The system is using only GA (Genetic Algorithm) which:
1. Doesn't enforce hard constraints strictly
2. Optimizes for speed over quality
3. Produces many conflicts

## 📊 EVIDENCE

### From Logs
```
2025-11-27 21:59:49 - engine.stage2_ga - INFO - [GA] Gen 3: Calling GPU batch fitness
2025-11-27 22:00:10 - engine.stage2_ga - INFO - GA Gen 3/5 (GPU): Best=0.3151
2025-11-27 22:00:28 - engine.stage2_ga - INFO - GA complete: Final fitness=0.3204
```

**No CP-SAT logs found!** Only GA is running.

### Why CP-SAT is Skipped
1. **Ultra-fast timeouts** - 1-2 seconds is too short for 2494 courses
2. **Aggressive feasibility checks** - Rejecting solvable clusters
3. **Max cluster size = 12** - Too small, creates 200+ clusters
4. **Not called from main.py** - Orchestration issue

## ✅ SOLUTION: 3-Part Fix

### Part 1: Fix CP-SAT Configuration
**File:** `backend/fastapi/engine/stage2_cpsat.py`

**Changes:**
1. Increase timeouts: 1-2s → 30-60s
2. Increase max cluster size: 12 → 50
3. Relax feasibility checks
4. Add proper constraint enforcement

### Part 2: Fix Orchestration
**File:** `backend/fastapi/main.py`

**Changes:**
1. Enable CP-SAT stage
2. Use CP-SAT before GA (not after)
3. Pass CP-SAT results to GA for refinement

### Part 3: Fix Constraint Enforcement
**File:** `backend/fastapi/engine/stage2_cpsat.py`

**Changes:**
1. Enforce ALL hard constraints:
   - HC1: Faculty conflicts (✅ already enforced)
   - HC2: Room conflicts (✅ already enforced)
   - HC3: Student conflicts (⚠️ only for "CRITICAL" students)
   - HC4: Time slot availability (✅ in domain filtering)
   - HC5: Room capacity (✅ in domain filtering)
   - HC6: Feature compatibility (✅ in domain filtering)
   - HC7: Faculty availability (✅ in domain filtering)
   - HC8: Workload limits (✅ already enforced)

2. **FIX HC3**: Add student constraints for ALL students, not just "CRITICAL"

## 🎯 IMPLEMENTATION PLAN

### Step 1: Update CP-SAT Timeouts (5 min)
```python
# stage2_cpsat.py - Line 28-42
STRATEGIES = [
    {
        "name": "Balanced",
        "student_priority": "ALL",  # Changed from "CRITICAL"
        "faculty_conflicts": True,
        "room_capacity": True,
        "timeout": 60,  # Changed from 2
        "max_constraints": 50000  # Changed from 3000
    },
    {
        "name": "Quick",
        "student_priority": "HIGH",
        "faculty_conflicts": True,
        "room_capacity": True,
        "timeout": 30,  # Changed from 1
        "max_constraints": 10000  # Changed from 1000
    }
]
```

### Step 2: Increase Max Cluster Size (2 min)
```python
# stage2_cpsat.py - Line 51
max_cluster_size: int = 50,  # Changed from 12
```

### Step 3: Fix Student Constraints (10 min)
```python
# stage2_cpsat.py - Line 550-600
def _add_hierarchical_student_constraints(self, model, variables, cluster, priority: str):
    """Add student constraints for ALL students"""
    
    if priority == "ALL":
        # ENFORCE for ALL students (not just critical)
        student_courses = defaultdict(list)
        for course in cluster:
            for student_id in course.student_ids:
                student_courses[student_id].append(course)
        
        for student_id, courses_list in student_courses.items():
            for t_slot in self.time_slots:
                student_vars = [
                    variables[(c.course_id, s, t_slot.slot_id, r.room_id)]
                    for c in courses_list
                    for s in range(c.duration)
                    for r in self.rooms
                    if (c.course_id, s, t_slot.slot_id, r.room_id) in variables
                ]
                if student_vars:
                    model.Add(sum(student_vars) <= 1)  # No conflicts!
```

### Step 4: Enable CP-SAT in Orchestration (15 min)
```python
# main.py - Add CP-SAT stage before GA
logger.info("[STAGE2A] Running CP-SAT for initial assignment")
cpsat_solver = AdaptiveCPSATSolver(
    courses=courses,
    rooms=rooms,
    time_slots=time_slots,
    faculty=faculty_dict,
    max_cluster_size=50,  # Larger clusters
    job_id=job_id,
    redis_client=redis_client
)

# Solve each cluster
cpsat_assignments = {}
for cluster in clusters:
    solution = cpsat_solver.solve_cluster(cluster, timeout=60)
    if solution:
        cpsat_assignments.update(solution)

logger.info(f"[STAGE2A] CP-SAT assigned {len(cpsat_assignments)} sessions")

# Pass to GA for refinement
logger.info("[STAGE2B] Running GA to refine CP-SAT solution")
ga_result = run_ga_optimization(
    initial_solution=cpsat_assignments,  # Start from CP-SAT
    ...
)
```

## 📈 EXPECTED RESULTS

### Before Fix
```
Conflicts: 84,338
Quality: 25%
Room Utilization: 5%
Time: 7 minutes
```

### After Fix
```
Conflicts: <100 (99.9% reduction)
Quality: 90%+ (3.6x improvement)
Room Utilization: 80%+ (16x improvement)
Time: 10-15 minutes (acceptable tradeoff)
```

## ⚠️ TRADEOFFS

### Pros
- ✅ Dramatically better quality
- ✅ Proper constraint enforcement
- ✅ Usable timetables
- ✅ Production-ready

### Cons
- ⚠️ Slower generation (7min → 15min)
- ⚠️ Higher memory usage
- ⚠️ More complex orchestration

## 🚀 DEPLOYMENT PLAN

### Phase 1: Test with Small Dataset (1 hour)
1. Apply fixes to stage2_cpsat.py
2. Test with 100 courses
3. Verify conflicts < 10
4. Verify quality > 90%

### Phase 2: Test with Full Dataset (2 hours)
1. Test with 2494 courses
2. Monitor memory usage
3. Verify conflicts < 100
4. Verify quality > 85%

### Phase 3: Production Deployment (1 hour)
1. Update main.py orchestration
2. Deploy to production
3. Monitor first generation
4. Rollback if issues

## 📝 ALTERNATIVE: Quick Win (If Time-Constrained)

If full CP-SAT fix takes too long, implement **Quick Win**:

### Option A: Stricter GA Constraints (30 min)
```python
# stage2_ga.py - Add hard constraint penalties
def fitness_function(solution):
    conflicts = count_conflicts(solution)
    if conflicts > 0:
        return 0.0  # REJECT solutions with ANY conflicts
    return calculate_quality(solution)
```

### Option B: Post-Processing Conflict Resolution (1 hour)
```python
# After GA, run conflict resolution
def resolve_conflicts(assignments):
    conflicts = detect_conflicts(assignments)
    for conflict in conflicts:
        # Move one course to different time/room
        resolve_single_conflict(conflict, assignments)
    return assignments
```

## 💡 RECOMMENDATION

**Implement Full CP-SAT Fix** because:
1. Root cause solution (not workaround)
2. Production-quality results
3. Maintainable long-term
4. Worth the 2-3 hour investment

**Quick Win is NOT recommended** because:
1. Doesn't fix root cause
2. Still produces conflicts
3. Technical debt
4. Will need to fix properly later anyway

---

**Status:** Analysis complete, ready to implement
**Priority:** CRITICAL - blocks all other features
**Estimated Time:** 2-3 hours for full fix
**Expected Improvement:** 99.9% conflict reduction
