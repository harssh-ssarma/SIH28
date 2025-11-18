"""
Prometheus Metrics for FastAPI Timetable Generation Service
ENTERPRISE PATTERN: Observability and monitoring
"""
from prometheus_client import Counter, Histogram, Gauge, Info
from prometheus_fastapi_instrumentator import Instrumentator
import logging

logger = logging.getLogger(__name__)


# =============================================================================
# CUSTOM METRICS: Timetable Generation
# =============================================================================

# Generation Requests
generation_requests_total = Counter(
    'timetable_generation_requests_total',
    'Total number of timetable generation requests',
    ['organization_id', 'priority']
)

generation_requests_success = Counter(
    'timetable_generation_requests_success_total',
    'Total number of successful timetable generations',
    ['organization_id', 'priority']
)

generation_requests_failed = Counter(
    'timetable_generation_requests_failed_total',
    'Total number of failed timetable generations',
    ['organization_id', 'priority', 'error_type']
)

# Generation Time Metrics
generation_duration_seconds = Histogram(
    'timetable_generation_duration_seconds',
    'Time spent generating timetables',
    ['organization_id', 'priority', 'phase'],
    buckets=[30, 60, 120, 300, 600, 900, 1800]  # 30s, 1m, 2m, 5m, 10m, 15m, 30m
)

# Algorithm Phase Metrics
algorithm_phase_duration = Histogram(
    'timetable_algorithm_phase_duration_seconds',
    'Time spent in each algorithm phase',
    ['phase'],
    buckets=[1, 5, 10, 30, 60, 120, 300]
)

# Queue Metrics
celery_queue_depth = Gauge(
    'celery_queue_depth',
    'Number of tasks in Celery queues',
    ['queue_name']
)

celery_active_workers = Gauge(
    'celery_active_workers',
    'Number of active Celery workers',
    ['queue_name']
)

# Resource Metrics
redis_connections = Gauge(
    'redis_connections_total',
    'Total Redis connections'
)

redis_memory_usage = Gauge(
    'redis_memory_usage_bytes',
    'Redis memory usage in bytes'
)

# Quality Metrics
timetable_quality_score = Histogram(
    'timetable_quality_score',
    'Quality score of generated timetables (0-100)',
    ['organization_id', 'variant'],
    buckets=[50, 60, 70, 80, 85, 90, 95, 100]
)

timetable_conflicts = Counter(
    'timetable_conflicts_total',
    'Total number of conflicts in generated timetables',
    ['organization_id', 'conflict_type']
)

# Variant Generation Metrics
variants_generated = Counter(
    'timetable_variants_generated_total',
    'Total number of variants generated',
    ['organization_id']
)

variant_selection = Counter(
    'timetable_variant_selected',
    'Which variant was selected by users',
    ['organization_id', 'variant_rank']
)

# WebSocket Metrics
websocket_connections = Gauge(
    'websocket_connections_active',
    'Number of active WebSocket connections'
)

websocket_messages_sent = Counter(
    'websocket_messages_sent_total',
    'Total WebSocket messages sent',
    ['message_type']
)

# Cache Metrics
redis_cache_hits = Counter(
    'redis_cache_hits_total',
    'Total Redis cache hits',
    ['cache_type']
)

redis_cache_misses = Counter(
    'redis_cache_misses_total',
    'Total Redis cache misses',
    ['cache_type']
)


# =============================================================================
# INSTRUMENTATOR: Auto-instrument FastAPI
# =============================================================================

def setup_metrics(app):
    """
    Setup Prometheus metrics for FastAPI application.

    Automatically instruments:
    - HTTP request count
    - HTTP request duration
    - HTTP request size
    - HTTP response size
    - Active requests

    Args:
        app: FastAPI application instance
    """
    instrumentator = Instrumentator(
        should_group_status_codes=True,
        should_ignore_untemplated=True,
        should_respect_env_var=True,
        should_instrument_requests_inprogress=True,
        excluded_handlers=["/metrics", "/health", "/docs", "/openapi.json"],
        env_var_name="ENABLE_METRICS",
        inprogress_name="fastapi_inprogress_requests",
        inprogress_labels=True,
    )

    # Add default metrics
    instrumentator.instrument(app)

    # Expose metrics endpoint
    instrumentator.expose(app, endpoint="/metrics", include_in_schema=False)

    logger.info("Prometheus metrics enabled at /metrics")

    return instrumentator


# =============================================================================
# HELPER FUNCTIONS: Record Metrics
# =============================================================================

def record_generation_request(organization_id: str, priority: str):
    """Record a new generation request."""
    generation_requests_total.labels(
        organization_id=organization_id,
        priority=priority
    ).inc()


def record_generation_success(organization_id: str, priority: str, duration: float):
    """Record a successful generation."""
    generation_requests_success.labels(
        organization_id=organization_id,
        priority=priority
    ).inc()

    generation_duration_seconds.labels(
        organization_id=organization_id,
        priority=priority,
        phase='total'
    ).observe(duration)


def record_generation_failure(organization_id: str, priority: str, error_type: str):
    """Record a failed generation."""
    generation_requests_failed.labels(
        organization_id=organization_id,
        priority=priority,
        error_type=error_type
    ).inc()


def record_phase_duration(phase: str, duration: float):
    """Record algorithm phase duration."""
    algorithm_phase_duration.labels(phase=phase).observe(duration)


def record_quality_score(organization_id: str, variant: int, score: float):
    """Record timetable quality score."""
    timetable_quality_score.labels(
        organization_id=organization_id,
        variant=str(variant)
    ).observe(score)


def record_conflict(organization_id: str, conflict_type: str):
    """Record a conflict in generated timetable."""
    timetable_conflicts.labels(
        organization_id=organization_id,
        conflict_type=conflict_type
    ).inc()


def update_queue_depth(queue_name: str, depth: int):
    """Update Celery queue depth."""
    celery_queue_depth.labels(queue_name=queue_name).set(depth)


def update_active_workers(queue_name: str, count: int):
    """Update active Celery workers count."""
    celery_active_workers.labels(queue_name=queue_name).set(count)


def record_websocket_connection(delta: int = 1):
    """Record WebSocket connection change."""
    if delta > 0:
        websocket_connections.inc()
    else:
        websocket_connections.dec()


def record_websocket_message(message_type: str):
    """Record WebSocket message sent."""
    websocket_messages_sent.labels(message_type=message_type).inc()


def record_cache_hit(cache_type: str):
    """Record Redis cache hit."""
    redis_cache_hits.labels(cache_type=cache_type).inc()


def record_cache_miss(cache_type: str):
    """Record Redis cache miss."""
    redis_cache_misses.labels(cache_type=cache_type).inc()
