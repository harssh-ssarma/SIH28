"""
Bulk Student Enrollment API
Creates subject enrollments for students based on their semester and department
"""
import logging

from django.db import models, transaction
from django.db.models import F, Q
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .attendance_models import SubjectEnrollment
from .attendance_serializers import SubjectEnrollmentSerializer
from .models import Faculty, Student, Subject

logger = logging.getLogger(__name__)


class BulkEnrollmentViewSet(viewsets.ViewSet):
    """
    Bulk enrollment operations for students
    """

    @action(detail=False, methods=["post"], url_path="auto-enroll")
    def auto_enroll(self, request):
        """
        Automatically enroll students in subjects based on their semester and department.

        Request Body:
        {
            "academic_year": "2024-25",
            "semester": 1,
            "department_id": "uuid" (optional - if not provided, enrolls all departments),
            "enrollment_type": "core_only" | "core_and_electives" | "all",
            "max_electives_per_student": 2
        }

        Returns:
        {
            "success": true,
            "message": "Enrolled 150 students in 8 subjects",
            "stats": {
                "students_enrolled": 150,
                "subjects_count": 8,
                "total_enrollments_created": 1200,
                "core_enrollments": 900,
                "elective_enrollments": 300
            }
        }
        """
        try:
            academic_year = request.data.get("academic_year", "2024-25")
            semester = request.data.get("semester")
            department_id = request.data.get("department_id")
            enrollment_type = request.data.get("enrollment_type", "core_and_electives")
            max_electives = int(request.data.get("max_electives_per_student", 2))

            if not semester:
                return Response(
                    {"error": "Semester is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Get students
            student_filters = Q(current_semester=semester, is_active=True)
            if department_id:
                student_filters &= Q(department_id=department_id)

            students = Student.objects.filter(student_filters).select_related(
                "department", "program"
            )

            if not students.exists():
                return Response(
                    {"error": f"No active students found for semester {semester}"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Get subjects for this semester
            subject_filters = Q(semester=semester, is_active=True)
            if department_id:
                subject_filters &= Q(department_id=department_id)

            subjects = Subject.objects.filter(subject_filters).select_related(
                "department"
            )

            if not subjects.exists():
                return Response(
                    {"error": f"No subjects found for semester {semester}"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Separate core and elective subjects
            core_subjects = subjects.filter(subject_type="core")
            elective_subjects = subjects.filter(subject_type="elective")

            stats = {
                "students_enrolled": 0,
                "subjects_count": 0,
                "total_enrollments_created": 0,
                "core_enrollments": 0,
                "elective_enrollments": 0,
                "cross_dept_enrollments": 0,
                "already_existed": 0,
            }

            with transaction.atomic():
                for student in students:
                    student_enrollments = 0

                    # Enroll in CORE subjects
                    if enrollment_type in ["core_only", "core_and_electives", "all"]:
                        # Enroll in core subjects of student's department
                        dept_core_subjects = core_subjects.filter(
                            department=student.department
                        )

                        for subject in dept_core_subjects:
                            (
                                enrollment,
                                created,
                            ) = SubjectEnrollment.objects.get_or_create(
                                student=student,
                                subject=subject,
                                academic_year=academic_year,
                                semester=semester,
                                defaults={
                                    "batch": student.batch
                                    if hasattr(student, "batch")
                                    else None,
                                    "is_active": True,
                                },
                            )
                            if created:
                                stats["core_enrollments"] += 1
                                student_enrollments += 1
                            else:
                                stats["already_existed"] += 1

                    # Enroll in ELECTIVE subjects
                    if (
                        enrollment_type in ["core_and_electives", "all"]
                        and elective_subjects.exists()
                    ):
                        # Enroll in some electives (can be from any department)
                        import random

                        # Get electives from student's department
                        dept_electives = list(
                            elective_subjects.filter(department=student.department)
                        )

                        # Get electives from other departments (cross-department)
                        other_dept_electives = list(
                            elective_subjects.exclude(department=student.department)
                        )

                        # Choose electives (mix of dept and cross-dept)
                        available_electives = dept_electives + other_dept_electives
                        num_electives = min(len(available_electives), max_electives)

                        if num_electives > 0:
                            selected_electives = random.sample(
                                available_electives, num_electives
                            )

                            for subject in selected_electives:
                                (
                                    enrollment,
                                    created,
                                ) = SubjectEnrollment.objects.get_or_create(
                                    student=student,
                                    subject=subject,
                                    academic_year=academic_year,
                                    semester=semester,
                                    defaults={
                                        "batch": student.batch
                                        if hasattr(student, "batch")
                                        else None,
                                        "is_active": True,
                                    },
                                )
                                if created:
                                    stats["elective_enrollments"] += 1
                                    student_enrollments += 1

                                    # Track cross-department enrollments
                                    if subject.department != student.department:
                                        stats["cross_dept_enrollments"] += 1
                                else:
                                    stats["already_existed"] += 1

                    if student_enrollments > 0:
                        stats["students_enrolled"] += 1

                stats["subjects_count"] = subjects.count()
                stats["total_enrollments_created"] = (
                    stats["core_enrollments"] + stats["elective_enrollments"]
                )

            logger.info(f"Bulk enrollment completed: {stats}")

            return Response(
                {
                    "success": True,
                    "message": f"Enrolled {stats['students_enrolled']} students in {stats['subjects_count']} subjects",
                    "stats": stats,
                    "details": {
                        "academic_year": academic_year,
                        "semester": semester,
                        "enrollment_type": enrollment_type,
                    },
                },
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            logger.error(f"Bulk enrollment failed: {str(e)}", exc_info=True)
            return Response(
                {"error": f"Bulk enrollment failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["post"], url_path="custom-enroll")
    def custom_enroll(self, request):
        """
        Enroll specific students in specific subjects.

        Request Body:
        {
            "academic_year": "2024-25",
            "semester": 1,
            "enrollments": [
                {
                    "student_id": "student_id",
                    "subject_ids": ["subject_id1", "subject_id2"]
                }
            ]
        }
        """
        try:
            academic_year = request.data.get("academic_year", "2024-25")
            semester = request.data.get("semester")
            enrollments_data = request.data.get("enrollments", [])

            if not semester or not enrollments_data:
                return Response(
                    {"error": "Semester and enrollments are required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            created_count = 0
            existed_count = 0

            with transaction.atomic():
                for enrollment_item in enrollments_data:
                    student_id = enrollment_item.get("student_id")
                    subject_ids = enrollment_item.get("subject_ids", [])

                    try:
                        student = Student.objects.get(student_id=student_id)
                    except Student.DoesNotExist:
                        continue

                    for subject_id in subject_ids:
                        try:
                            subject = Subject.objects.get(subject_id=subject_id)
                            (
                                enrollment,
                                created,
                            ) = SubjectEnrollment.objects.get_or_create(
                                student=student,
                                subject=subject,
                                academic_year=academic_year,
                                semester=semester,
                                defaults={
                                    "batch": student.batch
                                    if hasattr(student, "batch")
                                    else None,
                                    "is_active": True,
                                },
                            )
                            if created:
                                created_count += 1
                            else:
                                existed_count += 1
                        except Subject.DoesNotExist:
                            continue

            return Response(
                {
                    "success": True,
                    "message": f"Created {created_count} new enrollments, {existed_count} already existed",
                    "created": created_count,
                    "existed": existed_count,
                },
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            logger.error(f"Custom enrollment failed: {str(e)}", exc_info=True)
            return Response(
                {"error": f"Custom enrollment failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["get"], url_path="enrollment-summary")
    def enrollment_summary(self, request):
        """
        Get summary of current enrollments.

        Query Params:
        - academic_year: "2024-25"
        - semester: 1
        - department_id: "uuid" (optional)
        """
        try:
            academic_year = request.query_params.get("academic_year", "2024-25")
            semester = request.query_params.get("semester")
            department_id = request.query_params.get("department_id")

            filters = Q(academic_year=academic_year, is_active=True)
            if semester:
                filters &= Q(semester=semester)
            if department_id:
                filters &= Q(student__department_id=department_id)

            enrollments = SubjectEnrollment.objects.filter(filters)

            total_enrollments = enrollments.count()
            unique_students = enrollments.values("student").distinct().count()
            unique_subjects = enrollments.values("subject").distinct().count()

            # Core vs Elective breakdown
            core_count = enrollments.filter(subject__subject_type="core").count()
            elective_count = enrollments.filter(
                subject__subject_type="elective"
            ).count()

            # Cross-department enrollments
            cross_dept_count = enrollments.exclude(
                student__department=models.F("subject__department")
            ).count()

            return Response(
                {
                    "summary": {
                        "total_enrollments": total_enrollments,
                        "unique_students": unique_students,
                        "unique_subjects": unique_subjects,
                        "core_enrollments": core_count,
                        "elective_enrollments": elective_count,
                        "cross_department_enrollments": cross_dept_count,
                    },
                    "filters": {
                        "academic_year": academic_year,
                        "semester": semester,
                        "department_id": department_id,
                    },
                }
            )

        except Exception as e:
            logger.error(f"Enrollment summary failed: {str(e)}", exc_info=True)
            return Response(
                {"error": f"Failed to get enrollment summary: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["delete"], url_path="clear-enrollments")
    def clear_enrollments(self, request):
        """
        Clear enrollments for a specific semester/academic year.

        Query Params:
        - academic_year: "2024-25"
        - semester: 1
        - department_id: "uuid" (optional)

        USE WITH CAUTION!
        """
        try:
            academic_year = request.query_params.get("academic_year")
            semester = request.query_params.get("semester")
            department_id = request.query_params.get("department_id")
            confirm = request.query_params.get("confirm", "false").lower() == "true"

            if not confirm:
                return Response(
                    {"error": "Add ?confirm=true to confirm deletion"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if not academic_year or not semester:
                return Response(
                    {"error": "academic_year and semester are required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            filters = Q(academic_year=academic_year, semester=semester)
            if department_id:
                filters &= Q(student__department_id=department_id)

            deleted_count = SubjectEnrollment.objects.filter(filters).delete()[0]

            return Response(
                {
                    "success": True,
                    "message": f"Deleted {deleted_count} enrollments",
                    "deleted_count": deleted_count,
                }
            )

        except Exception as e:
            logger.error(f"Clear enrollments failed: {str(e)}", exc_info=True)
            return Response(
                {"error": f"Failed to clear enrollments: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
