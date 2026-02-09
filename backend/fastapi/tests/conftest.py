"""
Test Configuration
Pytest configuration and fixtures for the entire test suite
"""
import pytest
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def mock_redis():
    """Mock Redis client for testing"""
    class MockRedis:
        def __init__(self):
            self.data = {}
        
        def get(self, key):
            return self.data.get(key)
        
        def set(self, key, value, ex=None):
            self.data[key] = value
        
        def setex(self, key, time, value):
            self.data[key] = value
        
        def delete(self, key):
            if key in self.data:
                del self.data[key]
        
        def ping(self):
            return True
        
        def publish(self, channel, message):
            pass
    
    return MockRedis()


@pytest.fixture
def mock_hardware_profile():
    """Mock hardware profile for testing"""
    from engine.hardware import HardwareProfile, ExecutionStrategy
    
    return HardwareProfile(
        cpu_cores=4,
        cpu_threads=8,
        cpu_frequency=2.5,
        cpu_architecture="x86_64",
        total_ram_gb=8.0,
        available_ram_gb=4.0,
        has_nvidia_gpu=False,
        has_amd_gpu=False,
        gpu_memory_gb=0.0,
        cuda_version=None,
        opencl_available=False,
        storage_type="SSD",
        storage_speed_mbps=500.0,
        network_bandwidth_mbps=100.0,
        is_cloud_instance=False,
        cloud_provider=None,
        distributed_nodes=[],
        optimal_strategy=ExecutionStrategy.CPU_MULTI,
        fallback_strategies=[ExecutionStrategy.CPU_SINGLE],
        cpu_multiplier=1.0,
        gpu_multiplier=1.0,
        memory_multiplier=1.0
    )


@pytest.fixture
def sample_generation_request():
    """Sample generation request for testing"""
    return {
        "organization_id": "test-org-123",
        "semester": 1,
        "time_config": {
            "working_days": 6,
            "slots_per_day": 9,
            "start_time": "09:00",
            "slot_duration_minutes": 60
        }
    }
