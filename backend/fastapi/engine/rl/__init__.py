"""
Reinforcement Learning Module - Simplified Public API with Semester-Wise Learning
Following Google/Meta standards: SIMPLE, TABULAR, LOCAL swaps only
Executive verdict: "RL may suggest moves, not own the solution"

Production-safe framing:
- Q-learning with ε-greedy exploration (ε annealed and frozen during runtime)
- Context vectors as auxiliary decision signals (not decisions themselves)  
- Persistent transfer learning (semester-wise Q-table reuse creates institutional memory)

Three-layer architecture:
1. Runtime Scheduler (deterministic, NO learning)
2. Context Engine (read-only signals, batch updates)
3. RL Policy (semester-frozen, trained offline)

NO GPU, NO DQN, NO global repair
"""
from .qlearning import SimpleTabularQLearning
from .reward_calculator import calculate_simple_reward
from .state_manager import StateManager

__all__ = [
    'SimpleTabularQLearning',
    'calculate_simple_reward',
    'StateManager'
]
