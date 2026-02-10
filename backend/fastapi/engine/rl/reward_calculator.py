"""
Reinforcement Learning - Simplified Reward Calculator
Following Google/Meta standards: SIMPLE rewards, NO complex calculations
Executive verdict: +1 conflict reduced, -5 worsened, +0.2 load improved
"""
import logging
from typing import Dict, List
from collections import defaultdict

from models.timetable_models import Course

logger = logging.getLogger(__name__)


def calculate_simple_reward(
    old_schedule: Dict,
    new_schedule: Dict,
    courses: List[Course],
    old_conflicts: int,
    new_conflicts: int
) -> float:
    """
    Simple reward calculation (executive spec):
    +1  if conflict reduced
    -5  if conflict worsened
    +0.2 if student load improved
    
    NO complex multi-metric calculations
    NO deep analysis of feasibility
    """
    reward = 0.0
    
    # Primary: Conflict change
    conflict_delta = old_conflicts - new_conflicts
    if conflict_delta > 0:
        # Conflict reduced (good)
        reward += 1.0 * conflict_delta
    elif conflict_delta < 0:
        # Conflict worsened (bad)
        reward -= 5.0 * abs(conflict_delta)
    
    # Secondary: Load improvement (small bonus)
    load_improved = _check_load_improvement(old_schedule, new_schedule, courses)
    if load_improved:
        reward += 0.2
    
    return reward


def _check_load_improvement(
    old_schedule: Dict,
    new_schedule: Dict,
    courses: List[Course]
) -> bool:
    """
    Check if faculty load distribution improved
    Returns True if load became more balanced
    """
    old_load = _calculate_faculty_load(old_schedule, courses)
    new_load = _calculate_faculty_load(new_schedule, courses)
    
    if not old_load or not new_load:
        return False
    
    # Compare variance (lower is better)
    old_variance = _variance(list(old_load.values()))
    new_variance = _variance(list(new_load.values()))
    
    return new_variance < old_variance


def _calculate_faculty_load(schedule: Dict, courses: List[Course]) -> Dict[str, int]:
    """Calculate faculty workload"""
    load = defaultdict(int)
    for (course_id, session) in schedule.keys():
        course = next((c for c in courses if c.course_id == course_id), None)
        if course:
            load[course.faculty_id] += 1
    return dict(load)


def _variance(values: List[float]) -> float:
    """Calculate variance of list"""
    if not values:
        return 0.0
    mean = sum(values) / len(values)
    return sum((x - mean) ** 2 for x in values) / len(values)
