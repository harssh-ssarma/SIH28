"""
SCALABLE ENROLLMENT SYSTEM
=========================
Uses ManyToMany with minimal through model for efficiency
"""

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .models import Student, Subject


# Add to existing Student model
class StudentSubjectEnrollment(models.Model):
    """
    Minimal through model for student-subject relationship
    Only stores essential enrollment data
    """

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)

    # Minimal fields
    academic_year = models.CharField(max_length=9)  # '2024-25'
    semester = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(8)]
    )
    status = models.CharField(
        max_length=10,
        choices=[
            ("enrolled", "Enrolled"),
            ("completed", "Completed"),
            ("dropped", "Dropped"),
        ],
        default="enrolled",
    )

    # NEP constraint validation in Student model methods
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "student_subjects"
        unique_together = [["student", "subject", "academic_year"]]
        indexes = [
            models.Index(fields=["student", "semester"]),
            models.Index(fields=["academic_year", "semester"]),
        ]


# Enhanced Student model with enrollment methods
class StudentEnhanced(Student):
    """
    Enhanced Student model with enrollment validation methods
    Add these methods to existing Student model
    """

    # Add ManyToMany field to existing Student model
    enrolled_subjects = models.ManyToManyField(
        Subject, through=StudentSubjectEnrollment, related_name="enrolled_students"
    )

    class Meta:
        proxy = True  # Don't create new table

    def get_semester_subjects(self, semester, academic_year="2024-25"):
        """Get subjects for specific semester"""
        return self.enrolled_subjects.filter(
            studentsubjectenrollment__semester=semester,
            studentsubjectenrollment__academic_year=academic_year,
            studentsubjectenrollment__status="enrolled",
        )

    def get_semester_credits(self, semester, academic_year="2024-25"):
        """Get total credits for semester"""
        return (
            self.get_semester_subjects(semester, academic_year).aggregate(
                total=models.Sum("credits")
            )["total"]
            or 0
        )

    def get_semester_contact_hours(self, semester, academic_year="2024-25"):
        """Get total contact hours for semester"""
        subjects = self.get_semester_subjects(semester, academic_year)
        return sum(
            s.lecture_hours_per_week
            + s.tutorial_hours_per_week
            + s.practical_hours_per_week
            for s in subjects
        )

    def can_enroll_subject(self, subject, semester, academic_year="2024-25"):
        """
        NEP 2020 validation - check if student can enroll in subject
        Returns (can_enroll: bool, reason: str)
        """
        current_subjects = self.get_semester_subjects(semester, academic_year)
        current_credits = self.get_semester_credits(semester, academic_year)
        current_hours = self.get_semester_contact_hours(semester, academic_year)

        # Credit limits (NEP 2020)
        if current_credits + subject.credits > 26:
            return (
                False,
                f"Credit limit exceeded: {current_credits + subject.credits}/26",
            )

        if current_credits + subject.credits < 14 and current_subjects.count() >= 3:
            return False, "Minimum 14 credits required"

        # Course limits
        if current_subjects.count() >= 6:
            return False, "Maximum 6 courses per semester"

        # Lab limits
        if subject.requires_lab:
            lab_count = current_subjects.filter(requires_lab=True).count()
            if lab_count >= 2:
                return False, "Maximum 2 lab courses per semester"

        # Contact hours
        subject_hours = (
            subject.lecture_hours_per_week
            + subject.tutorial_hours_per_week
            + subject.practical_hours_per_week
        )
        if current_hours + subject_hours > 30:
            return False, f"Contact hours exceeded: {current_hours + subject_hours}/30"

        # Subject type limits (NEP 2020)
        core_count = current_subjects.filter(subject_type="core").count()
        if subject.subject_type == "core" and core_count >= 3:
            return False, "Maximum 3 core subjects per semester"

        elective_count = current_subjects.filter(subject_type="elective").count()
        if subject.subject_type == "elective" and elective_count >= 2:
            return False, "Maximum 2 department electives per semester"

        return True, "Can enroll"

    def enroll_subject(self, subject, semester, academic_year="2024-25"):
        """
        Enroll student in subject with validation
        """
        can_enroll, reason = self.can_enroll_subject(subject, semester, academic_year)

        if not can_enroll:
            raise ValueError(f"Cannot enroll: {reason}")

        # Create enrollment
        StudentSubjectEnrollment.objects.get_or_create(
            student=self,
            subject=subject,
            academic_year=academic_year,
            defaults={"semester": semester},
        )

        return True

    def bulk_enroll_semester(self, semester, academic_year="2024-25"):
        """
        Auto-enroll student in semester subjects following NEP constraints
        """
        enrolled_count = 0

        # Get subjects for student's semester and department
        available_subjects = Subject.objects.filter(
            department=self.department, semester=semester, is_active=True
        ).order_by(
            "subject_type", "credits"
        )  # Core first, then by credits

        # Enroll in subjects until constraints are met
        for subject in available_subjects:
            can_enroll, reason = self.can_enroll_subject(
                subject, semester, academic_year
            )

            if can_enroll:
                try:
                    self.enroll_subject(subject, semester, academic_year)
                    enrolled_count += 1
                except ValueError:
                    continue  # Skip if enrollment fails

            # Stop if we have enough credits and courses
            current_credits = self.get_semester_credits(semester, academic_year)
            current_courses = self.get_semester_subjects(
                semester, academic_year
            ).count()

            if current_credits >= 18 and current_courses >= 4:
                break  # Optimal load reached

        return enrolled_count
