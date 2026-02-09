"""
Context Feature Store - Read-Only Historical Signals
Following Google/Meta standards: Feature store pattern
Executive verdict: "Aggregate historical, slow-moving signals"

Updates: Once per semester or batch (NOT per request)
Output: Stable features that inform decisions (NOT decisions themselves)
"""
import logging
import json
from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger(__name__)


class ContextFeatureStore:
    """
    Read-only feature store for historical scheduling signals
    
    Updates: Semester-wise or batch only
    Role: Provide stable features to inform scheduling decisions
    NOT: Make decisions, trigger actions, or modify schedules
    
    Features (approved):
    - Faculty effectiveness by time-of-day
    - Course popularity trends
    - Student overload hotspots
    - Room utilization patterns
    - Co-enrollment statistics
    """
    
    def __init__(self, storage_path: str = "data/context_features"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Feature caches (loaded once, read many times)
        self.faculty_time_effectiveness: Dict[str, Dict[str, float]] = {}
        self.course_popularity: Dict[str, float] = {}
        self.student_overload_hotspots: Dict[str, List[str]] = {}
        self.room_utilization: Dict[str, float] = {}
        self.co_enrollment_stats: Dict[str, Dict[str, float]] = {}
        
        # Metadata
        self.last_update: Optional[datetime] = None
        self.semester_version: Optional[str] = None
        
        logger.info("[ContextStore] Initialized (read-only signal provider)")
    
    def load_features(self, semester_id: str):
        """
        Load pre-computed features for a semester
        This is called ONCE at semester start, not per request
        """
        feature_file = self.storage_path / f"features_{semester_id}.json"
        
        if not feature_file.exists():
            logger.warning(f"[ContextStore] No features for semester {semester_id}, using defaults")
            self._load_defaults()
            return
        
        try:
            with open(feature_file, 'r') as f:
                data = json.load(f)
            
            self.faculty_time_effectiveness = data.get('faculty_time_effectiveness', {})
            self.course_popularity = data.get('course_popularity', {})
            self.student_overload_hotspots = data.get('student_overload_hotspots', {})
            self.room_utilization = data.get('room_utilization', {})
            self.co_enrollment_stats = data.get('co_enrollment_stats', {})
            
            self.last_update = datetime.fromisoformat(data.get('last_update', datetime.now().isoformat()))
            self.semester_version = semester_id
            
            logger.info(f"[ContextStore] Loaded features for semester {semester_id}")
            logger.info(f"[ContextStore] Faculty patterns: {len(self.faculty_time_effectiveness)}")
            logger.info(f"[ContextStore] Course popularity: {len(self.course_popularity)}")
            
        except Exception as e:
            logger.error(f"[ContextStore] Failed to load features: {e}")
            self._load_defaults()
    
    def get_faculty_time_effectiveness(self, faculty_id: str, time_bucket: str) -> float:
        """
        Get faculty effectiveness score for a time bucket
        Returns: 0.0-1.0 (higher = historically more effective)
        
        Read-only: Does NOT modify anything
        """
        return self.faculty_time_effectiveness.get(faculty_id, {}).get(time_bucket, 0.5)
    
    def get_course_popularity(self, course_id: str) -> float:
        """
        Get course popularity score (enrollment trend)
        Returns: 0.0-1.0 (higher = more popular historically)
        
        Read-only: Does NOT modify anything
        """
        return self.course_popularity.get(course_id, 0.5)
    
    def get_overload_risk(self, student_id: str, time_slot: str) -> bool:
        """
        Check if time slot is an overload hotspot for student
        Returns: True if historically overloaded
        
        Read-only: Does NOT modify anything
        """
        hotspots = self.student_overload_hotspots.get(student_id, [])
        return time_slot in hotspots
    
    def get_room_utilization(self, room_id: str) -> float:
        """
        Get historical room utilization rate
        Returns: 0.0-1.0 (fraction of time room is used)
        
        Read-only: Does NOT modify anything
        """
        return self.room_utilization.get(room_id, 0.5)
    
    def get_co_enrollment_strength(self, course_id1: str, course_id2: str) -> float:
        """
        Get co-enrollment strength between two courses
        Returns: 0.0-1.0 (fraction of students taking both)
        
        Read-only: Does NOT modify anything
        """
        key = f"{min(course_id1, course_id2)}_{max(course_id1, course_id2)}"
        return self.co_enrollment_stats.get(key, {}).get('strength', 0.0)
    
    def get_feature_vector(
        self, 
        faculty_id: str, 
        course_id: str, 
        time_bucket: str,
        room_id: str
    ) -> Dict[str, float]:
        """
        Get aggregated feature vector for a scheduling decision
        
        This is the main API for getting context signals
        Returns: Dictionary of features (NOT decisions)
        
        Usage: RL uses this to bias exploration, NOT to make decisions
        """
        return {
            'faculty_time_effectiveness': self.get_faculty_time_effectiveness(faculty_id, time_bucket),
            'course_popularity': self.get_course_popularity(course_id),
            'room_utilization': self.get_room_utilization(room_id),
            'semester_version': self.semester_version or 'default'
        }
    
    def _load_defaults(self):
        """Load default neutral features"""
        self.faculty_time_effectiveness = defaultdict(lambda: defaultdict(lambda: 0.5))
        self.course_popularity = defaultdict(lambda: 0.5)
        self.student_overload_hotspots = defaultdict(list)
        self.room_utilization = defaultdict(lambda: 0.5)
        self.co_enrollment_stats = defaultdict(lambda: {'strength': 0.0})
        self.last_update = datetime.now()
        self.semester_version = 'default'
        logger.info("[ContextStore] Loaded default neutral features")
    
    def get_stats(self) -> Dict:
        """Get feature store statistics for monitoring"""
        return {
            'semester_version': self.semester_version,
            'last_update': self.last_update.isoformat() if self.last_update else None,
            'faculty_patterns_count': len(self.faculty_time_effectiveness),
            'course_count': len(self.course_popularity),
            'room_count': len(self.room_utilization),
            'co_enrollment_pairs': len(self.co_enrollment_stats)
        }
