"""
Redis Pub/Sub Manager for Real-Time Progress Updates
ENTERPRISE PATTERN: Event-driven progress streaming
"""
import redis
import json
import logging
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class RedisPublisher:
    """
    Redis publisher for broadcasting progress updates.

    ENTERPRISE PATTERN: Pub/Sub for real-time updates
    - Decouples progress tracking from WebSocket connections
    - Multiple subscribers can listen (Django admin, mobile app, etc.)
    - No data loss if WebSocket disconnects
    """

    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client

    def publish_progress(
        self,
        job_id: str,
        progress_data: Dict[str, Any]
    ) -> None:
        """
        Publish progress update to Redis channel.

        Args:
            job_id: Unique job identifier
            progress_data: Progress information (percent, eta, status, etc.)
        """
        try:
            channel = f"progress:{job_id}"

            # Add timestamp
            message = {
                **progress_data,
                'timestamp': datetime.utcnow().isoformat(),
                'job_id': job_id,
            }

            # Publish to Redis channel
            subscribers = self.redis.publish(channel, json.dumps(message))

            # Also store latest progress in Redis hash (for HTTP polling fallback)
            self.redis.hset(
                f"job:{job_id}:progress",
                mapping={
                    'data': json.dumps(message),
                    'updated_at': datetime.utcnow().isoformat(),
                }
            )

            # Set expiration (1 hour)
            self.redis.expire(f"job:{job_id}:progress", 3600)

            logger.debug(f"Published progress for job {job_id} to {subscribers} subscribers")

        except Exception as e:
            logger.error(f"Failed to publish progress for job {job_id}: {e}", exc_info=True)

    def publish_completion(
        self,
        job_id: str,
        status: str,
        result: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None
    ) -> None:
        """
        Publish job completion status.

        Args:
            job_id: Unique job identifier
            status: 'completed' or 'failed'
            result: Result data (variants, statistics, etc.)
            error: Error message if failed
        """
        try:
            channel = f"progress:{job_id}"

            message = {
                'job_id': job_id,
                'status': status,
                'progress': 100.0 if status == 'completed' else None,
                'timestamp': datetime.utcnow().isoformat(),
                'result': result,
                'error': error,
            }

            # Publish final status
            self.redis.publish(channel, json.dumps(message))

            # Store in hash
            self.redis.hset(
                f"job:{job_id}:progress",
                mapping={
                    'data': json.dumps(message),
                    'updated_at': datetime.utcnow().isoformat(),
                }
            )

            # Longer expiration for completed jobs (24 hours)
            self.redis.expire(f"job:{job_id}:progress", 86400)

            logger.info(f"Published completion for job {job_id}: {status}")

        except Exception as e:
            logger.error(f"Failed to publish completion for job {job_id}: {e}", exc_info=True)


class RedisSubscriber:
    """
    Redis subscriber for listening to progress updates.

    Used by WebSocket connections to stream updates to frontend.
    """

    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.pubsub = self.redis.pubsub()

    def subscribe(self, job_id: str) -> None:
        """Subscribe to progress channel for specific job."""
        channel = f"progress:{job_id}"
        self.pubsub.subscribe(channel)
        logger.info(f"Subscribed to channel: {channel}")

    def unsubscribe(self, job_id: str) -> None:
        """Unsubscribe from progress channel."""
        channel = f"progress:{job_id}"
        self.pubsub.unsubscribe(channel)
        logger.info(f"Unsubscribed from channel: {channel}")

    def listen(self):
        """
        Listen for messages on subscribed channels.

        Yields:
            Dict containing message data
        """
        for message in self.pubsub.listen():
            if message['type'] == 'message':
                try:
                    data = json.loads(message['data'])
                    yield data
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to decode message: {e}")
                    continue

    def close(self) -> None:
        """Close pub/sub connection."""
        self.pubsub.close()
