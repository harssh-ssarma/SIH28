"""
Hardware Detection Module - Public API
Following Google/Meta standards: Clean, minimal public interface
"""
from .profile import (
    HardwareProfile,
    ExecutionStrategy,
    calculate_performance_multipliers
)
from .detector import HardwareDetector
from .gpu_detector import detect_all_gpus, detect_nvidia_gpu, detect_amd_gpu
from .cloud_detector import detect_cloud_and_distributed, detect_cloud_provider
from .config import get_optimal_config


# Convenience function for quick access
def get_hardware_profile(force_refresh: bool = False) -> HardwareProfile:
    """
    Get current hardware profile
    Main entry point for hardware detection
    """
    detector = HardwareDetector()
    return detector.detect_hardware(force_refresh)


__all__ = [
    'HardwareProfile',
    'ExecutionStrategy',
    'HardwareDetector',
    'get_hardware_profile',
    'get_optimal_config',
    'calculate_performance_multipliers',
    'detect_all_gpus',
    'detect_nvidia_gpu',
    'detect_amd_gpu',
    'detect_cloud_and_distributed',
    'detect_cloud_provider'
]
