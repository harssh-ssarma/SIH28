"""
Context Engine Module - Read-Only Signal Provider
Following Google/Meta standards: SIGNALS, not DECISIONS
Executive verdict: "A read-only signal provider, not a decision engine"

Role: Aggregate historical, slow-moving signals that inform decisions
NOT: Trigger actions, modify schedules, run in CP-SAT loops
"""
from .feature_store import ContextFeatureStore
from .signal_extractor import SignalExtractor

__all__ = [
    'ContextFeatureStore',
    'SignalExtractor'
]
