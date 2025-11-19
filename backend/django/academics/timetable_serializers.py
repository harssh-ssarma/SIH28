"""
Serializers for timetable variants and review workflow
"""
from rest_framework import serializers

from .timetable_models import (
    FixedSlot,
    Shift,
    TimetableReview,
    TimetableVariant,
    TimetableWorkflow,
)


class TimetableVariantSerializer(serializers.ModelSerializer):
    """Serializer for timetable variants"""

    class Meta:
        model = TimetableVariant
        fields = [
            "id",
            "job_id",
            "variant_number",
            "optimization_priority",
            "organization_id",
            "department_id",
            "semester",
            "academic_year",
            "timetable_entries",
            "statistics",
            "quality_metrics",
            "is_selected",
            "selected_at",
            "selected_by",
            "generated_at",
        ]
        read_only_fields = ["id", "generated_at", "selected_at"]


class TimetableReviewSerializer(serializers.ModelSerializer):
    """Serializer for timetable reviews"""

    reviewer_name = serializers.CharField(
        source="reviewer.get_full_name", read_only=True
    )
    reviewer_username = serializers.CharField(
        source="reviewer.username", read_only=True
    )

    class Meta:
        model = TimetableReview
        fields = [
            "id",
            "timetable",
            "reviewer",
            "reviewer_name",
            "reviewer_username",
            "action",
            "comments",
            "suggested_changes",
            "reviewed_at",
        ]
        read_only_fields = ["id", "reviewed_at", "reviewer_name", "reviewer_username"]


class TimetableWorkflowSerializer(serializers.ModelSerializer):
    """Serializer for main timetable with review workflow"""

    variant_data = TimetableVariantSerializer(source="variant", read_only=True)
    reviews = TimetableReviewSerializer(many=True, read_only=True)

    created_by_name = serializers.CharField(
        source="created_by.get_full_name", read_only=True
    )
    submitted_by_name = serializers.CharField(
        source="submitted_by.get_full_name", read_only=True
    )
    published_by_name = serializers.CharField(
        source="published_by.get_full_name", read_only=True
    )

    class Meta:
        model = TimetableWorkflow
        fields = [
            "id",
            "variant",
            "variant_data",
            "job_id",
            "organization_id",
            "department_id",
            "semester",
            "academic_year",
            "status",
            "created_by",
            "created_by_name",
            "created_at",
            "submitted_for_review_at",
            "submitted_by",
            "submitted_by_name",
            "published_at",
            "published_by",
            "published_by_name",
            "timetable_entries",
            "reviews",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "submitted_for_review_at",
            "published_at",
            "created_by_name",
            "submitted_by_name",
            "published_by_name",
        ]


class FixedSlotSerializer(serializers.ModelSerializer):
    """Serializer for fixed time slots"""

    day_display = serializers.CharField(source="get_day_display", read_only=True)
    created_by_name = serializers.CharField(
        source="created_by.get_full_name", read_only=True
    )

    class Meta:
        model = FixedSlot
        fields = [
            "id",
            "organization_id",
            "department_id",
            "day",
            "day_display",
            "start_time",
            "end_time",
            "event_name",
            "description",
            "is_blocked",
            "is_active",
            "created_by",
            "created_by_name",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "day_display", "created_by_name"]


class ShiftSerializer(serializers.ModelSerializer):
    """Serializer for shifts"""

    class Meta:
        model = Shift
        fields = [
            "id",
            "organization_id",
            "name",
            "start_time",
            "end_time",
            "color",
            "is_active",
            "order",
        ]
        read_only_fields = ["id"]
