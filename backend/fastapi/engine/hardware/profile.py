"""
Hardware Profile Data Structures
Following Google/Meta standards: One file = one responsibility
"""
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class ExecutionStrategy(Enum):
    """Available execution strategies based on hardware"""
    CPU_SINGLE = "cpu_single"           # Basic CPU, single-threaded
    CPU_MULTI = "cpu_multi"             # Multi-core CPU, parallel processing
    GPU_CUDA = "gpu_cuda"               # NVIDIA GPU with CUDA
    GPU_OPENCL = "gpu_opencl"           # AMD/Intel GPU with OpenCL
    DISTRIBUTED_LOCAL = "distributed_local"  # Local cluster/multiple machines
    CLOUD_DISTRIBUTED = "cloud_distributed"  # Cloud-based distributed computing
    HYBRID = "hybrid"                   # Combination of multiple strategies


@dataclass
class HardwareProfile:
    """Complete hardware profile for optimization"""
    # CPU Information
    cpu_cores: int
    cpu_threads: int
    cpu_frequency: float
    cpu_architecture: str
    
    # Memory Information
    total_ram_gb: float
    available_ram_gb: float
    
    # GPU Information
    has_nvidia_gpu: bool
    has_amd_gpu: bool
    gpu_memory_gb: float
    cuda_version: Optional[str]
    opencl_available: bool
    
    # Storage Information
    storage_type: str  # SSD, HDD, NVMe
    storage_speed_mbps: float
    
    # Network Information
    network_bandwidth_mbps: float
    
    # Cloud/Distributed Information
    is_cloud_instance: bool
    cloud_provider: Optional[str]
    distributed_nodes: List[str]
    
    # Recommended Strategy
    optimal_strategy: ExecutionStrategy
    fallback_strategies: List[ExecutionStrategy]
    
    # Performance Multipliers
    cpu_multiplier: float
    gpu_multiplier: float
    memory_multiplier: float
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            'cpu_cores': self.cpu_cores,
            'cpu_threads': self.cpu_threads,
            'cpu_frequency': self.cpu_frequency,
            'cpu_architecture': self.cpu_architecture,
            'total_ram_gb': self.total_ram_gb,
            'available_ram_gb': self.available_ram_gb,
            'has_nvidia_gpu': self.has_nvidia_gpu,
            'has_amd_gpu': self.has_amd_gpu,
            'gpu_memory_gb': self.gpu_memory_gb,
            'cuda_version': self.cuda_version,
            'opencl_available': self.opencl_available,
            'storage_type': self.storage_type,
            'storage_speed_mbps': self.storage_speed_mbps,
            'network_bandwidth_mbps': self.network_bandwidth_mbps,
            'is_cloud_instance': self.is_cloud_instance,
            'cloud_provider': self.cloud_provider,
            'distributed_nodes': self.distributed_nodes,
            'optimal_strategy': self.optimal_strategy.value,
            'fallback_strategies': [s.value for s in self.fallback_strategies],
            'cpu_multiplier': self.cpu_multiplier,
            'gpu_multiplier': self.gpu_multiplier,
            'memory_multiplier': self.memory_multiplier
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'HardwareProfile':
        """Create HardwareProfile from dictionary"""
        return cls(
            cpu_cores=data['cpu_cores'],
            cpu_threads=data['cpu_threads'],
            cpu_frequency=data['cpu_frequency'],
            cpu_architecture=data['cpu_architecture'],
            total_ram_gb=data['total_ram_gb'],
            available_ram_gb=data['available_ram_gb'],
            has_nvidia_gpu=data['has_nvidia_gpu'],
            has_amd_gpu=data['has_amd_gpu'],
            gpu_memory_gb=data['gpu_memory_gb'],
            cuda_version=data['cuda_version'],
            opencl_available=data['opencl_available'],
            storage_type=data['storage_type'],
            storage_speed_mbps=data['storage_speed_mbps'],
            network_bandwidth_mbps=data['network_bandwidth_mbps'],
            is_cloud_instance=data['is_cloud_instance'],
            cloud_provider=data['cloud_provider'],
            distributed_nodes=data['distributed_nodes'],
            optimal_strategy=ExecutionStrategy(data['optimal_strategy']),
            fallback_strategies=[ExecutionStrategy(s) for s in data['fallback_strategies']],
            cpu_multiplier=data['cpu_multiplier'],
            gpu_multiplier=data['gpu_multiplier'],
            memory_multiplier=data['memory_multiplier']
        )


def calculate_performance_multipliers(cpu_info: Dict, gpu_info: Dict, memory_info: Dict) -> Dict:
    """
    Calculate performance multipliers based on hardware
    Separated utility function for testability
    """
    # CPU multiplier based on cores and frequency
    base_cpu_score = 4 * 2400  # 4 cores at 2.4GHz baseline
    actual_cpu_score = cpu_info['cores'] * cpu_info['frequency']
    cpu_multiplier = min(actual_cpu_score / base_cpu_score, 4.0)  # Cap at 4x
    
    # GPU multiplier
    gpu_multiplier = 1.0
    if gpu_info.get('has_nvidia') and gpu_info.get('memory_gb', 0) >= 4:
        gpu_multiplier = min(2.0 + (gpu_info['memory_gb'] / 8.0), 8.0)  # 2x to 8x
    elif gpu_info.get('has_amd') and gpu_info.get('memory_gb', 0) >= 4:
        gpu_multiplier = min(1.5 + (gpu_info['memory_gb'] / 8.0), 4.0)  # 1.5x to 4x
    
    # Memory multiplier
    base_memory = 8.0  # 8GB baseline
    memory_multiplier = min(memory_info['total_gb'] / base_memory, 4.0)  # Cap at 4x
    
    return {
        'cpu': cpu_multiplier,
        'gpu': gpu_multiplier,
        'memory': memory_multiplier
    }
