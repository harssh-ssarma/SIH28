"""
Enhanced timetable models for multiple options and review workflow
"""
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class TimetableVariant(models.Model):
    """
    Multiple timetable options generated from same request.
    Each optimized for different priorities.
    """

    OPTIMIZATION_CHOICES = [
        ("balanced", "Balanced - All constraints equally weighted"),
        ("room_utilization", "Maximize Room Utilization"),
        ("faculty_balance", "Minimize Faculty Workload Variance"),
        ("student_compact", "Maximize Student Schedule Compactness"),
        ("faculty_preference", "Maximize Faculty Preference Satisfaction"),
    ]

    job_id = models.CharField(max_length=100, db_index=True)
    variant_number = models.IntegerField()  # 1-5
    optimization_priority = models.CharField(
        max_length=50, choices=OPTIMIZATION_CHOICES
    )

    # Generation metadata
    organization_id = models.CharField(max_length=100)
    department_id = models.CharField(max_length=100)
    semester = models.IntegerField()
    academic_year = models.CharField(max_length=20)

    # Timetable data
    timetable_entries = models.JSONField()
    statistics = models.JSONField()
    quality_metrics = models.JSONField()

    # Selection
    is_selected = models.BooleanField(default=False)
    selected_at = models.DateTimeField(null=True, blank=True)
    selected_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="selected_variants",
    )

    # Timestamps
    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["job_id", "variant_number"]
        unique_together = ["job_id", "variant_number"]
        indexes = [
            models.Index(fields=["job_id", "is_selected"]),
            models.Index(fields=["organization_id", "department_id", "semester"]),
        ]

    def __str__(self):
        return f"{self.job_id} - Variant {self.variant_number} ({self.optimization_priority})"


class TimetableStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    PENDING_REVIEW = "pending_review", "Pending Review"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"
    PUBLISHED = "published", "Published"


class TimetableWorkflow(models.Model):
    """Workflow management for generated timetables (renamed to avoid conflict with existing Timetable model)"""

    # Link to selected variant
    variant = models.OneToOneField(
        TimetableVariant, on_delete=models.CASCADE, null=True, blank=True
    )
    job_id = models.CharField(max_length=100, unique=True, db_index=True)

    # Organization context
    organization_id = models.CharField(max_length=100)
    department_id = models.CharField(max_length=100)
    semester = models.IntegerField()
    academic_year = models.CharField(max_length=20)

    # Workflow status
    status = models.CharField(
        max_length=20, choices=TimetableStatus.choices, default=TimetableStatus.DRAFT
    )

    # Creator
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_workflow_timetables",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    # Submission
    submitted_for_review_at = models.DateTimeField(null=True, blank=True)
    submitted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="submitted_workflow_timetables",
    )

    # Publishing
    published_at = models.DateTimeField(null=True, blank=True)
    published_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="published_workflow_timetables",
    )

    # Timetable data (from selected variant)
    timetable_entries = models.JSONField(default=list)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "organization_id"]),
            models.Index(fields=["department_id", "semester", "academic_year"]),
        ]

    def __str__(self):
        return f"{self.department_id} - Semester {self.semester} ({self.status})"

    def submit_for_review(self, user):
        """Submit timetable for review"""
        self.status = TimetableStatus.PENDING_REVIEW
        self.submitted_for_review_at = timezone.now()
        self.submitted_by = user
        self.save()

    def publish(self, user):
        """Publish approved timetable"""
        if self.status != TimetableStatus.APPROVED:
            raise ValueError("Cannot publish unapproved timetable")
        self.status = TimetableStatus.PUBLISHED
        self.published_at = timezone.now()
        self.published_by = user
        self.save()


class TimetableReview(models.Model):
    """Review history and comments for timetables"""

    REVIEW_ACTIONS = [
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("revision_requested", "Revision Requested"),
    ]

    timetable = models.ForeignKey(
        TimetableWorkflow, on_delete=models.CASCADE, related_name="reviews"
    )
    reviewer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    action = models.CharField(max_length=20, choices=REVIEW_ACTIONS)
    comments = models.TextField(blank=True)

    # Suggested changes
    suggested_changes = models.JSONField(null=True, blank=True)

    reviewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-reviewed_at"]

    def __str__(self):
        return f"{self.timetable} - {self.action} by {self.reviewer}"

    def save(self, *args, **kwargs):
        """Update timetable status based on review action"""
        super().save(*args, **kwargs)

        if self.action == "approved":
            self.timetable.status = TimetableStatus.APPROVED
            self.timetable.save()
        elif self.action == "rejected":
            self.timetable.status = TimetableStatus.REJECTED
            self.timetable.save()
        elif self.action == "revision_requested":
            self.timetable.status = TimetableStatus.DRAFT
            self.timetable.save()


class FixedSlot(models.Model):
    """Fixed/blocked time slots (Assembly, Sports, etc.)"""

    organization_id = models.CharField(max_length=100)
    department_id = models.CharField(
        max_length=100, null=True, blank=True
    )  # Null = all departments

    # Time specification
    day = models.IntegerField(
        choices=[
            (0, "Monday"),
            (1, "Tuesday"),
            (2, "Wednesday"),
            (3, "Thursday"),
            (4, "Friday"),
        ]
    )
    start_time = models.TimeField()
    end_time = models.TimeField()

    # Event details
    event_name = models.CharField(max_length=100)  # "Assembly", "Sports", "Chapel"
    description = models.TextField(blank=True)

    # Control
    is_blocked = models.BooleanField(default=True)  # True = no classes can be scheduled
    is_active = models.BooleanField(default=True)

    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["day", "start_time"]
        indexes = [
            models.Index(fields=["organization_id", "is_active"]),
            models.Index(fields=["day", "start_time"]),
        ]

    def __str__(self):
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        return f"{self.event_name} - {days[self.day]} {self.start_time}-{self.end_time}"


class Shift(models.Model):
    """Time shifts for multi-shift scheduling"""

    organization_id = models.CharField(max_length=100)

    name = models.CharField(max_length=50)  # "Morning", "Afternoon", "Evening"
    start_time = models.TimeField()
    end_time = models.TimeField()

    # Display
    color = models.CharField(max_length=7, default="#3B82F6")  # Hex color for UI
    is_active = models.BooleanField(default=True)

    # Order
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ["organization_id", "order"]
        unique_together = ["organization_id", "name"]

    def __str__(self):
        return f"{self.name} ({self.start_time}-{self.end_time})"
