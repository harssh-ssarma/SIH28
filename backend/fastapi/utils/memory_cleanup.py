"""
Memory Cleanup Utilities
Aggressive cleanup to prevent Windows lag after generation
"""
import gc
import logging
import psutil
import os

logger = logging.getLogger(__name__)


def get_memory_usage() -> dict:
    """Get current memory usage"""
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()
    
    return {
        'rss_mb': mem_info.rss / (1024 * 1024),  # Resident Set Size
        'vms_mb': mem_info.vms / (1024 * 1024),  # Virtual Memory Size
        'percent': process.memory_percent()
    }


def aggressive_cleanup():
    """
    Aggressive memory cleanup to prevent Windows lag
    - Clears GPU cache
    - Forces 3-pass garbage collection
    - Logs memory before/after
    """
    # Memory before cleanup
    before = get_memory_usage()
    logger.info(f"[CLEANUP] Memory before: {before['rss_mb']:.1f}MB RSS, {before['percent']:.1f}%")
    
    # 1. Clear GPU cache
    try:
        import torch
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
            logger.info("[CLEANUP] GPU cache cleared")
    except ImportError:
        pass
    except Exception as e:
        logger.debug(f"[CLEANUP] GPU cleanup skipped: {e}")
    
    # 2. Force garbage collection (3 passes)
    collected = []
    for i in range(3):
        count = gc.collect()
        collected.append(count)
    
    logger.info(f"[CLEANUP] GC collected: {sum(collected)} objects in 3 passes")
    
    # Memory after cleanup
    after = get_memory_usage()
    freed_mb = before['rss_mb'] - after['rss_mb']
    
    logger.info(f"[CLEANUP] Memory after: {after['rss_mb']:.1f}MB RSS, {after['percent']:.1f}%")
    logger.info(f"[CLEANUP] Freed: {freed_mb:.1f}MB ({freed_mb/before['rss_mb']*100:.1f}%)")
    
    return {
        'before': before,
        'after': after,
        'freed_mb': freed_mb,
        'gc_collected': sum(collected)
    }


def cleanup_large_objects(*objects):
    """Delete large objects and force cleanup"""
    count = 0
    for obj in objects:
        if obj is not None:
            try:
                del obj
                count += 1
            except:
                pass
    
    if count > 0:
        gc.collect()
        logger.debug(f"[CLEANUP] Deleted {count} large objects")
