"""
CP-SAT Progress Tracking
Redis-based progress updates for timetable generation
Following Google/Meta standards: One file = progress tracking only
"""
import logging
import json
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger(__name__)


def update_progress(
    redis_client,
    job_id: str,
    cluster_id: int,
    total_clusters: int,
    completed_clusters: int,
    message: str
) -> None:
    """
    Send progress update via Redis pub/sub
    
    Args:
        redis_client: Redis client instance
        job_id: Job identifier
        cluster_id: Current cluster being processed
        total_clusters: Total number of clusters
        completed_clusters: Number of completed clusters
        message: Progress message
    """
    if not redis_client or not job_id or cluster_id is None:
        return
    
    try:
        progress_data = {
            'job_id': job_id,
            'stage': 'cpsat',
            'cluster_id': cluster_id,
            'message': f"Cluster {completed_clusters + 1}/{total_clusters}: {message}",
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        redis_client.publish(f"progress:{job_id}", json.dumps(progress_data))
        logger.debug(f"Progress update sent: {message}")
    except Exception as e:
        logger.warning(f"Failed to send progress update: {e}")


def log_cluster_start(cluster_id: int, course_count: int, slot_count: int) -> None:
    """Log cluster solving start"""
    logger.info(f"[CP-SAT] Starting cluster {cluster_id}: {course_count} courses, {slot_count} slots")


def log_cluster_success(cluster_id: int, solve_time: float) -> None:
    """Log successful cluster solve"""
    logger.info(f"[CP-SAT] Cluster {cluster_id} solved in {solve_time:.2f}s")


def log_cluster_timeout(cluster_id: int, timeout: int) -> None:
    """Log cluster timeout"""
    logger.warning(f"[CP-SAT] Cluster {cluster_id} timed out after {timeout}s")


def log_cluster_no_solution(cluster_id: int) -> None:
    """Log cluster with no feasible solution"""
    logger.warning(f"[CP-SAT] Cluster {cluster_id}: No feasible solution found")


def log_strategy_attempt(strategy_name: str, attempt: int, max_attempts: int) -> None:
    """Log strategy attempt"""
    logger.info(f"[CP-SAT] Attempting strategy {attempt}/{max_attempts}: {strategy_name}")
