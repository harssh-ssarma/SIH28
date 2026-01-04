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
        
        # User-friendly stage names (hide technical details)
        self.stage_display_names = {
            'load_data': 'Loading Data',
            'clustering': 'Assigning Courses',
            'cpsat': 'Scheduling Classes',
            'ga': 'Optimizing Schedule',
            'rl': 'Resolving Conflicts',
            'finalize': 'Finalizing Timetable'
        }
        
        # Stage configuration with ABSOLUTE cumulative progress boundaries
        # Total time: ~10-12 minutes = 600-720s
        # Observed: load=5s, cluster=10s, cpsat=180s, ga=300s, rl=180s, final=5s
        # Each stage has start_progress, end_progress, and expected_time
        self.stage_config = {
            'load_data': {'start': 0, 'end': 5, 'expected_time': 5},       # 0% -> 5%
            'clustering': {'start': 5, 'end': 10, 'expected_time': 10},    # 5% -> 10%
            'cpsat': {'start': 10, 'end': 60, 'expected_time': 180},       # 10% -> 60%
            'ga': {'start': 60, 'end': 85, 'expected_time': 300},          # 60% -> 85%
            'rl': {'start': 85, 'end': 95, 'expected_time': 180},          # 85% -> 95%
            'finalize': {'start': 95, 'end': 100, 'expected_time': 5}      # 95% -> 100%
        }
        
        # Current stage tracking
        self.current_stage = 'load_data'
        self.stage_start_time = self.start_time
        self.stage_start_progress = 0.0
        
        # Work-based tracking (for measurable stages)
        self.stage_items_total = 0
        self.stage_items_done = 0
        
        # Initialize ETA tracking variables - MUST be set before first update
        self._smoothed_eta = estimated_total_seconds
        self._last_eta_update = self.start_time
        self._last_eta_value = estimated_total_seconds
        self._last_update_time = self.start_time
        
        # Send initial progress to Redis immediately with ETA
        self._send_initial_progress()
        
        logger.info(f"[PROGRESS] Time-based virtual progress tracker initialized for {job_id} (ETA: {estimated_total_seconds}s)")
    
    def _send_initial_progress(self):
        """Send initial progress with ETA to Redis immediately (synchronous)"""
        if not self.redis_client:
            return
        
        try:
            # Calculate initial ETA
            remaining_seconds = self._smoothed_eta
            eta = (datetime.now(timezone.utc) + timedelta(seconds=remaining_seconds)).isoformat()
            
            # Get initial stage display name
            stage_display = self.stage_display_names.get(self.current_stage, 'Initializing')
            
            # Send initial progress data
            progress_data = {
                'job_id': self.job_id,
                'progress': 0,
                'progress_percent': 0,
                'status': 'running',
                'stage': stage_display,
                'message': f'Starting: {stage_display}',
                'time_remaining_seconds': remaining_seconds,
                'eta_seconds': remaining_seconds,
                'eta': eta,
                'timestamp': datetime.now(timezone.utc).timestamp()
            }
            
            # Store in Redis with 1 hour TTL
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
            
            logger.info(f"[PROGRESS] Initial progress sent: 0% with ETA {remaining_seconds}s")
            
        except Exception as e:
            logger.error(f"[PROGRESS] Failed to send initial progress: {e}")
    
    def set_stage(self, stage_name: str, total_items: int = 0):
        """Set current stage with ZERO JUMPS - TensorFlow/Chrome style continuous progress"""
        if stage_name in self.stage_config:
            stage_info = self.stage_config[stage_name]
            
            # CRITICAL: Use current progress as start - NEVER jump to stage boundaries
            # This is how TensorFlow/Chrome do it - always continue from where you are
            self.stage_start_progress = self.last_progress
            self.stage_end_progress = stage_info['end']
            self.current_stage = stage_name
            self.stage_start_time = time.time()
            
            # Work-based tracking
            self.stage_items_total = total_items
            self.stage_items_done = 0
            
            # Clear any catch-up targets from previous stage
            if hasattr(self, '_catch_up_target'):
                delattr(self, '_catch_up_target')
            
            # Get user-friendly name for logging
            display_name = self.stage_display_names.get(stage_name, stage_name)
            logger.info(f"[PROGRESS] Stage: {display_name} ({self.stage_start_progress:.1f}% -> {stage_info['end']}%, items: {total_items})")
    
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
        GOOGLE/TENSORFLOW STYLE: Smooth continuous progress with adaptive speed
        - NEVER jumps backward or forward
        - Accelerates when behind schedule (catching up)
        - Decelerates when ahead (preventing overshoot)
        - Uses work anchors when available for accuracy
        """
        now = time.time()
        time_since_last = now - getattr(self, '_last_update_time', now)
        self._last_update_time = now
        
        # Get stage boundaries and timing
        stage_info = self.stage_config.get(self.current_stage, {'start': 0, 'end': 100, 'expected_time': 5})
        stage_start = self.stage_start_progress  # Where we actually started this stage
        stage_end = stage_info['end']
        stage_range = stage_end - stage_start
        expected_time = stage_info.get('expected_time', 5)
        elapsed_in_stage = now - self.stage_start_time
        
        # Calculate target progress based on work/time
        if self.stage_items_total > 0 and self.stage_items_done > 0:
            # Work-based anchor: Use actual completed work for accuracy
            work_ratio = min(1.0, self.stage_items_done / self.stage_items_total)
            target_progress = stage_start + (work_ratio * stage_range)
        else:
            # Time-based: Smooth asymptotic approach (never quite reaches end)
            # This handles both: (1) no work tracking, (2) work tracking but no items done yet
            if elapsed_in_stage < expected_time:
                # Linear progress during expected time
                ratio = elapsed_in_stage / expected_time
            else:
                # Asymptotic slowdown after expected time (Google/Chrome style)
                overtime = elapsed_in_stage - expected_time
                # Approaches 95% of stage range asymptotically
                ratio = 0.95 * (1.0 - (0.5 ** (elapsed_in_stage / expected_time)))
            
            target_progress = stage_start + (ratio * stage_range)
            
            # CRITICAL FIX: If work tracking enabled but no work done yet,
            # ensure minimum progress to show activity (Google/TensorFlow style)
            if self.stage_items_total > 0 and self.stage_items_done == 0 and elapsed_in_stage > 2:
                # After 2 seconds, guarantee at least 1% progress in the stage
                min_progress = stage_start + min(1.0, elapsed_in_stage * 0.2)  # 0.2% per second
                target_progress = max(target_progress, min_progress)
        
        # Cap target at stage end (never exceed stage boundary)
        target_progress = min(stage_end - 0.5, target_progress)  # Leave 0.5% margin
        
        # ADAPTIVE SPEED: Accelerate/decelerate based on distance to target
        distance_to_target = target_progress - self.last_progress
        
        # Calculate adaptive step size (Google/TensorFlow approach)
        if distance_to_target > 0:
            # Accelerate when behind (proportional to distance)
            # Base: 0.2%/update (0.4%/sec), Max: 2%/update (4%/sec)
            acceleration_factor = min(3.0, 1.0 + (distance_to_target / 5.0))
            step = min(distance_to_target, 0.2 * acceleration_factor * (time_since_last / 0.5))
            new_progress = self.last_progress + step
        elif distance_to_target < -0.5:
            # Rarely happens, but if ahead, slow down dramatically
            deceleration_factor = 0.3
            step = 0.05 * deceleration_factor * (time_since_last / 0.5)
            new_progress = self.last_progress + step
        else:
            # At target or slightly ahead - maintain minimum forward progress
            # Always creep forward (NEVER stuck)
            min_step = 0.05 * (time_since_last / 0.5)
            new_progress = self.last_progress + min_step
        
        # Ensure never exceeds stage end
        new_progress = min(stage_end, new_progress)
        
        # Global cap at 98% (save 98-100% for finalization)
        new_progress = min(98.0, new_progress)
        
        # CRITICAL: Never go backward
        new_progress = max(self.last_progress, new_progress)
        
        self.last_progress = new_progress
        
        return self.last_progress
    
    def calculate_eta(self) -> tuple[int, str]:
        """
        ADAPTIVE ETA: TensorFlow/Google style - learns from actual speed
        Recalculates based on current progress rate, not fixed estimates
        """
        elapsed = time.time() - self.start_time
        
        # Method 1: Progress-based ETA (learns from actual speed)
        if self.last_progress > 1.0 and elapsed > 2:
            # Calculate actual progress rate
            progress_rate = self.last_progress / elapsed  # percent per second
            remaining_progress = 100.0 - self.last_progress
            progress_based_eta = int(remaining_progress / progress_rate) if progress_rate > 0 else 600
        else:
            # Not enough data yet, use total expected time
            progress_based_eta = sum(stage['expected_time'] for stage in self.stage_config.values())
        
        # Method 2: Stage-based ETA (sum of remaining stage times)
        stage_based_eta = 0
        current_stage_found = False
        
        for stage_name, config in self.stage_config.items():
            if not current_stage_found:
                if stage_name == self.current_stage:
                    current_stage_found = True
                    # Current stage: use remaining time
                    stage_elapsed = time.time() - self.stage_start_time
                    stage_expected = config['expected_time']
                    stage_remaining = max(1, stage_expected - stage_elapsed)
                    stage_based_eta += stage_remaining
            else:
                # Future stages: add full expected time
                stage_based_eta += config['expected_time']
        
        # Blend both methods (Google/TensorFlow approach)
        if self.last_progress < 10:
            # Early stage: trust stage estimates more (70% stage, 30% progress)
            blended_eta = int(0.7 * stage_based_eta + 0.3 * progress_based_eta)
        elif self.last_progress < 50:
            # Mid stage: balanced blend (50% each)
            blended_eta = int(0.5 * stage_based_eta + 0.5 * progress_based_eta)
        else:
            # Late stage: trust progress rate more (30% stage, 70% progress)
            blended_eta = int(0.3 * stage_based_eta + 0.7 * progress_based_eta)
        
        # Exponential moving average for smoothness
        if not hasattr(self, '_smoothed_eta'):
            self._smoothed_eta = blended_eta
            self._last_eta_update = time.time()
        else:
            time_since_update = time.time() - self._last_eta_update
            if time_since_update >= 1.0:  # Update every second
                # Adaptive alpha: more responsive early, more stable later
                if self.last_progress < 5:
                    alpha = 0.4  # Very responsive at start
                elif self.last_progress < 30:
                    alpha = 0.3  # Moderately responsive
                else:
                    alpha = 0.2  # Stable in late stages
                
                self._smoothed_eta = int((1 - alpha) * self._smoothed_eta + alpha * blended_eta)
                self._last_eta_update = time.time()
        
        # Clamp to reasonable range (1 second to 15 minutes)
        remaining = max(1, min(900, self._smoothed_eta))
        
        # Ensure ETA decreases over time (never increases)
        if hasattr(self, '_last_eta_value'):
            if remaining > self._last_eta_value + 5:  # Allow 5s tolerance for smoothing
                remaining = self._last_eta_value  # Don't let it jump up
        self._last_eta_value = remaining
        
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
                progress = round(progress_float)  # Round to nearest integer
            
            # Calculate ETA
            remaining_seconds, eta = self.calculate_eta()
            
            # Get user-friendly stage name
            stage_display = self.stage_display_names.get(self.current_stage, message)
            
            # Build progress data with user-friendly names
            progress_data = {
                'job_id': self.job_id,
                'progress': progress,
                'progress_percent': progress,
                'status': 'completed' if progress >= 100 else 'running',
                'stage': stage_display,  # User-friendly name
                'message': stage_display,  # User-friendly message
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
                # CHECK CANCELLATION: Stop progress updates if job cancelled
                if await self._check_cancellation():
                    logger.info(f"[PROGRESS] Job {self.tracker.job_id} cancelled - stopping progress updates")
                    self.running = False
                    break
                
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
            logger.info(f"[PROGRESS] Progress task cancelled for {self.tracker.job_id}")
        except Exception as e:
            logger.error(f"[PROGRESS] Update loop error: {e}")
    
    async def _check_cancellation(self) -> bool:
        """Check if job has been cancelled via Redis"""
        try:
            if self.tracker.redis_client and self.tracker.job_id:
                cancel_flag = self.tracker.redis_client.get(f"cancel:job:{self.tracker.job_id}")
                return cancel_flag is not None and cancel_flag
        except Exception as e:
            logger.debug(f"[PROGRESS] Cancellation check failed: {e}")
        return False
