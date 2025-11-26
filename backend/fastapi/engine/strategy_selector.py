"""
Unified Strategy Selector - Maps hardware + user preferences to optimal strategies
"""
import logging
from dataclasses import dataclass
from typing import Dict, Literal

logger = logging.getLogger(__name__)

QualityMode = Literal['fast', 'balanced', 'best']

@dataclass
class StrategyConfig:
    """Configuration for all stages"""
    # Stage 1: Clustering
    clustering_workers: int
    edge_threshold: float
    
    # Stage 2A: CP-SAT
    cpsat_timeout: float
    cpsat_workers: int
    student_limit: int
    
    # Stage 2B: GA
    ga_population: int
    ga_generations: int
    ga_islands: int
    use_sample_fitness: bool
    sample_size: int
    
    # Stage 3: RL
    rl_iterations: int
    rl_batch_size: int
    
    # Meta
    profile_name: str
    expected_time_min: int
    expected_quality: int


class StrategySelector:
    """Select optimal strategy based on hardware + user preference"""
    
    def __init__(self):
        self.strategies = self._define_strategies()
    
    def _define_strategies(self) -> Dict[str, Dict[QualityMode, StrategyConfig]]:
        """Define strategy matrix: hardware_profile -> quality_mode -> config"""
        return {
            'potato': {  # <6GB RAM
                'fast': StrategyConfig(
                    clustering_workers=1, edge_threshold=1.0,
                    cpsat_timeout=0.5, cpsat_workers=1, student_limit=10,
                    ga_population=3, ga_generations=5, ga_islands=1,
                    use_sample_fitness=True, sample_size=30,
                    rl_iterations=50, rl_batch_size=1,
                    profile_name='Potato-Fast', expected_time_min=30, expected_quality=70
                ),
                'balanced': StrategyConfig(
                    clustering_workers=1, edge_threshold=0.8,
                    cpsat_timeout=1.0, cpsat_workers=1, student_limit=20,
                    ga_population=5, ga_generations=10, ga_islands=1,
                    use_sample_fitness=True, sample_size=50,
                    rl_iterations=100, rl_batch_size=1,
                    profile_name='Potato-Balanced', expected_time_min=45, expected_quality=75
                ),
                'best': StrategyConfig(
                    clustering_workers=1, edge_threshold=0.5,
                    cpsat_timeout=2.0, cpsat_workers=1, student_limit=50,
                    ga_population=8, ga_generations=15, ga_islands=1,
                    use_sample_fitness=True, sample_size=100,
                    rl_iterations=150, rl_batch_size=1,
                    profile_name='Potato-Best', expected_time_min=60, expected_quality=78
                )
            },
            'laptop': {  # 6-16GB RAM
                'fast': StrategyConfig(
                    clustering_workers=2, edge_threshold=0.5,
                    cpsat_timeout=1.0, cpsat_workers=2, student_limit=50,
                    ga_population=8, ga_generations=8, ga_islands=1,
                    use_sample_fitness=True, sample_size=100,
                    rl_iterations=100, rl_batch_size=10,
                    profile_name='Laptop-Fast', expected_time_min=8, expected_quality=80
                ),
                'balanced': StrategyConfig(
                    clustering_workers=4, edge_threshold=0.5,
                    cpsat_timeout=1.5, cpsat_workers=4, student_limit=100,
                    ga_population=10, ga_generations=15, ga_islands=1,
                    use_sample_fitness=True, sample_size=200,
                    rl_iterations=150, rl_batch_size=10,
                    profile_name='Laptop-Balanced', expected_time_min=12, expected_quality=85
                ),
                'best': StrategyConfig(
                    clustering_workers=4, edge_threshold=0.3,
                    cpsat_timeout=2.0, cpsat_workers=4, student_limit=200,
                    ga_population=15, ga_generations=20, ga_islands=1,
                    use_sample_fitness=False, sample_size=0,
                    rl_iterations=200, rl_batch_size=10,
                    profile_name='Laptop-Best', expected_time_min=18, expected_quality=88
                )
            },
            'workstation': {  # 16-32GB RAM, GPU
                'fast': StrategyConfig(
                    clustering_workers=8, edge_threshold=0.3,
                    cpsat_timeout=1.5, cpsat_workers=8, student_limit=100,
                    ga_population=15, ga_generations=10, ga_islands=4,
                    use_sample_fitness=True, sample_size=200,
                    rl_iterations=150, rl_batch_size=50,
                    profile_name='Workstation-Fast', expected_time_min=4, expected_quality=85
                ),
                'balanced': StrategyConfig(
                    clustering_workers=12, edge_threshold=0.3,
                    cpsat_timeout=2.0, cpsat_workers=12, student_limit=200,
                    ga_population=20, ga_generations=25, ga_islands=4,
                    use_sample_fitness=False, sample_size=0,
                    rl_iterations=200, rl_batch_size=50,
                    profile_name='Workstation-Balanced', expected_time_min=6, expected_quality=90
                ),
                'best': StrategyConfig(
                    clustering_workers=16, edge_threshold=0.2,
                    cpsat_timeout=3.0, cpsat_workers=16, student_limit=500,
                    ga_population=30, ga_generations=40, ga_islands=8,
                    use_sample_fitness=False, sample_size=0,
                    rl_iterations=300, rl_batch_size=100,
                    profile_name='Workstation-Best', expected_time_min=10, expected_quality=93
                )
            },
            'server': {  # 32GB+ RAM, Multi-GPU
                'fast': StrategyConfig(
                    clustering_workers=16, edge_threshold=0.2,
                    cpsat_timeout=2.0, cpsat_workers=16, student_limit=200,
                    ga_population=30, ga_generations=20, ga_islands=8,
                    use_sample_fitness=False, sample_size=0,
                    rl_iterations=200, rl_batch_size=100,
                    profile_name='Server-Fast', expected_time_min=2, expected_quality=88
                ),
                'balanced': StrategyConfig(
                    clustering_workers=24, edge_threshold=0.1,
                    cpsat_timeout=3.0, cpsat_workers=24, student_limit=500,
                    ga_population=50, ga_generations=50, ga_islands=16,
                    use_sample_fitness=False, sample_size=0,
                    rl_iterations=500, rl_batch_size=100,
                    profile_name='Server-Balanced', expected_time_min=3, expected_quality=92
                ),
                'best': StrategyConfig(
                    clustering_workers=32, edge_threshold=0.1,
                    cpsat_timeout=5.0, cpsat_workers=32, student_limit=1000,
                    ga_population=100, ga_generations=100, ga_islands=16,
                    use_sample_fitness=False, sample_size=0,
                    rl_iterations=1000, rl_batch_size=500,
                    profile_name='Server-Best', expected_time_min=5, expected_quality=95
                )
            }
        }
    
    def select(self, hardware_profile, quality_mode: QualityMode = 'balanced') -> StrategyConfig:
        """Select optimal strategy"""
        # Determine hardware tier
        ram_gb = hardware_profile.available_ram_gb
        cpu_cores = hardware_profile.cpu_cores
        has_gpu = hardware_profile.has_nvidia_gpu
        
        if ram_gb < 6:
            tier = 'potato'
        elif ram_gb < 16:
            tier = 'laptop'
        elif ram_gb < 32 or not has_gpu:
            tier = 'workstation'
        else:
            tier = 'server'
        
        strategy = self.strategies[tier][quality_mode]
        
        # Adjust for actual CPU cores
        strategy.clustering_workers = min(strategy.clustering_workers, cpu_cores)
        strategy.cpsat_workers = min(strategy.cpsat_workers, cpu_cores)
        
        logger.info(f"Selected strategy: {strategy.profile_name}")
        logger.info(f"Expected: {strategy.expected_time_min}min, {strategy.expected_quality}% quality")
        
        return strategy


# Global selector
_selector = None

def get_strategy_selector() -> StrategySelector:
    global _selector
    if _selector is None:
        _selector = StrategySelector()
    return _selector
