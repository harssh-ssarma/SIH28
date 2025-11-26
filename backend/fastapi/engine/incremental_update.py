"""
Incremental Timetable Updates
"""
import logging
from typing import Dict, List, Set

logger = logging.getLogger(__name__)

class IncrementalUpdater:
    """Update existing timetable when courses change"""
    
    def __init__(self, existing_solution: Dict):
        self.solution = existing_solution
        self.affected_slots = set()
    
    def add_course(self, course, rooms, time_slots, faculty) -> Dict:
        """Add new course to existing timetable"""
        logger.info(f"Adding course {course.course_id} incrementally")
        
        # Find available slot
        used_slots = {(ts, rm) for (_, _), (ts, rm) in self.solution.items()}
        
        for time_slot in time_slots:
            for room in rooms:
                slot_key = (time_slot.slot_id, room.room_id)
                if slot_key not in used_slots:
                    # Check conflicts
                    if self._check_conflicts(course, time_slot.slot_id, room.room_id):
                        continue
                    
                    # Assign
                    self.solution[(course.course_id, 0)] = (time_slot.slot_id, room.room_id)
                    logger.info(f"Course {course.course_id} assigned to slot {time_slot.slot_id}")
                    return self.solution
        
        logger.warning(f"No available slot for course {course.course_id}")
        return self.solution
    
    def remove_course(self, course_id: str) -> Dict:
        """Remove course from timetable"""
        logger.info(f"Removing course {course_id} incrementally")
        
        keys_to_remove = [k for k in self.solution.keys() if k[0] == course_id]
        for key in keys_to_remove:
            del self.solution[key]
        
        return self.solution
    
    def update_course(self, course, rooms, time_slots, faculty) -> Dict:
        """Update existing course (remove + add)"""
        self.remove_course(course.course_id)
        return self.add_course(course, rooms, time_slots, faculty)
    
    def _check_conflicts(self, course, time_slot_id, room_id) -> bool:
        """Check if assignment causes conflicts"""
        for (cid, _), (ts, rm) in self.solution.items():
            if ts == time_slot_id:
                # Room conflict
                if rm == room_id:
                    return True
                # Student conflict (simplified)
                existing_course = next((c for c in [course] if c.course_id == cid), None)
                if existing_course:
                    students_overlap = set(course.student_ids) & set(getattr(existing_course, 'student_ids', []))
                    if students_overlap:
                        return True
        return False
