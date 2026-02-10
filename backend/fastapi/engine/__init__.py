"""Hardware-Adaptive Engine Package"""
from .hardware import HardwareDetector, get_hardware_profile
from .adaptive_executor import AdaptiveExecutor, get_adaptive_executor
from .stage1_clustering import LouvainClusterer
from .cpsat import AdaptiveCPSATSolver
from .ga import GeneticAlgorithmOptimizer
from .rl import SimpleTabularQLearning

__all__ = [
    'HardwareDetector', 'get_hardware_profile',
    'AdaptiveExecutor', 'get_adaptive_executor',
    'LouvainClusterer',
    'AdaptiveCPSATSolver',
    'GeneticAlgorithmOptimizer',
    'SimpleTabularQLearning'
]
