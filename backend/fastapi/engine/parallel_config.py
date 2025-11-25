"""
Parallelization Configuration
Defines which stages use parallel vs sequential execution
"""
from dataclasses import dataclass
from typing import Literal

ExecutionMode = Literal["parallel", "sequential"]


@dataclass
class StageConfig:
    """Configuration for a pipeline stage"""
    name: str
    mode: ExecutionMode
    max_workers: int
    reason: str


class ParallelizationStrategy:
    """
    Defines parallelization strategy for each stage
    
    PARALLEL stages: Independent operations, no shared state
    SEQUENTIAL stages: Shared state mutations, race conditions
    """
    
    # Stage 1: Clustering - PARALLEL for edge computation
    STAGE1_CLUSTERING = StageConfig(
        name="Stage 1: Clustering",
        mode="parallel",
        max_workers=4,
        reason="Edge weight computation is independent (read-only course data)"
    )
    
    # Stage 2A: CP-SAT - PARALLEL for cluster solving
    STAGE2A_CPSAT = StageConfig(
        name="Stage 2A: CP-SAT",
        mode="parallel",
        max_workers=4,
        reason="Each cluster is independent, no shared state between solvers"
    )
    
    # Stage 2B: GA Fitness - PARALLEL for evaluation
    STAGE2B_GA_FITNESS = StageConfig(
        name="Stage 2B: GA Fitness",
        mode="parallel",
        max_workers=4,
        reason="Fitness evaluation is read-only, no mutations"
    )
    
    # Stage 2B: GA Evolution - SEQUENTIAL (mutation)
    STAGE2B_GA_EVOLUTION = StageConfig(
        name="Stage 2B: GA Evolution",
        mode="sequential",
        max_workers=1,
        reason="Population mutation requires sequential updates to prevent race conditions"
    )
    
    # Stage 3: RL - SEQUENTIAL (Q-table updates)
    STAGE3_RL = StageConfig(
        name="Stage 3: RL",
        mode="sequential",
        max_workers=1,
        reason="Q-table updates have race conditions, must be sequential"
    )
    
    # Data Loading - SEQUENTIAL (integrity)
    DATA_LOADING = StageConfig(
        name="Data Loading",
        mode="sequential",
        max_workers=1,
        reason="Student enrollment data integrity requires sequential loading"
    )


def get_optimal_workers(stage: StageConfig, available_cores: int) -> int:
    """
    Calculate optimal worker count based on available cores
    
    Args:
        stage: Stage configuration
        available_cores: Number of available CPU cores
        
    Returns:
        Optimal number of workers
    """
    if stage.mode == "sequential":
        return 1
    
    # Use 50-75% of available cores for parallel stages
    return min(stage.max_workers, max(1, int(available_cores * 0.75)))
