"""
Views for timetable variants and review workflow
"""
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .timetable_models import (
    FixedSlot,
    Shift,
    TimetableReview,
    TimetableVariant,
    TimetableWorkflow,
)
from .timetable_serializers import (
    FixedSlotSerializer,
    ShiftSerializer,
    TimetableReviewSerializer,
    TimetableVariantSerializer,
    TimetableWorkflowSerializer,
)


class TimetableVariantViewSet(viewsets.ModelViewSet):
    """ViewSet for timetable variants - multiple optimization options"""

    serializer_class = TimetableVariantSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = TimetableVariant.objects.all()

        # Filter by job_id
        job_id = self.request.query_params.get("job_id", None)
        if job_id:
            queryset = queryset.filter(job_id=job_id)

        # Filter by organization
        org_id = self.request.query_params.get("organization_id", None)
        if org_id:
            queryset = queryset.filter(organization_id=org_id)

        return queryset

    @action(detail=False, methods=["post"])
    def select_variant(self, request):
        """Select a variant as the final timetable"""
        variant_id = request.data.get("variant_id")

        if not variant_id:
            return Response(
                {"error": "variant_id is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        variant = get_object_or_404(TimetableVariant, id=variant_id)

        # Deselect other variants with same job_id
        TimetableVariant.objects.filter(job_id=variant.job_id).update(
            is_selected=False, selected_at=None, selected_by=None
        )

        # Select this variant
        variant.is_selected = True
        variant.selected_at = timezone.now()
        variant.selected_by = request.user
        variant.save()

        # Create or update TimetableWorkflow
        timetable, created = TimetableWorkflow.objects.get_or_create(
            job_id=variant.job_id,
            defaults={
                "variant": variant,
                "organization_id": variant.organization_id,
                "department_id": variant.department_id,
                "semester": variant.semester,
                "academic_year": variant.academic_year,
                "created_by": request.user,
                "timetable_entries": variant.timetable_entries,
            },
        )

        if not created:
            timetable.variant = variant
            timetable.timetable_entries = variant.timetable_entries
            timetable.save()

        return Response(
            {
                "message": "Variant selected successfully",
                "timetable_id": timetable.id,
                "variant": TimetableVariantSerializer(variant).data,
            }
        )


class TimetableWorkflowViewSet(viewsets.ModelViewSet):
    """ViewSet for timetable review workflow"""

    serializer_class = TimetableWorkflowSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = TimetableWorkflow.objects.select_related(
            "variant", "created_by"
        ).prefetch_related("reviews")

        # Filter by status
        status_param = self.request.query_params.get("status", None)
        if status_param:
            queryset = queryset.filter(status=status_param)

        # Filter by organization
        org_id = self.request.query_params.get("organization_id", None)
        if org_id:
            queryset = queryset.filter(organization_id=org_id)

        # Filter by department
        dept_id = self.request.query_params.get("department_id", None)
        if dept_id:
            queryset = queryset.filter(department_id=dept_id)

        return queryset

    @action(detail=True, methods=["post"])
    def submit_for_review(self, request, pk=None):
        """Submit timetable for review"""
        timetable = self.get_object()

        if timetable.status != "draft":
            return Response(
                {"error": "Only draft timetables can be submitted for review"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        timetable.submit_for_review(request.user)

        return Response(
            {
                "message": "Timetable submitted for review",
                "timetable": TimetableWorkflowSerializer(timetable).data,
            }
        )

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        """Approve a timetable"""
        timetable = self.get_object()

        if timetable.status != "pending_review":
            return Response(
                {"error": "Only pending timetables can be approved"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create review record
        review = TimetableReview.objects.create(
            timetable=timetable,
            reviewer=request.user,
            action="approved",
            comments=request.data.get("comments", ""),
        )

        return Response(
            {
                "message": "Timetable approved",
                "timetable": TimetableWorkflowSerializer(timetable).data,
                "review": TimetableReviewSerializer(review).data,
            }
        )

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        """Reject a timetable"""
        timetable = self.get_object()

        if timetable.status != "pending_review":
            return Response(
                {"error": "Only pending timetables can be rejected"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        comments = request.data.get("comments", "")
        if not comments:
            return Response(
                {"error": "Comments are required for rejection"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create review record
        review = TimetableReview.objects.create(
            timetable=timetable,
            reviewer=request.user,
            action="rejected",
            comments=comments,
            suggested_changes=request.data.get("suggested_changes", {}),
        )

        return Response(
            {
                "message": "Timetable rejected",
                "timetable": TimetableWorkflowSerializer(timetable).data,
                "review": TimetableReviewSerializer(review).data,
            }
        )

    @action(detail=True, methods=["post"])
    def request_revision(self, request, pk=None):
        """Request revision on a timetable"""
        timetable = self.get_object()

        if timetable.status != "pending_review":
            return Response(
                {"error": "Only pending timetables can have revisions requested"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        comments = request.data.get("comments", "")
        if not comments:
            return Response(
                {"error": "Comments are required for revision request"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create review record
        review = TimetableReview.objects.create(
            timetable=timetable,
            reviewer=request.user,
            action="revision_requested",
            comments=comments,
            suggested_changes=request.data.get("suggested_changes", {}),
        )

        return Response(
            {
                "message": "Revision requested",
                "timetable": TimetableWorkflowSerializer(timetable).data,
                "review": TimetableReviewSerializer(review).data,
            }
        )

    @action(detail=True, methods=["post"])
    def publish(self, request, pk=None):
        """Publish approved timetable"""
        timetable = self.get_object()

        try:
            timetable.publish(request.user)
            return Response(
                {
                    "message": "Timetable published successfully",
                    "timetable": TimetableWorkflowSerializer(timetable).data,
                }
            )
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["get"])
    def pending_reviews(self, request):
        """Get all timetables pending review"""
        queryset = self.get_queryset().filter(status="pending_review")
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class FixedSlotViewSet(viewsets.ModelViewSet):
    """ViewSet for fixed time slots (Assembly, Sports, etc.)"""

    serializer_class = FixedSlotSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = FixedSlot.objects.all()

        # Filter by organization
        org_id = self.request.query_params.get("organization_id", None)
        if org_id:
            queryset = queryset.filter(organization_id=org_id)

        # Filter by active status
        is_active = self.request.query_params.get("is_active", None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == "true")

        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ShiftViewSet(viewsets.ModelViewSet):
    """ViewSet for time shifts"""

    serializer_class = ShiftSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Shift.objects.all()

        # Filter by organization
        org_id = self.request.query_params.get("organization_id", None)
        if org_id:
            queryset = queryset.filter(organization_id=org_id)

        # Filter by active status
        is_active = self.request.query_params.get("is_active", None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == "true")

        return queryset
