"""
GPU Detection Utilities
Detects NVIDIA, AMD, and OpenCL-capable GPUs
Following Google/Meta standards: One file = GPU detection only
"""
import logging
import subprocess
from typing import Dict

logger = logging.getLogger(__name__)


def detect_nvidia_gpu() -> Dict:
    """
    Detect NVIDIA GPU via nvidia-smi and PyTorch
    Returns dict with has_nvidia, memory_gb, cuda_version
    """
    gpu_info = {
        'has_nvidia': False,
        'memory_gb': 0.0,
        'cuda_version': None
    }
    
    # Method 1: nvidia-smi (most reliable)
    try:
        result = subprocess.run(
            ['nvidia-smi', '--query-gpu=name,memory.total', '--format=csv,noheader'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0 and result.stdout:
            lines = result.stdout.strip().split('\n')
            if lines:
                parts = lines[0].split(',')
                gpu_name = parts[0].strip()
                memory_mb = int(parts[1].strip().split()[0])
                gpu_info['has_nvidia'] = True
                gpu_info['memory_gb'] = memory_mb / 1024
                logger.info(f"[GPU] NVIDIA GPU: {gpu_name} ({gpu_info['memory_gb']:.1f}GB)")
                return gpu_info
    except Exception as e:
        logger.debug(f"nvidia-smi detection failed: {e}")
    
    # Method 2: PyTorch fallback
    try:
        import torch
        if torch.cuda.is_available():
            gpu_info['has_nvidia'] = True
            gpu_info['memory_gb'] = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            gpu_info['cuda_version'] = torch.version.cuda
            logger.info(f"[GPU] GPU via PyTorch: {torch.cuda.get_device_name(0)}")
    except ImportError:
        logger.debug("PyTorch not installed")
    except Exception as e:
        logger.debug(f"PyTorch GPU detection failed: {e}")
    
    return gpu_info


def detect_amd_gpu() -> Dict:
    """
    Detect AMD GPU via OpenCL
    Returns dict with has_amd, memory_gb, opencl_available
    """
    gpu_info = {
        'has_amd': False,
        'memory_gb': 0.0,
        'opencl_available': False
    }
    
    try:
        import pyopencl as cl
        platforms = cl.get_platforms()
        
        for platform in platforms:
            devices = platform.get_devices()
            for device in devices:
                if device.type == cl.device_type.GPU:
                    gpu_info['opencl_available'] = True
                    
                    if 'AMD' in device.vendor.upper():
                        gpu_info['has_amd'] = True
                        memory_gb = device.global_mem_size / (1024**3)
                        gpu_info['memory_gb'] = max(gpu_info['memory_gb'], memory_gb)
                        logger.info(f"[GPU] AMD GPU detected: {device.name} ({memory_gb:.1f}GB)")
                    else:
                        logger.info(f"[GPU] OpenCL GPU detected: {device.name}")
                        
    except ImportError:
        logger.debug("PyOpenCL not installed")
    except Exception as e:
        logger.debug(f"OpenCL GPU detection failed: {e}")
    
    return gpu_info


def detect_all_gpus() -> Dict:
    """
    Detect all GPUs (NVIDIA, AMD, OpenCL)
    Combines results from nvidia and amd detection
    """
    nvidia_info = detect_nvidia_gpu()
    amd_info = detect_amd_gpu()
    
    return {
        'has_nvidia': nvidia_info['has_nvidia'],
        'has_amd': amd_info['has_amd'],
        'memory_gb': max(nvidia_info['memory_gb'], amd_info['memory_gb']),
        'cuda_version': nvidia_info['cuda_version'],
        'opencl_available': amd_info['opencl_available']
    }
