"""Hardware-Adaptive Engine Package"""
from .hardware_detector import HardwareDetector, get_hardware_profile
from .adaptive_executor import AdaptiveExecutor, get_adaptive_executor
from .stage1_clustering import LouvainClusterer
from .stage2_cpsat import AdaptiveCPSATSolver
from .stage2_greedy import SmartGreedyScheduler
from .stage2_ga import GeneticAlgorithmOptimizer
from .stage3_rl import RLConflictResolver, ContextAwareRLAgent
from .memory_manager import (
    MemoryManager, get_memory_manager, reset_memory_manager,
    memory_monitored, check_memory_limit, batch_process
)
from .orchestrator import HardwareOrchestrator, get_orchestrator, reset_orchestrator

__all__ = [
    'HardwareDetector', 'get_hardware_profile',
    'AdaptiveExecutor', 'get_adaptive_executor',
    'LouvainClusterer',
    'AdaptiveCPSATSolver', 'SmartGreedyScheduler',
    'GeneticAlgorithmOptimizer',
    'RLConflictResolver', 'ContextAwareRLAgent',
    'MemoryManager', 'get_memory_manager', 'reset_memory_manager',
    'memory_monitored', 'check_memory_limit', 'batch_process',
    'HardwareOrchestrator', 'get_orchestrator', 'reset_orchestrator'
]
