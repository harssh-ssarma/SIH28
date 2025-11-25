"""Hardware-Adaptive Engine Package"""
from .hardware_detector import HardwareDetector, get_hardware_profile
from .adaptive_executor import AdaptiveExecutor, get_adaptive_executor
from .stage2_hybrid import CPSATSolver, GeneticAlgorithmOptimizer
from .stage3_rl import ContextAwareRLAgent, resolve_conflicts_with_enhanced_rl

__all__ = [
    'HardwareDetector', 'get_hardware_profile',
    'AdaptiveExecutor', 'get_adaptive_executor', 
    'CPSATSolver', 'GeneticAlgorithmOptimizer',
    'ContextAwareRLAgent', 'resolve_conflicts_with_enhanced_rl'
]
