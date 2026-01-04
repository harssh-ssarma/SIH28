"""
ULTRA-FAST API Views - Applied to ALL Endpoints
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.cache import cache
from django.db.models import Count
from .models import GenerationJob, Faculty, Course, Department, Student, Room
import logging

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def fast_generation_jobs(request):
    """Ultra-fast job list - 50 records max"""
    org_id = request.user.organization_id
    cache_key = f'jobs_{org_id}'
    
    cached = cache.get(cache_key)
    if cached:
        return Response(cached)
    
    jobs = GenerationJob.objects.filter(
        organization_id=org_id
    ).only('id', 'status', 'created_at').order_by('-created_at')[:50]
    
    data = [{'id': str(j.id), 'status': j.status, 'created_at': j.created_at.isoformat()} for j in jobs]
    cache.set(cache_key, data, 300)
    return Response(data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def fast_faculty(request):
    """Ultra-fast faculty - 20 records max"""
    org_id = request.user.organization_id
    limit = int(request.GET.get('page_size', 20))
    cache_key = f'faculty_{org_id}_{limit}'
    
    cached = cache.get(cache_key)
    if cached:
        return Response(cached)
    
    faculty = Faculty.objects.filter(
        organization_id=org_id, is_active=True
    ).only('faculty_id', 'first_name', 'last_name')[:limit]
    
    data = {'results': [{'faculty_id': str(f.faculty_id), 'name': f"{f.first_name} {f.last_name}"} for f in faculty]}
    cache.set(cache_key, data, 600)
    return Response(data)


@api_view(['GET'])
def fast_departments(request):
    """Ultra-fast departments"""
    org_id = request.GET.get('organization')
    cache_key = f'depts_{org_id}'
    
    cached = cache.get(cache_key)
    if cached:
        return Response(cached)
    
    depts = Department.objects.filter(
        organization_id=org_id, is_active=True
    ).only('dept_id', 'dept_name')
    
    data = [{'id': str(d.dept_id), 'name': d.dept_name} for d in depts]
    cache.set(cache_key, data, 600)
    return Response(data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def fast_courses(request):
    """Ultra-fast courses - 50 max"""
    org_id = request.user.organization_id
    cache_key = f'courses_{org_id}'
    
    cached = cache.get(cache_key)
    if cached:
        return Response(cached)
    
    courses = Course.objects.filter(
        organization_id=org_id, is_active=True
    ).only('course_id', 'course_name', 'course_code')[:50]
    
    data = [{'id': str(c.course_id), 'name': c.course_name, 'code': c.course_code} for c in courses]
    cache.set(cache_key, data, 600)
    return Response(data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def fast_students(request):
    """Ultra-fast students - 50 max"""
    org_id = request.user.organization_id
    cache_key = f'students_{org_id}'
    
    cached = cache.get(cache_key)
    if cached:
        return Response(cached)
    
    students = Student.objects.filter(
        organization_id=org_id, is_active=True
    ).only('student_id', 'first_name', 'last_name')[:50]
    
    data = [{'id': str(s.student_id), 'name': f"{s.first_name} {s.last_name}"} for s in students]
    cache.set(cache_key, data, 600)
    return Response(data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def fast_rooms(request):
    """Ultra-fast rooms - 50 max"""
    org_id = request.user.organization_id
    cache_key = f'rooms_{org_id}'
    
    cached = cache.get(cache_key)
    if cached:
        return Response(cached)
    
    rooms = Room.objects.filter(
        organization_id=org_id, is_active=True
    ).only('room_id', 'room_name', 'room_number')[:50]
    
    data = [{'id': str(r.room_id), 'name': r.room_name or r.room_number} for r in rooms]
    cache.set(cache_key, data, 600)
    return Response(data)
