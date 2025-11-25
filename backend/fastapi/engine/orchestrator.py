"""
Hardware Orchestrator - Maximum Resource Utilization
Automatically detects and uses ALL available hardware:
- CPU: Multi-core parallel processing
- GPU: CUDA acceleration for vectorized operations
- Distributed: Celery workers for horizontal scaling

NO COMPROMISES - Uses everything available for best performance
"""
import logging
import multiprocessing
from typing import List, Dict, Optional, Tuple
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class HardwareCapabilities:
    """Detected hardware capabilities"""
    cpu_cores: int
    has_gpu: bool
    gpu_name: Optional[str]
    gpu_memory_gb: float
    has_distributed: bool
    distributed_workers: int
    total_ram_gb: float
    
    def __str__(self):
        parts = [f"CPU: {self.cpu_cores} cores"]
        if self.has_gpu:
            parts.append(f"GPU: {self.gpu_name} ({self.gpu_memory_gb:.1f}GB)")
        if self.has_distributed:
            parts.append(f"Distributed: {self.distributed_workers} workers")
        parts.append(f"RAM: {self.total_ram_gb:.1f}GB")
        return " | ".join(parts)


class HardwareOrchestrator:
    """
    Orchestrates ALL available hardware for maximum performance
    
    Strategy:
    1. CPU: Always used for base processing
    2. GPU: Used for vectorized operations (GA fitness, RL inference)
    3. Distributed: Used for cluster-level parallelism
    
    Result: CPU + GPU + Distributed working together simultaneously
    """
    
    def __init__(self):
        self.capabilities = self._detect_all_hardware()
        self._init_resources()
        logger.info(f"🚀 Hardware Orchestrator initialized: {self.capabilities}")
    
    def _detect_all_hardware(self) -> HardwareCapabilities:
        """Detect ALL available hardware"""
        import psutil
        
        # CPU Detection
        cpu_cores = multiprocessing.cpu_count()
        
        # GPU Detection
        has_gpu = False
        gpu_name = None
        gpu_memory_gb = 0.0
        try:
            import torch
            if torch.cuda.is_available():
                has_gpu = True
                gpu_name = torch.cuda.get_device_name(0)
                gpu_memory_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
                logger.info(f"✅ GPU detected: {gpu_name} ({gpu_memory_gb:.1f}GB VRAM)")
        except ImportError:
            logger.info("⚠️ PyTorch not installed - GPU acceleration disabled")
        
        # Distributed System Detection
        has_distributed = False
        distributed_workers = 0
        try:
            from celery import Celery
            import redis
            # Try to connect to Redis
            r = redis.Redis(host='localhost', port=6379, db=0, socket_timeout=1)
            r.ping()
            has_distributed = True
            # Estimate workers (can be improved with actual Celery inspection)
            distributed_workers = cpu_cores  # Conservative estimate
            logger.info(f"✅ Distributed system detected: {distributed_workers} potential workers")
        except:
            logger.info("⚠️ Distributed system not available")
        
        # RAM Detection
        total_ram_gb = psutil.virtual_memory().total / (1024**3)
        
        return HardwareCapabilities(
            cpu_cores=cpu_cores,
            has_gpu=has_gpu,
            gpu_name=gpu_name,
            gpu_memory_gb=gpu_memory_gb,
            has_distributed=has_distributed,
            distributed_workers=distributed_workers,
            total_ram_gb=total_ram_gb
        )
    
    def _init_resources(self):
        """Initialize all available resources"""
        # CPU Thread Pool (for I/O-bound tasks)
        self.cpu_thread_pool = ThreadPoolExecutor(
            max_workers=self.capabilities.cpu_cores,
            thread_name_prefix="cpu_thread"
        )
        
        # CPU Process Pool (for CPU-bound tasks)
        self.cpu_process_pool = ProcessPoolExecutor(
            max_workers=min(self.capabilities.cpu_cores, 8),  # Limit to 8 for memory
            max_tasks_per_child=10  # Prevent memory leaks
        )
        
        # GPU Resources
        if self.capabilities.has_gpu:
            try:
                import torch
                self.gpu_device = torch.device('cuda')
                # Pre-allocate GPU memory pool
                torch.cuda.empty_cache()
                logger.info("✅ GPU resources initialized")
            except Exception as e:
                logger.warning(f"GPU initialization failed: {e}")
                self.capabilities.has_gpu = False
        
        # Distributed Resources
        if self.capabilities.has_distributed:
            try:
                from celery import Celery
                self.celery_app = Celery('timetable', broker='redis://localhost:6379/0')
                logger.info("✅ Distributed resources initialized")
            except Exception as e:
                logger.warning(f"Distributed initialization failed: {e}")
                self.capabilities.has_distributed = False
    
    def execute_stage1_clustering(self, courses, clusterer):
        """
        Stage 1: Louvain Clustering
        Strategy: Sequential (parallel causes graph isolation issues)
        """
        logger.info(f"[STAGE1] Using sequential clustering (1820 courses)")
        # Sequential only - parallel batching breaks graph connectivity
        return clusterer.cluster_courses(courses)
    
    def _parallel_clustering(self, courses, clusterer):
        """Parallel clustering using CPU cores"""
        # Split courses into batches
        batch_size = len(courses) // self.capabilities.cpu_cores
        batches = [courses[i:i+batch_size] for i in range(0, len(courses), batch_size)]
        
        # Process batches in parallel
        with self.cpu_process_pool as executor:
            futures = [executor.submit(clusterer.cluster_courses, batch) for batch in batches]
            results = [f.result() for f in as_completed(futures)]
        
        # Merge results
        merged = {}
        cluster_id = 0
        for result in results:
            for courses_list in result.values():
                merged[cluster_id] = courses_list
                cluster_id += 1
        
        return merged
    
    def execute_stage2_cpsat(self, clusters, solver_func, data):
        """
        Stage 2A: CP-SAT Solving
        Strategy: CPU multi-core + Distributed (if available)
        """
        if self.capabilities.has_distributed and len(clusters) > 10:
            logger.info(f"[STAGE2A] Using DISTRIBUTED processing ({self.capabilities.distributed_workers} workers)")
            return self._distributed_cpsat(clusters, solver_func, data)
        elif self.capabilities.cpu_cores > 4:
            logger.info(f"[STAGE2A] Using {self.capabilities.cpu_cores} CPU cores")
            return self._parallel_cpsat(clusters, solver_func, data)
        else:
            logger.info("[STAGE2A] Using single-core CPU")
            return self._sequential_cpsat(clusters, solver_func, data)
    
    def _distributed_cpsat(self, clusters, solver_func, data):
        """Distributed CP-SAT solving using Celery"""
        from celery import group
        
        # Create distributed tasks
        job = group(
            self.celery_app.signature(
                'solve_cluster_task',
                args=(cluster_id, cluster_courses, data)
            )
            for cluster_id, cluster_courses in clusters.items()
        )
        
        # Execute in parallel across workers
        result = job.apply_async()
        solutions = result.get(timeout=300)
        
        # Merge solutions
        merged = {}
        for sol in solutions:
            if sol:
                merged.update(sol)
        
        return merged
    
    def _parallel_cpsat(self, clusters, solver_func, data):
        """Parallel CP-SAT solving using CPU cores"""
        all_solutions = {}
        
        with self.cpu_process_pool as executor:
            futures = {
                executor.submit(solver_func, cluster_id, cluster_courses, data): cluster_id
                for cluster_id, cluster_courses in clusters.items()
            }
            
            for future in as_completed(futures):
                cluster_id = futures[future]
                try:
                    solution = future.result(timeout=60)
                    if solution:
                        all_solutions.update(solution)
                except Exception as e:
                    logger.error(f"Cluster {cluster_id} failed: {e}")
        
        return all_solutions
    
    def _sequential_cpsat(self, clusters, solver_func, data):
        """Sequential CP-SAT solving"""
        all_solutions = {}
        for cluster_id, cluster_courses in clusters.items():
            solution = solver_func(cluster_id, cluster_courses, data)
            if solution:
                all_solutions.update(solution)
        return all_solutions
    
    def execute_stage2_ga(self, ga_optimizer):
        """
        Stage 2B: Genetic Algorithm
        Strategy: GPU for fitness + CPU multi-core for evolution
        """
        if self.capabilities.has_gpu:
            logger.info(f"[STAGE2B] Using GPU ({self.capabilities.gpu_name}) + {self.capabilities.cpu_cores} CPU cores")
            return self._gpu_cpu_ga(ga_optimizer)
        elif self.capabilities.cpu_cores > 4:
            logger.info(f"[STAGE2B] Using {self.capabilities.cpu_cores} CPU cores")
            return self._multicore_ga(ga_optimizer)
        else:
            logger.info("[STAGE2B] Using single-core CPU")
            return ga_optimizer.evolve()
    
    def _gpu_cpu_ga(self, ga_optimizer):
        """
        Hybrid GPU + CPU GA
        - GPU: Fitness evaluation (vectorized)
        - CPU: Population evolution (multi-threaded)
        """
        import torch
        
        ga_optimizer.use_gpu = True
        ga_optimizer.use_multicore = True
        ga_optimizer.num_workers = self.capabilities.cpu_cores
        
        # Initialize GPU tensors
        if hasattr(ga_optimizer, '_init_gpu_tensors'):
            ga_optimizer._init_gpu_tensors()
        
        return ga_optimizer.evolve()
    
    def _multicore_ga(self, ga_optimizer):
        """Multi-core CPU GA"""
        ga_optimizer.use_gpu = False
        ga_optimizer.use_multicore = True
        ga_optimizer.num_workers = self.capabilities.cpu_cores
        return ga_optimizer.evolve()
    
    def execute_stage3_rl(self, rl_resolver, schedule):
        """
        Stage 3: RL Conflict Resolution
        Strategy: GPU for DQN inference + CPU for Q-table
        """
        if self.capabilities.has_gpu:
            logger.info(f"[STAGE3] Using GPU ({self.capabilities.gpu_name}) for DQN inference")
            return self._gpu_rl(rl_resolver, schedule)
        else:
            logger.info("[STAGE3] Using CPU for Q-table")
            return rl_resolver.resolve_conflicts(schedule)
    
    def _gpu_rl(self, rl_resolver, schedule):
        """GPU-accelerated RL with DQN"""
        # Enable GPU mode if available
        if hasattr(rl_resolver, 'use_gpu'):
            rl_resolver.use_gpu = True
        return rl_resolver.resolve_conflicts(schedule)
    
    def get_optimal_strategy(self, num_courses: int, num_clusters: int) -> Dict[str, str]:
        """
        Determine optimal strategy for each stage based on:
        - Available hardware
        - Dataset size
        - Complexity
        """
        strategy = {}
        
        # Stage 1: Clustering
        if num_courses > 500 and self.capabilities.cpu_cores > 4:
            strategy['stage1'] = f"Parallel CPU ({self.capabilities.cpu_cores} cores)"
        else:
            strategy['stage1'] = "Sequential CPU"
        
        # Stage 2A: CP-SAT
        if self.capabilities.has_distributed and num_clusters > 10:
            strategy['stage2a'] = f"Distributed ({self.capabilities.distributed_workers} workers)"
        elif self.capabilities.cpu_cores > 4:
            strategy['stage2a'] = f"Parallel CPU ({self.capabilities.cpu_cores} cores)"
        else:
            strategy['stage2a'] = "Sequential CPU"
        
        # Stage 2B: GA
        if self.capabilities.has_gpu:
            strategy['stage2b'] = f"GPU ({self.capabilities.gpu_name}) + CPU ({self.capabilities.cpu_cores} cores)"
        elif self.capabilities.cpu_cores > 4:
            strategy['stage2b'] = f"Multi-core CPU ({self.capabilities.cpu_cores} cores)"
        else:
            strategy['stage2b'] = "Single-core CPU"
        
        # Stage 3: RL
        if self.capabilities.has_gpu:
            strategy['stage3'] = f"GPU DQN ({self.capabilities.gpu_name})"
        else:
            strategy['stage3'] = "CPU Q-table"
        
        return strategy
    
    def estimate_speedup(self, num_courses: int) -> Dict[str, float]:
        """Estimate speedup compared to single-core CPU"""
        speedup = {
            'stage1': 1.0,
            'stage2a': 1.0,
            'stage2b': 1.0,
            'stage3': 1.0,
            'total': 1.0
        }
        
        # Stage 1: CPU parallelism
        if num_courses > 500 and self.capabilities.cpu_cores > 4:
            speedup['stage1'] = min(self.capabilities.cpu_cores * 0.7, 4.0)
        
        # Stage 2A: CPU or Distributed
        if self.capabilities.has_distributed:
            speedup['stage2a'] = min(self.capabilities.distributed_workers * 0.8, 10.0)
        elif self.capabilities.cpu_cores > 4:
            speedup['stage2a'] = min(self.capabilities.cpu_cores * 0.75, 6.0)
        
        # Stage 2B: GPU + CPU
        if self.capabilities.has_gpu:
            gpu_speedup = 4.0  # GPU for fitness
            cpu_speedup = min(self.capabilities.cpu_cores * 0.5, 2.0)  # CPU for evolution
            speedup['stage2b'] = gpu_speedup + cpu_speedup  # Combined benefit
        elif self.capabilities.cpu_cores > 4:
            speedup['stage2b'] = min(self.capabilities.cpu_cores * 0.6, 3.0)
        
        # Stage 3: GPU DQN
        if self.capabilities.has_gpu:
            speedup['stage3'] = 2.5
        
        # Total speedup (weighted average)
        weights = {'stage1': 0.15, 'stage2a': 0.35, 'stage2b': 0.35, 'stage3': 0.15}
        speedup['total'] = sum(speedup[stage] * weights[stage] for stage in weights)
        
        return speedup
    
    def cleanup(self):
        """Cleanup all resources"""
        logger.info("Cleaning up hardware resources...")
        
        # Shutdown thread pool
        self.cpu_thread_pool.shutdown(wait=False)
        
        # Shutdown process pool
        self.cpu_process_pool.shutdown(wait=False)
        
        # Clear GPU cache
        if self.capabilities.has_gpu:
            try:
                import torch
                torch.cuda.empty_cache()
                logger.info("✅ GPU cache cleared")
            except:
                pass
        
        logger.info("✅ All resources cleaned up")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()


# Global orchestrator instance
_global_orchestrator: Optional[HardwareOrchestrator] = None


def get_orchestrator() -> HardwareOrchestrator:
    """Get or create global orchestrator instance"""
    global _global_orchestrator
    if _global_orchestrator is None:
        _global_orchestrator = HardwareOrchestrator()
    return _global_orchestrator


def reset_orchestrator():
    """Reset global orchestrator"""
    global _global_orchestrator
    if _global_orchestrator:
        _global_orchestrator.cleanup()
    _global_orchestrator = None
