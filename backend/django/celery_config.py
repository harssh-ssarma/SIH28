"""
Celery Configuration
Auto-scales based on available resources
Works on free tier (512MB RAM) and scales to production
"""

import os
from celery import Celery
from celery.schedules import crontab
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'erp.settings')

# Auto-detect hardware and configure
try:
    from core.hardware_detector import HardwareDetector, get_config
    HardwareDetector.print_system_info()
    CELERY_WORKERS = get_config('celery_workers', 1)
    CELERY_CONCURRENCY = get_config('celery_concurrency', 1)
except:
    CELERY_WORKERS = int(os.getenv('CELERY_WORKERS', 1))
    CELERY_CONCURRENCY = 1

app = Celery('sih28')

# Load config from Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks
app.autodiscover_tasks()

# Celery Configuration
app.conf.update(
    # Broker settings (always use Redis)
    broker_url=os.getenv('REDIS_URL', 'redis://127.0.0.1:6379/0'),
    result_backend=os.getenv('REDIS_URL', 'redis://127.0.0.1:6379/0'),
    
    # Task settings
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    
    # Worker settings (auto-detected from hardware)
    worker_concurrency=CELERY_CONCURRENCY,  # Auto-detected: 1-16 based on RAM/CPU
    worker_prefetch_multiplier=1,  # Process one task at a time
    worker_max_tasks_per_child=50,  # Restart worker after 50 tasks (memory management)
    worker_max_memory_per_child=400000,  # 400MB per worker (auto-restart if exceeded)
    
    # Task execution settings
    task_acks_late=True,  # Acknowledge after completion (reliability)
    task_reject_on_worker_lost=True,  # Requeue if worker crashes
    task_time_limit=1800,  # 30 minutes hard limit
    task_soft_time_limit=1500,  # 25 minutes soft limit
    
    # Priority settings (for multi-tenant)
    task_default_priority=5,
    task_inherit_parent_priority=True,
    
    # Result backend settings
    result_expires=86400,  # Results expire after 24 hours
    result_compression='gzip',  # Compress results (save memory)
    
    # Resource management
    worker_disable_rate_limits=False,
    task_default_rate_limit='10/m',  # Max 10 tasks per minute on free tier
    
    # Monitoring
    worker_send_task_events=True,
    task_send_sent_event=True,
)

# Periodic tasks (Celery Beat)
app.conf.beat_schedule = {
    'cleanup-old-jobs': {
        'task': 'academics.celery_tasks.cleanup_old_jobs',
        'schedule': crontab(hour=2, minute=0),  # Run daily at 2 AM
    },
}

@app.task(bind=True)
def debug_task(self):
    """Debug task to test Celery setup"""
    print(f'Request: {self.request!r}')
