"""
Bulkhead Pattern - Resource Isolation
Prevents resource exhaustion by isolating workloads into separate thread pools.
Following patterns used at Netflix (Hystrix) and Meta's service isolation strategy.
"""
import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Any

logger = logging.getLogger(__name__)


class ResourceIsolation:
    """
    Bulkhead pattern - isolate resources into separate thread pools.
    Prevents one failing component from exhausting all resources.
    
    Usage:
        isolation = ResourceIsolation()
        result = await isolation.execute_clustering(my_function, arg1, arg2)
    """
    
    def __init__(self, max_workers_per_pool: int = 2):
        """
        Initialize resource isolation with separate thread pools.
        
        Args:
            max_workers_per_pool: Maximum workers per isolated pool
        """
        # Minimal thread pools to prevent memory leaks and resource exhaustion
        self.clustering_pool = ThreadPoolExecutor(
            max_workers=max_workers_per_pool,
            thread_name_prefix="clustering"
        )
        self.cpsat_pool = ThreadPoolExecutor(
            max_workers=max_workers_per_pool,
            thread_name_prefix="cpsat"
        )
        self.context_pool = ThreadPoolExecutor(
            max_workers=max_workers_per_pool,
            thread_name_prefix="context"
        )
        
        logger.info(f"Resource isolation initialized with {max_workers_per_pool} workers per pool")
    
    async def execute_clustering(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute clustering work in isolated thread pool.
        
        Args:
            func: Function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Result from function execution
        """
        loop = asyncio.get_event_loop()
        logger.debug("Executing clustering in isolated thread pool")
        return await loop.run_in_executor(self.clustering_pool, func, *args)
    
    async def execute_cpsat(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute CP-SAT solving in isolated thread pool.
        
        Args:
            func: Function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Result from function execution
        """
        loop = asyncio.get_event_loop()
        logger.debug("Executing CP-SAT in isolated thread pool")
        return await loop.run_in_executor(self.cpsat_pool, func, *args)
    
    async def execute_context(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute context-aware work in isolated thread pool.
        
        Args:
            func: Function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Result from function execution
        """
        loop = asyncio.get_event_loop()
        logger.debug("Executing context work in isolated thread pool")
        return await loop.run_in_executor(self.context_pool, func, *args)
    
    def shutdown(self, wait: bool = True):
        """
        Shutdown all thread pools.
        
        Args:
            wait: Whether to wait for pending tasks to complete
        """
        logger.info("Shutting down resource isolation thread pools")
        self.clustering_pool.shutdown(wait=wait)
        self.cpsat_pool.shutdown(wait=wait)
        self.context_pool.shutdown(wait=wait)
    
    def get_stats(self) -> dict:
        """Get statistics about thread pool usage"""
        return {
            'clustering_pool': {
                'max_workers': self.clustering_pool._max_workers,
                'thread_name_prefix': self.clustering_pool._thread_name_prefix
            },
            'cpsat_pool': {
                'max_workers': self.cpsat_pool._max_workers,
                'thread_name_prefix': self.cpsat_pool._thread_name_prefix
            },
            'context_pool': {
                'max_workers': self.context_pool._max_workers,
                'thread_name_prefix': self.context_pool._thread_name_prefix
            }
        }
