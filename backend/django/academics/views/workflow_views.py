"""
Timetable Workflow API - Review and Approval System
"""
import logging

from django.core.cache import cache
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models import GenerationJob
from core.rbac import (
    CanApproveTimetable,
    CanViewTimetable,
)

logger = logging.getLogger(__name__)


PENDING_APPROVAL_STATUSES = ['completed', 'approved', 'rejected']
PENDING_ONLY_STATUS = 'completed'


class TimetableWorkflowViewSet(viewsets.ViewSet):
    """Timetable workflow management"""
    permission_classes = [IsAuthenticated, CanViewTimetable]

    def list(self, request):
        """List generation jobs available for approval review."""
        status_filter = request.query_params.get('status', '')
        cache_key = f'workflows_list_{request.user.id}_{status_filter}'
        cached = cache.get(cache_key)
        if cached:
            return Response(cached)

        qs = (
            GenerationJob.objects
            .only('id', 'organization_id', 'status', 'academic_year', 'semester', 'created_at')
            .order_by('-created_at')
        )
        if status_filter in PENDING_APPROVAL_STATUSES:
            qs = qs.filter(status=status_filter)
        else:
            qs = qs.filter(status__in=PENDING_APPROVAL_STATUSES)

        items = [
            {
                'id': str(j.id),
                'status': j.status,
                'academic_year': j.academic_year or '',
                'semester': j.semester,
                'created_at': j.created_at.isoformat(),
                'organization_id': str(j.organization_id),
            }
            for j in qs[:50]
        ]
        data = {'count': len(items), 'results': items}
        cache.set(cache_key, data, 60)
        return Response(data)

    def retrieve(self, request, pk=None):
        """Get workflow details by ID - FAST VERSION"""
        cache_key = f'workflow_{pk}'
        cached = cache.get(cache_key)
        if cached:
            response = Response(cached)
            response['Cache-Control'] = 'private, max-age=300'
            return response

        try:
            job = GenerationJob.objects.only(
                'id', 'organization_id', 'created_at', 'status',
                'academic_year', 'semester',
            ).get(id=pk)

            data = {
                'id': str(job.id),
                'job_id': str(job.id),
                'organization_id': str(job.organization_id),
                'status': job.status,
                'academic_year': job.academic_year,
                'semester': job.semester,
                'created_at': job.created_at.isoformat(),
                'timetable_entries': [],  # Don't load entries here
            }
            # Immutable once completed/failed - cache for 1 hour; otherwise 5 min
            ttl = 3600 if job.status in ('completed', 'failed') else 300
            cache.set(cache_key, data, ttl)
            response = Response(data)
            response['Cache-Control'] = f'private, max-age={ttl}'
            return response
        except GenerationJob.DoesNotExist:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, CanApproveTimetable])
    def approve(self, request, pk=None):
        """Approve timetable workflow (Registrar only)"""
        try:
            job = GenerationJob.objects.get(id=pk)
            comments = request.data.get('comments', '')
            
            job.status = 'approved'
            job.save(update_fields=['status', 'updated_at'])
            cache.delete(f'workflow_{pk}')
            cache.delete_pattern(f'workflows_list_*')  # Bust list caches

            logger.info(
                "Workflow approved",
                extra={"workflow_id": str(pk), "user_id": str(request.user.id)},
            )
            return Response({
                'success': True,
                'message': 'Timetable approved successfully',
                'workflow_id': str(pk),
                'status': 'approved',
            })
        except GenerationJob.DoesNotExist:
            return Response(
                {'error': 'Workflow not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, CanApproveTimetable])
    def reject(self, request, pk=None):
        """Reject timetable workflow (Registrar only)"""
        try:
            job = GenerationJob.objects.get(id=pk)
            comments = request.data.get('comments', '')
            
            if not comments:
                return Response(
                    {'error': 'Comments required for rejection'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            job.status = 'rejected'
            job.error_message = f"Rejected: {comments}"
            job.save(update_fields=['status', 'error_message', 'updated_at'])
            cache.delete(f'workflow_{pk}')
            cache.delete_pattern(f'workflows_list_*')  # Bust list caches

            logger.info(
                "Workflow rejected",
                extra={"workflow_id": str(pk), "user_id": str(request.user.id)},
            )
            return Response({
                'success': True,
                'message': 'Timetable rejected',
                'workflow_id': str(pk),
                'status': 'rejected',
            })
        except GenerationJob.DoesNotExist:
            return Response(
                {'error': 'Workflow not found'},
                status=status.HTTP_404_NOT_FOUND
            )

