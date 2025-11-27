"""
Department View Service - Filter timetable by department
Uses Django ORM for database queries
"""
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


class DepartmentViewService:
    """Service for filtering timetable entries by department"""
    
    @staticmethod
    def filter_by_department(timetable_entries, department_id):
        """Filter timetable entries to show only courses from specified department"""
        if department_id == 'all':
            return timetable_entries
        
        filtered = [
            entry for entry in timetable_entries 
            if entry.get('department_id') == department_id
        ]
        
        logger.info(f"Filtered {len(timetable_entries)} entries to {len(filtered)} for department {department_id}")
        return filtered
    
    @staticmethod
    def get_department_stats(timetable_entries):
        """Get statistics grouped by department"""
        dept_stats = defaultdict(lambda: {
            'total_classes': 0,
            'unique_subjects': set(),
            'unique_faculty': set(),
            'unique_rooms': set()
        })
        
        for entry in timetable_entries:
            dept_id = entry.get('department_id', 'Unknown')
            dept_stats[dept_id]['total_classes'] += 1
            dept_stats[dept_id]['unique_subjects'].add(entry.get('subject_code'))
            dept_stats[dept_id]['unique_faculty'].add(entry.get('faculty_name'))
            dept_stats[dept_id]['unique_rooms'].add(entry.get('room_number'))
        
        # Convert sets to counts
        result = {}
        for dept_id, stats in dept_stats.items():
            result[dept_id] = {
                'department_id': dept_id,
                'total_classes': stats['total_classes'],
                'unique_subjects': len(stats['unique_subjects']),
                'unique_faculty': len(stats['unique_faculty']),
                'unique_rooms': len(stats['unique_rooms'])
            }
        
        return result
