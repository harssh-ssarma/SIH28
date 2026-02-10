"""
Circuit Breaker Pattern - Industry Standard Implementation
Protects services from cascading failures following the patterns used
at Netflix (Hystrix) and Google (Cloud Circuit Breaker)
"""
import time
import logging
from functools import wraps
from fastapi import HTTPException

logger = logging.getLogger(__name__)


class CircuitBreaker:
    """
    Circuit breaker pattern for service protection.
    
    States:
    - CLOSED: Normal operation, requests flow through
    - OPEN: Service is failing, requests are rejected
    - HALF_OPEN: Testing if service has recovered
    
    Usage:
        breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=60)
        
        @breaker
        async def my_function():
            ...
    """
    
    def __init__(self, failure_threshold: int = 3, recovery_timeout: int = 60):
        """
        Initialize circuit breaker.
        
        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Seconds to wait before attempting recovery
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
        logger.info(f"Circuit breaker initialized: threshold={failure_threshold}, timeout={recovery_timeout}s")
    
    def __call__(self, func):
        """Decorator to wrap function with circuit breaker"""
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Check circuit state
            if self.state == 'OPEN':
                if time.time() - self.last_failure_time > self.recovery_timeout:
                    self.state = 'HALF_OPEN'
                    logger.info("Circuit breaker moving to HALF_OPEN - testing recovery")
                else:
                    logger.warning("Circuit breaker OPEN - rejecting request")
                    raise HTTPException(
                        status_code=503,
                        detail="Service temporarily unavailable (circuit breaker open)"
                    )
            
            try:
                # Execute function
                result = await func(*args, **kwargs)
                
                # If in HALF_OPEN and succeeded, close circuit
                if self.state == 'HALF_OPEN':
                    self.state = 'CLOSED'
                    self.failure_count = 0
                    logger.info("Circuit breaker CLOSED - service recovered")
                
                return result
                
            except Exception as e:
                # Record failure
                self.failure_count += 1
                self.last_failure_time = time.time()
                
                # Open circuit if threshold reached
                if self.failure_count >= self.failure_threshold:
                    self.state = 'OPEN'
                    logger.error(f"Circuit breaker OPEN - service failing (failures: {self.failure_count})")
                
                raise e
        
        return wrapper
    
    def reset(self):
        """Manually reset circuit breaker"""
        self.state = 'CLOSED'
        self.failure_count = 0
        self.last_failure_time = None
        logger.info("Circuit breaker manually reset")
    
    def get_state(self) -> dict:
        """Get current circuit breaker state"""
        return {
            'state': self.state,
            'failure_count': self.failure_count,
            'failure_threshold': self.failure_threshold,
            'last_failure_time': self.last_failure_time,
            'recovery_timeout': self.recovery_timeout
        }
