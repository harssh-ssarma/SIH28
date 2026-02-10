"""
Signal Extractor - Batch Feature Computation
Following Google/Meta standards: Offline batch processing
Executive verdict: "Runs once per semester, once per night, or as offline batch"

Role: Extract features from historical data (OFFLINE)
NOT: Run during scheduling, run in real-time, block scheduling
"""
import logging
import json
from typing import Dict, List
from pathlib import Path
from datetime import datetime
from collections import defaultdict, Counter

logger = logging.getLogger(__name__)


class SignalExtractor:
    """
    Batch signal extractor for offline feature computation
    
    When: Once per semester, nightly batch, or manual trigger
    NOT: During scheduling, per request, or in real-time
    
    Output: JSON feature file consumed by ContextFeatureStore
    """
    
    def __init__(self, output_path: str = "data/context_features"):
        self.output_path = Path(output_path)
        self.output_path.mkdir(parents=True, exist_ok=True)
        logger.info("[SignalExtractor] Initialized for batch processing")
    
    def extract_features_from_history(
        self,
        semester_id: str,
        historical_schedules: List[Dict],
        faculty_feedback: List[Dict],
        student_enrollments: List[Dict],
        room_usage: List[Dict]
    ) -> Dict:
        """
        Extract features from historical data (OFFLINE BATCH)
        
        This runs:
        - End of semester
        - Nightly batch job
        - Manual admin trigger
        
        This does NOT run:
        - During scheduling
        - Per HTTP request
        - In real-time
        
        Returns: Feature dictionary to be saved to disk
        """
        logger.info(f"[SignalExtractor] Starting batch extraction for semester {semester_id}")
        
        features = {
            'semester_id': semester_id,
            'extraction_time': datetime.now().isoformat(),
            'last_update': datetime.now().isoformat(),
            'faculty_time_effectiveness': self._extract_faculty_time_patterns(
                historical_schedules, 
                faculty_feedback
            ),
            'course_popularity': self._extract_course_popularity(student_enrollments),
            'student_overload_hotspots': self._extract_overload_hotspots(
                historical_schedules,
                student_enrollments
            ),
            'room_utilization': self._extract_room_utilization(room_usage),
            'co_enrollment_stats': self._extract_co_enrollment(student_enrollments)
        }
        
        # Save to disk
        output_file = self.output_path / f"features_{semester_id}.json"
        with open(output_file, 'w') as f:
            json.dump(features, f, indent=2)
        
        logger.info(f"[SignalExtractor] Features saved to {output_file}")
        logger.info(f"[SignalExtractor] Faculty patterns: {len(features['faculty_time_effectiveness'])}")
        logger.info(f"[SignalExtractor] Course popularity: {len(features['course_popularity'])}")
        
        return features
    
    def _extract_faculty_time_patterns(
        self,
        historical_schedules: List[Dict],
        faculty_feedback: List[Dict]
    ) -> Dict[str, Dict[str, float]]:
        """
        Extract faculty effectiveness by time-of-day
        
        Logic:
        - Aggregate faculty performance metrics per time bucket
        - Normalize to 0.0-1.0 range
        """
        patterns = defaultdict(lambda: defaultdict(list))
        
        # Aggregate feedback scores by time bucket
        for feedback in faculty_feedback:
            faculty_id = feedback.get('faculty_id')
            time_bucket = feedback.get('time_bucket', 'morning')  # morning/midday/evening
            score = feedback.get('effectiveness_score', 0.5)  # 0.0-1.0
            
            if faculty_id:
                patterns[faculty_id][time_bucket].append(score)
        
        # Average scores
        result = {}
        for faculty_id, buckets in patterns.items():
            result[faculty_id] = {
                bucket: sum(scores) / len(scores) if scores else 0.5
                for bucket, scores in buckets.items()
            }
        
        logger.debug(f"[SignalExtractor] Extracted patterns for {len(result)} faculty")
        return result
    
    def _extract_course_popularity(self, student_enrollments: List[Dict]) -> Dict[str, float]:
        """
        Extract course popularity from enrollment trends
        
        Logic:
        - Count enrollments per course
        - Normalize by max enrollment
        """
        enrollment_counts = Counter()
        
        for enrollment in student_enrollments:
            course_id = enrollment.get('course_id')
            if course_id:
                enrollment_counts[course_id] += 1
        
        # Normalize to 0.0-1.0
        max_enrollment = max(enrollment_counts.values()) if enrollment_counts else 1
        popularity = {
            course_id: count / max_enrollment
            for course_id, count in enrollment_counts.items()
        }
        
        logger.debug(f"[SignalExtractor] Extracted popularity for {len(popularity)} courses")
        return popularity
    
    def _extract_overload_hotspots(
        self,
        historical_schedules: List[Dict],
        student_enrollments: List[Dict]
    ) -> Dict[str, List[str]]:
        """
        Extract time slots where students are historically overloaded
        
        Logic:
        - Find time slots with >4 courses per student
        - Mark as hotspots
        """
        hotspots = defaultdict(set)
        
        # Group courses by student and time slot
        student_schedules = defaultdict(lambda: defaultdict(list))
        for schedule in historical_schedules:
            for enrollment in student_enrollments:
                student_id = enrollment.get('student_id')
                course_id = enrollment.get('course_id')
                time_slot = schedule.get(course_id, {}).get('time_slot')
                
                if student_id and time_slot:
                    student_schedules[student_id][time_slot].append(course_id)
        
        # Identify overload slots (>4 courses)
        for student_id, time_slots in student_schedules.items():
            for time_slot, courses in time_slots.items():
                if len(courses) > 4:
                    hotspots[student_id].add(time_slot)
        
        # Convert sets to lists
        result = {sid: list(slots) for sid, slots in hotspots.items()}
        
        logger.debug(f"[SignalExtractor] Found hotspots for {len(result)} students")
        return result
    
    def _extract_room_utilization(self, room_usage: List[Dict]) -> Dict[str, float]:
        """
        Extract room utilization rates
        
        Logic:
        - usage_count / total_slots
        """
        usage_counts = defaultdict(int)
        total_slots = 50  # Assume 50 total slots per semester
        
        for usage in room_usage:
            room_id = usage.get('room_id')
            if room_id:
                usage_counts[room_id] += 1
        
        utilization = {
            room_id: count / total_slots
            for room_id, count in usage_counts.items()
        }
        
        logger.debug(f"[SignalExtractor] Extracted utilization for {len(utilization)} rooms")
        return utilization
    
    def _extract_co_enrollment(self, student_enrollments: List[Dict]) -> Dict[str, Dict[str, float]]:
        """
        Extract co-enrollment statistics (which courses are taken together)
        
        Logic:
        - Find pairs of courses taken by same students
        - Calculate co-enrollment strength
        """
        # Group courses by student
        student_courses = defaultdict(set)
        for enrollment in student_enrollments:
            student_id = enrollment.get('student_id')
            course_id = enrollment.get('course_id')
            if student_id and course_id:
                student_courses[student_id].add(course_id)
        
        # Count co-enrollments
        co_enrollment_counts = defaultdict(int)
        course_total_students = Counter()
        
        for student_id, courses in student_courses.items():
            courses_list = list(courses)
            for i, c1 in enumerate(courses_list):
                course_total_students[c1] += 1
                for c2 in courses_list[i+1:]:
                    key = f"{min(c1, c2)}_{max(c1, c2)}"
                    co_enrollment_counts[key] += 1
        
        # Calculate strength (Jaccard similarity)
        co_enrollment_stats = {}
        for key, count in co_enrollment_counts.items():
            c1, c2 = key.split('_')
            total = course_total_students[c1] + course_total_students[c2]
            strength = (2 * count) / total if total > 0 else 0.0
            co_enrollment_stats[key] = {'strength': strength, 'count': count}
        
        logger.debug(f"[SignalExtractor] Extracted {len(co_enrollment_stats)} co-enrollment pairs")
        return co_enrollment_stats
