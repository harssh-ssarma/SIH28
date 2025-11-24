"""
Celery Tasks for Timetable Generation
Software-level parallelization ready for horizontal scaling
Works on free tier (sequential) but scales automatically with better hardware
"""

from celery import shared_task, group, chord
from django.conf import settings
import requests
import logging
from .models import GenerationJob
from django.utils import timezone

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3, soft_time_limit=1800)
def generate_timetable_task(self, job_id, org_id, academic_year, semester):
    """
    Celery task for timetable generation
    Auto-adapts to available hardware:
    - Free tier (512MB): Sequential processing
    - Pro tier (4GB): 4 parallel workers
    - Enterprise (16GB+): 40 parallel workers
    """
    try:
        # Check if system can handle load
        from core.hardware_detector import HardwareDetector
        if not HardwareDetector.can_handle_load(required_memory_gb=2.0):
            logger.warning(f"Insufficient resources, retrying job {job_id} in 60s")
            raise self.retry(countdown=60, max_retries=5)
        
        job = GenerationJob.objects.get(job_id=job_id)
        job.status = 'running'
        job.started_at = timezone.now()
        job.save()
        
        # Call FastAPI optimization service
        response = requests.post(
            f"{settings.FASTAPI_URL}/api/v1/optimize",
            json={
                'job_id': job_id,
                'org_id': org_id,
                'academic_year': academic_year,
                'semester': semester,
                'generation_type': 'full',
                'scope': 'university'
            },
            timeout=1800  # 30 minutes
        )
        
        if response.status_code == 200:
            logger.info(f"Job {job_id} queued successfully")
            return {'status': 'queued', 'job_id': job_id}
        else:
            raise Exception(f"FastAPI error: {response.text}")
            
    except Exception as e:
        logger.error(f"Job {job_id} failed: {str(e)}")
        job.status = 'failed'
        job.error_message = str(e)
        job.save()
        
        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))


@shared_task
def generate_department_timetable(job_id, dept_id, org_id, academic_year, semester):
    """
    Generate timetable for single department
    Used for parallel processing when multiple workers available
    """
    try:
        response = requests.post(
            f"{settings.FASTAPI_URL}/api/v1/optimize/department",
            json={
                'job_id': job_id,
                'dept_id': dept_id,
                'org_id': org_id,
                'academic_year': academic_year,
                'semester': semester
            },
            timeout=600  # 10 minutes per department
        )
        
        return {
            'dept_id': dept_id,
            'status': 'completed' if response.status_code == 200 else 'failed',
            'data': response.json() if response.status_code == 200 else None
        }
        
    except Exception as e:
        logger.error(f"Department {dept_id} failed: {str(e)}")
        return {'dept_id': dept_id, 'status': 'failed', 'error': str(e)}


@shared_task
def generate_parallel_timetable(job_id, org_id, academic_year, semester, department_ids):
    """
    Parallel timetable generation using Celery groups
    - Free tier: Processes sequentially (1 worker)
    - Paid tier: Processes in parallel (10+ workers)
    
    Celery automatically handles worker availability
    """
    try:
        job = GenerationJob.objects.get(job_id=job_id)
        job.status = 'running'
        job.started_at = timezone.now()
        job.save()
        
        # Create parallel tasks (Celery handles sequential/parallel automatically)
        tasks = group(
            generate_department_timetable.s(
                job_id, dept_id, org_id, academic_year, semester
            )
            for dept_id in department_ids
        )
        
        # Execute with callback
        callback = merge_department_results.s(job_id)
        chord(tasks)(callback)
        
        return {'status': 'queued', 'job_id': job_id, 'departments': len(department_ids)}
        
    except Exception as e:
        logger.error(f"Parallel generation failed: {str(e)}")
        job.status = 'failed'
        job.error_message = str(e)
        job.save()
        raise


@shared_task
def merge_department_results(results, job_id):
    """
    Merge results from parallel department generation
    Called automatically after all departments complete
    """
    try:
        job = GenerationJob.objects.get(job_id=job_id)
        
        # Check if all departments succeeded
        failed = [r for r in results if r['status'] == 'failed']
        
        if failed:
            job.status = 'partial'
            job.error_message = f"{len(failed)} departments failed"
        else:
            job.status = 'completed'
            job.progress = 100
        
        job.completed_at = timezone.now()
        job.save()
        
        logger.info(f"Job {job_id} completed: {len(results)} departments")
        return {'job_id': job_id, 'total': len(results), 'failed': len(failed)}
        
    except Exception as e:
        logger.error(f"Merge failed: {str(e)}")
        raise


@shared_task
def cleanup_old_jobs():
    """
    Periodic task to cleanup old generation jobs
    Run daily via Celery Beat
    """
    from datetime import timedelta
    cutoff = timezone.now() - timedelta(days=30)
    
    deleted = GenerationJob.objects.filter(
        created_at__lt=cutoff,
        status__in=['completed', 'failed']
    ).delete()
    
    logger.info(f"Cleaned up {deleted[0]} old jobs")
    return deleted[0]


@shared_task(bind=True, max_retries=3)
def check_resource_availability(self):
    """
    Check if system has resources for new generation
    Implements resource-aware queuing
    """
    import psutil
    
    # Get system resources
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    
    # Check if resources available
    if cpu_percent > 90 or memory.percent > 85:
        logger.warning(f"Resources exhausted: CPU {cpu_percent}%, RAM {memory.percent}%")
        raise self.retry(countdown=60)  # Retry after 1 minute
    
    return {
        'cpu_available': 100 - cpu_percent,
        'memory_available': 100 - memory.percent,
        'can_process': True
    }


@shared_task
def priority_queue_task(job_id, priority='normal'):
    """
    Priority-based task execution
    - 'high': Premium universities (priority=9)
    - 'normal': Regular universities (priority=5)
    - 'low': Free tier universities (priority=1)
    """
    job = GenerationJob.objects.get(job_id=job_id)
    
    # Set priority in job metadata
    job.metadata = job.metadata or {}
    job.metadata['priority'] = priority
    job.save()
    
    # Queue with priority
    if priority == 'high':
        generate_timetable_task.apply_async(
            args=[job_id, job.org_id, job.academic_year, job.semester],
            priority=9
        )
    elif priority == 'low':
        generate_timetable_task.apply_async(
            args=[job_id, job.org_id, job.academic_year, job.semester],
            priority=1
        )
    else:
        generate_timetable_task.apply_async(
            args=[job_id, job.org_id, job.academic_year, job.semester],
            priority=5
        )
