"""
NEP 2020 Compliant Student Enrollment System
===========================================
Implements Harvard/Stanford-style flexible enrollment with Indian NEP constraints
"""

import uuid

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .models import Faculty, Organization, Student, Subject


class StudentEnrollment(models.Model):
    """
    NEP 2020 compliant student-subject enrollment with validation
    """

    ENROLLMENT_STATUS_CHOICES = [
        ("enrolled", "Enrolled"),
        ("waitlisted", "Waitlisted"),
        ("dropped", "Dropped"),
        ("completed", "Completed"),
    ]

    LOAD_TYPE_CHOICES = [
        ("low", "Low Load (14-16 credits)"),
        ("regular", "Regular Load (18-22 credits)"),
        ("heavy", "Heavy Load (24-26 credits)"),
    ]

    enrollment_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="enrollments"
    )
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE, related_name="enrollments"
    )

    academic_year = models.CharField(max_length=20)  # e.g., '2024-25'
    semester = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(8)]
    )

    status = models.CharField(
        max_length=20, choices=ENROLLMENT_STATUS_CHOICES, default="enrolled"
    )
    load_type = models.CharField(
        max_length=10, choices=LOAD_TYPE_CHOICES, default="regular"
    )

    # NEP 2020 Fields
    is_core_subject = models.BooleanField(default=False)
    is_department_elective = models.BooleanField(default=False)
    is_open_elective = models.BooleanField(default=False)
    is_skill_course = models.BooleanField(default=False)  # AEC/SEC
    is_multidisciplinary = models.BooleanField(default=False)  # MDC

    # Approval
    requires_advisor_approval = models.BooleanField(default=False)
    approved_by = models.ForeignKey(
        Faculty, on_delete=models.SET_NULL, null=True, blank=True
    )
    approved_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "student_enrollments"
        unique_together = [["student", "subject", "academic_year", "semester"]]
        indexes = [
            models.Index(fields=["organization", "academic_year", "semester"]),
            models.Index(fields=["student", "semester", "status"]),
        ]

    def clean(self):
        """NEP 2020 enrollment validation"""
        self._validate_credit_limits()
        self._validate_course_limits()
        self._validate_lab_limits()
        self._validate_contact_hours()
        self._validate_subject_distribution()

    def _validate_credit_limits(self):
        """Validate credit constraints (14-26 credits per semester)"""
        current_credits = self._get_semester_credits()
        new_credits = current_credits + self.subject.credits

        if new_credits < 14:
            raise ValidationError(
                f"Minimum 14 credits required. Current: {new_credits}"
            )

        if self.load_type == "low" and new_credits > 16:
            raise ValidationError(
                f"Low load maximum 16 credits. Current: {new_credits}"
            )
        elif self.load_type == "regular" and new_credits > 22:
            raise ValidationError(
                f"Regular load maximum 22 credits. Current: {new_credits}"
            )
        elif self.load_type == "heavy" and new_credits > 26:
            raise ValidationError(
                f"Heavy load maximum 26 credits. Current: {new_credits}"
            )

    def _validate_course_limits(self):
        """Validate course count (3-6 courses per semester)"""
        current_courses = self._get_semester_course_count()

        if current_courses >= 6:
            raise ValidationError(
                f"Maximum 6 courses per semester. Current: {current_courses + 1}"
            )

    def _validate_lab_limits(self):
        """Validate lab course limits (max 2 labs per semester)"""
        if self.subject.requires_lab:
            current_labs = self._get_semester_lab_count()
            if current_labs >= 2:
                raise ValidationError(
                    f"Maximum 2 lab courses per semester. Current: {current_labs + 1}"
                )

    def _validate_contact_hours(self):
        """Validate total contact hours (max 30 hours/week)"""
        current_hours = self._get_semester_contact_hours()
        subject_hours = (
            self.subject.lecture_hours_per_week
            + self.subject.tutorial_hours_per_week
            + self.subject.practical_hours_per_week
        )

        total_hours = current_hours + subject_hours
        if total_hours > 30:
            raise ValidationError(
                f"Maximum 30 contact hours/week. Current: {total_hours}"
            )

    def _validate_subject_distribution(self):
        """Validate NEP 2020 subject distribution per semester"""
        semester_enrollments = self._get_semester_enrollments()

        # Count by type
        core_count = sum(1 for e in semester_enrollments if e.is_core_subject)
        dept_elective_count = sum(
            1 for e in semester_enrollments if e.is_department_elective
        )
        open_elective_count = sum(1 for e in semester_enrollments if e.is_open_elective)

        # NEP 2020 constraints
        if self.is_core_subject and core_count >= 3:
            raise ValidationError("Maximum 3 core subjects per semester")

        if self.is_department_elective and dept_elective_count >= 2:
            raise ValidationError("Maximum 2 department electives per semester")

        if self.is_open_elective and open_elective_count >= 2:
            raise ValidationError("Maximum 2 open electives per semester")

    def _get_semester_credits(self):
        """Get total credits for current semester"""
        return (
            StudentEnrollment.objects.filter(
                student=self.student,
                academic_year=self.academic_year,
                semester=self.semester,
                status="enrolled",
            )
            .exclude(pk=self.pk)
            .aggregate(total=models.Sum("subject__credits"))["total"]
            or 0
        )

    def _get_semester_course_count(self):
        """Get course count for current semester"""
        return (
            StudentEnrollment.objects.filter(
                student=self.student,
                academic_year=self.academic_year,
                semester=self.semester,
                status="enrolled",
            )
            .exclude(pk=self.pk)
            .count()
        )

    def _get_semester_lab_count(self):
        """Get lab course count for current semester"""
        return (
            StudentEnrollment.objects.filter(
                student=self.student,
                academic_year=self.academic_year,
                semester=self.semester,
                status="enrolled",
                subject__requires_lab=True,
            )
            .exclude(pk=self.pk)
            .count()
        )

    def _get_semester_contact_hours(self):
        """Get total contact hours for current semester"""
        enrollments = (
            StudentEnrollment.objects.filter(
                student=self.student,
                academic_year=self.academic_year,
                semester=self.semester,
                status="enrolled",
            )
            .exclude(pk=self.pk)
            .select_related("subject")
        )

        total_hours = 0
        for enrollment in enrollments:
            total_hours += (
                enrollment.subject.lecture_hours_per_week
                + enrollment.subject.tutorial_hours_per_week
                + enrollment.subject.practical_hours_per_week
            )
        return total_hours

    def _get_semester_enrollments(self):
        """Get all enrollments for current semester"""
        return StudentEnrollment.objects.filter(
            student=self.student,
            academic_year=self.academic_year,
            semester=self.semester,
            status="enrolled",
        ).exclude(pk=self.pk)

    def save(self, *args, **kwargs):
        """Override save to run validation"""
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.roll_number} → {self.subject.subject_code} ({self.academic_year} S{self.semester})"


class EnrollmentConstraints(models.Model):
    """
    Organization-specific enrollment constraints
    """

    constraint_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    organization = models.OneToOneField(
        Organization, on_delete=models.CASCADE, related_name="enrollment_constraints"
    )

    # Credit Limits
    min_credits_per_semester = models.IntegerField(default=14)
    max_credits_regular_load = models.IntegerField(default=22)
    max_credits_heavy_load = models.IntegerField(default=26)

    # Course Limits
    min_courses_per_semester = models.IntegerField(default=3)
    max_courses_per_semester = models.IntegerField(default=6)
    max_lab_courses_per_semester = models.IntegerField(default=2)

    # Contact Hours
    max_contact_hours_per_week = models.IntegerField(default=30)

    # NEP 2020 Distribution
    max_core_per_semester = models.IntegerField(default=3)
    max_dept_electives_per_semester = models.IntegerField(default=2)
    max_open_electives_per_semester = models.IntegerField(default=2)

    # Approval Requirements
    heavy_load_requires_approval = models.BooleanField(default=True)
    cross_dept_electives_require_approval = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "enrollment_constraints"

    def __str__(self):
        return f"Enrollment Constraints - {self.organization.org_code}"
