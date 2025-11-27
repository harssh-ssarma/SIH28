"""
Resource Utilization Analytics API Views
"""
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.cache import cache

from .models import GenerationJob
from .analytics_service import AnalyticsService
from core.rbac import CanViewTimetable


class AnalyticsViewSet(viewsets.ViewSet):
    """Resource utilization analytics"""
    permission_classes = [IsAuthenticated, CanViewTimetable]
    
    @action(detail=False, methods=['get'])
    def room_utilization(self, request):
        """Get room utilization heatmap data"""
        job_id = request.query_params.get('job_id')
        variant_id = request.query_params.get('variant_id', 0)
        
        if not job_id:
            return Response({'error': 'job_id required'}, status=status.HTTP_400_BAD_REQUEST)
        
        cache_key = f'room_util_{job_id}_{variant_id}'
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
            
            result = AnalyticsService.calculate_room_utilization(entries)
            
            cache.set(cache_key, result, 600)
            return Response(result)
            
        except GenerationJob.DoesNotExist:
            return Response({'error': 'Job not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['get'])
    def faculty_load(self, request):
        """Get faculty teaching load data"""
        job_id = request.query_params.get('job_id')
        variant_id = request.query_params.get('variant_id', 0)
        
        if not job_id:
            return Response({'error': 'job_id required'}, status=status.HTTP_400_BAD_REQUEST)
        
        cache_key = f'faculty_load_{job_id}_{variant_id}'
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
            
            result = AnalyticsService.calculate_faculty_load(entries)
            
            cache.set(cache_key, result, 600)
            return Response(result)
            
        except GenerationJob.DoesNotExist:
            return Response({'error': 'Job not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['get'])
    def department_matrix(self, request):
        """Get department interaction matrix"""
        job_id = request.query_params.get('job_id')
        variant_id = request.query_params.get('variant_id', 0)
        
        if not job_id:
            return Response({'error': 'job_id required'}, status=status.HTTP_400_BAD_REQUEST)
        
        cache_key = f'dept_matrix_{job_id}_{variant_id}'
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
            
            result = AnalyticsService.calculate_department_matrix(entries)
            
            cache.set(cache_key, result, 600)
            return Response(result)
            
        except GenerationJob.DoesNotExist:
            return Response({'error': 'Job not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get overall utilization summary"""
        job_id = request.query_params.get('job_id')
        variant_id = request.query_params.get('variant_id', 0)
        
        if not job_id:
            return Response({'error': 'job_id required'}, status=status.HTTP_400_BAD_REQUEST)
        
        cache_key = f'util_summary_{job_id}_{variant_id}'
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
            
            result = AnalyticsService.get_utilization_summary(entries)
            
            cache.set(cache_key, result, 600)
            return Response(result)
            
        except GenerationJob.DoesNotExist:
            return Response({'error': 'Job not found'}, status=status.HTTP_404_NOT_FOUND)
