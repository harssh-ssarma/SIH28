"""
Genetic Algorithm - Simplified Fitness Evaluation
Following Google/Meta standards: SIMPLE, FAST, 3 metrics only
NO feasibility checking (CP-SAT already ensured it)
NO GPU (dict-based data structures don't belong on GPU)
"""
import logging
from typing import Dict, List
from collections import defaultdict

from models.timetable_models import Course, Faculty, Room, TimeSlot

logger = logging.getLogger(__name__)


def evaluate_fitness_simple(
    solution: Dict,
    courses: List[Course],
    faculty: Dict[str, Faculty],
    time_slots: List[TimeSlot],
    rooms: List[Room]
) -> float:
    """
    Simple, fast fitness evaluation with ONLY 3 metrics:
    1. Faculty preferences (40%)
    2. Room utilization (30%)
    3. Peak spreading (30%)
    
    NO feasibility checking - CP-SAT already guaranteed feasibility
    NO complex metrics - those are policy decisions, not solver concerns
    """
    score = 0.0
    
    # Metric 1: Faculty preferences (40% weight)
    faculty_score = _evaluate_faculty_preferences(solution, courses, time_slots)
    score += 0.4 * faculty_score
    
    # Metric 2: Room utilization (30% weight)
    room_score = _evaluate_room_utilization(solution, courses, rooms)
    score += 0.3 * room_score
    
    # Metric 3: Peak spreading (30% weight)
    spread_score = _evaluate_peak_spreading(solution, courses, time_slots)
    score += 0.3 * spread_score
    
    return score


def _evaluate_faculty_preferences(solution: Dict, courses: List[Course], time_slots: List[TimeSlot]) -> float:
    """
    Faculty preference scoring (higher = better)
    Penalize: early morning (< 8am) and late evening (> 6pm)
    """
    score = 100.0
    
    for course in courses:
        for session in range(course.duration):
            key = (course.course_id, session)
            if key in solution:
                t_slot_id, _ = solution[key]
                # Assume 10 slots per day, 5 days/week
                slot_of_day = t_slot_id % 10
                
                # Penalize early (slots 0-1 = 8-9am) and late (slots 8-9 = 4-5pm)
                if slot_of_day < 2:  # Before 9am
                    score -= 5.0
                elif slot_of_day > 7:  # After 4pm
                    score -= 3.0
    
    return max(0, score)


def _evaluate_room_utilization(solution: Dict, courses: List[Course], rooms: List[Room]) -> float:
    """
    Room utilization scoring (higher = better)
    Prefer: rooms with capacity close to enrolled students
    """
    score = 100.0
    room_capacity_map = {r.room_id: r.capacity for r in rooms}
    
    for course in courses:
        for session in range(course.duration):
            key = (course.course_id, session)
            if key in solution:
                _, room_id = solution[key]
                room_capacity = room_capacity_map.get(room_id, 100)
                enrolled = getattr(course, 'enrolled_students', 30)
                
                # Penalize if room is way too big (waste)
                if room_capacity > enrolled * 2:
                    score -= 5.0
                # Small bonus if room size is appropriate
                elif enrolled <= room_capacity <= enrolled * 1.5:
                    score += 2.0
    
    return max(0, score)


def _evaluate_peak_spreading(solution: Dict, courses: List[Course], time_slots: List) -> float:
    """
    Peak spreading scoring (higher = better)
    Prefer: even distribution across time slots (avoid overload)
    """
    score = 100.0
    
    # Count sessions per time slot
    slot_counts = defaultdict(int)
    for course in courses:
        for session in range(course.duration):
            key = (course.course_id, session)
            if key in solution:
                t_slot_id, _ = solution[key]
                slot_counts[t_slot_id] += 1
    
    if slot_counts:
        # Penalize slots with too many sessions (peak load)
        max_count = max(slot_counts.values())
        avg_count = sum(slot_counts.values()) / len(slot_counts)
        
        # Heavy penalty for overloaded slots
        if max_count > avg_count * 2:
            score -= (max_count - avg_count * 2) * 10.0
    
    return max(0, score)
