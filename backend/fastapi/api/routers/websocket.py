"""
WebSocket Router
Handles real-time progress streaming for timetable generation
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
import logging
import json
import os

from api.deps import get_redis_client

router = APIRouter(tags=["websocket"])
logger = logging.getLogger(__name__)


@router.websocket("/ws/progress/{job_id}")
async def websocket_progress(websocket: WebSocket, job_id: str):
    """
    Real-time progress streaming via WebSocket.
    
    Clients connect to this endpoint to receive live updates
    about timetable generation progress.
    
    Args:
        websocket: WebSocket connection
        job_id: Job identifier to track
    """
    try:
        import aioredis
        
        await websocket.accept()
        logger.info(f"WebSocket connected for job {job_id}")
        
        # Send initial snapshot if exists
        try:
            # Get Redis client from app state
            redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
            redis_pool = await aioredis.create_redis_pool(redis_url, encoding='utf-8')
            
            # Try to get snapshot from Redis
            snapshot = await redis_pool.get(f"progress:job:{job_id}")
            if snapshot:
                await websocket.send_text(snapshot)
                logger.debug(f"Sent snapshot for job {job_id}")
        except Exception as e:
           logger.warning(f"Could not send snapshot: {e}")
        
        # Subscribe to Redis pub/sub for real-time updates
        try:
            channels = await redis_pool.subscribe(f"progress:{job_id}")
            ch = channels[0]
            
            logger.info(f"Subscribed to progress updates for job {job_id}")
            
            # Stream updates
            while await ch.wait_message():
                msg = await ch.get()
                await websocket.send_text(msg)
                
                # Check if job completed
                data = json.loads(msg)
                if data.get('status') in ['completed', 'failed', 'cancelled']:
                    logger.info(f"Job {job_id} finished with status: {data.get('status')}")
                    break
                    
        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected for job {job_id}")
        except Exception as e:
            logger.error(f"WebSocket streaming error: {e}")
            
    except Exception as e:
        logger.error(f"WebSocket error for job {job_id}: {e}")
    finally:
        # Cleanup
        try:
            await redis_pool.unsubscribe(f"progress:{job_id}")
            redis_pool.close()
            await redis_pool.wait_closed()
            logger.debug(f"Cleaned up WebSocket resources for job {job_id}")
        except:
            pass
