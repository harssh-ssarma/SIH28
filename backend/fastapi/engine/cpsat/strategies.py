"""
CP-SAT Solver Strategies
Progressive relaxation strategies for timetable solving
Following Google/Meta standards: One file = strategy configuration
"""
from typing import List, Dict


# Strategy definitions for progressive relaxation
STRATEGIES: List[Dict] = [
    {
        "name": "Fast Solve with Priority Students",
        "student_priority": "CRITICAL",  # Only critical students (5+ courses)
        "faculty_conflicts": True,
        "room_capacity": True,
        "timeout": 60,  # Increased: model building alone takes 200s, need time for solving
        "max_constraints": 10000,
        "student_limit": 500
    },
    {
        "name": "Faculty + Room Only",
        "student_priority": None,  # No student constraints for speed
        "faculty_conflicts": True,
        "room_capacity": True,
        "timeout": 45,  # Increased to allow time for solving after model construction
        "max_constraints": 5000,
        "student_limit": 0
    },
    {
        "name": "Minimal Hard Constraints Only",
        "student_priority": None,
        "faculty_conflicts": True,  # Only faculty conflicts
        "room_capacity": False,  # Relax room capacity
        "timeout": 30,  # Increased for last resort attempt
        "max_constraints": 1000,
        "student_limit": 0
    }
]


def get_strategy_by_index(index: int) -> Dict:
    """
    Get strategy by index with bounds checking
    Returns strategy dict or raises IndexError
    """
    if 0 <= index < len(STRATEGIES):
        return STRATEGIES[index]
    raise IndexError(f"Strategy index {index} out of range (0-{len(STRATEGIES)-1})")


def get_strategy_by_name(name: str) -> Dict:
    """
    Get strategy by name
    Returns strategy dict or None if not found
    """
    for strategy in STRATEGIES:
        if strategy["name"] == name:
            return strategy
    return None


def select_strategy_for_cluster_size(cluster_size: int) -> Dict:
    """
    Select appropriate strategy based on cluster size
    Smaller clusters can use more complex strategies
    """
    if cluster_size <= 10:
        return STRATEGIES[0]  # Full constraints
    elif cluster_size <= 30:
        return STRATEGIES[1]  # Faculty + Room
    else:
        return STRATEGIES[2]  # Minimal constraints
