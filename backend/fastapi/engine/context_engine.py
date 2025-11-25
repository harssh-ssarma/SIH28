"""
Multi-Dimensional Context Engine (Θ_t, Θ_b, Θ_a, Θ_s, Θ_l)
Provides context-aware weight adjustment for timetable optimization
"""
import numpy as np
import json
import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime, time
from dataclasses import dataclass
from models.timetable_models import Course, Faculty, Student, Room, TimeSlot
from config import settings

logger = logging.getLogger(__name__)


@dataclass
class ContextVector:
    """5-dimensional context vector"""
    temporal: float      # Θ_t: Time-of-day effectiveness
    behavioral: float    # Θ_b: Historical patterns
    academic: float      # Θ_a: Curricular coherence
    social: float        # Θ_s: Peer group cohesion
    spatial: float       # Θ_l: Spatial optimization


class TemporalContext:
    """Θ_t: Temporal Context - Time-of-day preferences and effectiveness patterns"""

    def __init__(self):
        # Time-of-day effectiveness patterns (based on educational research)
        self.effectiveness_patterns = {
            'morning': {'start': 8, 'end': 12, 'multiplier': 0.95},    # High alertness
            'peak': {'start': 10, 'end': 14, 'multiplier': 1.0},       # Peak performance
            'afternoon': {'start': 14, 'end': 17, 'multiplier': 0.85}, # Post-lunch dip
            'evening': {'start': 17, 'end': 20, 'multiplier': 0.75}    # Lower effectiveness
        }

        # Day-of-week patterns
        self.day_effectiveness = {
            'monday': 0.9,     # Monday blues
            'tuesday': 1.0,    # Peak productivity
            'wednesday': 1.0,  # Peak productivity
            'thursday': 0.95,  # Slight decline
            'friday': 0.8,     # TGIF effect
            'saturday': 0.7    # Weekend mode
        }

        # Semester phase awareness
        self.semester_phases = {
            'add_drop': {'weeks': [1, 2], 'stability': 0.6},      # High volatility
            'stable': {'weeks': list(range(3, 13)), 'stability': 1.0},  # Stable period
            'exam_prep': {'weeks': [13, 14, 15], 'stability': 0.8}      # Stress period
        }

    def get_time_effectiveness(self, time_slot: TimeSlot) -> float:
        """Calculate time-of-day effectiveness multiplier"""
        # Handle both string and time object
        if isinstance(time_slot.start_time, str):
            hour = int(time_slot.start_time.split(':')[0])
        else:
            hour = time_slot.start_time.hour

        for period, config in self.effectiveness_patterns.items():
            if config['start'] <= hour < config['end']:
                return config['multiplier']

        return 0.7  # Default for unusual hours

    def get_day_effectiveness(self, day) -> float:
        """Get day-of-week effectiveness"""
        # Handle both int (0-6) and string day
        if isinstance(day, int):
            day_names = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
            day = day_names[day % 7]
        return self.day_effectiveness.get(str(day).lower(), 0.8)

    def get_semester_phase_stability(self, current_week: int) -> float:
        """Get semester phase stability factor"""
        for phase, config in self.semester_phases.items():
            if current_week in config['weeks']:
                return config['stability']
        return 0.8  # Default


class BehavioralContext:
    """Θ_b: Behavioral Context - Historical patterns and effectiveness"""

    def __init__(self):
        # Faculty teaching effectiveness by time slot (learned from historical data)
        self.faculty_effectiveness = {}

        # Student performance correlation with schedule patterns
        self.student_performance_patterns = {}

        # Co-enrollment patterns (which courses students take together)
        self.co_enrollment_matrix = {}

    def update_faculty_effectiveness(self, faculty_id: str, time_slot_id: str, effectiveness: float):
        """Update faculty effectiveness for specific time slot"""
        if faculty_id not in self.faculty_effectiveness:
            self.faculty_effectiveness[faculty_id] = {}
        self.faculty_effectiveness[faculty_id][time_slot_id] = effectiveness

    def get_faculty_effectiveness(self, faculty_id: str, time_slot_id: str) -> float:
        """Get faculty effectiveness for time slot"""
        return self.faculty_effectiveness.get(faculty_id, {}).get(time_slot_id, 0.8)

    def analyze_co_enrollment_patterns(self, courses: List[Course]) -> Dict[str, Dict[str, float]]:
        """Analyze which courses students commonly take together"""
        co_enrollment = {}

        for i, course_i in enumerate(courses):
            co_enrollment[course_i.course_id] = {}

            for j, course_j in enumerate(courses):
                if i != j:
                    # Calculate Jaccard similarity of student sets
                    students_i = set(course_i.student_ids)
                    students_j = set(course_j.student_ids)

                    if len(students_i) > 0 and len(students_j) > 0:
                        intersection = len(students_i & students_j)
                        union = len(students_i | students_j)
                        similarity = intersection / union if union > 0 else 0
                        co_enrollment[course_i.course_id][course_j.course_id] = similarity

        return co_enrollment


class AcademicContext:
    """Θ_a: Academic Context - Curricular coherence and credit balancing"""

    def __init__(self):
        # Prerequisite relationship graph
        self.prerequisite_graph = {}

        # Credit load balancing targets
        self.credit_targets = {
            'min_credits_per_semester': 14,
            'max_credits_per_semester': 26,
            'optimal_credits_per_semester': 20
        }

        # Subject type priorities
        self.subject_type_priorities = {
            'core': 1.0,
            'elective': 0.8,
            'open_elective': 0.6,
            'minor': 0.7,
            'skill_course': 0.5
        }

    def build_prerequisite_graph(self, courses: List[Course]):
        """Build prerequisite relationship graph"""
        for course in courses:
            self.prerequisite_graph[course.course_id] = {
                'prerequisites': getattr(course, 'prerequisite_courses', []) or [],
                'credits': course.credits,
                'subject_type': course.subject_type
            }

    def calculate_curricular_coherence(self, student_schedule: List[str]) -> float:
        """Calculate how well courses fit together academically"""
        if len(student_schedule) < 2:
            return 1.0

        coherence_score = 0.0
        total_pairs = 0

        for i, course_i in enumerate(student_schedule):
            for j, course_j in enumerate(student_schedule[i+1:], start=i+1):
                # Check if courses are related (same department, prerequisite chain, etc.)
                relatedness = self._calculate_course_relatedness(course_i, course_j)
                coherence_score += relatedness
                total_pairs += 1

        return coherence_score / total_pairs if total_pairs > 0 else 1.0

    def _calculate_course_relatedness(self, course_i: str, course_j: str) -> float:
        """Calculate how related two courses are"""
        # Simplified: courses in same department are more related
        # In practice, this would use department codes, prerequisite chains, etc.
        return 0.7  # Default moderate relatedness

    def calculate_credit_balance_score(self, student_credits: int) -> float:
        """Calculate how well student's credit load is balanced"""
        optimal = self.credit_targets['optimal_credits_per_semester']
        min_credits = self.credit_targets['min_credits_per_semester']
        max_credits = self.credit_targets['max_credits_per_semester']

        if min_credits <= student_credits <= max_credits:
            # Within acceptable range, score based on distance from optimal
            distance_from_optimal = abs(student_credits - optimal)
            return max(0.5, 1.0 - (distance_from_optimal / optimal))
        else:
            # Outside acceptable range
            return 0.2


class SocialContext:
    """Θ_s: Social Context - Peer group cohesion and social networks"""

    def __init__(self):
        # Peer group networks (derived from co-enrollment patterns)
        self.peer_networks = {}

        # Departmental identity strength
        self.departmental_cohesion = {}

    def analyze_peer_networks(self, students: Dict[str, Student], courses: List[Course]):
        """Analyze peer group networks from enrollment patterns"""
        # Build student-student similarity matrix based on shared courses
        student_similarity = {}

        for student_id in students.keys():
            student_similarity[student_id] = {}

            # Find courses this student is enrolled in
            student_courses = [c.course_id for c in courses if student_id in c.student_ids]

            for other_student_id in students.keys():
                if student_id != other_student_id:
                    # Find courses other student is enrolled in
                    other_courses = [c.course_id for c in courses if other_student_id in c.student_ids]

                    # Calculate Jaccard similarity
                    shared_courses = set(student_courses) & set(other_courses)
                    total_courses = set(student_courses) | set(other_courses)

                    similarity = len(shared_courses) / len(total_courses) if total_courses else 0
                    student_similarity[student_id][other_student_id] = similarity

        return student_similarity

    def calculate_peer_cohesion_score(self, course_students: List[str], peer_networks: Dict) -> float:
        """Calculate how cohesive the peer group is for a course"""
        if len(course_students) < 2:
            return 1.0

        total_similarity = 0.0
        total_pairs = 0

        for i, student_i in enumerate(course_students):
            for j, student_j in enumerate(course_students[i+1:], start=i+1):
                similarity = peer_networks.get(student_i, {}).get(student_j, 0.0)
                total_similarity += similarity
                total_pairs += 1

        return total_similarity / total_pairs if total_pairs > 0 else 0.5


class SpatialContext:
    """Θ_l: Spatial Context - Room features and inter-building distances"""

    def __init__(self):
        # Building coordinates (for distance calculations)
        self.building_coordinates = {}

        # Room preference patterns (learned from usage data)
        self.room_preferences = {}

        # Inter-building travel times
        self.travel_times = {}

    def calculate_travel_penalty(self, room1_id: str, room2_id: str, time_gap: int) -> float:
        """Calculate penalty for traveling between rooms"""
        # Get buildings for rooms
        building1 = self._get_room_building(room1_id)
        building2 = self._get_room_building(room2_id)

        if building1 == building2:
            return 1.0  # Same building, no penalty

        # Get travel time between buildings
        travel_time = self.travel_times.get((building1, building2), 10)  # Default 10 minutes

        if time_gap >= travel_time:
            return 1.0  # Sufficient time
        else:
            return max(0.3, time_gap / travel_time)  # Penalty based on insufficient time

    def _get_room_building(self, room_id: str) -> str:
        """Extract building from room ID"""
        # Simplified: assume room ID format like "CSE-101" where "CSE" is building
        return room_id.split('-')[0] if '-' in room_id else 'MAIN'

    def calculate_room_preference_score(self, course_id: str, room_id: str) -> float:
        """Calculate preference score for course-room assignment"""
        return self.room_preferences.get(course_id, {}).get(room_id, 0.8)


class MultiDimensionalContextEngine:
    """Main Context Engine integrating all 5 dimensions"""

    def __init__(self):
        self.temporal = TemporalContext()
        self.behavioral = BehavioralContext()
        self.academic = AcademicContext()
        self.social = SocialContext()
        self.spatial = SpatialContext()

        # Context weights (how much each dimension influences decisions)
        self.dimension_weights = {
            'temporal': 0.25,
            'behavioral': 0.25,
            'academic': 0.20,
            'social': 0.15,
            'spatial': 0.15
        }

    def initialize_context(
        self,
        courses: List[Course],
        faculty: Dict[str, Faculty],
        students: Dict[str, Student],
        rooms: List[Room],
        time_slots: List[TimeSlot]
    ):
        """Initialize context engine with current data and timeout protection"""
        logger.info("Initializing Multi-Dimensional Context Engine...")
        
        # Progress tracking
        from timeout_handler import ProcessMonitor
        monitor = ProcessMonitor()
        monitor.update_progress()
        
        # Check dataset size and reduce if necessary
        if len(courses) > 1000:
            logger.warning(f"Large dataset detected: {len(courses)} courses. Using simplified initialization.")
            return self._simplified_initialization(courses, faculty, students, rooms, time_slots)
        
        try:
            # Initialize with timeout protection
            import signal
            
            def timeout_handler(signum, frame):
                raise TimeoutError("Context initialization timeout")
            
            # Set 2-minute timeout
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(120)
            
            # Initialize academic context
            logger.info("Building prerequisite graph...")
            self.academic.build_prerequisite_graph(courses)

            # Analyze behavioral patterns (limit to first 500 courses)
            logger.info("Analyzing behavioral patterns...")
            limited_courses = courses[:500] if len(courses) > 500 else courses
            co_enrollment = self.behavioral.analyze_co_enrollment_patterns(limited_courses)

            # Analyze social networks (limit to first 1000 students)
            logger.info("Analyzing social networks...")
            limited_students = dict(list(students.items())[:1000]) if len(students) > 1000 else students
            peer_networks = self.social.analyze_peer_networks(limited_students, limited_courses)
            
            signal.alarm(0)  # Cancel timeout
            logger.info("Context engine initialization complete")
            
        except TimeoutError:
            signal.alarm(0)
            logger.warning("Context initialization timed out, using simplified mode")
            return self._simplified_initialization(courses, faculty, students, rooms, time_slots)
        except Exception as e:
            signal.alarm(0)
            logger.error(f"Context initialization failed: {e}")
            return self._simplified_initialization(courses, faculty, students, rooms, time_slots)
    
    def _simplified_initialization(self, courses, faculty, students, rooms, time_slots):
        """Simplified initialization for large datasets"""
        logger.info("Using simplified context initialization...")
        
        # Only initialize essential components
        limited_courses = courses[:200]  # Limit to 200 courses
        self.academic.build_prerequisite_graph(limited_courses)
        
        # Set default effectiveness patterns
        for course in limited_courses:
            if hasattr(course, 'faculty_id'):
                self.behavioral.faculty_effectiveness[course.faculty_id] = {
                    'default': 0.8
                }
        
        logger.info("Simplified context initialization complete")

    def get_context_vector(
        self,
        course: Course,
        time_slot: TimeSlot,
        room: Room,
        current_week: int = 8
    ) -> ContextVector:
        """Calculate 5-dimensional context vector for a specific assignment"""

        # Θ_t: Temporal effectiveness
        temporal_score = (
            self.temporal.get_time_effectiveness(time_slot) *
            self.temporal.get_day_effectiveness(time_slot.day) *
            self.temporal.get_semester_phase_stability(current_week)
        )

        # Θ_b: Behavioral effectiveness
        behavioral_score = self.behavioral.get_faculty_effectiveness(
            course.faculty_id,
            time_slot.slot_id
        )

        # Θ_a: Academic coherence (simplified)
        academic_score = self.academic.subject_type_priorities.get(
            course.subject_type, 0.8
        )

        # Θ_s: Social cohesion (simplified)
        social_score = 0.8  # Would need peer network analysis

        # Θ_l: Spatial optimization
        spatial_score = self.spatial.calculate_room_preference_score(
            course.course_id,
            room.room_id
        )

        return ContextVector(
            temporal=temporal_score,
            behavioral=behavioral_score,
            academic=academic_score,
            social=social_score,
            spatial=spatial_score
        )

    def adjust_soft_constraint_weights(
        self,
        base_weights: Dict[str, float],
        context_vector: ContextVector
    ) -> Dict[str, float]:
        """Dynamically adjust soft constraint weights based on context"""

        adjusted_weights = base_weights.copy()

        # Temporal adjustments
        if context_vector.temporal < 0.8:
            # Low temporal effectiveness - prioritize faculty preferences
            adjusted_weights['faculty_preference'] *= 1.2
            adjusted_weights['compactness'] *= 0.9

        # Behavioral adjustments
        if context_vector.behavioral > 0.9:
            # High behavioral effectiveness - maintain current assignment
            adjusted_weights['faculty_preference'] *= 1.1

        # Academic adjustments
        if context_vector.academic > 0.9:
            # High academic coherence - prioritize continuity
            adjusted_weights['continuity'] *= 1.15

        # Social adjustments
        if context_vector.social > 0.8:
            # High social cohesion - maintain peer groups
            adjusted_weights['compactness'] *= 1.1

        # Spatial adjustments
        if context_vector.spatial < 0.7:
            # Poor spatial fit - prioritize room utilization
            adjusted_weights['room_utilization'] *= 1.2

        # Normalize weights to sum to 1.0
        total_weight = sum(adjusted_weights.values())
        for key in adjusted_weights:
            adjusted_weights[key] /= total_weight

        return adjusted_weights

    def get_contextual_fitness_multiplier(
        self,
        course: Course,
        time_slot: TimeSlot,
        room: Room,
        assignment_context: Dict = None
    ) -> float:
        """Calculate context-aware fitness multiplier for an assignment"""

        context_vector = self.get_context_vector(course, time_slot, room)

        # Weighted combination of all context dimensions
        multiplier = (
            self.dimension_weights['temporal'] * context_vector.temporal +
            self.dimension_weights['behavioral'] * context_vector.behavioral +
            self.dimension_weights['academic'] * context_vector.academic +
            self.dimension_weights['social'] * context_vector.social +
            self.dimension_weights['spatial'] * context_vector.spatial
        )

        return multiplier

    def save_context_learning(self, filepath: str):
        """Save learned context patterns for next semester"""
        context_data = {
            'faculty_effectiveness': self.behavioral.faculty_effectiveness,
            'room_preferences': self.spatial.room_preferences,
            'co_enrollment_patterns': self.behavioral.co_enrollment_matrix,
            'timestamp': datetime.now().isoformat()
        }

        with open(filepath, 'w') as f:
            json.dump(context_data, f, indent=2)

        logger.info(f"Context learning data saved to {filepath}")

    def load_context_learning(self, filepath: str):
        """Load context patterns from previous semester"""
        try:
            with open(filepath, 'r') as f:
                context_data = json.load(f)

            self.behavioral.faculty_effectiveness = context_data.get('faculty_effectiveness', {})
            self.spatial.room_preferences = context_data.get('room_preferences', {})
            self.behavioral.co_enrollment_matrix = context_data.get('co_enrollment_patterns', {})

            logger.info(f"Context learning data loaded from {filepath}")
        except FileNotFoundError:
            logger.info("No previous context learning data found, starting fresh")
