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
                        # Capacity check
                        if student_count > room.capacity:
                            continue
                        
                        # Feature compatibility (using pre-computed sets)
                        if course_features and not course_features.issubset(room_features.get(room.room_id, set())):
                            continue
                        
                        valid_pairs.append((t_slot.slot_id, room.room_id))
                
                valid_domains[(course.course_id, session)] = valid_pairs
        
        # Clear temporary data
        del room_features
        
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
