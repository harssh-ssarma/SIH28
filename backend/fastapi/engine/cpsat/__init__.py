"""
CP-SAT Module - Public API
Following Google/Meta standards: Clean public interface
"""
from .solver import AdaptiveCPSATSolver
from .strategies import STRATEGIES, get_strategy_by_index, select_strategy_for_cluster_size
from .progress import update_progress, log_cluster_start
from .constraints import (
    add_faculty_constraints,
    add_room_constraints,
    add_student_constraints
)

__all__ = [
    'AdaptiveCPSATSolver',
    'STRATEGIES',
    'get_strategy_by_index',
    'select_strategy_for_cluster_size',
    'update_progress',
    'log_cluster_start',
    'add_faculty_constraints',
    'add_room_constraints',
    'add_student_constraints'
]
