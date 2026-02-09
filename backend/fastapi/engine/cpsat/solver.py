"""
CP-SAT Solver - Main Orchestrator
Adaptive solver with progressive relaxation
Following Google/Meta standards: Main solver logic only
"""
import logging
import time
from typing import List, Dict, Optional, Tuple
from collections import defaultdict
from ortools.sat.python import cp_model

from models.timetable_models import Course, Room, TimeSlot, Faculty
from .strategies import STRATEGIES
from .progress import update_progress, log_cluster_start, log_cluster_success
from .constraints import (
    add_faculty_constraints,
    add_room_constraints,
    add_student_constraints
)

logger = logging.getLogger(__name__)


class AdaptiveCPSATSolver:
    """
    Adaptive CP-SAT solver with progressive relaxation
    Tries multiple strategies until one succeeds
    """
    
    def __init__(
        self,
        courses: List[Course],
        rooms: List[Room],
        time_slots: List[TimeSlot],
        faculty: Dict[str, Faculty],
        max_cluster_size: int = 50,
        job_id: str = None,
        redis_client = None,
        cluster_id: int = None,
        total_clusters: int = None,
        completed_clusters: int = 0,
        global_student_schedule: Dict[str, List[Tuple[int, int]]] = None
    ):
        self.courses = courses
        self.rooms = rooms
        self.time_slots = time_slots
        self.faculty = faculty
        self.max_cluster_size = max_cluster_size
        self.job_id = job_id
        self.redis_client = redis_client
        self.cluster_id = cluster_id
        self.total_clusters = total_clusters
        self.completed_clusters = completed_clusters
        self.global_student_schedule = global_student_schedule or {}
        
        # Auto-detect CPU cores
        import multiprocessing
        self.num_workers = min(8, multiprocessing.cpu_count())
        logger.info(f"[CP-SAT] Using {self.num_workers} CPU cores")
    
    def solve_cluster(self, cluster: List[Course], timeout: float = None) -> Optional[Dict]:
        """
        Solve cluster with progressive strategy relaxation
        Returns assignments or None if no solution found
        """
        log_cluster_start(
            self.cluster_id if self.cluster_id is not None else 0,
            len(cluster),
            len(self.time_slots)
        )
        
        # STEP 1: Build global indexes (O(N) once instead of O(N²) repeatedly)
        self.course_by_id = {c.course_id: c for c in cluster}
        self.faculty_of_course = {c.course_id: c.faculty_id for c in cluster}
        self.students_of_course = {c.course_id: set(c.student_ids) if hasattr(c, 'student_ids') else set() for c in cluster}
        logger.info(f"[CP-SAT] Built indexes for {len(cluster)} courses")
        
        # STEP 2: Precompute valid domains (room/time filtering)
        self.valid_domains = self._precompute_valid_domains(cluster)
        logger.info(f"[CP-SAT] Precomputed {sum(len(v) for v in self.valid_domains.values())} valid domain entries")
        
        # Try each strategy
        for strategy_idx, strategy in enumerate(STRATEGIES):
            logger.info(f"[CP-SAT] Attempting strategy {strategy_idx + 1}/{len(STRATEGIES)}: {strategy['name']}")
            
            solution = self._solve_with_strategy(cluster, strategy)
            
            if solution:
                log_cluster_success(
                    self.cluster_id if self.cluster_id is not None else 0,
                    time.time()
                )
                return solution
        
        # All strategies failed
        logger.warning("[CP-SAT] All strategies failed - will use greedy fallback")
        return None
    
    def _solve_with_strategy(self, cluster: List[Course], strategy: Dict) -> Optional[Dict]:
        """Solve cluster using specific strategy"""
        try:
            model = cp_model.CpModel()
            solver = cp_model.CpSolver()
            solver.parameters.max_time_in_seconds = strategy['timeout']
            solver.parameters.num_search_workers = self.num_workers
            
            # Create variables ONLY for valid domains (no full grid iteration)
            variables = {}
            for course in cluster:
                for session in range(course.duration):
                    # Use precomputed valid domains instead of full grid
                    domain_key = (course.course_id, session)
                    if domain_key in self.valid_domains:
                        for (t_slot_id, room_id) in self.valid_domains[domain_key]:
                            var_name = f"x_{course.course_id}_s{session}_t{t_slot_id}_r{room_id}"
                            var = model.NewBoolVar(var_name)
                            variables[(course.course_id, session, t_slot_id, room_id)] = var
            
            # Assignment constraints: each session assigned exactly once
            for course in cluster:
                for session in range(course.duration):
                    session_vars = [
                        var for (c_id, s_idx, _, _), var in variables.items()
                        if c_id == course.course_id and s_idx == session
                    ]
                    if session_vars:
                        model.Add(sum(session_vars) == 1)
            
            # Add constraints based on strategy (pass indexes)
            if strategy['faculty_conflicts']:
                add_faculty_constraints(model, variables, cluster, self.faculty_of_course)
            
            if strategy['room_capacity']:
                add_room_constraints(model, variables, cluster)
            
            # REMOVED: Faculty workload constraints (moved to pre-clustering)
            # add_workload_constraints() was causing O(N²) explosion
            
            if strategy.get('student_priority'):
                add_student_constraints(model, variables, cluster, strategy['student_priority'], self.students_of_course)
            
            # Solve
            logger.info(f"[CP-SAT] Starting solver with timeout {strategy['timeout']}s...")
            status = solver.Solve(model)
            
            # Extract solution (use variables dict directly, no grid iteration)
            if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
                solution = {}
                # Iterate only through actual variables (no full grid scan)
                for (course_id, session, t_slot_id, room_id), var in variables.items():
                    if solver.Value(var):
                        solution[(course_id, session)] = (t_slot_id, room_id)
                
                logger.info(f"[CP-SAT] Solution found: {len(solution)} assignments")
                return solution
            
            logger.warning(f"[CP-SAT] No solution with strategy: {strategy['name']}")
            return None
        
        except Exception as e:
            logger.error(f"[CP-SAT] Strategy failed: {e}")
            return None
    
    def _precompute_valid_domains(self, cluster: List[Course]) -> Dict:
        """
        Precompute valid (time_slot, room) pairs for each (course, session)
        This eliminates full grid iteration in variable creation and solution extraction
        """
        valid_domains = {}
        
        for course in cluster:
            for session in range(course.duration):
                valid_pairs = []
                for t_slot in self.time_slots:
                    for room in self.rooms:
                        # Basic filtering (can be enhanced with more heuristics)
                        if room.capacity >= getattr(course, 'enrolled_students', 0):
                            valid_pairs.append((t_slot.slot_id, room.room_id))
                
                valid_domains[(course.course_id, session)] = valid_pairs
        
        return valid_domains
    
    def _check_cancellation(self) -> bool:
        """Check if job was cancelled"""
        if not self.redis_client or not self.job_id:
            return False
        
        try:
            cancel_flag = self.redis_client.get(f"cancel:{self.job_id}")
            return cancel_flag is not None
        except:
            return False
