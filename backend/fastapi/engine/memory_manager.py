"""
Memory Management Utilities for Timetable Generation
Monitors and optimizes memory usage across all stages
"""
import psutil
import gc
import logging
from typing import Optional, Dict, Any
from functools import wraps

logger = logging.getLogger(__name__)


class MemoryManager:
    """
    Smart memory manager for timetable generation pipeline
    """
    
    def __init__(self, max_memory_percent: float = 80.0):
        """
        Initialize memory manager
        
        Args:
            max_memory_percent: Maximum memory usage threshold (default 80%)
        """
        self.max_memory_percent = max_memory_percent
        self.process = psutil.Process()
        self.initial_memory = self.get_memory_usage()
        
    def get_memory_usage(self) -> Dict[str, float]:
        """Get current memory usage statistics"""
        memory_info = self.process.memory_info()
        virtual_memory = psutil.virtual_memory()
        
        return {
            'rss_mb': memory_info.rss / (1024 * 1024),  # Resident Set Size
            'vms_mb': memory_info.vms / (1024 * 1024),  # Virtual Memory Size
            'percent': self.process.memory_percent(),
            'available_mb': virtual_memory.available / (1024 * 1024),
            'total_mb': virtual_memory.total / (1024 * 1024),
            'system_percent': virtual_memory.percent
        }
    
    def check_memory_threshold(self) -> bool:
        """Check if memory usage exceeds threshold"""
        usage = self.get_memory_usage()
        return usage['system_percent'] > self.max_memory_percent
    
    def force_cleanup(self):
        """Force garbage collection and memory cleanup"""
        gc.collect()
        logger.info("Forced garbage collection completed")
    
    def log_memory_stats(self, stage: str):
        """Log memory statistics for a stage"""
        usage = self.get_memory_usage()
        logger.info(
            f"[{stage}] Memory: RSS={usage['rss_mb']:.1f}MB, "
            f"Process={usage['percent']:.1f}%, System={usage['system_percent']:.1f}%"
        )
    
    def get_memory_delta(self) -> float:
        """Get memory increase since initialization"""
        current = self.get_memory_usage()
        return current['rss_mb'] - self.initial_memory['rss_mb']


def memory_monitored(stage_name: str):
    """
    Decorator to monitor memory usage for a function
    
    Usage:
        @memory_monitored("Stage 1: Clustering")
        def cluster_courses(self, courses):
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            manager = MemoryManager()
            
            # Log before execution
            manager.log_memory_stats(f"{stage_name} - START")
            
            # Check memory threshold
            if manager.check_memory_threshold():
                logger.warning(f"{stage_name}: Memory threshold exceeded, forcing cleanup")
                manager.force_cleanup()
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Log after execution
            manager.log_memory_stats(f"{stage_name} - END")
            delta = manager.get_memory_delta()
            logger.info(f"{stage_name}: Memory delta = {delta:+.1f}MB")
            
            # Cleanup after stage
            manager.force_cleanup()
            
            return result
        return wrapper
    return decorator


def optimize_dict_memory(data: Dict[Any, Any], max_size: int = 10000) -> Dict[Any, Any]:
    """
    Optimize dictionary memory by limiting size
    
    Args:
        data: Dictionary to optimize
        max_size: Maximum number of entries to keep
        
    Returns:
        Optimized dictionary
    """
    if len(data) > max_size:
        logger.warning(f"Dictionary size {len(data)} exceeds max {max_size}, truncating")
        # Keep only most recent entries
        items = list(data.items())[-max_size:]
        return dict(items)
    return data


def batch_process(items: list, batch_size: int = 100):
    """
    Generator to process items in batches for memory efficiency
    
    Usage:
        for batch in batch_process(large_list, batch_size=50):
            process(batch)
    """
    for i in range(0, len(items), batch_size):
        yield items[i:i + batch_size]


class MemoryLimitExceeded(Exception):
    """Exception raised when memory limit is exceeded"""
    pass


def check_memory_limit(max_percent: float = 90.0):
    """
    Check if memory usage exceeds critical limit
    
    Args:
        max_percent: Maximum allowed memory percentage
        
    Raises:
        MemoryLimitExceeded: If memory usage exceeds limit
    """
    memory = psutil.virtual_memory()
    if memory.percent > max_percent:
        raise MemoryLimitExceeded(
            f"Memory usage {memory.percent:.1f}% exceeds limit {max_percent}%"
        )


def get_optimal_batch_size(total_items: int, available_memory_mb: float = 1000) -> int:
    """
    Calculate optimal batch size based on available memory
    
    Args:
        total_items: Total number of items to process
        available_memory_mb: Available memory in MB
        
    Returns:
        Optimal batch size
    """
    # Estimate ~1KB per item (conservative)
    item_size_kb = 1
    items_per_mb = 1024 / item_size_kb
    
    # Use 50% of available memory for batch
    max_batch_items = int((available_memory_mb * 0.5) * items_per_mb)
    
    # Clamp between 10 and 1000
    batch_size = max(10, min(max_batch_items, 1000))
    
    logger.info(f"Calculated optimal batch size: {batch_size} for {total_items} items")
    return batch_size


# Global memory manager instance
_global_memory_manager: Optional[MemoryManager] = None


def get_memory_manager() -> MemoryManager:
    """Get or create global memory manager instance"""
    global _global_memory_manager
    if _global_memory_manager is None:
        _global_memory_manager = MemoryManager()
    return _global_memory_manager


def reset_memory_manager():
    """Reset global memory manager"""
    global _global_memory_manager
    _global_memory_manager = None
    gc.collect()
