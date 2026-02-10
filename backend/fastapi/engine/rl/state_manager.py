"""
Reinforcement Learning - Simplified State Manager
Following Google/Meta standards: SIMPLE, DISCRETE, 4-6 dimensions MAX
Executive verdict: "Collapse state space intentionally"
"""
import logging
from typing import Tuple, List, Dict
from collections import defaultdict

from models.timetable_models import Course, Faculty

logger = logging.getLogger(__name__)


class StateManager:
    """
    Simple discrete state manager for RL agent
    State: (conflict_type, load_bucket, time_bucket)
    NO continuous high-dim state, NO unbounded state space
    """
    
    def __init__(self, courses: List[Course], faculty: Dict[str, Faculty]):
        self.courses = courses
        self.faculty = faculty
        logger.info(f"[RL-State] Simple discrete state manager initialized")
    
    def get_state(
        self, 
        schedule: Dict, 
        conflict_type: str = "none"
    ) -> Tuple[str, str, str]:
        """
        Get simple discrete state (4-6 dimensions MAX)
        Returns: (conflict_type, load_bucket, time_bucket)
        """
        # Dimension 1: Conflict type
        # Values: student, faculty, room, none
        
        # Dimension 2: Faculty load bucket
        faculty_workload = self._calculate_faculty_workload(schedule)
        max_load = max(faculty_workload.values()) if faculty_workload else 0
        if max_load < 12:
            load_bucket = "low"
        elif max_load < 18:
            load_bucket = "medium"
        else:
            load_bucket = "high"
        
        # Dimension 3: Time density bucket
        time_density = self._calculate_time_density(schedule)
        if time_density < 0.3:
            time_bucket = "morning"
        elif time_density < 0.6:
            time_bucket = "midday"
        else:
            time_bucket = "evening"
        
        return (conflict_type, load_bucket, time_bucket)
    
    def _calculate_faculty_workload(self, schedule: Dict) -> Dict[str, int]:
        """Calculate faculty workload from schedule"""
        workload = defaultdict(int)
        for (course_id, session), (t_slot, room) in schedule.items():
            course = next((c for c in self.courses if c.course_id == course_id), None)
            if course:
                workload[course.faculty_id] += 1
        return dict(workload)
    
    def _calculate_time_density(self, schedule: Dict) -> float:
        """Calculate time density (fraction of slots used)"""
        if not schedule:
            return 0.0
        
        unique_slots = set(t_slot for (t_slot, room) in schedule.values())
        # Assume 50 total time slots
        return len(unique_slots) / 50.0
        max_workload = max(self.faculty_workload.values()) if self.faculty_workload else 0
        if max_workload > 18:
            reward -= (max_workload - 18) * 5
        
        return reward
