"""
Timetable Data Models - NEP 2020 Compliant
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from enum import Enum


class CourseType(str, Enum):
    LECTURE = "lecture"
    LAB = "lab"
    TUTORIAL = "tutorial"
    SEMINAR = "seminar"


class Course(BaseModel):
    """Course Characterization (NEP 2020-Specific)"""
    course_id: str
    course_code: str
    course_name: str
    faculty_id: str = ""
    student_ids: List[str] = Field(default_factory=list)
    batch_ids: List[str] = Field(default_factory=list)
    duration: int = Field(default=3, ge=1, le=10, description="Sessions per week")
    type: Optional[str] = None
    credits: int = Field(default=3, ge=1, le=10, description="NEP 2020 credit structure")
    required_features: List[str] = Field(default_factory=list)
    department_id: str
    subject_type: str = Field(default="core", description="core, elective, or open_elective")
    
    @property
    def dept_id(self) -> str:
        """Alias for department_id"""
        return self.department_id


class Faculty(BaseModel):
    """Faculty Member"""
    faculty_id: str
    faculty_name: str
    faculty_code: str = ""
    department_id: str
    max_hours_per_week: int = Field(default=18, description="Max hours per week")
    specialization: str = ""
    available_slots: List[int] = Field(default_factory=list)
    preferred_slots: Dict[int, float] = Field(default_factory=dict)


class Room(BaseModel):
    """Room with heterogeneous capacities and features"""
    room_id: str
    room_code: str
    room_name: str
    room_type: str = "classroom"
    capacity: int
    features: List[str] = Field(default_factory=list)
    dept_id: Optional[str] = None  # Department constraint for room allocation
    department_id: Optional[str] = None  # Alias for dept_id


class TimeSlot(BaseModel):
    """Time Slot - NEP 2020: Universal time grid for centralized university-wide scheduling
    
    All departments share the SAME 54 time slots (9 periods × 6 days).
    This ensures students can take courses across departments without time conflicts.
    
    Example: ALL courses scheduled at "Monday Period 1" use slot_id=0, regardless of department.
    Wall-clock synchronization is automatic - students physically can't attend two classes
    at Monday 9:00-10:00 AM, even if they're in different departments.
    """
    slot_id: str
    day_of_week: str
    day: int = Field(..., ge=0, le=5, description="0=Mon, 5=Sat")
    period: int = Field(..., ge=0, le=9, description="Period number")
    start_time: str
    end_time: str
    slot_name: str = ""


class Student(BaseModel):
    """Student"""
    student_id: str
    student_name: str
    enrollment_number: str
    department_id: str
    semester: int
    batch_id: str = ""
    enrolled_course_ids: List[str] = Field(default_factory=list)


class Batch(BaseModel):
    """Batch/Section"""
    batch_id: str
    batch_code: str
    batch_name: str
    department_id: str
    semester: int
    total_students: int


class TimetableEntry(BaseModel):
    """Single timetable entry (one session)"""
    course_id: str
    course_code: str
    course_name: str
    faculty_id: str
    room_id: str
    time_slot_id: str
    session_number: int
    day: int
    start_time: str
    end_time: str
    student_ids: List[str]
    batch_ids: List[str]


class GenerationRequest(BaseModel):
    """
    Request to generate timetable

    ENTERPRISE PATTERN: job_id passed from Django
    - Django creates job_id and workflow record FIRST
    - Django calls FastAPI with this request including job_id
    - FastAPI uses Django's job_id (not generating its own)
    """
    job_id: Optional[str] = None  # Django's job_id (if Django-first architecture)
    organization_id: str
    campus_id: Optional[str] = None
    school_id: Optional[str] = None
    department_id: str
    batch_ids: List[str]
    semester: int
    academic_year: str
    include_electives: bool = True
    user_id: Optional[str] = None  # Make optional for backward compatibility


class GenerationResponse(BaseModel):
    """Response after initiating generation"""
    job_id: str
    status: str
    message: str
    estimated_time_seconds: int


class GenerationStatistics(BaseModel):
    """Generation statistics"""
    total_courses: int
    total_sessions: int
    scheduled_sessions: int
    total_clusters: int
    total_students: int
    total_faculty: int
    total_rooms: int
    total_time_slots: int
    generation_time_seconds: float
    stage1_time: float
    stage2_time: float
    stage3_time: float


class QualityMetrics(BaseModel):
    """Quality metrics"""
    hard_constraint_violations: int
    faculty_conflicts: int
    room_conflicts: int
    student_conflicts: int
    compactness_score: float
    workload_balance_score: float
    room_utilization: float


class TimetableResult(BaseModel):
    """Complete timetable result"""
    job_id: str
    timetable_entries: List[TimetableEntry]
    statistics: GenerationStatistics
    metrics: QualityMetrics
    generation_time_seconds: float


# ============================================================================
# DEPARTMENT VIEW MODELS (Enterprise Features)
# ============================================================================

class DepartmentStats(BaseModel):
    """Department-level statistics"""
    department_id: str
    department_name: str
    total_courses: int
    scheduled_courses: int
    pending_courses: int
    total_faculty: int
    active_faculty: int
    total_students: int
    cross_enrollment_out: int  # Dept students taking other dept courses
    cross_enrollment_in: int   # Other students taking dept courses
    room_utilization: float
    faculty_utilization: float


class CrossEnrollmentEntry(BaseModel):
    """Cross-department enrollment tracking"""
    course_id: str
    course_code: str
    course_name: str
    offering_department: str
    total_enrolled: int
    own_department_count: int
    external_count: int
    external_departments: Dict[str, int]  # dept_id -> count
    conflict_potential: str  # "high", "medium", "low"
    conflicting_courses: List[str] = Field(default_factory=list)


class FacultySchedule(BaseModel):
    """Faculty schedule summary"""
    faculty_id: str
    faculty_name: str
    department_id: str
    weekly_hours: int
    max_hours: int
    courses: List[str]
    load_status: str  # "normal", "full", "overload", "underload"
    schedule_entries: List[TimetableEntry] = Field(default_factory=list)


class ConflictAlert(BaseModel):
    """Conflict detection alert"""
    conflict_id: str
    conflict_type: str  # "student", "faculty", "room"
    severity: str  # "critical", "high", "medium", "low"
    description: str
    affected_courses: List[str]
    affected_entities: List[str]  # student_ids, faculty_ids, or room_ids
    suggested_resolution: Optional[str] = None
    timestamp: str


class DepartmentTimetableView(BaseModel):
    """Complete department view of timetable"""
    department_id: str
    department_name: str
    semester: int
    academic_year: str
    stats: DepartmentStats
    own_courses: List[TimetableEntry]
    cross_enrollment: List[CrossEnrollmentEntry]
    faculty_schedules: List[FacultySchedule]
    conflicts: List[ConflictAlert]
    last_updated: str


class UniversityDashboard(BaseModel):
    """Registrar's university-wide dashboard"""
    total_departments: int
    total_courses: int
    total_faculty: int
    total_students: int
    total_rooms: int
    scheduled_courses: int
    pending_courses: int
    overall_faculty_utilization: float
    overall_room_utilization: float
    total_conflicts: int
    critical_conflicts: int
    department_stats: List[DepartmentStats]
    recent_alerts: List[ConflictAlert]
