"""
Continuous Resource Monitor - Detects memory pressure and triggers emergency actions
"""
import psutil
import logging
import asyncio
from typing import Callable, Optional

logger = logging.getLogger(__name__)


class ResourceMonitor:
    """Monitor system resources and trigger emergency actions"""
    
    def __init__(self):
        self.monitoring = False
        self.emergency_callback: Optional[Callable] = None
        self.critical_callback: Optional[Callable] = None
    
    async def start_monitoring(self, job_id: str, interval: int = 30):
        """Start continuous monitoring"""
        self.monitoring = True
        logger.info(f"[MONITOR] Started resource monitoring for job {job_id}")
        
        while self.monitoring:
            try:
                mem = psutil.virtual_memory()
                
                if mem.percent > 95:
                    # CRITICAL: Abort
                    logger.error(f"[MONITOR] CRITICAL memory: {mem.percent}%")
                    if self.critical_callback:
                        await self.critical_callback()
                    self.monitoring = False
                    break
                    
                elif mem.percent > 85:
                    # WARNING: Emergency actions
                    logger.warning(f"[MONITOR] Memory pressure: {mem.percent}%")
                    if self.emergency_callback:
                        await self.emergency_callback()
                
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.error(f"[MONITOR] Error: {e}")
                break
        
        logger.info(f"[MONITOR] Stopped monitoring for job {job_id}")
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring = False
    
    def set_emergency_callback(self, callback: Callable):
        """Set callback for 85% memory"""
        self.emergency_callback = callback
    
    def set_critical_callback(self, callback: Callable):
        """Set callback for 95% memory"""
        self.critical_callback = callback
