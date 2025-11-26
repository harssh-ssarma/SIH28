"""
Department Preference Service - Hybrid Governance Model
Allows departments to submit preferences before centralized generation
"""
import logging
from typing import List, Dict, Optional
from pydantic import BaseModel
from datetime import datetime

logger = logging.getLogger(__name__)


class CoursePreference(BaseModel):
    """Department preference for a course"""
    course_id: str
    preferred_time_slots: List[str] = []  # Morning, Afternoon, Evening
    preferred_days: List[int] = []  # 0=Mon, 1=Tue, etc.
    required_room_type: Optional[str] = None  # Lab, Auditorium, Classroom
    min_room_capacity: Optional[int] = None
    consecutive_sessions: bool = False  # Prefer consecutive time slots
    notes: Optional[str] = None


class DepartmentPreferences(BaseModel):
    """Complete department preferences"""
    department_id: str
    semester: int
    academic_year: str
    course_preferences: List[CoursePreference]
    general_notes: Optional[str] = None
    submitted_at: str
    submitted_by: str


class DepartmentPreferenceService:
    """Service for managing department preferences"""
    
    def __init__(self, redis_client=None):
        self.redis_client = redis_client
    
    def submit_preferences(self, preferences: DepartmentPreferences) -> Dict:
        """Submit department preferences for upcoming semester"""
        logger.info(f"Submitting preferences for {preferences.department_id}")
        
        # Validate preferences
        validation = self._validate_preferences(preferences)
        if not validation['valid']:
            return {
                'success': False,
                'errors': validation['errors']
            }
        
        # Store in Redis
        if self.redis_client:
            key = f"dept_prefs:{preferences.department_id}:{preferences.semester}"
            self.redis_client.setex(
                key,
                86400 * 30,  # 30 days
                preferences.json()
            )
        
        logger.info(f"Stored {len(preferences.course_preferences)} course preferences")
        return {
            'success': True,
            'department_id': preferences.department_id,
            'courses_count': len(preferences.course_preferences),
            'submitted_at': preferences.submitted_at
        }
    
    def get_preferences(self, department_id: str, semester: int) -> Optional[DepartmentPreferences]:
        """Get department preferences"""
        if not self.redis_client:
            return None
        
        key = f"dept_prefs:{department_id}:{semester}"
        data = self.redis_client.get(key)
        
        if data:
            return DepartmentPreferences.parse_raw(data)
        return None
    
    def get_all_preferences(self, semester: int) -> List[DepartmentPreferences]:
        """Get all department preferences for semester"""
        if not self.redis_client:
            return []
        
        pattern = f"dept_prefs:*:{semester}"
        keys = self.redis_client.keys(pattern)
        
        preferences = []
        for key in keys:
            data = self.redis_client.get(key)
            if data:
                preferences.append(DepartmentPreferences.parse_raw(data))
        
        return preferences
    
    def apply_preferences_to_generation(self, preferences: List[DepartmentPreferences]) -> Dict:
        """
        Apply department preferences to generation config
        Returns modified config with preferences integrated
        """
        config = {
            'time_slot_weights': {},
            'room_type_requirements': {},
            'consecutive_requirements': []
        }
        
        for dept_prefs in preferences:
            for course_pref in dept_prefs.course_preferences:
                # Time slot preferences
                if course_pref.preferred_time_slots:
                    config['time_slot_weights'][course_pref.course_id] = {
                        'slots': course_pref.preferred_time_slots,
                        'weight': 2.0  # 2x weight for preferred slots
                    }
                
                # Room type requirements
                if course_pref.required_room_type:
                    config['room_type_requirements'][course_pref.course_id] = course_pref.required_room_type
                
                # Consecutive sessions
                if course_pref.consecutive_sessions:
                    config['consecutive_requirements'].append(course_pref.course_id)
        
        logger.info(f"Applied preferences from {len(preferences)} departments")
        return config
    
    def _validate_preferences(self, preferences: DepartmentPreferences) -> Dict:
        """Validate department preferences"""
        errors = []
        
        # Check for duplicate course IDs
        course_ids = [p.course_id for p in preferences.course_preferences]
        if len(course_ids) != len(set(course_ids)):
            errors.append("Duplicate course IDs found")
        
        # Validate time slots
        valid_time_slots = ['Morning', 'Afternoon', 'Evening']
        for pref in preferences.course_preferences:
            for slot in pref.preferred_time_slots:
                if slot not in valid_time_slots:
                    errors.append(f"Invalid time slot: {slot}")
        
        # Validate days
        for pref in preferences.course_preferences:
            for day in pref.preferred_days:
                if day < 0 or day > 6:
                    errors.append(f"Invalid day: {day}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def get_preference_statistics(self, semester: int) -> Dict:
        """Get statistics on submitted preferences"""
        all_prefs = self.get_all_preferences(semester)
        
        stats = {
            'total_departments': len(all_prefs),
            'total_courses': sum(len(p.course_preferences) for p in all_prefs),
            'departments_submitted': [p.department_id for p in all_prefs],
            'submission_dates': [p.submitted_at for p in all_prefs],
            'preference_breakdown': {
                'time_slot_prefs': 0,
                'room_type_prefs': 0,
                'consecutive_prefs': 0
            }
        }
        
        for prefs in all_prefs:
            for course_pref in prefs.course_preferences:
                if course_pref.preferred_time_slots:
                    stats['preference_breakdown']['time_slot_prefs'] += 1
                if course_pref.required_room_type:
                    stats['preference_breakdown']['room_type_prefs'] += 1
                if course_pref.consecutive_sessions:
                    stats['preference_breakdown']['consecutive_prefs'] += 1
        
        return stats
