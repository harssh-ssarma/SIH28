"""
NEP 2020 Enrollment Management APIs
Handles student enrollments, cross-department tracking, and Redis caching
"""
import json
import logging
from datetime import timedelta

from django.core.cache import cache
from django.db.models import Count, F, Q
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .attendance_models import SubjectEnrollment
from .attendance_serializers import SubjectEnrollmentSerializer
from .models import Classroom, Department, Faculty, Student, Subject
from .serializers import (
    ClassroomSerializer,
    FacultySerializer,
    StudentSerializer,
    SubjectSerializer,
)

logger = logging.getLogger(__name__)


class EnrollmentCacheViewSet(viewsets.ViewSet):
    """
    Redis-backed cache management for timetable generation data
    Stores pre-fetched enrollment data for fast form loading and editing
    """

    permission_classes = [IsAuthenticated]

    def list(self, request):
        """
        GET /api/v1/timetable/enrollment-cache/?cache_key={key}
        Check if data exists in Redis cache
        """
        cache_key = request.query_params.get("cache_key")
        if not cache_key:
            return Response(
                {"error": "cache_key parameter required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        cached_data = cache.get(cache_key)

        if cached_data:
            return Response(
                {"exists": True, "data": cached_data, "cache_key": cache_key}
            )
        else:
            return Response({"exists": False, "cache_key": cache_key})

    def create(self, request):
        """
        POST /api/v1/timetable/enrollment-cache/
        Store enrollment data in Redis cache (24 hour TTL)
        """
        try:
            data = request.data
            cache_key = data.get("cache_key")

            if not cache_key:
                return Response(
                    {"error": "cache_key required"}, status=status.HTTP_400_BAD_REQUEST
                )

            # Store in Redis with 24 hour expiry
            cache.set(cache_key, data, timeout=86400)  # 24 hours

            logger.info(f"Cached enrollment data for key: {cache_key}")

            return Response(
                {
                    "success": True,
                    "message": "Data cached successfully",
                    "cache_key": cache_key,
                    "expires_in": "24 hours",
                },
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            logger.error(f"Failed to cache data: {str(e)}", exc_info=True)
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def update(self, request, pk=None):
        """
        PUT /api/v1/timetable/enrollment-cache/
        Update existing Redis cache
        """
        try:
            data = request.data
            cache_key = data.get("cache_key")

            if not cache_key:
                return Response(
                    {"error": "cache_key required"}, status=status.HTTP_400_BAD_REQUEST
                )

            # Update cache with new 24 hour expiry
            cache.set(cache_key, data, timeout=86400)

            logger.info(f"Updated cached data for key: {cache_key}")

            return Response(
                {
                    "success": True,
                    "message": "Cache updated successfully",
                    "cache_key": cache_key,
                }
            )

        except Exception as e:
            logger.error(f"Failed to update cache: {str(e)}", exc_info=True)
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def destroy(self, request, pk=None):
        """
        DELETE /api/v1/timetable/enrollment-cache/?cache_key={key}
        Clear Redis cache entry
        """
        cache_key = request.query_params.get("cache_key")
        if not cache_key:
            return Response(
                {"error": "cache_key parameter required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        cache.delete(cache_key)

        logger.info(f"Cleared cache for key: {cache_key}")

        return Response({"success": True, "message": "Cache cleared successfully"})


class StudentEnrollmentViewSet(viewsets.ViewSet):
    """
    Student enrollment data API for timetable generation
    Fetches students and their subject enrollments for a given department/semester
    """

    permission_classes = [IsAuthenticated]

    def list(self, request):
        """
        GET /api/v1/students/enrollments/
        ?department_id={dept}&semester={sem}&academic_year={year}

        Returns all students enrolled in department's subjects (core + taking department's subjects as electives)
        """
        department_id = request.query_params.get("department_id")
        semester = request.query_params.get("semester")
        academic_year = request.query_params.get("academic_year")

        if not all([department_id, semester, academic_year]):
            return Response(
                {"error": "department_id, semester, and academic_year are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            semester = int(semester)

            # Get all subject enrollments for this department's subjects
            enrollments = SubjectEnrollment.objects.filter(
                subject__department_id=department_id,
                semester=semester,
                academic_year=academic_year,
                is_active=True,
            ).select_related("student", "subject", "batch")

            # Get unique students
            student_ids = enrollments.values_list("student_id", flat=True).distinct()
            students = Student.objects.filter(
                student_id__in=student_ids
            ).select_related("department")

            # Serialize data
            students_data = []
            for student in students:
                students_data.append(
                    {
                        "student_id": student.student_id,
                        "student_roll_no": student.roll_number or student.student_id,
                        "student_name": student.name,
                        "department_id": student.department_id,
                        "current_semester": student.current_semester,
                        "batch_id": student.batch_id
                        if hasattr(student, "batch_id")
                        else None,
                    }
                )

            enrollments_data = []
            for enrollment in enrollments:
                # Determine if core or elective
                is_core = (
                    enrollment.student.department_id == enrollment.subject.department_id
                )

                enrollments_data.append(
                    {
                        "enrollment_id": str(enrollment.enrollment_id),
                        "student_id": enrollment.student.student_id,
                        "student_name": enrollment.student.name,
                        "student_roll_no": enrollment.student.roll_number
                        or enrollment.student.student_id,
                        "subject_id": enrollment.subject.subject_id,
                        "subject_code": enrollment.subject.subject_code,
                        "subject_name": enrollment.subject.subject_name,
                        "department_id": enrollment.subject.department_id,
                        "is_core": is_core,
                        "is_elective": not is_core,
                    }
                )

            logger.info(
                f"Fetched {len(students_data)} students, {len(enrollments_data)} enrollments for {department_id}, Sem {semester}"
            )

            return Response(
                {
                    "students": students_data,
                    "enrollments": enrollments_data,
                    "total_students": len(students_data),
                    "total_enrollments": len(enrollments_data),
                }
            )

        except Exception as e:
            logger.error(
                f"Failed to fetch student enrollments: {str(e)}", exc_info=True
            )
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TimetableEnrollmentViewSet(viewsets.ViewSet):
    """
    Subject enrollment summaries for timetable generation
    Aggregates enrollments by subject with cross-department tracking
    """

    permission_classes = [IsAuthenticated]

    def list(self, request):
        """
        GET /api/v1/timetable/enrollments/
        ?department_id={dept}&semester={sem}&academic_year={year}&include_cross_dept=true

        Returns subject enrollment summaries with student lists
        department_id is optional - if omitted, returns all departments (NEP 2020)
        """
        department_id = request.query_params.get("department_id")
        semester = request.query_params.get("semester")
        academic_year = request.query_params.get("academic_year")
        include_cross_dept = (
            request.query_params.get("include_cross_dept", "false").lower() == "true"
        )

        if not all([semester, academic_year]):
            return Response(
                {"error": "semester and academic_year are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            semester = int(semester)

            # Build enrollment filter - department_id is optional for organization-wide queries
            enrollment_filter = Q(
                semester=semester, academic_year=academic_year, is_active=True
            )
            if department_id:
                enrollment_filter &= Q(subject__department_id=department_id)

            enrollments = SubjectEnrollment.objects.filter(
                enrollment_filter
            ).select_related("student", "subject", "subject__department")

            # Group by subject
            subject_map = {}
            cross_dept_summary = {}

            for enrollment in enrollments:
                subject_id = enrollment.subject.subject_id
                student_dept = enrollment.student.department_id

                if subject_id not in subject_map:
                    subject_map[subject_id] = {
                        "subject_id": subject_id,
                        "subject_code": enrollment.subject.subject_code,
                        "subject_name": enrollment.subject.subject_name,
                        "subject_type": enrollment.subject.subject_type,
                        "department_id": enrollment.subject.department_id,
                        "department_name": enrollment.subject.department.dept_name
                        if hasattr(enrollment.subject, "department")
                        else enrollment.subject.department_id,
                        "student_ids": [],
                        "enrolled_students_count": 0,
                        "total_enrolled": 0,
                        "core_enrolled": 0,
                        "elective_enrolled": 0,
                        "cross_dept_enrolled": 0,
                        "is_cross_department": False,
                    }

                subject_map[subject_id]["student_ids"].append(
                    enrollment.student.student_id
                )
                subject_map[subject_id]["enrolled_students_count"] += 1
                subject_map[subject_id]["total_enrolled"] += 1

                # Track core vs elective enrollments
                is_core = student_dept == enrollment.subject.department_id
                if is_core:
                    subject_map[subject_id]["core_enrolled"] += 1
                else:
                    subject_map[subject_id]["elective_enrolled"] += 1

                # Track cross-department enrollments
                if student_dept != enrollment.subject.department_id:
                    subject_map[subject_id]["is_cross_department"] = True
                    subject_map[subject_id]["cross_dept_enrolled"] += 1

                    if student_dept not in cross_dept_summary:
                        cross_dept_summary[student_dept] = {
                            "from_department": student_dept,
                            "student_count": 0,
                            "subjects": [],
                        }
                    cross_dept_summary[student_dept]["student_count"] += 1
                    if subject_id not in cross_dept_summary[student_dept]["subjects"]:
                        cross_dept_summary[student_dept]["subjects"].append(subject_id)

            # Convert to list
            summary = list(subject_map.values())
            cross_dept_list = list(cross_dept_summary.values())

            # Get individual enrollments
            enrollments_data = []
            for enrollment in enrollments:
                is_core = (
                    enrollment.student.department_id == enrollment.subject.department_id
                )
                enrollments_data.append(
                    {
                        "enrollment_id": str(enrollment.enrollment_id),
                        "student_id": enrollment.student.student_id,
                        "student_name": enrollment.student.name,
                        "student_roll_no": enrollment.student.roll_number
                        or enrollment.student.student_id,
                        "subject_id": enrollment.subject.subject_id,
                        "subject_code": enrollment.subject.subject_code,
                        "subject_name": enrollment.subject.subject_name,
                        "department_id": enrollment.subject.department_id,
                        "is_core": is_core,
                        "is_elective": not is_core,
                    }
                )

            logger.info(
                f"Generated summary for {len(summary)} subjects with {len(cross_dept_list)} cross-dept departments"
            )

            return Response(
                {
                    "enrollments": enrollments_data,
                    "summary": summary,
                    "cross_department_summary": cross_dept_list,
                    "total_subjects": len(summary),
                    "total_enrollments": len(enrollments_data),
                }
            )

        except Exception as e:
            logger.error(f"Failed to fetch enrollment summary: {str(e)}", exc_info=True)
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class FacultyByEnrollmentViewSet(viewsets.ViewSet):
    """
    Fetch faculty teaching subjects in a given department/semester
    Includes cross-department faculty

    List-only ViewSet - no detail routes
    """

    permission_classes = [IsAuthenticated]
    # Explicitly disable detail routes by only implementing list()

    def list(self, request):
        """
        GET /api/v1/faculty/by-enrollment/
        ?department_id={dept}&semester={sem}

        Returns all faculty teaching subjects for the given semester
        department_id is optional - if omitted, returns all faculty (NEP 2020)
        """
        department_id = request.query_params.get("department_id")
        semester = request.query_params.get("semester")

        if not semester:
            return Response(
                {"error": "semester is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            semester = int(semester)

            # Build subject filter - department_id is optional for organization-wide queries
            subject_filter = Q(semester=semester)
            if department_id:
                subject_filter &= Q(department_id=department_id)

            subjects = Subject.objects.filter(subject_filter).values_list(
                "subject_id", flat=True
            )

            # Get faculty teaching these subjects or from specified departments
            if department_id:
                faculty = (
                    Faculty.objects.filter(
                        Q(department_id=department_id)
                        | Q(  # Same department
                            subject__subject_id__in=subjects
                        )  # Teaching these subjects
                    )
                    .distinct()
                    .select_related("department")
                )
            else:
                # Organization-wide: get all available faculty
                faculty = (
                    Faculty.objects.filter(is_available=True)
                    .distinct()
                    .select_related("department")
                )

            faculty_data = []
            for fac in faculty:
                faculty_data.append(
                    {
                        "faculty_id": fac.faculty_id,
                        "faculty_name": fac.faculty_name,
                        "department_id": fac.department_id,
                        "department_name": fac.department.dept_name
                        if hasattr(fac, "department")
                        else fac.department_id,
                        "max_teaching_hours_per_week": fac.max_teaching_hours_per_week,
                        "specialization": fac.specialization,
                    }
                )

            logger.info(
                f"Fetched {len(faculty_data)} faculty for {department_id}, Sem {semester}"
            )

            return Response(faculty_data)

        except Exception as e:
            logger.error(f"Failed to fetch faculty: {str(e)}", exc_info=True)
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
