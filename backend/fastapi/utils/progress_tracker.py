"""
Progress Tracker for Algorithm Instrumentation
ENTERPRISE PATTERN: Real-time progress reporting with percentage + ETA
"""
import redis
import json
import time
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from collections import deque
from models.progress_models import ProgressUpdate, GenerationStage
from config import settings
import logging

logger = logging.getLogger(__name__)


class ProgressTracker:
    """
    Track algorithm progress with percentage and ETA estimation.

    ENTERPRISE PATTERN: Instrumented algorithm progress
    - Reports percentage completion
    - Estimates time remaining (ETA)
    - Tracks phase transitions
    - Maintains moving average for accurate ETA
    - Publishes to Redis Pub/Sub for real-time streaming
    """

    def __init__(self, job_id: str, redis_client: redis.Redis, redis_publisher=None):
        self.job_id = job_id
        self.redis_client = redis_client
        self.redis_publisher = redis_publisher
        self.start_time = time.time()
        self.redis_key = f"{settings.REDIS_PROGRESS_PREFIX}{job_id}"

        # Progress tracking
        self.current_phase = "Initializing"
        self.current_progress = 0.0

        # Phase weights (sum to 100%)
        self.phases = {
            'initialization': {'weight': 5, 'progress': 0},
            'clustering': {'weight': 15, 'progress': 0},
            'constraint_solving': {'weight': 50, 'progress': 0},
            'optimization': {'weight': 25, 'progress': 0},
            'finalization': {'weight': 5, 'progress': 0},
        }

        # ETA estimation (moving average)
        self.iteration_times = deque(maxlen=20)  # Last 20 iterations
        self.last_update = time.time()

        # Statistics
        self.total_iterations = 0
        self.completed_iterations = 0

        # Initialize progress
        self.update(
            stage="initializing",
            progress=0.0,
            step="Starting timetable generation"
        )

    def set_phase(self, phase_name: str, total_steps: int = 100) -> None:
        """Set current algorithm phase with total steps."""
        if phase_name not in self.phases:
            logger.warning(f"Unknown phase: {phase_name}")
            return

        self.current_phase = phase_name
        self.phases[phase_name]['total_steps'] = total_steps
        self.phases[phase_name]['completed_steps'] = 0

        logger.info(f"Phase transition: {phase_name} (total steps: {total_steps})")
        self._publish_update()

    def update_phase_progress(self, step: int, status_message: Optional[str] = None) -> None:
        """Update progress within current phase."""
        phase = self.phases[self.current_phase]
        total_steps = phase.get('total_steps', 100)

        # Calculate phase progress
        phase_progress = min(100.0, (step / total_steps) * 100)
        phase['progress'] = phase_progress
        phase['completed_steps'] = step

        # Calculate overall progress (weighted sum)
        overall_progress = sum(
            p['weight'] * p['progress'] / 100.0
            for p in self.phases.values()
        )

        self.current_progress = min(99.0, overall_progress)

        # Track iteration time for ETA
        now = time.time()
        iteration_time = now - self.last_update
        self.iteration_times.append(iteration_time)
        self.last_update = now

        self.completed_iterations = step

        # Publish update (throttled to every 1 second)
        if now - getattr(self, '_last_publish', 0) >= 1.0:
            self._publish_update(status_message)
            self._last_publish = now

    def estimate_eta(self) -> int:
        """Estimate time remaining in seconds."""
        if not self.iteration_times or self.current_progress == 0:
            return 0

        avg_time_per_iteration = sum(self.iteration_times) / len(self.iteration_times)

        # Calculate remaining steps
        phase = self.phases[self.current_phase]
        total_steps = phase.get('total_steps', 100)
        completed_steps = phase.get('completed_steps', 0)
        remaining_steps_in_phase = total_steps - completed_steps

        remaining_steps_total = remaining_steps_in_phase
        current_phase_passed = False

        for phase_name, phase_data in self.phases.items():
            if phase_name == self.current_phase:
                current_phase_passed = True
                continue
            if current_phase_passed:
                remaining_steps_total += phase_data.get('total_steps', 100)

        eta_seconds = remaining_steps_total * avg_time_per_iteration
        return max(0, int(eta_seconds))

    def _publish_update(self, status_message: Optional[str] = None) -> None:
        """Publish progress update to Redis Pub/Sub."""
        eta_seconds = self.estimate_eta()
        elapsed_seconds = int(time.time() - self.start_time)

        progress_data = {
            'job_id': self.job_id,
            'progress': round(self.current_progress, 2),
            'phase': self.current_phase,
            'status': status_message or f"Processing {self.current_phase}...",
            'eta_seconds': eta_seconds,
            'elapsed_seconds': elapsed_seconds,
            'estimated_completion': (
                datetime.utcnow() + timedelta(seconds=eta_seconds)
            ).isoformat() if eta_seconds > 0 else None,
        }

        # Store in Redis (for HTTP polling fallback)
        try:
            self.redis_client.setex(
                self.redis_key,
                settings.PROGRESS_EXPIRE_SECONDS,
                json.dumps(progress_data)
            )
        except Exception as e:
            logger.error(f"Failed to store progress in Redis: {e}")

        # Publish to Pub/Sub channel
        if self.redis_publisher:
            try:
                self.redis_publisher.publish_progress(self.job_id, progress_data)
            except Exception as e:
                logger.error(f"Failed to publish progress: {e}")

        logger.debug(
            f"Job {self.job_id}: {self.current_progress:.1f}% "
            f"(Phase: {self.current_phase}, ETA: {eta_seconds}s)"
        )

    def update(
        self,
        stage: str = None,
        progress: float = None,
        step: str = None,
        details: Optional[Dict] = None
    ):
        """Legacy update method for backward compatibility."""
        if stage:
            # Map legacy stages to new phases
            stage_map = {
                'initializing': 'initialization',
                'clustering': 'clustering',
                'solving': 'constraint_solving',
                'optimizing': 'optimization',
                'finalizing': 'finalization',
            }
            mapped_phase = stage_map.get(stage, 'initialization')

            if mapped_phase != self.current_phase:
                self.set_phase(mapped_phase)

        if progress is not None:
            # Convert percentage to step within phase
            phase = self.phases[self.current_phase]
            total_steps = phase.get('total_steps', 100)
            step_num = int((progress / 100.0) * total_steps)
            self.update_phase_progress(step_num, step)

        try:
            # Also maintain legacy Redis format
            current_data = self.redis_client.get(self.redis_key)
            if current_data:
                current = json.loads(current_data)
            else:
                current = {
                    "job_id": self.job_id,
                    "stage": "initializing",
                    "progress_percent": 0.0,
                    "current_step": "Starting",
                    "time_elapsed_seconds": 0.0,
                    "estimated_time_remaining_seconds": None,
                    "details": {}
                }

            if stage:
                current["stage"] = stage
            if progress is not None:
                current["progress_percent"] = progress
            if step:
                current["current_step"] = step
            if details:
                current["details"] = details

            elapsed = time.time() - self.start_time
            current["time_elapsed_seconds"] = round(elapsed, 2)

            eta = self.estimate_eta()
            current["estimated_time_remaining_seconds"] = eta

            # Save to Redis with expiration
            self.redis_client.setex(
                self.redis_key,
                settings.PROGRESS_EXPIRE_SECONDS,
                json.dumps(current)
            )

            logger.debug(f"Progress updated: {progress:.1f}% - {step}")

        except Exception as e:
            logger.error(f"Failed to update progress: {e}")

    def get_progress(self) -> Optional[ProgressUpdate]:
        """Get current progress"""
        try:
            data = self.redis_client.get(self.redis_key)
            if data:
                return ProgressUpdate(**json.loads(data))
            return None
        except Exception as e:
            logger.error(f"Failed to get progress: {e}")
            return None

    def update_context_metrics(self, context_data: Dict[str, Any]):
        """Update progress with context engine metrics"""
        try:
            current_data = self.redis_client.get(self.redis_key)
            if current_data:
                current = json.loads(current_data)
                current["context_metrics"] = context_data

                self.redis_client.setex(
                    self.redis_key,
                    settings.PROGRESS_EXPIRE_SECONDS,
                    json.dumps(current)
                )

                if self.redis_publisher:
                    self.redis_publisher.publish_context_update(self.job_id, context_data)

        except Exception as e:
            logger.error(f"Failed to update context metrics: {e}")

    def update_cluster_progress(self, completed_clusters: int, total_clusters: int, cluster_metrics: List[Dict]):
        """Update progress for cluster-based processing"""
        try:
            cluster_progress = {
                "completed_clusters": completed_clusters,
                "total_clusters": total_clusters,
                "cluster_metrics": cluster_metrics,
                "completion_rate": completed_clusters / total_clusters if total_clusters > 0 else 0
            }

            current_data = self.redis_client.get(self.redis_key)
            if current_data:
                current = json.loads(current_data)
                current["cluster_progress"] = cluster_progress

                self.redis_client.setex(
                    self.redis_key,
                    settings.PROGRESS_EXPIRE_SECONDS,
                    json.dumps(current)
                )

        except Exception as e:
            logger.error(f"Failed to update cluster progress: {e}")

    def complete(self, result: Optional[Dict[str, Any]] = None, success: bool = True, error: Optional[str] = None):
        """Mark job as complete and publish final status."""
        self.current_progress = 100.0
        elapsed = int(time.time() - self.start_time)

        logger.info(f"Job {self.job_id} completed in {elapsed}s")

        if success:
            stage = GenerationStage.COMPLETED

            if self.redis_publisher:
                self.redis_publisher.publish_completion(
                    self.job_id,
                    status='completed',
                    result={
                        **(result or {}),
                        'elapsed_seconds': elapsed,
                    }
                )
        else:
            stage = GenerationStage.FAILED

            if self.redis_publisher:
                self.redis_publisher.publish_completion(
                    self.job_id,
                    status='failed',
                    error=error
                )

        # Legacy update
        self.update(
            stage=stage.value,
            progress=100.0 if success else -1.0,
            step="Generation complete" if success else f"Failed: {error}",
            details={"success": success, "error": error, "result": result}
        )
