"""
Smart Greedy Scheduler with Domain Filtering
Optimized fallback when CP-SAT fails or cluster too large
"""
import logging
from typing import List, Dict, Tuple, Optional
from collections import defaultdict
from models.timetable_models import Course, Room, TimeSlot, Faculty

logger = logging.getLogger(__name__)


class SmartGreedyScheduler:
    """
    Domain-aware greedy algorithm
    Uses pre-computed valid domains for fast scheduling
    """
    
    def __init__(
        self,
        courses: List[Course],
        rooms: List[Room],
        time_slots: List[TimeSlot],
        faculty: Dict[str, Faculty]
    ):
        self.courses = courses
        self.rooms = rooms
        self.time_slots = time_slots
        self.faculty = faculty
        
    def solve(self, cluster: List[Course], valid_domains: Optional[Dict] = None) -> Dict:
        """
        Greedy scheduling with domain filtering and memory management
        """
        # Precompute valid domains if not provided
        if valid_domains is None:
            valid_domains = self._precompute_valid_domains(cluster)
        
        # Sort courses by constraint difficulty (fewest options first)
        sorted_courses = sorted(
            cluster,
            key=lambda c: self._compute_difficulty(c, valid_domains)
        )
        
        assignments = {}
        faculty_schedule = {}
        room_schedule = {}
        student_schedule = {}
        
        for course in sorted_courses:
            # Pre-convert student_ids to set for faster lookup
            student_set = set(course.student_ids)
            
            for session in range(course.duration):
                assigned = False
                
                # Try valid domains in order of preference
                valid_pairs = valid_domains.get((course.course_id, session), [])
                
                for time_slot_id, room_id in valid_pairs:
                    # Check faculty conflict
                    faculty_id = course.faculty_id
                    if (faculty_id, time_slot_id) in faculty_schedule:
                        continue
                    
                    # Check room conflict
                    if (room_id, time_slot_id) in room_schedule:
                        continue
                    
                    # Check student conflicts (optimized)
                    has_student_conflict = any(
                        (student_id, time_slot_id) in student_schedule
                        for student_id in student_set
                    )
                    
                    if has_student_conflict:
                        continue
                    
                    # Assign
                    assignments[(course.course_id, session)] = (time_slot_id, room_id)
                    
                    # Update tracking
                    faculty_schedule[(faculty_id, time_slot_id)] = True
                    room_schedule[(room_id, time_slot_id)] = True
                    
                    for student_id in student_set:
                        student_schedule[(student_id, time_slot_id)] = True
                    
                    assigned = True
                    break
                
                if not assigned:
                    logger.warning(f"Could not assign course {course.course_id} session {session}")
        
        # Clear valid_domains to free memory
        valid_domains.clear()
        
        logger.info(f"Greedy assigned {len(assignments)}/{sum(c.duration for c in cluster)} sessions")
        return assignments
    
    def _precompute_valid_domains(self, cluster: List[Course]) -> Dict:
        """
        Pre-filter valid (time, room) pairs for each course with memory optimization
        """
        valid_domains = {}
        
        # CRITICAL DEBUG: Check inputs
        logger.info(f"[GREEDY] Precomputing domains: {len(cluster)} courses, {len(self.rooms)} rooms, {len(self.time_slots)} time_slots")
        
        if len(self.rooms) == 0:
            logger.error("[GREEDY] NO ROOMS AVAILABLE - Cannot schedule anything!")
            return {}
        
        if len(self.time_slots) == 0:
            logger.error("[GREEDY] NO TIME SLOTS AVAILABLE - Cannot schedule anything!")
            return {}
        
        # DEBUG: Check department distribution
        course_depts = set(getattr(c, 'department_id', None) for c in cluster)
        room_depts = set(getattr(r, 'dept_id', None) or getattr(r, 'department_id', None) for r in self.rooms)
        logger.info(f"[GREEDY] Course departments: {course_depts}")
        logger.info(f"[GREEDY] Room departments: {room_depts}")
        logger.info(f"[GREEDY] Matching departments: {course_depts & room_depts}")
        
        # Pre-compute room features for faster lookup
        room_features = {r.room_id: set(getattr(r, 'features', [])) for r in self.rooms}
        
        for course in cluster:
            course_features = set(getattr(course, 'required_features', []))
            student_count = len(course.student_ids)
            faculty_avail = None
            
            if course.faculty_id in self.faculty:
                faculty_avail = set(getattr(self.faculty[course.faculty_id], 'available_slots', []))
            
            for session in range(course.duration):
                valid_pairs = []
                
                for t_slot in self.time_slots:
                    # Faculty availability check
                    if faculty_avail and t_slot.slot_id not in faculty_avail:
                        continue
                    
                    for room in self.rooms:
                        # CRITICAL: Department matching constraint
                        course_dept = getattr(course, 'department_id', None)
                        room_dept = getattr(room, 'dept_id', None) or getattr(room, 'department_id', None)
                        if course_dept and room_dept and course_dept != room_dept:
                            continue
                        
                        # Capacity check
                        if student_count > room.capacity:
                            continue
                        
                        # Feature compatibility (using pre-computed sets)
                        if course_features and not course_features.issubset(room_features.get(room.room_id, set())):
                            continue
                        
                        valid_pairs.append((t_slot.slot_id, room.room_id))
                
                valid_domains[(course.course_id, session)] = valid_pairs
                
                # DEBUG: Log courses with no valid pairs
                if len(valid_pairs) == 0:
                    course_dept = getattr(course, 'department_id', None)
                    matching_rooms = sum(1 for r in self.rooms if (getattr(r, 'dept_id', None) or getattr(r, 'department_id', None)) == course_dept)
                    logger.warning(f"[GREEDY] Course {course.course_code} session {session}: NO VALID PAIRS (dept={course_dept}, students={student_count}, matching_rooms={matching_rooms}/{len(self.rooms)})")
        
        # Clear temporary data
        del room_features
        
        # CRITICAL DEBUG: Summary
        total_pairs = sum(len(pairs) for pairs in valid_domains.values())
        logger.info(f"[GREEDY] Computed {total_pairs} valid pairs for {len(cluster)} courses ({total_pairs/max(len(cluster),1):.1f} avg per course)")
        
        if total_pairs == 0:
            logger.error(f"[GREEDY] ZERO valid pairs! Department mismatch: courses need rooms from {course_depts} but rooms are from {room_depts}")
        
        return valid_domains
    
    def _compute_difficulty(self, course: Course, valid_domains: Dict) -> int:
        """
        Compute difficulty score for course
        Lower score = more constrained = schedule first
        """
        # Count total valid options across all sessions
        total_options = sum(
            len(valid_domains.get((course.course_id, session), []))
            for session in range(course.duration)
        )
        
        # Penalize courses with many students (harder to place)
        student_penalty = len(course.student_ids) * 10
        
        # Penalize courses with special requirements
        feature_penalty = len(getattr(course, 'required_features', [])) * 100
        
        return total_options - student_penalty - feature_penalty
