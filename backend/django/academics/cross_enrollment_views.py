"""
Cross-Enrollment API Views
"""
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.cache import cache

from .models import GenerationJob
from .cross_enrollment_service import CrossEnrollmentService
from core.rbac import CanViewTimetable, DepartmentAccessPermission, has_department_access


class CrossEnrollmentViewSet(viewsets.ViewSet):
    """Cross-enrollment tracking"""
    permission_classes = [IsAuthenticated, CanViewTimetable]
    
    @action(detail=False, methods=['get'])
    def analyze(self, request):
        """Analyze cross-enrollment for department"""
        job_id = request.query_params.get('job_id')
        variant_id = request.query_params.get('variant_id', 0)
        department_id = request.query_params.get('department_id')
        
        if not job_id or not department_id:
            return Response(
                {'error': 'job_id and department_id required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check department access
        if not has_department_access(request.user, department_id):
            return Response(
                {'error': 'Access denied to this department'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        cache_key = f'cross_enrollment_{job_id}_{variant_id}_{department_id}'
        cached = cache.get(cache_key)
        if cached:
            return Response(cached)
        
        try:
            job = GenerationJob.objects.get(id=job_id)
            variants = (job.timetable_data or {}).get('variants', [])
            
            if not variants or int(variant_id) >= len(variants):
                return Response({'error': 'Variant not found'}, status=status.HTTP_404_NOT_FOUND)
            
            variant = variants[int(variant_id)]
            entries = variant.get('timetable_entries', [])
            
            # Analyze cross-enrollment
            analysis = CrossEnrollmentService.analyze_cross_enrollment(entries, department_id)
            
            cache.set(cache_key, analysis, 600)  # 10 min
            return Response(analysis)
            
        except GenerationJob.DoesNotExist:
            return Response({'error': 'Job not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['get'])
    def outgoing(self, request):
        """Get outgoing students (our students taking other depts' courses)"""
        job_id = request.query_params.get('job_id')
        variant_id = request.query_params.get('variant_id', 0)
        department_id = request.query_params.get('department_id')
        
        if not job_id or not department_id:
            return Response(
                {'error': 'job_id and department_id required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check department access
        if not has_department_access(request.user, department_id):
            return Response(
                {'error': 'Access denied to this department'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        cache_key = f'outgoing_{job_id}_{variant_id}_{department_id}'
        cached = cache.get(cache_key)
        if cached:
            return Response(cached)
        
        try:
            job = GenerationJob.objects.get(id=job_id)
            variants = (job.timetable_data or {}).get('variants', [])
            
            if not variants or int(variant_id) >= len(variants):
                return Response({'error': 'Variant not found'}, status=status.HTTP_404_NOT_FOUND)
            
            variant = variants[int(variant_id)]
            entries = variant.get('timetable_entries', [])
            
            # Get outgoing students
            outgoing = CrossEnrollmentService.get_outgoing_students(entries, department_id)
            
            cache.set(cache_key, outgoing, 600)
            return Response(outgoing)
            
        except GenerationJob.DoesNotExist:
            return Response({'error': 'Job not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['get'])
    def incoming(self, request):
        """Get incoming students (other students taking our courses)"""
        job_id = request.query_params.get('job_id')
        variant_id = request.query_params.get('variant_id', 0)
        department_id = request.query_params.get('department_id')
        
        if not job_id or not department_id:
            return Response(
                {'error': 'job_id and department_id required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check department access
        if not has_department_access(request.user, department_id):
            return Response(
                {'error': 'Access denied to this department'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        cache_key = f'incoming_{job_id}_{variant_id}_{department_id}'
        cached = cache.get(cache_key)
        if cached:
            return Response(cached)
        
        try:
            job = GenerationJob.objects.get(id=job_id)
            variants = (job.timetable_data or {}).get('variants', [])
            
            if not variants or int(variant_id) >= len(variants):
                return Response({'error': 'Variant not found'}, status=status.HTTP_404_NOT_FOUND)
            
            variant = variants[int(variant_id)]
            entries = variant.get('timetable_entries', [])
            
            # Get incoming students
            incoming = CrossEnrollmentService.get_incoming_students(entries, department_id)
            
            cache.set(cache_key, incoming, 600)
            return Response(incoming)
            
        except GenerationJob.DoesNotExist:
            return Response({'error': 'Job not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get university-wide cross-enrollment summary (Registrar only)"""
        job_id = request.query_params.get('job_id')
        variant_id = request.query_params.get('variant_id', 0)
        
        if not job_id:
            return Response({'error': 'job_id required'}, status=status.HTTP_400_BAD_REQUEST)
        
        cache_key = f'cross_summary_{job_id}_{variant_id}'
        cached = cache.get(cache_key)
        if cached:
            return Response(cached)
        
        try:
            job = GenerationJob.objects.get(id=job_id)
            variants = (job.timetable_data or {}).get('variants', [])
            
            if not variants or int(variant_id) >= len(variants):
                return Response({'error': 'Variant not found'}, status=status.HTTP_404_NOT_FOUND)
            
            variant = variants[int(variant_id)]
            entries = variant.get('timetable_entries', [])
            
            # Get summary
            summary = CrossEnrollmentService.get_cross_enrollment_summary(entries)
            
            cache.set(cache_key, summary, 600)
            return Response(summary)
            
        except GenerationJob.DoesNotExist:
            return Response({'error': 'Job not found'}, status=status.HTTP_404_NOT_FOUND)
