"""
Timetable Generation Orchestrator
Coordinates three-stage hybrid architecture for NEP 2020-compliant timetabling
"""
import logging
import pickle
import json
from typing import Dict, List, Optional
from datetime import datetime

from models.timetable_models import (
    Course, Faculty, Room, TimeSlot, Student, Batch,
    TimetableEntry, GenerationStatistics, QualityMetrics
)
from utils.progress_tracker import ProgressTracker
from utils.redis_pubsub import RedisPublisher
from utils.django_client import DjangoAPIClient
from engine.stage1_clustering import ConstraintGraphClustering
from engine.stage2_hybrid import HybridScheduler
from engine.stage3_rl import OptimizedQLearningResolver
from engine.context_engine import MultiDimensionalContextEngine
from config import settings

logger = logging.getLogger(__name__)


class TimetableOrchestrator:
    """
    ENTERPRISE PATTERN: Orchestrator with Real-Time Progress Reporting

    Coordinates three-stage timetable generation with instrumented progress tracking:
    1. Stage 1: Louvain-based constraint graph clustering (15% of total time)
    2. Stage 2: Parallel CP-SAT + GA hybrid scheduling (50% of total time)
    3. Stage 3: Q-Learning conflict resolution (25% of total time)
    4. Stage 4: Finalization (10% of total time)

    Progress is published to Redis Pub/Sub for WebSocket streaming to frontend.
    """

    def __init__(self, job_id: str, redis_client):
        self.job_id = job_id
        self.redis_client = redis_client

        # ENTERPRISE PATTERN: Progress tracking with Pub/Sub
        self.redis_publisher = RedisPublisher(redis_client)
        self.progress_tracker = ProgressTracker(job_id, redis_client, self.redis_publisher)

        self.django_client = DjangoAPIClient()

        # Data containers
        self.courses: List[Course] = []
        self.faculty: Dict[str, Faculty] = {}
        self.rooms: List[Room] = []
        self.time_slots: List[TimeSlot] = []
        self.students: Dict[str, Student] = {}
        self.batches: Dict[str, Batch] = {}

        # Results
        self.clusters: Dict[str, int] = {}
        self.cluster_schedules: Dict[int, Dict] = {}
        self.global_schedule: Dict = {}
        self.timetable_entries: List[TimetableEntry] = []

        # Context Engine for intelligent optimization
        self.context_engine = MultiDimensionalContextEngine()

        # Timing
        self.start_time: Optional[datetime] = None
        self.stage_times: Dict[str, float] = {}

    async def generate_timetable(
        self,
        department_id: str,
        batch_ids: List[str],
        semester: int,
        prefetched_data: Dict = None  # OPTIMIZATION: Accept pre-fetched data
    ) -> Dict:
        """
        Main entry point for timetable generation.

        Args:
            department_id: Department identifier
            batch_ids: List of batch identifiers
            semester: Semester number
            prefetched_data: Optional pre-fetched data to skip API calls

        Returns:
            Dictionary containing timetable entries, statistics, and metrics
        """
        try:
            self.start_time = datetime.now()

            # Stage 0: Fetch or use pre-fetched data
            if prefetched_data:
                # OPTIMIZED: Use cached data (saves 5-10 seconds)
                self._load_prefetched_data(prefetched_data)
            else:
                # Fetch from Django backend
                await self._fetch_all_data(department_id, batch_ids, semester)

            # Stage 1: Constraint Graph Clustering (10-20% runtime)
            self._execute_stage1_clustering()

            # Stage 2: Parallel Hybrid Scheduling (60-70% runtime)
            self._execute_stage2_scheduling()

            # Stage 3: Q-Learning Conflict Resolution (10-20% runtime)
            self._execute_stage3_resolution()

            # Convert to timetable entries
            self._convert_to_timetable_entries()

            # Calculate statistics and quality metrics
            statistics = self._calculate_statistics()
            metrics = self._calculate_quality_metrics()

            # Mark as completed
            self.progress_tracker.update(
                stage="completed",
                progress=100.0,
                step="Timetable generation completed successfully"
            )

            # Save to Django backend
            await self._save_timetable(department_id, semester, statistics, metrics)

            return {
                "job_id": self.job_id,
                "timetable_entries": [entry.model_dump() for entry in self.timetable_entries],
                "statistics": statistics.model_dump(),
                "metrics": metrics.model_dump(),
                "stage_times": self.stage_times
            }

        except Exception as e:
            logger.error(f"Timetable generation failed: {str(e)}", exc_info=True)
            self.progress_tracker.update(
                stage="failed",
                progress=0.0,
                step=f"Generation failed: {str(e)}"
            )
            raise

    async def _fetch_all_data(self, department_id: str, batch_ids: List[str], semester: int):
        """Fetch all required data from Django API"""
        self.progress_tracker.update(
            stage="initializing",
            progress=0.0,
            step="Fetching data from Django backend"
        )

        # Fetch courses with actual student enrollments (NEP 2020)
        courses_data = await self.django_client.fetch_courses(department_id, batch_ids, semester)
        self.courses = [Course(**c) for c in courses_data]
        logger.info(f"Fetched {len(self.courses)} courses")

        # Fetch faculty
        faculty_data = await self.django_client.fetch_faculty(department_id)
        self.faculty = {f["faculty_id"]: Faculty(**f) for f in faculty_data}
        logger.info(f"Fetched {len(self.faculty)} faculty members")

        # Fetch rooms
        rooms_data = await self.django_client.fetch_rooms(department_id)
        self.rooms = [Room(**r) for r in rooms_data]
        logger.info(f"Fetched {len(self.rooms)} rooms")

        # Fetch time slots
        time_slots_data = await self.django_client.fetch_time_slots()
        self.time_slots = [TimeSlot(**t) for t in time_slots_data]
        logger.info(f"Fetched {len(self.time_slots)} time slots")

        # Fetch individual student enrollments (NEP 2020 critical)
        students_data = await self.django_client.fetch_students(batch_ids)
        self.students = {s["student_id"]: Student(**s) for s in students_data}
        logger.info(f"Fetched {len(self.students)} students")

        # Fetch batches (for grouping, not constraint logic)
        batches_data = await self.django_client.fetch_batches(batch_ids)
        self.batches = {b["batch_id"]: Batch(**b) for b in batches_data}
        logger.info(f"Fetched {len(self.batches)} batches")

        self.progress_tracker.update(progress=5.0, step="Data fetching completed")

    def _load_prefetched_data(self, prefetched_data: Dict):
        """
        Load pre-fetched data (OPTIMIZATION for parallel variant generation)
        Skips API calls, saves 5-10 seconds per variant
        """
        from models.timetable_models import Course, Faculty, Room, TimeSlot, Student, Batch

        self.progress_tracker.update(progress=1.0, step="Loading cached data")

        # Load cached data
        self.courses = [Course(**c) for c in prefetched_data['courses']]
        self.faculty = {f["faculty_id"]: Faculty(**f) for f in prefetched_data['faculty']}
        self.rooms = [Room(**r) for r in prefetched_data['rooms']]
        self.time_slots = [TimeSlot(**t) for t in prefetched_data['time_slots']]
        self.students = {s["student_id"]: Student(**s) for s in prefetched_data['students']}
        self.batches = {b["batch_id"]: Batch(**b) for b in prefetched_data['batches']}

        logger.info(f"Loaded cached data: {len(self.courses)} courses, "
                   f"{len(self.faculty)} faculty, {len(self.rooms)} rooms")

        self.progress_tracker.update(progress=5.0, step="Cached data loaded")

    def _execute_stage1_clustering(self):
        """Execute Stage 1: Louvain constraint graph clustering"""
        stage_start = datetime.now()

        self.progress_tracker.update(
            stage="clustering",
            progress=5.0,
            step="Building constraint graph with NEP 2020 student overlaps"
        )

        clusterer = ConstraintGraphClustering(
            courses=self.courses,
            faculty=self.faculty,
            students=self.students,
            progress_tracker=self.progress_tracker,
            num_threads=16  # Ultra-parallel processing
        )

        # Build graph with student-level conflict detection
        clusterer.build_constraint_graph()

        # Apply Louvain clustering
        self.clusters = clusterer.apply_louvain_clustering()

        # Validate clusters
        clusterer.validate_and_adjust_clusters(
            self.clusters,
            max_size=settings.MAX_CLUSTER_SIZE,
            min_size=settings.MIN_CLUSTER_SIZE
        )

        stage_time = (datetime.now() - stage_start).total_seconds()
        self.stage_times["stage1_clustering"] = stage_time

        logger.info(f"Stage 1 completed in {stage_time:.2f}s - {len(set(self.clusters.values()))} clusters")
        self.progress_tracker.update(progress=20.0, step=f"Clustering complete: {len(set(self.clusters.values()))} clusters")

    def _execute_stage2_scheduling(self):
        """Execute Stage 2: Parallel CP-SAT + GA hybrid scheduling"""
        stage_start = datetime.now()

        self.progress_tracker.update(
            stage="scheduling",
            progress=20.0,
            step="Starting parallel hybrid scheduling (CP-SAT + GA)"
        )

        scheduler = HybridScheduler(
            clusters=self.clusters,
            courses=self.courses,
            rooms=self.rooms,
            time_slots=self.time_slots,
            faculty=self.faculty,
            students=self.students,  # NEP 2020: Individual students
            progress_tracker=self.progress_tracker,
            context_engine=self.context_engine
        )

        # Schedule all clusters in parallel (8-core = 8× speedup)
        self.cluster_schedules, _ = scheduler.execute()

        stage_time = (datetime.now() - stage_start).total_seconds()
        self.stage_times["stage2_scheduling"] = stage_time

        logger.info(f"Stage 2 completed in {stage_time:.2f}s - {len(self.cluster_schedules)} clusters scheduled")
        self.progress_tracker.update(progress=80.0, step="Parallel scheduling complete")

    def _execute_stage3_resolution(self):
        """Execute Stage 3: Q-Learning conflict resolution"""
        stage_start = datetime.now()

        self.progress_tracker.update(
            stage="resolving",
            progress=80.0,
            step="Resolving inter-cluster conflicts with Q-Learning"
        )

        # Load existing Q-table if available (semester-to-semester learning)
        q_table = self._load_q_table()

        resolver = OptimizedQLearningResolver(
            courses=self.courses,
            rooms=self.rooms,
            time_slots=self.time_slots,
            faculty=self.faculty,
            students=self.students,  # NEP 2020: Individual student conflicts
            progress_tracker=self.progress_tracker,
            q_table_path=settings.Q_TABLE_PATH,
            context_engine=self.context_engine
        )

        # Merge clusters and resolve conflicts with optimized algorithm
        self.global_schedule, _ = resolver.execute(self.cluster_schedules)

        # Save updated Q-table for next semester
        self._save_q_table(resolver.q_table)

        stage_time = (datetime.now() - stage_start).total_seconds()
        self.stage_times["stage3_resolution"] = stage_time

        logger.info(f"Stage 3 completed in {stage_time:.2f}s")
        self.progress_tracker.update(progress=95.0, step="Conflict resolution complete")

    def _convert_to_timetable_entries(self):
        """Convert schedule dictionary to TimetableEntry objects"""
        self.progress_tracker.update(progress=95.0, step="Converting to timetable entries")

        for (course_id, session), (time_slot_id, room_id) in self.global_schedule.items():
            course = next(c for c in self.courses if c.course_id == course_id)
            time_slot = next(t for t in self.time_slots if t.slot_id == time_slot_id)
            room = next(r for r in self.rooms if r.room_id == room_id)

            entry = TimetableEntry(
                course_id=course_id,
                course_code=course.course_code,
                course_name=course.course_name,
                faculty_id=course.faculty_id,
                room_id=room_id,
                time_slot_id=time_slot_id,
                session_number=session,
                day=time_slot.day,
                start_time=time_slot.start_time,
                end_time=time_slot.end_time,
                student_ids=course.student_ids,  # NEP 2020: Individual students
                batch_ids=course.batch_ids  # For grouping display only
            )
            self.timetable_entries.append(entry)

        logger.info(f"Generated {len(self.timetable_entries)} timetable entries")

    def _calculate_statistics(self) -> GenerationStatistics:
        """Calculate generation statistics"""
        total_time = (datetime.now() - self.start_time).total_seconds()

        return GenerationStatistics(
            total_courses=len(self.courses),
            total_sessions=sum(c.duration for c in self.courses),
            scheduled_sessions=len(self.timetable_entries),
            total_clusters=len(set(self.clusters.values())),
            total_students=len(self.students),  # NEP 2020: Individual students
            total_faculty=len(self.faculty),
            total_rooms=len(self.rooms),
            total_time_slots=len(self.time_slots),
            generation_time_seconds=total_time,
            stage1_time=self.stage_times.get("stage1_clustering", 0),
            stage2_time=self.stage_times.get("stage2_scheduling", 0),
            stage3_time=self.stage_times.get("stage3_resolution", 0)
        )

    def _calculate_quality_metrics(self) -> QualityMetrics:
        """Calculate timetable quality metrics"""
        # Detect conflicts (should be zero after Stage 3)
        faculty_conflicts = self._count_faculty_conflicts()
        room_conflicts = self._count_room_conflicts()
        student_conflicts = self._count_student_conflicts()  # NEP 2020: Individual students

        # Calculate soft constraint satisfaction
        compactness = self._calculate_compactness()
        workload_balance = self._calculate_workload_balance()
        room_utilization = self._calculate_room_utilization()

        return QualityMetrics(
            hard_constraint_violations=faculty_conflicts + room_conflicts + student_conflicts,
            faculty_conflicts=faculty_conflicts,
            room_conflicts=room_conflicts,
            student_conflicts=student_conflicts,
            compactness_score=compactness,
            workload_balance_score=workload_balance,
            room_utilization=room_utilization
        )

    def _count_faculty_conflicts(self) -> int:
        """Count faculty scheduling conflicts"""
        faculty_schedule = {}
        conflicts = 0

        for entry in self.timetable_entries:
            key = (entry.faculty_id, entry.time_slot_id)
            if key in faculty_schedule:
                conflicts += 1
            faculty_schedule[key] = True

        return conflicts

    def _count_room_conflicts(self) -> int:
        """Count room scheduling conflicts"""
        room_schedule = {}
        conflicts = 0

        for entry in self.timetable_entries:
            key = (entry.room_id, entry.time_slot_id)
            if key in room_schedule:
                conflicts += 1
            room_schedule[key] = True

        return conflicts

    def _count_student_conflicts(self) -> int:
        """Count individual student scheduling conflicts (NEP 2020)"""
        student_schedule = {}
        conflicts = 0

        for entry in self.timetable_entries:
            for student_id in entry.student_ids:
                key = (student_id, entry.time_slot_id)
                if key in student_schedule:
                    conflicts += 1
                    logger.warning(f"Student {student_id} conflict at {entry.time_slot_id}")
                student_schedule[key] = True

        return conflicts

    def _calculate_compactness(self) -> float:
        """Calculate schedule compactness (fewer gaps)"""
        # Group by student and day, calculate gap ratio
        student_daily_schedules = {}

        for entry in self.timetable_entries:
            for student_id in entry.student_ids:
                key = (student_id, entry.day)
                if key not in student_daily_schedules:
                    student_daily_schedules[key] = []
                student_daily_schedules[key].append(entry.start_time)

        gap_ratios = []
        for schedules in student_daily_schedules.values():
            if len(schedules) > 1:
                schedules_sorted = sorted(schedules)
                total_span = schedules_sorted[-1] - schedules_sorted[0]
                gaps = sum(schedules_sorted[i+1] - schedules_sorted[i]
                          for i in range(len(schedules_sorted) - 1))
                if total_span > 0:
                    gap_ratios.append(1.0 - (gaps / total_span))

        return sum(gap_ratios) / len(gap_ratios) if gap_ratios else 1.0

    def _calculate_workload_balance(self) -> float:
        """Calculate faculty workload balance"""
        faculty_loads = {}

        for entry in self.timetable_entries:
            faculty_loads[entry.faculty_id] = faculty_loads.get(entry.faculty_id, 0) + 1

        if not faculty_loads:
            return 1.0

        loads = list(faculty_loads.values())
        mean_load = sum(loads) / len(loads)
        variance = sum((l - mean_load) ** 2 for l in loads) / len(loads)

        # Normalize: lower variance = higher balance score
        return 1.0 / (1.0 + variance)

    def _calculate_room_utilization(self) -> float:
        """Calculate room utilization efficiency"""
        total_slots = len(self.rooms) * len(self.time_slots)
        used_slots = len(set((e.room_id, e.time_slot_id) for e in self.timetable_entries))

        return used_slots / total_slots if total_slots > 0 else 0.0

    def _load_q_table(self) -> Optional[Dict]:
        """Load Q-table from previous semester"""
        try:
            with open(settings.Q_TABLE_PATH, 'rb') as f:
                q_table = pickle.load(f)
                logger.info(f"Loaded Q-table with {len(q_table)} entries")
                return q_table
        except FileNotFoundError:
            logger.info("No existing Q-table found, starting fresh")
            return None

    def _save_q_table(self, q_table: Dict):
        """Save Q-table for next semester"""
        try:
            with open(settings.Q_TABLE_PATH, 'wb') as f:
                pickle.dump(q_table, f)
                logger.info(f"Saved Q-table with {len(q_table)} entries")
        except Exception as e:
            logger.error(f"Failed to save Q-table: {str(e)}")

    async def _save_timetable(
        self,
        department_id: str,
        semester: int,
        statistics: GenerationStatistics,
        metrics: QualityMetrics
    ):
        """Save timetable to Django backend"""
        self.progress_tracker.update(progress=98.0, step="Saving timetable to database")

        timetable_data = {
            "department_id": department_id,
            "semester": semester,
            "entries": [entry.model_dump() for entry in self.timetable_entries],
            "statistics": statistics.model_dump(),
            "metrics": metrics.model_dump()
        }

        await self.django_client.save_timetable(timetable_data)
        logger.info("Timetable saved to Django backend")
