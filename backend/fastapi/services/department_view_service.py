"""
Department View Service - Enterprise Multi-Department Timetable Views
Provides filtered views for department heads, registrars, and coordinators
"""
import logging
from typing import List, Dict, Optional
from collections import defaultdict
from datetime import datetime
from models.timetable_models import (
    TimetableEntry, DepartmentStats, CrossEnrollmentEntry,
    FacultySchedule, ConflictAlert, DepartmentTimetableView,
    UniversityDashboard, Course, Faculty, Student
)

logger = logging.getLogger(__name__)


class DepartmentViewService:
    """Service for generating department-specific views of master timetable"""
    
    def __init__(self, timetable_entries: List[TimetableEntry], 
                 courses: List[Course], 
                 faculty: List[Faculty],
                 students: List[Student]):
        self.timetable_entries = timetable_entries
        self.courses = {c.course_id: c for c in courses}
        self.faculty = {f.faculty_id: f for f in faculty}
        self.students = {s.student_id: s for s in students}
        
        # Build indexes
        self._build_indexes()
    
    def _build_indexes(self):
        """Build fast lookup indexes"""
        self.entries_by_course = defaultdict(list)
        self.entries_by_faculty = defaultdict(list)
        self.entries_by_department = defaultdict(list)
        
        for entry in self.timetable_entries:
            self.entries_by_course[entry.course_id].append(entry)
            self.entries_by_faculty[entry.faculty_id].append(entry)
            
            # Get department from course
            if entry.course_id in self.courses:
                dept_id = self.courses[entry.course_id].department_id
                self.entries_by_department[dept_id].append(entry)
    
    def get_department_view(self, department_id: str, semester: int, 
                           academic_year: str) -> DepartmentTimetableView:
        """Get complete department view"""
        logger.info(f"Generating department view for {department_id}")
        
        # Get department stats
        stats = self._compute_department_stats(department_id)
        
        # Get own courses
        own_courses = self.entries_by_department.get(department_id, [])
        
        # Get cross-enrollment data
        cross_enrollment = self._compute_cross_enrollment(department_id)
        
        # Get faculty schedules
        faculty_schedules = self._compute_faculty_schedules(department_id)
        
        # Detect conflicts
        conflicts = self._detect_conflicts(department_id)
        
        return DepartmentTimetableView(
            department_id=department_id,
            department_name=f"Department {department_id}",
            semester=semester,
            academic_year=academic_year,
            stats=stats,
            own_courses=own_courses,
            cross_enrollment=cross_enrollment,
            faculty_schedules=faculty_schedules,
            conflicts=conflicts,
            last_updated=datetime.now().isoformat()
        )
    
    def _compute_department_stats(self, department_id: str) -> DepartmentStats:
        """Compute department statistics"""
        dept_courses = [c for c in self.courses.values() if c.department_id == department_id]
        dept_faculty = [f for f in self.faculty.values() if f.department_id == department_id]
        dept_students = [s for s in self.students.values() if s.department_id == department_id]
        
        scheduled_courses = len(set(e.course_id for e in self.entries_by_department.get(department_id, [])))
        
        # Cross-enrollment counts
        cross_out = 0
        cross_in = 0
        
        for student in dept_students:
            for course_id in student.enrolled_course_ids:
                if course_id in self.courses:
                    course_dept = self.courses[course_id].department_id
                    if course_dept != department_id:
                        cross_out += 1
        
        for course in dept_courses:
            for student_id in course.student_ids:
                if student_id in self.students:
                    student_dept = self.students[student_id].department_id
                    if student_dept != department_id:
                        cross_in += 1
        
        # Faculty utilization
        total_hours = sum(len(self.entries_by_faculty.get(f.faculty_id, [])) for f in dept_faculty)
        max_hours = sum(f.max_hours_per_week for f in dept_faculty)
        faculty_util = (total_hours / max_hours * 100) if max_hours > 0 else 0
        
        return DepartmentStats(
            department_id=department_id,
            department_name=f"Department {department_id}",
            total_courses=len(dept_courses),
            scheduled_courses=scheduled_courses,
            pending_courses=len(dept_courses) - scheduled_courses,
            total_faculty=len(dept_faculty),
            active_faculty=len([f for f in dept_faculty if self.entries_by_faculty.get(f.faculty_id)]),
            total_students=len(dept_students),
            cross_enrollment_out=cross_out,
            cross_enrollment_in=cross_in,
            room_utilization=0.0,
            faculty_utilization=faculty_util
        )
    
    def _compute_cross_enrollment(self, department_id: str) -> List[CrossEnrollmentEntry]:
        """Compute cross-department enrollment"""
        dept_courses = [c for c in self.courses.values() if c.department_id == department_id]
        cross_entries = []
        
        for course in dept_courses:
            external_depts = defaultdict(int)
            own_count = 0
            
            for student_id in course.student_ids:
                if student_id in self.students:
                    student_dept = self.students[student_id].department_id
                    if student_dept == department_id:
                        own_count += 1
                    else:
                        external_depts[student_dept] += 1
            
            external_count = sum(external_depts.values())
            
            if external_count > 0:
                conflict_potential = "low"
                if external_count > 50:
                    conflict_potential = "high"
                elif external_count > 20:
                    conflict_potential = "medium"
                
                cross_entries.append(CrossEnrollmentEntry(
                    course_id=course.course_id,
                    course_code=course.course_code,
                    course_name=course.course_name,
                    offering_department=department_id,
                    total_enrolled=len(course.student_ids),
                    own_department_count=own_count,
                    external_count=external_count,
                    external_departments=dict(external_depts),
                    conflict_potential=conflict_potential,
                    conflicting_courses=[]
                ))
        
        return cross_entries
    
    def _compute_faculty_schedules(self, department_id: str) -> List[FacultySchedule]:
        """Compute faculty schedules"""
        dept_faculty = [f for f in self.faculty.values() if f.department_id == department_id]
        schedules = []
        
        for faculty_member in dept_faculty:
            entries = self.entries_by_faculty.get(faculty_member.faculty_id, [])
            weekly_hours = len(entries)
            max_hours = faculty_member.max_hours_per_week
            
            if weekly_hours == 0:
                load_status = "underload"
            elif weekly_hours > max_hours:
                load_status = "overload"
            elif weekly_hours == max_hours:
                load_status = "full"
            else:
                load_status = "normal"
            
            courses = list(set(e.course_code for e in entries))
            
            schedules.append(FacultySchedule(
                faculty_id=faculty_member.faculty_id,
                faculty_name=faculty_member.faculty_name,
                department_id=department_id,
                weekly_hours=weekly_hours,
                max_hours=max_hours,
                courses=courses,
                load_status=load_status,
                schedule_entries=entries
            ))
        
        return schedules
    
    def _detect_conflicts(self, department_id: str) -> List[ConflictAlert]:
        """Detect conflicts for department"""
        conflicts = []
        
        dept_students = [s for s in self.students.values() if s.department_id == department_id]
        
        for student in dept_students:
            student_entries = [e for e in self.timetable_entries if student.student_id in e.student_ids]
            
            time_slots = defaultdict(list)
            for entry in student_entries:
                key = (entry.day, entry.start_time)
                time_slots[key].append(entry)
            
            for (day, time), entries in time_slots.items():
                if len(entries) > 1:
                    conflicts.append(ConflictAlert(
                        conflict_id=f"student_{student.student_id}_{day}_{time}",
                        conflict_type="student",
                        severity="high",
                        description=f"Student {student.student_name} has overlapping courses",
                        affected_courses=[e.course_code for e in entries],
                        affected_entities=[student.student_id],
                        suggested_resolution="Reschedule one of the courses",
                        timestamp=datetime.now().isoformat()
                    ))
        
        dept_faculty = [f for f in self.faculty.values() if f.department_id == department_id]
        
        for faculty_member in dept_faculty:
            entries = self.entries_by_faculty.get(faculty_member.faculty_id, [])
            
            if len(entries) > faculty_member.max_hours_per_week:
                conflicts.append(ConflictAlert(
                    conflict_id=f"faculty_{faculty_member.faculty_id}_overload",
                    conflict_type="faculty",
                    severity="medium",
                    description=f"Faculty {faculty_member.faculty_name} is overloaded ({len(entries)} > {faculty_member.max_hours_per_week} hours)",
                    affected_courses=[e.course_code for e in entries],
                    affected_entities=[faculty_member.faculty_id],
                    suggested_resolution="Redistribute courses or increase max hours",
                    timestamp=datetime.now().isoformat()
                ))
        
        return conflicts
    
    def get_university_dashboard(self) -> UniversityDashboard:
        """Get registrar's university-wide dashboard"""
        logger.info("Generating university dashboard")
        
        departments = set(c.department_id for c in self.courses.values())
        dept_stats = [self._compute_department_stats(dept_id) for dept_id in departments]
        
        total_conflicts = sum(len(self._detect_conflicts(dept_id)) for dept_id in departments)
        
        return UniversityDashboard(
            total_departments=len(departments),
            total_courses=len(self.courses),
            total_faculty=len(self.faculty),
            total_students=len(self.students),
            total_rooms=0,
            scheduled_courses=len(set(e.course_id for e in self.timetable_entries)),
            pending_courses=len(self.courses) - len(set(e.course_id for e in self.timetable_entries)),
            overall_faculty_utilization=sum(s.faculty_utilization for s in dept_stats) / len(dept_stats) if dept_stats else 0,
            overall_room_utilization=0.0,
            total_conflicts=total_conflicts,
            critical_conflicts=0,
            department_stats=dept_stats,
            recent_alerts=[]
        )
