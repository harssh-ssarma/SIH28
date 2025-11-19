from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .bulk_enrollment_views import BulkEnrollmentViewSet
from .enrollment_views import (
    EnrollmentCacheViewSet,
    FacultyByEnrollmentViewSet,
    StudentEnrollmentViewSet,
    TimetableEnrollmentViewSet,
)
from .generation_views import GenerationJobViewSet
from .timetable_views import (
    FixedSlotViewSet,
    ShiftViewSet,
    TimetableVariantViewSet,
    TimetableWorkflowViewSet,
)
from .views import (  # AttendanceViewSet - Old attendance system, replaced by attendance_urls
    BatchViewSet,
    ClassroomViewSet,
    CourseViewSet,
    DepartmentViewSet,
    FacultyViewSet,
    LabViewSet,
    StudentViewSet,
    SubjectViewSet,
    TimetableSlotViewSet,
    TimetableViewSet,
    UserViewSet,
    current_user_view,
    dashboard_stats_view,
    login_view,
    logout_view,
    refresh_token_view,
)

router = DefaultRouter()
router.register(r"users", UserViewSet)
router.register(r"departments", DepartmentViewSet)
router.register(
    r"courses", CourseViewSet, basename="course"
)  # CourseViewSet is an alias for ProgramViewSet
router.register(
    r"programs", CourseViewSet, basename="program"
)  # Same ViewSet, different URL
router.register(r"subjects", SubjectViewSet)
router.register(r"faculty", FacultyViewSet)
router.register(r"students", StudentViewSet)
router.register(r"batches", BatchViewSet)
router.register(r"classrooms", ClassroomViewSet)
router.register(r"labs", LabViewSet, basename="lab")  # Labs now use Classroom model
router.register(r"timetables", TimetableViewSet)
router.register(r"timetable-slots", TimetableSlotViewSet)
# Old attendance ViewSet - commented out in favor of new attendance system
# router.register(r"attendance", AttendanceViewSet)
router.register(r"generation-jobs", GenerationJobViewSet, basename="generation-job")

# New timetable workflow routes
router.register(
    r"timetable-variants", TimetableVariantViewSet, basename="timetable-variant"
)
router.register(
    r"timetable-workflow", TimetableWorkflowViewSet, basename="timetable-workflow"
)
router.register(r"fixed-slots", FixedSlotViewSet, basename="fixed-slot")
router.register(r"shifts", ShiftViewSet, basename="shift")

# NEP 2020 Enrollment routes
router.register(
    r"timetable/enrollment-cache", EnrollmentCacheViewSet, basename="enrollment-cache"
)
router.register(
    r"students/enrollments", StudentEnrollmentViewSet, basename="student-enrollments"
)
router.register(
    r"timetable/enrollments",
    TimetableEnrollmentViewSet,
    basename="timetable-enrollments",
)
router.register(
    r"enrollment-faculty", FacultyByEnrollmentViewSet, basename="enrollment-faculty"
)

# Bulk Enrollment routes
router.register(r"enrollments/bulk", BulkEnrollmentViewSet, basename="bulk-enrollment")

urlpatterns = [
    path("", include(router.urls)),
    # New Attendance management routes (takes priority)
    path("attendance/", include("academics.attendance_urls")),
    # Auth endpoints - CSRF exempt via APICSRFExemptMiddleware
    path("auth/login/", login_view, name="login"),
    path("auth/login", login_view, name="login-no-slash"),
    path("auth/logout/", logout_view, name="logout"),
    path("auth/logout", logout_view, name="logout-no-slash"),
    path("auth/refresh/", refresh_token_view, name="refresh-token"),
    path("auth/refresh", refresh_token_view, name="refresh-token-no-slash"),
    path("auth/me/", current_user_view, name="current-user"),
    path("auth/me", current_user_view, name="current-user-no-slash"),
    # Dashboard stats endpoint
    path("dashboard/stats/", dashboard_stats_view, name="dashboard-stats"),
    path("dashboard/stats", dashboard_stats_view, name="dashboard-stats-no-slash"),
]
