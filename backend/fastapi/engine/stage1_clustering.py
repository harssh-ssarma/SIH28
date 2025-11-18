"""Stage 1: Intelligent Constraint Graph Clustering with Louvain Algorithm"""
import networkx as nx
import community.community_louvain as louvain
import numpy as np
from typing import List, Dict, Tuple, Set
import logging
from models.timetable_models import Course, Faculty, Student
from utils.progress_tracker import ProgressTracker

logger = logging.getLogger(__name__)


class ConstraintGraphClustering:
    """
    Implements intelligent constraint graph clustering using Louvain algorithm
    for modular timetabling decomposition.
    """

    def __init__(
        self,
        courses: List[Course],
        faculty: Dict[str, Faculty],
        students: Dict[str, Student],
        progress_tracker: ProgressTracker,
        modularity_threshold: float = 0.7,
        density_threshold: float = 0.6,
        coupling_threshold: float = 0.15
    ):
        self.courses = courses
        self.faculty = faculty
        self.students = students
        self.progress_tracker = progress_tracker
        self.modularity_threshold = modularity_threshold
        self.density_threshold = density_threshold
        self.coupling_threshold = coupling_threshold
        self.graph = None

        # Weight parameters for edge weight calculation
        self.alpha_faculty = 10.0
        self.alpha_student = 10.0
        self.alpha_batch = 5.0
        self.alpha_room = 3.0

    def build_constraint_graph(self) -> nx.Graph:
        """
        Construct weighted undirected constraint graph G = (V, E, w)
        - Vertices: Each course is a vertex
        - Edges: Exist if courses share constraints
        - Weights: Quantify constraint strength
        """
        self.progress_tracker.update(
            stage="building_graph",
            progress=5.0,
            step="Building constraint graph"
        )

        G = nx.Graph()

        # Add all courses as vertices
        for course in self.courses:
            G.add_node(
                course.course_id,
                course_code=course.course_code,
                faculty_id=course.faculty_id,
                student_count=len(course.student_ids),
                credits=course.credits
            )

        logger.info(f"Added {len(self.courses)} course vertices")

        # Build edge weights based on shared constraints
        total_comparisons = len(self.courses) * (len(self.courses) - 1) // 2
        comparison_count = 0

        for i, course_i in enumerate(self.courses):
            for j, course_j in enumerate(self.courses[i+1:], start=i+1):
                weight = self._calculate_edge_weight(course_i, course_j)

                if weight > 0:
                    G.add_edge(course_i.course_id, course_j.course_id, weight=weight)

                comparison_count += 1
                if comparison_count % 100 == 0:
                    progress = 5.0 + (comparison_count / total_comparisons) * 5.0
                    self.progress_tracker.update(
                        progress=progress,
                        step=f"Computing edge weights: {comparison_count}/{total_comparisons}"
                    )

        logger.info(f"Built graph with {G.number_of_edges()} edges")
        self.graph = G
        return G

    def _calculate_edge_weight(self, course_i: Course, course_j: Course) -> float:
        """
        Calculate edge weight w(c_i, c_j) based on NEP 2020 student-centric model:
        1. Shared faculty (same prof teaches both)
        2. Student overlap (individual students enrolled in BOTH courses - PRIMARY signal)
        3. Room competition (same special facility needs)

        NOTE: Batch overlap removed - NEP 2020 students take interdisciplinary electives,
        so batches are NOT homogeneous. Only actual student enrollment overlap matters.
        """
        weight = 0.0

        # α₁ · I[faculty(c_i) = faculty(c_j)] - Shared faculty
        if course_i.faculty_id == course_j.faculty_id:
            weight += self.alpha_faculty

        # α₂ · |students(c_i) ∩ students(c_j)| / max_enrollment - Student overlap (PRIMARY)
        # This is the CRITICAL constraint for NEP 2020 - students enrolled in BOTH courses
        # create hard conflicts that must be scheduled in different time slots
        students_i = set(course_i.student_ids)
        students_j = set(course_j.student_ids)
        overlap = len(students_i & students_j)
        if overlap > 0:
            max_enrollment = max(len(students_i), len(students_j))
            weight += self.alpha_student * (overlap / max_enrollment)

        # α₃ · room_competition_score(c_i, c_j) - Room scarcity
        # Courses with same required features compete for scarce resources
        features_i = set(course_i.required_features)
        features_j = set(course_j.required_features)
        if features_i and features_j:
            feature_overlap = len(features_i & features_j) / max(len(features_i), len(features_j))
            weight += self.alpha_room * feature_overlap

        return weight

    def apply_louvain_clustering(self) -> Dict[str, int]:
        """
        Apply Louvain algorithm to partition graph into clusters by maximizing modularity Q.

        Modularity Q = (1/2m) · Σᵢⱼ [A_ij - (k_i · k_j)/2m] · δ(c_i, c_j)

        Returns:
            Dictionary mapping course_id to cluster_id
        """
        self.progress_tracker.update(
            stage="clustering",
            progress=10.0,
            step="Applying Louvain community detection"
        )

        # Apply Louvain algorithm
        partition = louvain.best_partition(self.graph, weight='weight')

        # Calculate modularity
        modularity = louvain.modularity(partition, self.graph, weight='weight')

        logger.info(f"Louvain clustering complete: {len(set(partition.values()))} clusters, modularity={modularity:.4f}")

        self.progress_tracker.update(
            progress=15.0,
            step=f"Clustering complete: {len(set(partition.values()))} clusters",
            details={
                "num_clusters": len(set(partition.values())),
                "modularity": round(modularity, 4)
            }
        )

        return partition, modularity

    def validate_and_refine_clusters(
        self,
        partition: Dict[str, int],
        modularity: float
    ) -> Tuple[Dict[int, List[str]], Dict]:
        """
        Validate cluster quality and refine if necessary.

        Metrics:
        - Intra-cluster density > 0.6
        - Inter-cluster coupling < 0.15
        - Modularity Q > 0.7
        """
        self.progress_tracker.update(
            progress=17.0,
            step="Validating cluster quality"
        )

        # Organize courses by cluster
        clusters = {}
        for course_id, cluster_id in partition.items():
            if cluster_id not in clusters:
                clusters[cluster_id] = []
            clusters[cluster_id].append(course_id)

        # Calculate metrics
        metrics = {
            "modularity": modularity,
            "num_clusters": len(clusters),
            "intra_cluster_densities": {},
            "inter_cluster_coupling": 0.0,
            "cluster_sizes": {}
        }

        total_edges = self.graph.number_of_edges()
        inter_cluster_edges = 0

        for cluster_id, course_ids in clusters.items():
            # Calculate intra-cluster density
            subgraph = self.graph.subgraph(course_ids)
            n = len(course_ids)
            possible_edges = n * (n - 1) / 2
            actual_edges = subgraph.number_of_edges()
            density = actual_edges / possible_edges if possible_edges > 0 else 0

            metrics["intra_cluster_densities"][cluster_id] = density
            metrics["cluster_sizes"][cluster_id] = n

            logger.info(f"Cluster {cluster_id}: {n} courses, density={density:.4f}")

        # Calculate inter-cluster coupling
        for u, v in self.graph.edges():
            if partition[u] != partition[v]:
                inter_cluster_edges += 1

        metrics["inter_cluster_coupling"] = inter_cluster_edges / total_edges if total_edges > 0 else 0

        # Check thresholds
        quality_pass = (
            modularity >= self.modularity_threshold and
            metrics["inter_cluster_coupling"] <= self.coupling_threshold and
            all(d >= self.density_threshold for d in metrics["intra_cluster_densities"].values())
        )

        if not quality_pass:
            logger.warning(f"Cluster quality below thresholds. Applying refinements...")
            clusters = self._refine_clusters(clusters, partition)

        self.progress_tracker.update(
            progress=20.0,
            step="Cluster validation complete",
            details=metrics
        )

        return clusters, metrics

    def _refine_clusters(
        self,
        clusters: Dict[int, List[str]],
        partition: Dict[str, int]
    ) -> Dict[int, List[str]]:
        """
        Refine clusters by:
        1. Bisecting large clusters with low density
        2. Merging small under-dense clusters
        """
        refined_clusters = {}
        next_cluster_id = max(clusters.keys()) + 1

        for cluster_id, course_ids in clusters.items():
            # Check if cluster too large (>100 courses) or low density
            if len(course_ids) > 100:
                # Bisect large cluster
                mid = len(course_ids) // 2
                refined_clusters[cluster_id] = course_ids[:mid]
                refined_clusters[next_cluster_id] = course_ids[mid:]
                next_cluster_id += 1
                logger.info(f"Bisected cluster {cluster_id} into {cluster_id} and {next_cluster_id-1}")
            else:
                refined_clusters[cluster_id] = course_ids

        return refined_clusters

    def execute(self) -> Tuple[Dict[int, List[str]], Dict]:
        """
        Execute complete Stage 1: Constraint Graph Clustering

        Returns:
            - clusters: Dict mapping cluster_id to list of course_ids
            - metrics: Clustering quality metrics
        """
        logger.info("=" * 80)
        logger.info("STAGE 1: INTELLIGENT CONSTRAINT GRAPH CLUSTERING")
        logger.info("=" * 80)

        # Step 1: Build constraint graph
        self.build_constraint_graph()

        # Step 2: Apply Louvain clustering
        partition, modularity = self.apply_louvain_clustering()

        # Step 3: Validate and refine
        clusters, metrics = self.validate_and_refine_clusters(partition, modularity)

        logger.info(f"Stage 1 complete: {len(clusters)} clusters ready for parallel scheduling")

        return clusters, metrics
