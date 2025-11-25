"""
Timeout Handler for FastAPI Service
Prevents hanging processes and implements fallback strategies
"""
import signal
import asyncio
import time
import logging
from functools import wraps
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)

class TimeoutError(Exception):
    """Custom timeout exception"""
    pass

def timeout_handler(signum, frame):
    """Signal handler for timeout"""
    raise TimeoutError("Operation timed out")

def with_timeout(timeout_seconds: int):
    """Decorator to add timeout to functions"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Set timeout signal
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(timeout_seconds)
            
            try:
                result = func(*args, **kwargs)
                signal.alarm(0)  # Cancel alarm
                return result
            except TimeoutError:
                logger.warning(f"Function {func.__name__} timed out after {timeout_seconds}s")
                return None
            except Exception as e:
                signal.alarm(0)  # Cancel alarm on any exception
                raise e
            finally:
                signal.alarm(0)  # Ensure alarm is always cancelled
        return wrapper
    return decorator

async def with_async_timeout(coro, timeout_seconds: int):
    """Async timeout wrapper"""
    try:
        return await asyncio.wait_for(coro, timeout=timeout_seconds)
    except asyncio.TimeoutError:
        logger.warning(f"Async operation timed out after {timeout_seconds}s")
        return None

class DataReducer:
    """Reduces dataset size to prevent hanging"""
    
    def __init__(self, max_courses=500, max_faculty=300, max_rooms=200):
        self.max_courses = max_courses
        self.max_faculty = max_faculty
        self.max_rooms = max_rooms
    
    def reduce_dataset(self, courses, faculty, rooms):
        """Reduce dataset size if too large"""
        reduced_courses = courses
        reduced_faculty = faculty
        reduced_rooms = rooms
        
        # Reduce courses
        if len(courses) > self.max_courses:
            # Prioritize core courses
            core_courses = [c for c in courses if getattr(c, 'subject_type', '') == 'core']
            other_courses = [c for c in courses if getattr(c, 'subject_type', '') != 'core']
            
            core_limit = min(len(core_courses), self.max_courses // 2)
            other_limit = self.max_courses - core_limit
            
            reduced_courses = core_courses[:core_limit] + other_courses[:other_limit]
            logger.info(f"Reduced courses from {len(courses)} to {len(reduced_courses)}")
        
        # Reduce faculty
        if isinstance(faculty, dict) and len(faculty) > self.max_faculty:
            faculty_items = list(faculty.items())[:self.max_faculty]
            reduced_faculty = dict(faculty_items)
            logger.info(f"Reduced faculty from {len(faculty)} to {len(reduced_faculty)}")
        elif isinstance(faculty, list) and len(faculty) > self.max_faculty:
            reduced_faculty = faculty[:self.max_faculty]
            logger.info(f"Reduced faculty from {len(faculty)} to {len(reduced_faculty)}")
        
        # Reduce rooms
        if len(rooms) > self.max_rooms:
            reduced_rooms = rooms[:self.max_rooms]
            logger.info(f"Reduced rooms from {len(rooms)} to {len(reduced_rooms)}")
        
        return reduced_courses, reduced_faculty, reduced_rooms

class ProcessMonitor:
    """Monitor process health and detect hanging"""
    
    def __init__(self, hang_threshold=120):  # 2 minutes
        self.hang_threshold = hang_threshold
        self.last_progress_time = time.time()
        self.is_monitoring = False
    
    def update_progress(self):
        """Call this when progress is made"""
        self.last_progress_time = time.time()
    
    def check_hanging(self) -> bool:
        """Check if process appears to be hanging"""
        elapsed = time.time() - self.last_progress_time
        return elapsed > self.hang_threshold
    
    async def monitor_with_callback(self, callback_func):
        """Monitor process and call callback if hanging detected"""
        self.is_monitoring = True
        
        while self.is_monitoring:
            if self.check_hanging():
                logger.warning("Process hanging detected!")
                await callback_func()
                break
            
            await asyncio.sleep(10)  # Check every 10 seconds
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.is_monitoring = False