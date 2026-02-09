"""
Genetic Algorithm Module - Production CPU-Only Implementation

DESIGN FREEZE: Removed GPU, Island Model, Distributed modes
- CPU-only execution (no GPU dependencies)
- Single population (no threading/multiprocessing)
- Deterministic and testable
- Backward compatible interface
"""
from .optimizer import GeneticAlgorithmOptimizer
from .fitness import evaluate_fitness_simple
from .operators import crossover, mutate, tournament_selection

__all__ = [
    'GeneticAlgorithmOptimizer',
    'evaluate_fitness_simple',
    'crossover',
    'mutate',
    'tournament_selection'
]


