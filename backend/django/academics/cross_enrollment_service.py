"""
Cross-Enrollment Tracking Service
NEP 2020 compliance - track students taking courses across departments
"""
from typing import List, Dict
from collections import defaultdict


class CrossEnrollmentService:
    """Track cross-department enrollments"""
    
    @staticmethod
    def analyze_cross_enrollment(timetable_entries: List[Dict], department_id: str) -> Dict:
        """Analyze cross-enrollment for a department"""
        
        # Separate entries by department
        our_courses = []
        other_courses = []
        
        for entry in timetable_entries:
            dept = entry.get('department_id', '')
            if dept == department_id:
                our_courses.append(entry)
            else:
                other_courses.append(entry)
        
        return {
            'department_id': department_id,
            'our_courses': our_courses,
            'other_courses': other_courses,
            'our_courses_count': len(our_courses),
            'other_courses_count': len(other_courses),
            'cross_enrollment_ratio': len(other_courses) / len(timetable_entries) if timetable_entries else 0
        }
    
    @staticmethod
    def get_outgoing_students(timetable_entries: List[Dict], department_id: str) -> Dict:
        """Get students from our department taking other departments' courses"""
        
        # Group by target department
        by_dept = defaultdict(list)
        
        for entry in timetable_entries:
            dept = entry.get('department_id', '')
            if dept != department_id:
                by_dept[dept].append(entry)
        
        outgoing = []
        for dept, entries in by_dept.items():
            outgoing.append({
                'target_department': dept,
                'courses': [{'code': e.get('subject_code'), 'name': e.get('subject_name')} for e in entries],
                'course_count': len(entries)
            })
        
        return {
            'department_id': department_id,
            'outgoing_enrollments': outgoing,
            'total_outgoing': sum(len(e['courses']) for e in outgoing),
            'departments_count': len(outgoing)
        }
    
    @staticmethod
    def get_incoming_students(timetable_entries: List[Dict], department_id: str) -> Dict:
        """Get students from other departments taking our courses"""
        
        # Get our courses
        our_courses = [e for e in timetable_entries if e.get('department_id') == department_id]
        
        # Group by source department (from batch_name or other indicator)
        by_source = defaultdict(list)
        
        for entry in our_courses:
            batch = entry.get('batch_name', '')
            # If batch indicates different department, it's incoming
            if batch and batch != department_id:
                by_source[batch].append(entry)
        
        incoming = []
        for source, entries in by_source.items():
            incoming.append({
                'source_department': source,
                'courses': [{'code': e.get('subject_code'), 'name': e.get('subject_name')} for e in entries],
                'course_count': len(entries)
            })
        
        return {
            'department_id': department_id,
            'incoming_enrollments': incoming,
            'total_incoming': sum(len(e['courses']) for e in incoming),
            'departments_count': len(incoming)
        }
    
    @staticmethod
    def get_cross_enrollment_summary(timetable_entries: List[Dict]) -> Dict:
        """Get university-wide cross-enrollment summary"""
        
        # Get all departments
        departments = set(e.get('department_id', '') for e in timetable_entries if e.get('department_id'))
        
        summary = []
        for dept in departments:
            dept_entries = [e for e in timetable_entries if e.get('department_id') == dept]
            
            # Count cross-enrollments (simplified)
            cross_count = len([e for e in timetable_entries if e.get('batch_name') != dept and e.get('department_id') == dept])
            
            summary.append({
                'department_id': dept,
                'total_courses': len(dept_entries),
                'cross_enrollment_count': cross_count,
                'cross_enrollment_percentage': (cross_count / len(dept_entries) * 100) if dept_entries else 0
            })
        
        return {
            'total_departments': len(departments),
            'departments': summary,
            'total_entries': len(timetable_entries)
        }
