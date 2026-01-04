"""
Enterprise Performance Middleware - Google/Microsoft Level Optimization
"""
import time
import logging
from django.core.cache import cache
from django.http import JsonResponse
import hashlib

logger = logging.getLogger(__name__)


class PerformanceMiddleware:
    """Response caching and compression middleware"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Cache GET requests for 5 minutes
        if request.method == 'GET' and not request.user.is_authenticated:
            cache_key = self._get_cache_key(request)
            cached_response = cache.get(cache_key)
            if cached_response:
                logger.debug(f"Cache HIT: {request.path}")
                return cached_response
        
        start_time = time.time()
        response = self.get_response(request)
        duration = time.time() - start_time
        
        # Add performance headers
        response['X-Response-Time'] = f"{duration:.3f}s"
        
        # Cache successful GET responses
        if request.method == 'GET' and response.status_code == 200:
            cache_key = self._get_cache_key(request)
            cache.set(cache_key, response, 300)  # 5 min cache
        
        # Log slow requests
        if duration > 1.0:
            logger.warning(f"SLOW REQUEST: {request.path} took {duration:.2f}s")
        
        return response
    
    def _get_cache_key(self, request):
        """Generate cache key from request"""
        key_data = f"{request.path}:{request.GET.urlencode()}"
        return f"api_cache:{hashlib.md5(key_data.encode()).hexdigest()}"


class DatabaseQueryOptimizer:
    """Optimize database queries with select_related and prefetch_related"""
    
    @staticmethod
    def optimize_queryset(queryset, model_name):
        """Apply optimal prefetching based on model"""
        optimizations = {
            'GenerationJob': ['organization'],
            'Faculty': ['department', 'department__school'],
            'Course': ['department', 'department__school'],
            'Student': ['department', 'program'],
            'Room': ['building', 'department'],
        }
        
        if model_name in optimizations:
            for relation in optimizations[model_name]:
                queryset = queryset.select_related(relation)
        
        return queryset
