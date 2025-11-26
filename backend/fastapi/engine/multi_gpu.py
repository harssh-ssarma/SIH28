"""
Multi-GPU Support for GA Islands
"""
import torch
import logging
from typing import List

logger = logging.getLogger(__name__)

class MultiGPUManager:
    """Manage multiple GPUs for parallel island evolution"""
    
    def __init__(self):
        self.num_gpus = 0
        self.devices = []
        self._detect_gpus()
    
    def _detect_gpus(self):
        """Detect available GPUs"""
        if not torch.cuda.is_available():
            logger.info("No GPUs available")
            return
        
        self.num_gpus = torch.cuda.device_count()
        self.devices = [torch.device(f'cuda:{i}') for i in range(self.num_gpus)]
        
        for i, device in enumerate(self.devices):
            props = torch.cuda.get_device_properties(device)
            logger.info(f"GPU {i}: {props.name} ({props.total_memory / 1024**3:.1f}GB)")
    
    def distribute_islands(self, num_islands: int) -> List[int]:
        """Distribute islands across GPUs"""
        if self.num_gpus == 0:
            return [0] * num_islands  # CPU fallback
        
        # Round-robin distribution
        gpu_assignments = [i % self.num_gpus for i in range(num_islands)]
        logger.info(f"Distributed {num_islands} islands across {self.num_gpus} GPUs")
        return gpu_assignments
    
    def get_device(self, gpu_id: int):
        """Get device for GPU ID"""
        if gpu_id >= len(self.devices):
            return torch.device('cpu')
        return self.devices[gpu_id]

multi_gpu_manager = MultiGPUManager()
