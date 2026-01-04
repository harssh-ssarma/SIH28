"""
Optimized API Views - Minimal Response Payloads
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.cache import cache
from django.db.models import Count, Prefetch
from .models import GenerationJob, Faculty, Course, Department
import logging

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def optimized_timetables_list(request):
    """Ultra-fast timetables list - only essential data"""
    org_id = request.user.organization_id
    cache_key = f'timetables_list_{org_id}'
    
    # Check cache first
    cached = cache.get(cache_key)
    if cached:
        return Response(cached)
    
    # Minimal query with aggregation
    jobs = GenerationJob.objects.filter(
        organization_id=org_id,
        status='completed'
    ).values(
        'id', 'created_at', 'status'
    ).annotate(
        variant_count=Count('id')
    )[:50]  # Limit to 50 most recent
    
    # Transform to minimal format
    data = [{
        'id': str(j['id']),
        'created_at': j['created_at'].isoformat(),
        'status': j['status'],
        'variants': j['variant_count']
    } for j in jobs]
    
    # Cache for 2 minutes
    cache.set(cache_key, data, 120)
    
    return Response(data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def optimized_faculty_list(request):
    """Ultra-fast faculty list - only names and IDs"""
    org_id = request.user.organization_id
    page_size = int(request.GET.get('page_size', 20))
    
    cache_key = f'faculty_minimal_{org_id}_{page_size}'
    cached = cache.get(cache_key)
    if cached:
        return Response(cached)
    
    # Minimal query - only essential fields
    faculty = Faculty.objects.filter(
        organization_id=org_id,
        is_active=True
    ).values('faculty_id', 'first_name', 'last_name', 'is_active')[:page_size]
    
    # Minimal response
    data = {
        'results': [{
            'faculty_id': str(f['faculty_id']),
            'name': f"{f['first_name']} {f['last_name']}",
            'is_active': f['is_active']
        } for f in faculty],
        'count': page_size
    }
    
    cache.set(cache_key, data, 300)  # 5 min cache
    return Response(data)


@api_view(['GET'])
def optimized_departments_list(request):
    """Ultra-fast departments - cached and minimal"""
    org_id = request.GET.get('organization')
    cache_key = f'departments_{org_id}'
    
    cached = cache.get(cache_key)
    if cached:
        return Response(cached)
    
    depts = Department.objects.filter(
        organization_id=org_id,
        is_active=True
    ).values('dept_id', 'dept_name', 'dept_code')
    
    data = [{
        'id': str(d['dept_id']),
        'name': d['dept_name'],
        'code': d['dept_code']
    } for d in depts]
    
    cache.set(cache_key, data, 600)  # 10 min cache
    return Response(data)
