"""
Production Memory Monitor - Background RAM Management
Following Google/Meta standards: Non-blocking, configurable, safe cleanup strategies

Pattern: Google SRE monitoring, Meta resource management
Role: Monitor RAM usage and trigger cleanup when thresholds exceeded
NOT: Block execution, kill processes without warning, run continuously

Key Design Principles:
- Non-blocking background thread
- Graceful degradation (GC → cache eviction → job cancellation)
- Clear metrics and logging
- Configurable thresholds
- Safe shutdown
"""
import logging
import threading
import time
import gc
import psutil
from typing import Optional, Callable, List, Dict
from datetime import datetime
from collections import deque

logger = logging.getLogger(__name__)


class MemoryMonitor:
    """
    Production-grade memory monitor with background monitoring
    
    Monitoring Strategy (Google/Meta pattern):
    1. Check RAM every N seconds (default: 10s)
    2. If > warning threshold (80%): Log warning
    3. If > critical threshold (90%): Trigger cleanup
    4. Cleanup sequence: GC → Cache → Jobs (graceful degradation)
    
    NOT a continuous monitor - periodic checks only
    """
    
    def __init__(
        self,
        warning_threshold: float = 0.80,  # 80%
        critical_threshold: float = 0.90,  # 90%
        check_interval: int = 10,  # seconds
        enabled: bool = True
    ):
        self.warning_threshold = warning_threshold
        self.critical_threshold = critical_threshold
        self.check_interval = check_interval
        self.enabled = enabled
        
        # Background monitoring
        self._monitor_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._running = False
        
        # Cleanup callbacks (strategy pattern)
        self._cleanup_callbacks: List[Callable[[], int]] = []
        
        # Metrics
        self._memory_history = deque(maxlen=100)  # Last 100 checks
        self._cleanup_count = 0
        self._warning_count = 0
        
        logger.info(f"[MemoryMonitor] Initialized: warning={warning_threshold*100:.0f}%, critical={critical_threshold*100:.0f}%")
    
    def start(self):
        """
        Start background monitoring thread
        
        GUARDRAIL: Non-blocking, daemon thread
        """
        if not self.enabled:
            logger.info("[MemoryMonitor] Disabled, not starting")
            return
        
        if self._running:
            logger.warning("[MemoryMonitor] Already running")
            return
        
        self._running = True
        self._stop_event.clear()
        
        # Daemon thread - won't block shutdown
        self._monitor_thread = threading.Thread(
            target=self._monitor_loop,
            name="MemoryMonitor",
            daemon=True
        )
        self._monitor_thread.start()
        
        logger.info(f"[MemoryMonitor] Started (check interval: {self.check_interval}s)")
    
    def stop(self):
        """
        Stop background monitoring thread gracefully
        
        GUARDRAIL: Graceful shutdown
        """
        if not self._running:
            return
        
        logger.info("[MemoryMonitor] Stopping...")
        self._running = False
        self._stop_event.set()
        
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5.0)
        
        logger.info("[MemoryMonitor] Stopped")
    
    def register_cleanup_callback(self, callback: Callable[[], int]):
        """
        Register cleanup callback (strategy pattern)
        
        Callback should:
        - Return number of bytes freed (approximate)
        - Be fast (< 1 second)
        - Be idempotent (safe to call multiple times)
        
        Example callbacks:
        - Clear cache: lambda: cache_manager.clear()
        - Cancel low-priority jobs: lambda: job_queue.cancel_low_priority()
        """
        self._cleanup_callbacks.append(callback)
        logger.debug(f"[MemoryMonitor] Registered cleanup callback: {callback.__name__}")
    
    def get_memory_usage(self) -> Dict[str, float]:
        """
        Get current memory usage
        
        Returns:
            {
                'percent': 0.75,  # 75% used
                'used_gb': 12.5,
                'available_gb': 3.5,
                'total_gb': 16.0
            }
        """
        memory = psutil.virtual_memory()
        return {
            'percent': memory.percent / 100.0,
            'used_gb': memory.used / (1024**3),
            'available_gb': memory.available / (1024**3),
            'total_gb': memory.total / (1024**3)
        }
    
    def force_cleanup(self) -> Dict[str, int]:
        """
        Force cleanup immediately (manual trigger)
        
        Returns:
            {
                'gc_collected': 1234,
                'callbacks_freed_bytes': 5678910,
                'total_freed_mb': 5.4
            }
        """
        logger.info("[MemoryMonitor] Force cleanup triggered")
        return self._execute_cleanup()
    
    def _monitor_loop(self):
        """
        Background monitoring loop
        
        Pattern: Google SRE periodic checks (NOT continuous polling)
        """
        logger.info("[MemoryMonitor] Monitor loop started")
        
        while self._running and not self._stop_event.is_set():
            try:
                # Check memory
                usage = self.get_memory_usage()
                percent = usage['percent']
                
                # Record metrics
                self._memory_history.append({
                    'timestamp': datetime.now().isoformat(),
                    'percent': percent,
                    'used_gb': usage['used_gb']
                })
                
                # Decision logic (graceful escalation)
                if percent >= self.critical_threshold:
                    # CRITICAL: Trigger cleanup
                    logger.error(
                        f"[MemoryMonitor] CRITICAL: RAM usage {percent*100:.1f}% "
                        f"(threshold: {self.critical_threshold*100:.0f}%)"
                    )
                    self._execute_cleanup()
                
                elif percent >= self.warning_threshold:
                    # WARNING: Log only
                    self._warning_count += 1
                    if self._warning_count % 6 == 1:  # Log every ~1 minute
                        logger.warning(
                            f"[MemoryMonitor] WARNING: RAM usage {percent*100:.1f}% "
                            f"(threshold: {self.warning_threshold*100:.0f}%)"
                        )
                
                else:
                    # Normal: Reset warning counter
                    self._warning_count = 0
                
            except Exception as e:
                logger.error(f"[MemoryMonitor] Error in monitor loop: {e}", exc_info=True)
            
            # Sleep (interruptible)
            self._stop_event.wait(self.check_interval)
        
        logger.info("[MemoryMonitor] Monitor loop stopped")
    
    def _execute_cleanup(self) -> Dict[str, int]:
        """
        Execute cleanup sequence (graceful degradation)
        
        Strategy (Google/Meta pattern):
        1. Python garbage collection (fast, safe)
        2. Registered callbacks (cache eviction, etc.)
        3. Log results
        
        NOT: Kill processes, block execution, infinite loops
        """
        self._cleanup_count += 1
        
        logger.info("[MemoryMonitor] Executing cleanup sequence...")
        
        # Get before state
        before = self.get_memory_usage()
        
        # Step 1: Python garbage collection
        logger.info("[MemoryMonitor] Step 1: Garbage collection")
        gc_collected = gc.collect()
        logger.info(f"[MemoryMonitor] GC collected {gc_collected} objects")
        
        # Step 2: Registered callbacks (cache eviction, etc.)
        total_freed_bytes = 0
        for i, callback in enumerate(self._cleanup_callbacks):
            try:
                logger.info(f"[MemoryMonitor] Step 2.{i+1}: Running callback {callback.__name__}")
                freed_bytes = callback()
                total_freed_bytes += freed_bytes
                logger.info(f"[MemoryMonitor] Callback freed ~{freed_bytes / (1024**2):.1f} MB")
            except Exception as e:
                logger.error(f"[MemoryMonitor] Callback {callback.__name__} failed: {e}")
        
        # Get after state
        time.sleep(1)  # Allow memory to settle
        after = self.get_memory_usage()
        
        # Calculate results
        freed_gb = before['used_gb'] - after['used_gb']
        result = {
            'gc_collected': gc_collected,
            'callbacks_freed_bytes': total_freed_bytes,
            'total_freed_gb': freed_gb,
            'before_percent': before['percent'],
            'after_percent': after['percent']
        }
        
        logger.info(
            f"[MemoryMonitor] Cleanup complete: "
            f"{before['percent']*100:.1f}% → {after['percent']*100:.1f}% "
            f"(freed ~{freed_gb:.2f} GB)"
        )
        
        return result
    
    def get_stats(self) -> Dict:
        """
        Get monitoring statistics
        
        Use case: Metrics dashboard, health checks
        """
        current = self.get_memory_usage()
        
        # Calculate averages from history
        if self._memory_history:
            avg_percent = sum(h['percent'] for h in self._memory_history) / len(self._memory_history)
            max_percent = max(h['percent'] for h in self._memory_history)
        else:
            avg_percent = current['percent']
            max_percent = current['percent']
        
        return {
            'enabled': self.enabled,
            'running': self._running,
            'current_usage_percent': current['percent'] * 100,
            'current_used_gb': current['used_gb'],
            'total_gb': current['total_gb'],
            'warning_threshold': self.warning_threshold * 100,
            'critical_threshold': self.critical_threshold * 100,
            'cleanup_count': self._cleanup_count,
            'warning_count': self._warning_count,
            'avg_usage_percent': avg_percent * 100,
            'max_usage_percent': max_percent * 100,
            'history_size': len(self._memory_history)
        }
    
    def __enter__(self):
        """Context manager support"""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager support"""
        self.stop()


# Singleton instance (Google pattern: global monitoring)
_global_monitor: Optional[MemoryMonitor] = None


def get_memory_monitor() -> MemoryMonitor:
    """
    Get global memory monitor instance
    
    Pattern: Singleton for application-wide monitoring
    """
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = MemoryMonitor()
    return _global_monitor


def start_memory_monitoring(
    warning_threshold: float = 0.80,
    critical_threshold: float = 0.90,
    check_interval: int = 10
):
    """
    Start global memory monitoring
    
    Usage (at application startup):
        from core.memory_monitor import start_memory_monitoring
        start_memory_monitoring()
    """
    monitor = get_memory_monitor()
    monitor.warning_threshold = warning_threshold
    monitor.critical_threshold = critical_threshold
    monitor.check_interval = check_interval
    monitor.start()
    logger.info("[App] Memory monitoring started")


def stop_memory_monitoring():
    """
    Stop global memory monitoring
    
    Usage (at application shutdown):
        from core.memory_monitor import stop_memory_monitoring
        stop_memory_monitoring()
    """
    monitor = get_memory_monitor()
    monitor.stop()
    logger.info("[App] Memory monitoring stopped")
