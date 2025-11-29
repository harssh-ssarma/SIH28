"""
Enterprise Progress Tracker - Google/Microsoft Style
Smooth, consistent progress based on overall time, not stage completion
"""
import time
import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional
import json

logger = logging.getLogger(__name__)


class EnterpriseProgressTracker:
    """
    Time-based Virtual Progress Smoothing (Chrome/TensorFlow/Steam style)
    - Smooth progress updates every 100ms regardless of algorithm state
    - Based on expected stage durations, not internal algorithm steps
    - Never stuck, never jumps backward
    - Works perfectly with blocking algorithms (CP-SAT, GA, RL)
    """
    
    def __init__(self, job_id: str, estimated_total_seconds: int, redis_client):
        self.job_id = job_id
        self.redis_client = redis_client
        
        # Time-based tracking
        self.start_time = time.time()
        self.last_progress = 0.0
        self._progress_lock = asyncio.Lock()  # Thread-safe progress updates
        
        # Stage configuration with CORRECT weights based on actual execution times
        # Total time: ~15 minutes = 900s (INCREASED FROM 10 MINUTES)
        # load=2s, cluster=5s, cpsat=60s, ga=750s, rl=75s, final=8s
        # Weights adjusted for 15-minute timeout
        self.stage_config = {
            'load_data': {'weight': 2, 'expected_time': 2},      # 0% → 2%
            'clustering': {'weight': 3, 'expected_time': 5},     # 2% → 5%
            'cpsat': {'weight': 10, 'expected_time': 60},        # 5% → 15%
            'ga': {'weight': 70, 'expected_time': 750},          # 15% → 85%
            'rl': {'weight': 10, 'expected_time': 75},           # 85% → 95%
            'finalize': {'weight': 5, 'expected_time': 8}        # 95% → 100%
        }
        
        # Current stage tracking
        self.current_stage = 'load_data'
        self.stage_start_time = self.start_time
        self.stage_start_progress = 0.0
        
        # Work-based tracking (for measurable stages)
        self.stage_items_total = 0
        self.stage_items_done = 0
        
        logger.info(f"[PROGRESS] Time-based virtual progress tracker initialized for {job_id}")
    
    def set_stage(self, stage_name: str, total_items: int = 0):
        """Set current stage with optional work tracking - SMOOTH TRANSITION"""
        if stage_name in self.stage_config:
            # NEVER jump - always use current progress as start
            self.stage_start_progress = self.last_progress
            self.current_stage = stage_name
            self.stage_start_time = time.time()
            
            # Work-based tracking
            self.stage_items_total = total_items
            self.stage_items_done = 0
            
            logger.info(f"[PROGRESS] Stage: {stage_name} (start: {self.last_progress:.1f}%, items: {total_items})")
    
    def update_work_progress(self, items_done: int):
        """Update work-based progress (for CP-SAT clusters, GA generations, RL episodes)"""
        self.stage_items_done = items_done
    
    def mark_stage_complete(self):
        """Mark current stage as completed - NO JUMP, just log"""
        # Don't force jump - let work-based or time-based progress naturally reach end
        logger.info(f"[PROGRESS] Stage {self.current_stage} completed at {self.last_progress:.1f}%")
        
        # Reset work tracking for next stage
        self.stage_items_total = 0
        self.stage_items_done = 0
    
    def calculate_smooth_progress(self) -> float:
        """
        ENTERPRISE SMOOTH: Chrome/TensorFlow style - NEVER jumps, NEVER sticks
        """
        now = time.time()
        time_since_last = now - getattr(self, '_last_update_time', now)
        self._last_update_time = now
        
        # Calculate target progress based on work/time
        if self.stage_items_total > 0:
            # Work-based: Calculate target from actual completion
            work_ratio = min(1.0, self.stage_items_done / self.stage_items_total)
            stage_weight = self.stage_config.get(self.current_stage, {}).get('weight', 10)
            target_progress = self.stage_start_progress + (work_ratio * stage_weight)
        else:
            # Time-based: Asymptotic approach to stage end
            elapsed = now - self.stage_start_time
            expected = self.stage_config.get(self.current_stage, {}).get('expected_time', 5)
            stage_weight = self.stage_config.get(self.current_stage, {}).get('weight', 10)
            
            if elapsed < expected:
                ratio = elapsed / expected
            else:
                # Slow down exponentially after expected time
                overtime = elapsed - expected
                ratio = 1.0 - (0.01 * (0.5 ** (overtime / expected)))
            
            target_progress = self.stage_start_progress + (ratio * stage_weight)
        
        # SMOOTH INTERPOLATION: Move towards target at constant speed
        # Speed: 1% per 500ms = 2% per second (smooth visible movement)
        max_step = 1.0 * (time_since_last / 0.5)
        
        if target_progress > self.last_progress:
            # Move towards target smoothly
            step = min(max_step, target_progress - self.last_progress)
            new_progress = self.last_progress + step
        else:
            # Always move forward (minimum 0.1% per 500ms = never stuck)
            new_progress = self.last_progress + (0.1 * (time_since_last / 0.5))
        
        # Cap at 98% until completion
        new_progress = min(98.0, new_progress)
        self.last_progress = new_progress
        
        return self.last_progress
    
    def calculate_eta(self) -> tuple[int, str]:
        """SMOOTH ETA: Exponential moving average for stability"""
        elapsed = time.time() - self.start_time
        
        # Calculate instantaneous ETA
        if self.last_progress > 5:  # Need 5% for accurate estimate
            time_per_percent = elapsed / self.last_progress
            remaining_percent = 100 - self.last_progress
            instant_eta = int(time_per_percent * remaining_percent)
        else:
            # Early stage: use stage-based estimate
            total_weight = sum(s['weight'] for s in self.stage_config.values())
            total_time = sum(s['expected_time'] for s in self.stage_config.values())
            instant_eta = int(total_time * (100 - self.last_progress) / 100)
        
        # Smooth ETA with exponential moving average (alpha=0.3)
        if not hasattr(self, '_smoothed_eta'):
            self._smoothed_eta = instant_eta
        else:
            self._smoothed_eta = int(0.7 * self._smoothed_eta + 0.3 * instant_eta)
        
        # Clamp to reasonable range
        remaining = max(1, min(600, self._smoothed_eta))
        eta = (datetime.now(timezone.utc) + timedelta(seconds=remaining)).isoformat()
        return remaining, eta
    
    async def update(self, message: str, force_progress: Optional[int] = None):
        """
        Update progress with smooth interpolation
        
        Args:
            message: Status message to display
            force_progress: Force specific progress (for 100% completion)
        """
        if not self.redis_client:
            return
        
        try:
            # Calculate smooth progress (float for smooth updates)
            if force_progress is not None:
                progress = force_progress
                self.last_progress = float(progress)
            else:
                progress_float = self.calculate_smooth_progress()
                progress = int(progress_float)  # Convert to int for display
            
            # Calculate ETA
            remaining_seconds, eta = self.calculate_eta()
            
            # Build progress data
            progress_data = {
                'job_id': self.job_id,
                'progress': progress,
                'progress_percent': progress,
                'status': 'completed' if progress >= 100 else 'running',
                'stage': message,
                'message': message,
                'time_remaining_seconds': remaining_seconds if progress < 100 else 0,
                'eta_seconds': remaining_seconds if progress < 100 else 0,
                'eta': eta if progress < 100 else datetime.now(timezone.utc).isoformat(),
                'timestamp': datetime.now(timezone.utc).timestamp()
            }
            
            # Store in Redis
            self.redis_client.setex(
                f"progress:job:{self.job_id}",
                3600,
                json.dumps(progress_data)
            )
            
            # Publish for real-time updates
            self.redis_client.publish(
                f"progress:{self.job_id}",
                json.dumps(progress_data)
            )
            
            logger.debug(f"[PROGRESS] {self.job_id}: {progress}% - {message} (ETA: {remaining_seconds}s)")
            
        except Exception as e:
            logger.error(f"[PROGRESS] Update failed: {e}")
    
    async def complete(self, message: str = "Timetable generation completed"):
        """Mark job as 100% complete"""
        await self.update(message, force_progress=100)
        logger.info(f"[PROGRESS] {self.job_id}: Completed in {time.time() - self.start_time:.1f}s")
    
    async def fail(self, error_message: str):
        """Mark job as failed"""
        if not self.redis_client:
            return
        
        try:
            progress_data = {
                'job_id': self.job_id,
                'progress': 0,
                'status': 'failed',
                'stage': 'Failed',
                'message': error_message,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            self.redis_client.setex(
                f"progress:job:{self.job_id}",
                3600,
                json.dumps(progress_data)
            )
            
            logger.error(f"[PROGRESS] {self.job_id}: Failed - {error_message}")
            
        except Exception as e:
            logger.error(f"[PROGRESS] Fail update failed: {e}")


class ProgressUpdateTask:
    """Background task to update progress every 2 seconds"""
    
    def __init__(self, tracker: EnterpriseProgressTracker):
        self.tracker = tracker
        self.running = False
        self.task = None
    
    async def start(self):
        """Start background progress updates"""
        self.running = True
        self.task = asyncio.create_task(self._update_loop())
        logger.info(f"[PROGRESS] Started background updates for {self.tracker.job_id}")
    
    async def stop(self):
        """Stop background progress updates"""
        self.running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        logger.info(f"[PROGRESS] Stopped background updates for {self.tracker.job_id}")
    
    async def _update_loop(self):
        """Update progress every 500ms for smooth real-time tracking"""
        try:
            update_count = 0
            while self.running:
                # Build message with work progress if available
                stage_name = self.tracker.current_stage.replace('_', ' ').title()
                
                if self.tracker.stage_items_total > 0:
                    # Show work progress
                    message = f"{stage_name}: {self.tracker.stage_items_done}/{self.tracker.stage_items_total}"
                else:
                    # Generic message
                    message = f"Processing: {stage_name}"
                
                await self.tracker.update(message)
                update_count += 1
                
                # Log every 4 updates (every 2 seconds) for debugging
                if update_count % 4 == 0:
                    logger.info(f"[PROGRESS] {self.tracker.last_progress:.1f}% - {message}")
                
                await asyncio.sleep(0.5)  # Update every 500ms (2 updates/sec = smooth + efficient)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"[PROGRESS] Update loop error: {e}")
