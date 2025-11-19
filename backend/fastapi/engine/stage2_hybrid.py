"""Stage 2: Parallel Hybrid Micro-Scheduling (CP-SAT + Genetic Algorithm)"""
from ortools.sat.python import cp_model
import random
import numpy as np
from typing import List, Dict, Tuple, Optional
from concurrent.futures import ProcessPoolExecutor
import multiprocessing
import logging
from models.timetable_models import Course, Room, TimeSlot, Faculty, TimetableEntry
from utils.progress_tracker import ProgressTracker
from engine.context_engine import MultiDimensionalContextEngine
from config import settings

logger = logging.getLogger(__name__)


class CPSATSolver:
    """Phase 2A: CP-SAT for Hard Constraint Satisfaction"""

    def __init__(
        self,
        courses: List[Course],
        rooms: List[Room],
        time_slots: List[TimeSlot],
        faculty: Dict[str, Faculty],
        timeout_seconds: int = 30
    ):
        self.courses = courses
        self.rooms = rooms
        self.time_slots = time_slots
        self.faculty = faculty
        self.timeout_seconds = timeout_seconds
        self.model = cp_model.CpModel()
        self.solver = cp_model.CpSolver()
        self.variables = {}
        self._apply_advanced_heuristics()

    def _apply_advanced_heuristics(self):
        """Apply advanced CP-SAT optimization heuristics"""
        # Portfolio search with multiple strategies
        self.solver.parameters.search_branching = cp_model.PORTFOLIO_SEARCH

        # Enable preprocessing and symmetry detection
        self.solver.parameters.cp_model_presolve = True
        self.solver.parameters.symmetry_level = 2

        # Parallel search with multiple workers
        self.solver.parameters.num_search_workers = min(8, multiprocessing.cpu_count())

        # Advanced restart strategies
        self.solver.parameters.restart_algorithms = [
            cp_model.LUBY_RESTART, cp_model.DL_MOVING_AVERAGE_RESTART
        ]

        # Conflict-driven learning
        self.solver.parameters.clause_cleanup_period = 10000
        self.solver.parameters.max_time_in_seconds = self.timeout_seconds

    def solve(self) -> Optional[Dict[str, Tuple[int, int]]]:
        """
        Find ANY feasible solution satisfying all hard constraints.

        Returns:
            Dictionary mapping (course_id, session_num) -> (time_slot_id, room_id)
            or None if infeasible
        """
        # Intelligent preprocessing and domain reduction
        valid_domains = self._precompute_valid_domains()

        # Decision Variables: x[c, t, r] ∈ {0, 1} - only for valid combinations
        self.variables = {}

        for course in self.courses:
            for session in range(course.duration):
                valid_pairs = valid_domains.get((course.course_id, session), [])
                for t_slot_id, room_id in valid_pairs:
                    var_name = f"x_{course.course_id}_s{session}_t{t_slot_id}_r{room_id}"
                    self.variables[(course.course_id, session, t_slot_id, room_id)] = \
                        self.model.NewBoolVar(var_name)

        # Each session must be assigned exactly one (time, room) pair
        for course in self.courses:
            for session in range(course.duration):
                self.model.Add(
                    sum(
                        self.variables[(course.course_id, session, t.slot_id, r.room_id)]
                        for t in self.time_slots
                        for r in self.rooms
                    ) == 1
                )

        # HC1: Faculty Conflict Prevention
        for faculty_id in set(c.faculty_id for c in self.courses):
            faculty_courses = [c for c in self.courses if c.faculty_id == faculty_id]
            for t_slot in self.time_slots:
                self.model.Add(
                    sum(
                        self.variables[(c.course_id, s, t_slot.slot_id, r.room_id)]
                        for c in faculty_courses
                        for s in range(c.duration)
                        for r in self.rooms
                    ) <= 1
                )

        # HC2: Room Conflict Prevention
        for room in self.rooms:
            for t_slot in self.time_slots:
                self.model.Add(
                    sum(
                        self.variables[(c.course_id, s, t_slot.slot_id, room.room_id)]
                        for c in self.courses
                        for s in range(c.duration)
                    ) <= 1
                )

        # HC3: Student Conflict Prevention (NEP 2020 - Individual Student Level)
        # Each student can have at most 1 course at any time slot
        # Build student→courses mapping
        student_courses = {}
        for course in self.courses:
            for student_id in course.student_ids:
                if student_id not in student_courses:
                    student_courses[student_id] = []
                student_courses[student_id].append(course)

        # For each student, ensure no more than 1 course at same time
        for student_id, courses_list in student_courses.items():
            if len(courses_list) > 1:  # Only add constraint if student has multiple courses
                for t_slot in self.time_slots:
                    self.model.Add(
                        sum(
                            self.variables[(c.course_id, s, t_slot.slot_id, r.room_id)]
                            for c in courses_list
                            for s in range(c.duration)
                            for r in self.rooms
                        ) <= 1
                    )

        # HC4: Room Capacity
        for course in self.courses:
            for session in range(course.duration):
                for t_slot in self.time_slots:
                    for room in self.rooms:
                        if len(course.student_ids) > room.capacity:
                            # Can't assign this course to this room
                            self.model.Add(
                                self.variables[(course.course_id, session, t_slot.slot_id, room.room_id)] == 0
                            )

        # HC5: Room Feature Compatibility
        for course in self.courses:
            if course.required_features:
                for session in range(course.duration):
                    for t_slot in self.time_slots:
                        for room in self.rooms:
                            if not all(feat in room.features for feat in course.required_features):
                                self.model.Add(
                                    self.variables[(course.course_id, session, t_slot.slot_id, room.room_id)] == 0
                                )

        # HC6: Faculty Availability
        for course in self.courses:
            faculty_avail = self.faculty[course.faculty_id].available_slots
            if faculty_avail:
                for session in range(course.duration):
                    for t_slot in self.time_slots:
                        if t_slot.slot_id not in faculty_avail:
                            for room in self.rooms:
                                self.model.Add(
                                    self.variables[(course.course_id, session, t_slot.slot_id, room.room_id)] == 0
                                )

        # Solve with optimized parameters already set
        status = self.solver.Solve(self.model)

    def _precompute_valid_domains(self) -> Dict:
        """Precompute valid (time, room) pairs for each course session"""
        valid_domains = {}

        for course in self.courses:
            for session in range(course.duration):
                valid_pairs = []

                for t_slot in self.time_slots:
                    for room in self.rooms:
                        # Check capacity constraint
                        if len(course.student_ids) > room.capacity:
                            continue

                        # Check feature compatibility
                        if not all(feat in room.features for feat in course.required_features):
                            continue

                        # Check faculty availability
                        faculty_avail = self.faculty[course.faculty_id].available_slots
                        if faculty_avail and t_slot.slot_id not in faculty_avail:
                            continue

                        valid_pairs.append((t_slot.slot_id, room.room_id))

                valid_domains[(course.course_id, session)] = valid_pairs

        return valid_domains

        if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
            # Extract solution
            solution = {}
            for course in self.courses:
                for session in range(course.duration):
                    for t_slot in self.time_slots:
                        for room in self.rooms:
                            if self.solver.Value(
                                self.variables[(course.course_id, session, t_slot.slot_id, room.room_id)]
                            ):
                                solution[(course.course_id, session)] = (t_slot.slot_id, room.room_id)

            logger.info(f"CP-SAT found feasible solution in {self.solver.WallTime():.2f}s")
            return solution
        else:
            logger.warning(f"CP-SAT could not find feasible solution (status={status})")
            return None


class GeneticAlgorithmOptimizer:
    """Phase 2B: Genetic Algorithm for Soft Constraint Optimization"""

    def __init__(
        self,
        courses: List[Course],
        rooms: List[Room],
        time_slots: List[TimeSlot],
        faculty: Dict[str, Faculty],
        students: Dict[str, any],
        initial_solution: Optional[Dict] = None,
        population_size: int = 50,
        generations: int = 100,
        mutation_rate: float = 0.1,
        crossover_rate: float = 0.8,
        elitism_rate: float = 0.1,
        context_engine: Optional[MultiDimensionalContextEngine] = None
    ):
        self.courses = courses
        self.rooms = rooms
        self.time_slots = time_slots
        self.faculty = faculty
        self.students = students
        self.initial_solution = initial_solution
        # Adaptive population sizing: O(√n) instead of fixed
        self.population_size = max(20, int(math.sqrt(len(courses)) * 2))
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.elitism_rate = elitism_rate

        # Island model setup for parallel evolution
        self.num_islands = min(8, multiprocessing.cpu_count())
        self.island_size = self.population_size // self.num_islands
        self.migration_rate = 0.1
        self.migration_interval = 10

        self.population = []
        self.islands = []

        # Context Engine for dynamic weight adjustment
        self.context_engine = context_engine or MultiDimensionalContextEngine()
        self.context_engine.initialize_context(courses, faculty, students, rooms, time_slots)

        # Build valid domain cache for smart operators
        self._build_valid_domains()

    def _build_valid_domains(self):
        """Pre-compute valid (time, room) pairs for each course"""
        self.valid_domains = {}

        for course in self.courses:
            valid_pairs = []
            for t_slot in self.time_slots:
                for room in self.rooms:
                    # Check room capacity
                    if len(course.student_ids) > room.capacity:
                        continue

                    # Check room features
                    if not all(feat in room.features for feat in course.required_features):
                        continue

                    # Check faculty availability
                    faculty_avail = self.faculty[course.faculty_id].available_slots
                    if faculty_avail and t_slot.slot_id not in faculty_avail:
                        continue

                    valid_pairs.append((t_slot.slot_id, room.room_id))

            for session in range(course.duration):
                self.valid_domains[(course.course_id, session)] = valid_pairs

    def initialize_population(self):
        """Initialize population with CP-SAT solution + perturbations + random"""
        self.population = []

        # Add CP-SAT solution if available
        if self.initial_solution:
            self.population.append(self.initial_solution.copy())

            # Add perturbed versions
            for _ in range(min(19, self.population_size - 1)):
                perturbed = self._perturb_solution(self.initial_solution)
                if perturbed:
                    self.population.append(perturbed)

        # Fill remaining with random feasible solutions
        while len(self.population) < self.population_size:
            random_sol = self._generate_random_solution()
            if random_sol:
                self.population.append(random_sol)

        logger.info(f"Initialized population with {len(self.population)} individuals")

    def _generate_random_solution(self) -> Optional[Dict]:
        """Generate random feasible solution"""
        solution = {}

        for course in self.courses:
            for session in range(course.duration):
                valid_pairs = self.valid_domains.get((course.course_id, session), [])
                if not valid_pairs:
                    return None

                # Random selection from valid domain
                time_slot, room_id = random.choice(valid_pairs)
                solution[(course.course_id, session)] = (time_slot, room_id)

        # Check conflicts (quick validation)
        if not self._is_feasible(solution):
            return None

        return solution

    def _perturb_solution(self, solution: Dict) -> Optional[Dict]:
        """Perturb solution by changing random assignments"""
        perturbed = solution.copy()

        # Randomly select 10-20% of assignments to change
        keys = list(perturbed.keys())
        num_changes = max(1, int(len(keys) * random.uniform(0.1, 0.2)))

        for _ in range(num_changes):
            key = random.choice(keys)
            course_id, session = key

            valid_pairs = self.valid_domains.get(key, [])
            if valid_pairs:
                perturbed[key] = random.choice(valid_pairs)

        if self._is_feasible(perturbed):
            return perturbed
        return None

    def fitness(self, solution: Dict) -> float:
        """
        Context-Aware Multi-objective fitness function:
        Fitness(σ) = Σᵢ wᵢ(context) · SCᵢ(σ) · context_multiplier(σ) - 1000 · hard_constraint_violations(σ)
        """
        if not self._is_feasible(solution):
            violations = self._count_violations(solution)
            return -1000 * violations

        # Base soft constraint weights
        base_weights = {
            'faculty_preference': settings.WEIGHT_FACULTY_PREFERENCE,
            'compactness': settings.WEIGHT_COMPACTNESS,
            'room_utilization': settings.WEIGHT_ROOM_UTILIZATION,
            'workload_balance': settings.WEIGHT_WORKLOAD_BALANCE,
            'peak_spreading': settings.WEIGHT_PEAK_SPREADING,
            'continuity': settings.WEIGHT_CONTINUITY
        }

        # Calculate context-aware fitness with dynamic weights
        total_fitness = 0.0
        total_assignments = 0

        for (course_id, session), (time_slot_id, room_id) in solution.items():
            course = next(c for c in self.courses if c.course_id == course_id)
            time_slot = next(t for t in self.time_slots if t.slot_id == time_slot_id)
            room = next(r for r in self.rooms if r.room_id == room_id)

            # Get context vector for this assignment
            context_vector = self.context_engine.get_context_vector(course, time_slot, room)

            # Adjust weights based on context
            adjusted_weights = self.context_engine.adjust_soft_constraint_weights(
                base_weights, context_vector
            )

            # Calculate context multiplier
            context_multiplier = self.context_engine.get_contextual_fitness_multiplier(
                course, time_slot, room
            )

            # Calculate soft constraints for this assignment
            sc1 = self._faculty_preference_satisfaction_single(course, time_slot)
            sc2 = self._schedule_compactness_single(course, time_slot, solution)
            sc3 = self._room_utilization_single(room, time_slot)
            sc4 = self._workload_balance_single(course.faculty_id, solution)
            sc5 = self._peak_spreading_single(time_slot_id, solution)
            sc6 = self._lecture_continuity_single(course, session, solution)

            assignment_fitness = (
                adjusted_weights['faculty_preference'] * sc1 +
                adjusted_weights['compactness'] * sc2 +
                adjusted_weights['room_utilization'] * sc3 +
                adjusted_weights['workload_balance'] * sc4 +
                adjusted_weights['peak_spreading'] * sc5 +
                adjusted_weights['continuity'] * sc6
            ) * context_multiplier

            total_fitness += assignment_fitness
            total_assignments += 1

        return total_fitness / total_assignments if total_assignments > 0 else 0.0

    def _is_feasible(self, solution: Dict) -> bool:
        """Quick feasibility check - NEP 2020 student-centric"""
        # Check faculty conflicts
        faculty_schedule = {}
        for (course_id, session), (time_slot, room_id) in solution.items():
            course = next(c for c in self.courses if c.course_id == course_id)
            faculty_id = course.faculty_id

            if (faculty_id, time_slot) in faculty_schedule:
                return False
            faculty_schedule[(faculty_id, time_slot)] = True

        # Check room conflicts
        room_schedule = {}
        for (course_id, session), (time_slot, room_id) in solution.items():
            if (room_id, time_slot) in room_schedule:
                return False
            room_schedule[(room_id, time_slot)] = True

        # Check student conflicts (NEP 2020 CRITICAL)
        # Each individual student can have at most 1 course at any time slot
        student_schedule = {}
        for (course_id, session), (time_slot, room_id) in solution.items():
            course = next(c for c in self.courses if c.course_id == course_id)
            for student_id in course.student_ids:
                if (student_id, time_slot) in student_schedule:
                    return False  # Student conflict detected
                student_schedule[(student_id, time_slot)] = True

        return True

    def _count_violations(self, solution: Dict) -> int:
        """Count hard constraint violations - NEP 2020 student-centric"""
        violations = 0

        # Faculty conflicts
        faculty_schedule = {}
        for (course_id, session), (time_slot, room_id) in solution.items():
            course = next(c for c in self.courses if c.course_id == course_id)
            key = (course.faculty_id, time_slot)
            faculty_schedule[key] = faculty_schedule.get(key, 0) + 1

        # Student conflicts (NEP 2020)
        student_schedule = {}
        for (course_id, session), (time_slot, room_id) in solution.items():
            course = next(c for c in self.courses if c.course_id == course_id)
            for student_id in course.student_ids:
                key = (student_id, time_slot)
                student_schedule[key] = student_schedule.get(key, 0) + 1

        violations += sum(max(0, count - 1) for count in faculty_schedule.values())
        violations += sum(max(0, count - 1) for count in student_schedule.values())

        # Room conflicts
        room_schedule = {}
        for (course_id, session), (time_slot, room_id) in solution.items():
            key = (room_id, time_slot)
            room_schedule[key] = room_schedule.get(key, 0) + 1

        violations += sum(max(0, count - 1) for count in room_schedule.values())

        return violations

    # Soft constraint calculators
    def _faculty_preference_satisfaction(self, solution: Dict) -> float:
        """SC₁ - Faculty time preference satisfaction"""
        total_score = 0
        count = 0

        for (course_id, session), (time_slot, room_id) in solution.items():
            course = next(c for c in self.courses if c.course_id == course_id)
            faculty_prefs = self.faculty[course.faculty_id].preferred_slots

            if time_slot in faculty_prefs:
                total_score += faculty_prefs[time_slot]
            else:
                total_score += 0.5  # Neutral score for no preference

            count += 1

        return total_score / count if count > 0 else 0.0

    def _schedule_compactness(self, solution: Dict) -> float:
        """SC₂ - Schedule compactness (gap minimization)"""
        # Count gaps for students and faculty
        total_gaps = 0

        # Faculty gaps
        for faculty_id in set(c.faculty_id for c in self.courses):
            time_slots_used = sorted([
                time_slot for (cid, s), (time_slot, _) in solution.items()
                if next(c for c in self.courses if c.course_id == cid).faculty_id == faculty_id
            ])

            if len(time_slots_used) > 1:
                # Count gaps between consecutive classes
                gaps = sum(
                    time_slots_used[i+1] - time_slots_used[i] - 1
                    for i in range(len(time_slots_used) - 1)
                )
                total_gaps += gaps

        max_gaps = len(self.courses) * 5  # Arbitrary max
        return max(0, 1 - total_gaps / max_gaps)

    def _room_utilization(self, solution: Dict) -> float:
        """SC₃ - Room utilization efficiency"""
        utilized_slots = len(set((room_id, time_slot) for _, (time_slot, room_id) in solution.items()))
        total_slots = len(self.rooms) * len(self.time_slots)
        return utilized_slots / total_slots if total_slots > 0 else 0

    def _workload_balance(self, solution: Dict) -> float:
        """SC₄ - Balanced faculty workload"""
        workloads = {}

        for course in self.courses:
            faculty_id = course.faculty_id
            workloads[faculty_id] = workloads.get(faculty_id, 0) + course.duration

        if not workloads:
            return 1.0

        mean_load = np.mean(list(workloads.values()))
        std_load = np.std(list(workloads.values()))

        return max(0, 1 - std_load / mean_load) if mean_load > 0 else 1.0

    def _peak_spreading(self, solution: Dict) -> float:
        """SC₅ - Peak time spreading"""
        slot_loads = {}

        for _, (time_slot, _) in solution.items():
            slot_loads[time_slot] = slot_loads.get(time_slot, 0) + 1

        max_load = max(slot_loads.values()) if slot_loads else 0
        total_courses = len(self.courses)

        return max(0, 1 - max_load / total_courses) if total_courses > 0 else 1.0

    def _lecture_continuity(self, solution: Dict) -> float:
        """SC₆ - Lecture continuity (prefer MWF or TTh patterns)"""
        continuity_score = 0
        count = 0

        for course in self.courses:
            if course.duration >= 2:
                sessions = []
                for session in range(course.duration):
                    time_slot, _ = solution[(course.course_id, session)]
                    day = time_slot // 10  # Assuming 10 periods per day
                    sessions.append(day)

                sessions.sort()

                # Check for MWF (0, 2, 4) or TTh (1, 3) patterns
                if sessions == [0, 2, 4] or sessions == [0, 2] or sessions == [1, 3]:
                    continuity_score += 1

                count += 1

        return continuity_score / count if count > 0 else 1.0

    # Context-aware single assignment fitness functions
    def _faculty_preference_satisfaction_single(self, course: Course, time_slot: TimeSlot) -> float:
        """Faculty preference for single assignment"""
        faculty_prefs = self.faculty[course.faculty_id].preferred_slots
        if time_slot.slot_id in faculty_prefs:
            return faculty_prefs[time_slot.slot_id]
        return 0.5

    def _schedule_compactness_single(self, course: Course, time_slot: TimeSlot, solution: Dict) -> float:
        """Compactness contribution of single assignment"""
        # Simplified: check if this creates gaps
        faculty_slots = [ts for (cid, s), (ts, _) in solution.items()
                        if next(c for c in self.courses if c.course_id == cid).faculty_id == course.faculty_id]
        faculty_slots.sort()

        if len(faculty_slots) <= 1:
            return 1.0

        # Calculate gap penalty
        gaps = sum(faculty_slots[i+1] - faculty_slots[i] - 1 for i in range(len(faculty_slots) - 1))
        return max(0.3, 1.0 - gaps / (len(faculty_slots) * 2))

    def _room_utilization_single(self, room: Room, time_slot: TimeSlot) -> float:
        """Room utilization for single assignment"""
        return 1.0  # Simplified

    def _workload_balance_single(self, faculty_id: str, solution: Dict) -> float:
        """Workload balance for single faculty assignment"""
        return 1.0  # Simplified

    def _peak_spreading_single(self, time_slot_id: str, solution: Dict) -> float:
        """Peak spreading for single time slot"""
        slot_usage = sum(1 for _, (ts, _) in solution.items() if ts == time_slot_id)
        return max(0.5, 1.0 - slot_usage / 10)  # Penalty for overused slots

    def _lecture_continuity_single(self, course: Course, session: int, solution: Dict) -> float:
        """Continuity contribution of single session"""
        return 1.0  # Simplified

    def smart_crossover(self, parent1: Dict, parent2: Dict) -> Dict:
        """Constraint-preserving crossover"""
        child = {}

        for key in parent1.keys():
            # Try inheriting from parent1
            if random.random() < 0.5:
                child[key] = parent1[key]
            else:
                child[key] = parent2[key]

        # If infeasible, repair
        if not self._is_feasible(child):
            child = self._repair_solution(child)

        return child

    def smart_mutation(self, solution: Dict) -> Dict:
        """Constraint-preserving mutation"""
        mutated = solution.copy()

        for key in list(mutated.keys()):
            if random.random() < self.mutation_rate:
                valid_pairs = self.valid_domains.get(key, [])
                if valid_pairs:
                    mutated[key] = random.choice(valid_pairs)

        # Repair if necessary
        if not self._is_feasible(mutated):
            mutated = self._repair_solution(mutated)

        return mutated

    def _repair_solution(self, solution: Dict) -> Dict:
        """Repair infeasible solution"""
        # Simple repair: reassign conflicting courses
        repaired = solution.copy()

        for key, (time_slot, room_id) in list(repaired.items()):
            # If creates conflict, find alternative
            temp = repaired.copy()
            del temp[key]

            if not self._is_feasible_with_assignment(temp, key, (time_slot, room_id)):
                # Find alternative
                valid_pairs = self.valid_domains.get(key, [])
                for alt_time, alt_room in valid_pairs:
                    if self._is_feasible_with_assignment(temp, key, (alt_time, alt_room)):
                        repaired[key] = (alt_time, alt_room)
                        break

        return repaired

    def _is_feasible_with_assignment(self, partial_solution: Dict, key: Tuple, value: Tuple) -> bool:
        """Check if adding assignment maintains feasibility"""
        test_solution = partial_solution.copy()
        test_solution[key] = value
        return self._is_feasible(test_solution)

    def evolve(self) -> Dict:
        """Run parallel island model genetic algorithm evolution"""
        self.initialize_population()

        # Create islands
        self._create_islands()

        best_solution = None
        best_fitness = float('-inf')

        # Parallel island evolution
        with ProcessPoolExecutor(max_workers=self.num_islands) as executor:
            for generation in range(0, self.generations, self.migration_interval):
                # Evolve each island in parallel
                futures = []
                for i, island in enumerate(self.islands):
                    future = executor.submit(
                        self._evolve_island,
                        island,
                        self.migration_interval,
                        i
                    )
                    futures.append(future)

                # Collect evolved islands
                evolved_islands = []
                for future in futures:
                    evolved_island = future.result()
                    evolved_islands.append(evolved_island)

                self.islands = evolved_islands

                # Migration between islands
                self._migrate_individuals()

                # Track best solution
                current_best = self._get_global_best()
                current_fitness = self.fitness(current_best)

                if current_fitness > best_fitness:
                    best_fitness = current_fitness
                    best_solution = current_best

                if generation % 20 == 0:
                    logger.info(f"Generation {generation}: Best fitness = {best_fitness:.4f}")

        logger.info(f"Island GA optimization complete: Final fitness = {best_fitness:.4f}")
        return best_solution

    def _tournament_select(self, fitness_scores: List[Tuple[Dict, float]], k: int = 5) -> Dict:
        """Tournament selection"""
        tournament = random.sample(fitness_scores, min(k, len(fitness_scores)))
        winner = max(tournament, key=lambda x: x[1])
        return winner[0]

    def _create_islands(self):
        """Create islands for parallel evolution"""
        self.islands = []
        for i in range(self.num_islands):
            start_idx = i * self.island_size
            end_idx = min((i + 1) * self.island_size, len(self.population))
            island = self.population[start_idx:end_idx]
            self.islands.append(island)

    def _evolve_island(self, island: List[Dict], generations: int, island_id: int) -> List[Dict]:
        """Evolve a single island for specified generations"""
        current_population = island.copy()

        for gen in range(generations):
            # Evaluate fitness
            fitness_scores = [(sol, self.fitness(sol)) for sol in current_population]
            fitness_scores.sort(key=lambda x: x[1], reverse=True)

            # Selection and reproduction
            elite_count = max(1, int(len(current_population) * self.elitism_rate))
            new_population = [sol for sol, _ in fitness_scores[:elite_count]]

            # Fill rest with offspring
            while len(new_population) < len(current_population):
                if random.random() < self.crossover_rate:
                    parent1 = self._tournament_select(fitness_scores)
                    parent2 = self._tournament_select(fitness_scores)
                    child = self.smart_crossover(parent1, parent2)
                else:
                    parent = self._tournament_select(fitness_scores)
                    child = parent.copy()

                child = self.smart_mutation(child)
                new_population.append(child)

            current_population = new_population

        return current_population

    def _migrate_individuals(self):
        """Migrate best individuals between islands"""
        if len(self.islands) < 2:
            return

        # Get best individual from each island
        migrants = []
        for island in self.islands:
            if island:
                best = max(island, key=lambda x: self.fitness(x))
                migrants.append(best)

        # Ring topology migration
        for i in range(len(self.islands)):
            next_island = (i + 1) % len(self.islands)
            if migrants and self.islands[next_island]:
                # Replace worst individual with migrant
                worst_idx = min(range(len(self.islands[next_island])),
                              key=lambda x: self.fitness(self.islands[next_island][x]))
                self.islands[next_island][worst_idx] = migrants[i].copy()

    def _get_global_best(self) -> Dict:
        """Get best solution across all islands"""
        all_individuals = []
        for island in self.islands:
            all_individuals.extend(island)

        if not all_individuals:
            return self.population[0] if self.population else {}

        return max(all_individuals, key=lambda x: self.fitness(x))


def schedule_cluster(
    cluster_courses: List[Course],
    rooms: List[Room],
    time_slots: List[TimeSlot],
    faculty: Dict[str, Faculty],
    students: Dict[str, any],
    cluster_id: int,
    context_engine: Optional[MultiDimensionalContextEngine] = None
) -> Tuple[int, Optional[Dict], Dict]:
    """
    Schedule a single cluster using CP-SAT + GA pipeline.
    Returns: (cluster_id, solution, metrics)
    """
    logger.info(f"Scheduling cluster {cluster_id} with {len(cluster_courses)} courses")

    # Phase 2A: CP-SAT
    cpsat_solver = CPSATSolver(
        cluster_courses,
        rooms,
        time_slots,
        faculty,
        timeout_seconds=settings.CPSAT_TIMEOUT_SECONDS
    )

    feasible_solution = cpsat_solver.solve()

    if not feasible_solution:
        logger.error(f"Cluster {cluster_id} is infeasible!")
        return cluster_id, None, {"status": "infeasible"}

    # Phase 2B: GA Optimization with Context Engine
    ga_optimizer = GeneticAlgorithmOptimizer(
        cluster_courses,
        rooms,
        time_slots,
        faculty,
        students,
        initial_solution=feasible_solution,
        population_size=settings.GA_POPULATION_SIZE,
        generations=settings.GA_GENERATIONS,
        mutation_rate=settings.GA_MUTATION_RATE,
        crossover_rate=settings.GA_CROSSOVER_RATE,
        elitism_rate=settings.GA_ELITISM_RATE,
        context_engine=context_engine
    )

    optimized_solution = ga_optimizer.evolve()
    final_fitness = ga_optimizer.fitness(optimized_solution)

    metrics = {
        "status": "success",
        "cluster_id": cluster_id,
        "num_courses": len(cluster_courses),
        "fitness": final_fitness
    }

    logger.info(f"Cluster {cluster_id} scheduled successfully with fitness {final_fitness:.4f}")

    return cluster_id, optimized_solution, metrics


class HybridScheduler:
    """Stage 2 Orchestrator: Parallel hybrid micro-scheduling"""

    def __init__(
        self,
        clusters: Dict[int, List[str]],
        courses: List[Course],
        rooms: List[Room],
        time_slots: List[TimeSlot],
        faculty: Dict[str, Faculty],
        students: Dict[str, any],
        progress_tracker: ProgressTracker,
        context_engine: Optional[MultiDimensionalContextEngine] = None
    ):
        self.clusters = clusters
        self.courses_dict = {c.course_id: c for c in courses}
        self.rooms = rooms
        self.time_slots = time_slots
        self.faculty = faculty
        self.students = students
        self.progress_tracker = progress_tracker

        # Initialize context engine
        self.context_engine = context_engine or MultiDimensionalContextEngine()
        self.context_engine.initialize_context(courses, faculty, students, rooms, time_slots)

    def execute(self) -> Tuple[Dict[int, Dict], Dict]:
        """Execute parallel hybrid scheduling for all clusters"""
        logger.info("=" * 80)
        logger.info("STAGE 2: PARALLEL HYBRID MICRO-SCHEDULING")
        logger.info("=" * 80)

        self.progress_tracker.update(
            stage="cpsat_solving",
            progress=25.0,
            step=f"Starting parallel scheduling of {len(self.clusters)} clusters"
        )

        cluster_schedules = {}
        all_metrics = []

        # Parallel execution
        num_workers = min(multiprocessing.cpu_count(), len(self.clusters))

        with ProcessPoolExecutor(max_workers=num_workers) as executor:
            futures = []

            for cluster_id, course_ids in self.clusters.items():
                cluster_courses = [self.courses_dict[cid] for cid in course_ids]

                future = executor.submit(
                    schedule_cluster,
                    cluster_courses,
                    self.rooms,
                    self.time_slots,
                    self.faculty,
                    self.students,
                    cluster_id,
                    self.context_engine
                )
                futures.append(future)

            # Collect results
            completed = 0
            for future in futures:
                cluster_id, solution, metrics = future.result()

                if solution is None:
                    logger.error(f"Cluster {cluster_id} failed!")
                    return None, {"error": f"Cluster {cluster_id} infeasible"}

                cluster_schedules[cluster_id] = solution
                all_metrics.append(metrics)

                completed += 1
                progress = 25.0 + (completed / len(futures)) * 45.0
                self.progress_tracker.update(
                    stage="ga_optimization",
                    progress=progress,
                    step=f"Completed {completed}/{len(futures)} clusters",
                    details={"clusters_completed": completed, "total_clusters": len(futures)}
                )

        logger.info("Stage 2 complete: All clusters scheduled")

        return cluster_schedules, {"cluster_metrics": all_metrics}
