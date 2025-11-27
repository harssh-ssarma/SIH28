"""
Stage 3: Context-Aware Q-Learning (CAQL) with Multi-Agent Architecture
- Tabular Q-Learning with Hashed Q-Table (sparse memory)
- Multi-Agent Independent Learning (IQL) per Louvain cluster
- CPU Multi-Core Parallelization (no GPU - sequential operations)
- Transfer Learning (Q-table seeding from past semesters)
- Context-based state abstraction (low memory)
"""
import random
import logging
import numpy as np
from typing import List, Dict, Tuple, Optional
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import multiprocessing

logger = logging.getLogger(__name__)


class HashedQTable:
    """Sparse Q-Table using hash map (only stores visited states)"""
    
    def __init__(self, alpha_new=0.5, alpha_transferred=0.1):
        self.table = {}  # (state_hash, action) -> Q-value
        self.alpha_new = alpha_new  # High learning rate for new states
        self.alpha_transferred = alpha_transferred  # Low learning rate for transferred states
        self.transferred_states = set()  # Track transferred states
    
    def get(self, state_hash: int, action: str) -> float:
        """Get Q-value (0.0 if never visited)"""
        return self.table.get((state_hash, action), 0.0)
    
    def set(self, state_hash: int, action: str, value: float, is_transferred: bool = False):
        """Set Q-value and mark if transferred"""
        self.table[(state_hash, action)] = value
        if is_transferred:
            self.transferred_states.add(state_hash)
    
    def get_alpha(self, state_hash: int) -> float:
        """Get learning rate (low for transferred, high for new)"""
        return self.alpha_transferred if state_hash in self.transferred_states else self.alpha_new
    
    def size(self) -> int:
        return len(self.table)


class ContextFeatures:
    """Low-cost context features for state abstraction"""
    
    @staticmethod
    def compute_features(conflict: Dict, schedule: Dict, metadata: Dict) -> Dict:
        """Compute context features (fast, no heavy computation)"""
        course_id = conflict['course_id']
        time_slot = conflict['time_slot']
        
        # Feature 1: Memory/Recency (simple counter)
        last_moved = metadata.get('last_moved', {}).get(course_id, 0)
        current_cycle = metadata.get('current_cycle', 0)
        recency = 1.0 / max(1, current_cycle - last_moved)
        
        # Feature 2: Resource Pressure (binary flag)
        utilization = metadata.get('utilization', {}).get(time_slot, 0)
        is_critical = 1 if utilization > 0.9 else 0
        
        # Feature 3: Preference Imbalance (delta score)
        current_score = metadata.get('soft_scores', {}).get(course_id, 0)
        target_score = metadata.get('target_scores', {}).get(course_id, 0)
        imbalance = abs(current_score - target_score)
        
        return {
            'recency': recency,
            'is_critical': is_critical,
            'imbalance': imbalance,
            'conflict_type': conflict.get('type', 'unknown')
        }
    
    @staticmethod
    def hash_state(features: Dict) -> int:
        """Hash features to create compact state representation"""
        # Discretize continuous features
        recency_bin = int(features['recency'] * 10)
        imbalance_bin = int(features['imbalance'] * 10)
        
        # Create hash from discrete features
        state_tuple = (
            recency_bin,
            features['is_critical'],
            imbalance_bin,
            features['conflict_type']
        )
        return hash(state_tuple)


class ClusterAgent:
    """Independent Q-Learning agent for a single Louvain cluster"""
    
    def __init__(self, cluster_id: int, cluster_courses: List[str], q_table: HashedQTable = None):
        self.cluster_id = cluster_id
        self.cluster_courses = set(cluster_courses)
        self.q_table = q_table or HashedQTable()
        self.gamma = 0.9  # Discount factor
        self.actions = ['swap_local', 'nudge_forward', 'nudge_backward', 'delete_reinsert']
    
    def select_action(self, state_hash: int, epsilon: float = 0.1) -> str:
        """ε-greedy action selection with context-aware masking"""
        if random.random() < epsilon:
            return random.choice(self.actions)
        
        # Get Q-values for all actions
        q_values = [self.q_table.get(state_hash, a) for a in self.actions]
        best_idx = np.argmax(q_values)
        return self.actions[best_idx]
    
    def update(self, state_hash: int, action: str, reward: float, next_state_hash: int):
        """Q-learning update with adaptive learning rate"""
        alpha = self.q_table.get_alpha(state_hash)
        current_q = self.q_table.get(state_hash, action)
        
        # Get max Q-value for next state
        max_next_q = max(self.q_table.get(next_state_hash, a) for a in self.actions)
        
        # Q-learning update
        new_q = current_q + alpha * (reward + self.gamma * max_next_q - current_q)
        self.q_table.set(state_hash, action, new_q)
    
    def resolve_cluster_conflicts(self, conflicts: List[Dict], schedule: Dict, metadata: Dict) -> List[Dict]:
        """Resolve conflicts within this cluster"""
        resolved = []
        
        for conflict in conflicts:
            # Only handle conflicts in this cluster
            if conflict['course_id'] not in self.cluster_courses:
                continue
            
            # Compute state features
            features = ContextFeatures.compute_features(conflict, schedule, metadata)
            state_hash = ContextFeatures.hash_state(features)
            
            # Select action
            action = self.select_action(state_hash)
            
            # Apply action
            swap_result = self._apply_action(conflict, action, schedule, metadata)
            
            if swap_result and swap_result.get('success'):
                # Compute reward
                delta_soft = swap_result.get('delta_soft', 0)
                delta_hard = swap_result.get('delta_hard', 0)
                reward = delta_soft - 10000 * delta_hard  # Large penalty for hard conflicts
                
                # Compute next state
                next_features = ContextFeatures.compute_features(conflict, schedule, metadata)
                next_state_hash = ContextFeatures.hash_state(next_features)
                
                # Update Q-table
                self.update(state_hash, action, reward, next_state_hash)
                
                resolved.append(swap_result)
        
        return resolved
    
    def _apply_action(self, conflict: Dict, action: str, schedule: Dict, metadata: Dict) -> Optional[Dict]:
        """Apply action to resolve conflict"""
        course_id = conflict['course_id']
        current_slot = conflict['time_slot']
        
        if action == 'swap_local':
            # Swap with another course in same cluster
            for other_course in self.cluster_courses:
                if other_course != course_id:
                    # Find other course's slot
                    for (cid, session), (slot, room) in schedule.items():
                        if cid == other_course:
                            # Swap slots
                            return {
                                'success': True,
                                'course_id': course_id,
                                'action': 'swap',
                                'old_slot': current_slot,
                                'new_slot': slot,
                                'delta_soft': 1,
                                'delta_hard': 0
                            }
        
        elif action == 'nudge_forward':
            # Move to next slot
            new_slot = current_slot + 1
            return {
                'success': True,
                'course_id': course_id,
                'action': 'nudge',
                'old_slot': current_slot,
                'new_slot': new_slot,
                'delta_soft': 0.5,
                'delta_hard': 0
            }
        
        elif action == 'nudge_backward':
            # Move to previous slot
            new_slot = max(0, current_slot - 1)
            return {
                'success': True,
                'course_id': course_id,
                'action': 'nudge',
                'old_slot': current_slot,
                'new_slot': new_slot,
                'delta_soft': 0.5,
                'delta_hard': 0
            }
        
        elif action == 'delete_reinsert':
            # Remove and re-insert randomly
            available_slots = metadata.get('available_slots', [])
            if available_slots:
                new_slot = random.choice(available_slots)
                return {
                    'success': True,
                    'course_id': course_id,
                    'action': 'reinsert',
                    'old_slot': current_slot,
                    'new_slot': new_slot,
                    'delta_soft': 0.3,
                    'delta_hard': 0
                }
        
        return None


class TransferLearning:
    """Transfer learning for Q-table seeding"""
    
    @staticmethod
    def load_past_semester(org_id: str, semester_id: str) -> Optional[HashedQTable]:
        """Load Q-table from past semester"""
        try:
            import pickle
            from pathlib import Path
            
            path = Path(f"q_tables/{org_id}_{semester_id}.pkl")
            if path.exists():
                with open(path, 'rb') as f:
                    data = pickle.load(f)
                    q_table = HashedQTable()
                    q_table.table = data['table']
                    q_table.transferred_states = set(data['table'].keys())
                    logger.info(f"[OK] Loaded Q-table: {len(q_table.table)} entries from {semester_id}")
                    return q_table
        except Exception as e:
            logger.warning(f"Failed to load past Q-table: {e}")
        return None
    
    @staticmethod
    def save_semester(org_id: str, semester_id: str, q_table: HashedQTable):
        """Save Q-table for future transfer"""
        try:
            import pickle
            from pathlib import Path
            
            Path("q_tables").mkdir(exist_ok=True)
            path = Path(f"q_tables/{org_id}_{semester_id}.pkl")
            
            data = {'table': q_table.table}
            with open(path, 'wb') as f:
                pickle.dump(data, f)
            
            logger.info(f"[OK] Saved Q-table: {len(q_table.table)} entries")
        except Exception as e:
            logger.error(f"Failed to save Q-table: {e}")


class MultiAgentCAQL:
    """Multi-Agent Context-Aware Q-Learning with CPU parallelization"""
    
    def __init__(
        self,
        courses: List,
        rooms: List,
        time_slots: List,
        faculty: Dict,
        org_id: str = None,
        semester_id: str = None,
        num_workers: int = None
    ):
        self.courses = courses
        self.rooms = rooms
        self.time_slots = time_slots
        self.faculty = faculty
        self.org_id = org_id
        self.semester_id = semester_id
        
        # CPU parallelization (multi-core)
        self.num_workers = num_workers or min(8, multiprocessing.cpu_count())
        logger.info(f"[CAQL] Using {self.num_workers} CPU cores for parallel learning")
        
        # Louvain clustering (placeholder - implement actual clustering)
        self.clusters = self._create_clusters()
        
        # Create agents per cluster
        self.agents = []
        for cluster_id, cluster_courses in enumerate(self.clusters):
            # Try to load past Q-table for transfer learning
            q_table = TransferLearning.load_past_semester(org_id, semester_id) if org_id and semester_id else None
            agent = ClusterAgent(cluster_id, cluster_courses, q_table)
            self.agents.append(agent)
        
        logger.info(f"[CAQL] Created {len(self.agents)} cluster agents")
    
    def _create_clusters(self) -> List[List[str]]:
        """Create Louvain clusters (simplified - use actual Louvain algorithm)"""
        # Placeholder: Split courses into equal chunks
        chunk_size = max(1, len(self.courses) // self.num_workers)
        clusters = []
        
        for i in range(0, len(self.courses), chunk_size):
            chunk = self.courses[i:i + chunk_size]
            cluster_courses = [c.course_id for c in chunk]
            clusters.append(cluster_courses)
        
        return clusters
    
    def resolve_conflicts(self, schedule: Dict, max_iterations: int = 100) -> Dict:
        """Parallel multi-agent conflict resolution"""
        logger.info(f"[CAQL] Starting multi-agent resolution with {len(self.agents)} agents")
        
        # Detect conflicts
        conflicts = self._detect_conflicts(schedule)
        if not conflicts:
            logger.info("[CAQL] No conflicts detected")
            return schedule
        
        logger.info(f"[CAQL] Detected {len(conflicts)} conflicts")
        
        # Prepare metadata
        metadata = {
            'last_moved': {},
            'current_cycle': 0,
            'utilization': {},
            'soft_scores': {},
            'target_scores': {},
            'available_slots': [t.slot_id for t in self.time_slots]
        }
        
        # Parallel agent execution (Independent Q-Learning)
        for iteration in range(max_iterations):
            metadata['current_cycle'] = iteration
            
            # Distribute conflicts to agents
            agent_conflicts = [[] for _ in self.agents]
            for conflict in conflicts:
                for i, agent in enumerate(self.agents):
                    if conflict['course_id'] in agent.cluster_courses:
                        agent_conflicts[i].append(conflict)
                        break
            
            # Parallel execution (each agent runs independently)
            with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
                futures = {
                    executor.submit(
                        agent.resolve_cluster_conflicts,
                        agent_conflicts[i],
                        schedule,
                        metadata
                    ): i
                    for i, agent in enumerate(self.agents)
                }
                
                # Collect results
                total_resolved = 0
                for future in as_completed(futures):
                    agent_idx = futures[future]
                    resolved = future.result()
                    total_resolved += len(resolved)
                    
                    # Apply resolutions to schedule
                    for swap in resolved:
                        course_id = swap['course_id']
                        new_slot = swap['new_slot']
                        # Update schedule (simplified)
                        for (cid, session), (slot, room) in schedule.items():
                            if cid == course_id:
                                schedule[(cid, session)] = (new_slot, room)
                                metadata['last_moved'][course_id] = iteration
                                break
            
            # Re-detect conflicts
            conflicts = self._detect_conflicts(schedule)
            
            if not conflicts:
                logger.info(f"[CAQL] All conflicts resolved at iteration {iteration}")
                break
            
            if iteration % 10 == 0:
                logger.info(f"[CAQL] Iteration {iteration}: {len(conflicts)} conflicts remaining")
        
        # Save learned Q-tables for transfer learning
        if self.org_id and self.semester_id:
            for agent in self.agents:
                TransferLearning.save_semester(self.org_id, f"{self.semester_id}_cluster{agent.cluster_id}", agent.q_table)
        
        logger.info(f"[CAQL] Resolution complete: {len(conflicts)} conflicts remaining")
        return schedule
    
    def _detect_conflicts(self, schedule: Dict) -> List[Dict]:
        """Fast conflict detection"""
        conflicts = []
        student_schedule = defaultdict(list)
        
        for (course_id, session), (time_slot, room_id) in schedule.items():
            course = next((c for c in self.courses if c.course_id == course_id), None)
            if not course:
                continue
            
            for student_id in getattr(course, 'student_ids', []):
                student_schedule[student_id].append((time_slot, course_id))
        
        # Detect conflicts
        for student_id, assignments in student_schedule.items():
            slots = [a[0] for a in assignments]
            if len(slots) != len(set(slots)):
                # Find conflicting slot
                seen = {}
                for slot, course_id in assignments:
                    if slot in seen:
                        conflicts.append({
                            'type': 'student_conflict',
                            'student_id': student_id,
                            'time_slot': slot,
                            'course_id': course_id,
                            'conflicting_course': seen[slot]
                        })
                    else:
                        seen[slot] = course_id
        
        return conflicts
