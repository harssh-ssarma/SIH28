# Enterprise Architecture - Timetable Generation System

## Overview
Scalable, fault-tolerant, async architecture for large-scale timetable generation (1800+ courses, 19000+ students).

## Architecture Flow

```
┌─────────────┐
│   Frontend  │ (React/Next.js)
└──────┬──────┘
       │ 1. POST /api/timetables/generate
       ↓
┌─────────────┐
│   Django    │ (REST API + Database)
│   API       │
└──────┬──────┘
       │ 2. Create GenerationJob in DB
       │ 3. Queue Celery task
       │ 4. Return job_id immediately (200 OK)
       ↓
┌─────────────┐
│   Celery    │ (Async Task Queue)
│   Worker    │
└──────┬──────┘
       │ 5. Call FastAPI POST /api/generate_variants
       │ 6. FastAPI returns immediately (queued)
       │ 7. Celery task completes in <5s
       ↓
┌─────────────┐
│   FastAPI   │ (AI Engine)
│   Service   │
└──────┬──────┘
       │ 8. Run generation in background (2-5 min)
       │ 9. Update Redis every 5 seconds
       │ 10. On completion: Send Celery callback
       ↓
┌─────────────┐
│    Redis    │ (Progress Cache)
│   (Upstash) │
└──────┬──────┘
       │
       ↓
┌─────────────┐
│   Frontend  │ Polls Django every 2s
│   Polling   │ Django reads from Redis
└─────────────┘
```

## Component Responsibilities

### 1. Frontend (Next.js)
- **Initiates**: POST to Django `/api/timetables/generate`
- **Receives**: `job_id` immediately (within 1 second)
- **Polls**: Django `/api/progress/{job_id}` every 2 seconds
- **Displays**: Real-time progress (0-100%)
- **Timeout**: None (polls until completion or failure)

### 2. Django (Core API)
- **Creates**: `GenerationJob` record in PostgreSQL
- **Queues**: Celery task `generate_timetable_task`
- **Returns**: `job_id` to frontend immediately
- **Serves**: Progress endpoint (reads from Redis)
- **Updates**: Final job status in database (via callback)

### 3. Celery (Task Queue)
- **Receives**: Task from Django
- **Calls**: FastAPI `/api/generate_variants` (fire-and-forget)
- **Timeout**: 5 seconds (FastAPI must respond immediately)
- **Completes**: Task in <5 seconds
- **Retries**: 2 times on failure (60s delay)

### 4. FastAPI (AI Engine)
- **Receives**: Generation request from Celery
- **Returns**: Immediately with `status: queued` (<1 second)
- **Runs**: Generation in background (2-5 minutes)
- **Updates**: Redis progress every 5 seconds
- **Callbacks**: Sends Celery task when complete
- **Handles**: 1800+ courses, 19000+ students, 2320 faculty

### 5. Redis (Progress Store)
- **Stores**: Progress data with 2-hour TTL
- **Key**: `progress:job:{job_id}`
- **Data**: `{job_id, progress, status, stage, message, timestamp}`
- **Read**: By Django (for frontend polling)
- **Write**: By FastAPI (during generation)

## Data Flow Timeline

```
Time    Component   Action
────────────────────────────────────────────────────────────
0.0s    Frontend    POST /api/timetables/generate
0.1s    Django      Create job, queue Celery, return job_id
0.2s    Frontend    Receives job_id, starts polling
0.5s    Celery      Receives task, calls FastAPI
0.6s    FastAPI     Returns "queued", starts background
0.7s    Celery      Task completes successfully
2.0s    Frontend    First poll: "queued, 0%"
5.0s    FastAPI     Updates Redis: "loading data, 10%"
6.0s    Frontend    Poll: "loading data, 10%"
15.0s   FastAPI     Updates Redis: "generating, 30%"
16.0s   Frontend    Poll: "generating, 30%"
...     ...         ...
180.0s  FastAPI     Generation complete, sends callback
180.1s  Celery      Receives callback, updates database
182.0s  Frontend    Poll: "completed, 100%"
182.1s  Frontend    Fetches results, displays timetable
```

## Failure Handling

### Scenario 1: FastAPI Down
- **Celery**: Fails after 5s timeout
- **Django**: Marks job as failed in database
- **Redis**: Updated with error message
- **Frontend**: Shows error immediately

### Scenario 2: Redis Down
- **FastAPI**: Continues generation, logs errors
- **Django**: Returns "unknown" status to frontend
- **Frontend**: Shows "processing" message
- **Recovery**: When Redis comes back, progress resumes

### Scenario 3: Celery Down
- **Django**: Task queued in Redis (persistent)
- **Celery**: Picks up task when restarted
- **Frontend**: Continues polling
- **Impact**: Delayed start (no data loss)

### Scenario 4: Database Down
- **Django**: Cannot create job (returns 500)
- **Frontend**: Shows error, user retries
- **Impact**: No job created (safe failure)

### Scenario 5: Generation Timeout (>30 min)
- **FastAPI**: Marks as failed, sends callback
- **Redis**: Updated with timeout error
- **Database**: Job marked as failed
- **Frontend**: Shows timeout message

## Performance Characteristics

### Latency
- **Job Creation**: <500ms (Django + Celery queue)
- **FastAPI Response**: <1s (just queues background task)
- **Progress Updates**: Every 5s (Redis write)
- **Frontend Polling**: Every 2s (Redis read)

### Throughput
- **Concurrent Jobs**: 10 per organization (configurable)
- **Total System**: 100+ concurrent jobs (with proper resources)
- **Data Size**: 1800 courses, 19000 students, 2320 faculty
- **Generation Time**: 2-5 minutes (depends on data size)

### Scalability
- **Horizontal**: Add more Celery workers
- **Vertical**: FastAPI uses all CPU cores (OR-Tools parallel)
- **Database**: PostgreSQL connection pooling
- **Cache**: Redis cluster for high availability

## Configuration

### Django Settings
```python
CELERY_BROKER_URL = 'rediss://...'  # Upstash Redis
CELERY_TASK_SOFT_TIME_LIMIT = 3600  # 1 hour
FASTAPI_URL = 'http://localhost:8001'
```

### Celery Settings
```python
task_soft_time_limit = 3600  # 1 hour
task_time_limit = 7200  # 2 hours
task_max_retries = 2
task_default_retry_delay = 60  # 1 minute
```

### FastAPI Settings
```python
REDIS_URL = 'rediss://...'  # Upstash Redis
DATABASE_URL = 'postgresql://...'  # Direct DB access
```

### Redis TTL
```python
progress_ttl = 7200  # 2 hours
result_ttl = 86400  # 24 hours
```

## Monitoring

### Key Metrics
1. **Job Creation Rate**: Jobs/minute
2. **Job Completion Rate**: Jobs/minute
3. **Average Generation Time**: Seconds
4. **Failure Rate**: Percentage
5. **Queue Length**: Pending jobs
6. **Redis Hit Rate**: Cache efficiency

### Logging
- **Django**: Job creation, status updates
- **Celery**: Task execution, retries, failures
- **FastAPI**: Generation stages, progress, errors
- **Redis**: Cache hits/misses

### Alerts
- **High Failure Rate**: >10% in 5 minutes
- **Long Queue**: >50 pending jobs
- **Slow Generation**: >10 minutes per job
- **Redis Down**: Connection failures

## Best Practices

1. **Always return immediately**: No endpoint should block >1 second
2. **Use Redis for progress**: Single source of truth
3. **Callback via Celery**: More reliable than HTTP
4. **Set proper timeouts**: Prevent hanging requests
5. **Log everything**: Essential for debugging
6. **Handle failures gracefully**: Update Redis + Database
7. **Clean up resources**: Delete old jobs, clear cache
8. **Monitor queue depth**: Scale workers as needed

## Security

1. **Authentication**: JWT tokens (HttpOnly cookies)
2. **Authorization**: Role-based access control
3. **Rate Limiting**: 10 jobs per org per hour
4. **Input Validation**: Pydantic models
5. **SQL Injection**: Parameterized queries
6. **XSS Protection**: Content Security Policy
7. **CORS**: Whitelist frontend domains

## Deployment

### Development
```bash
# Terminal 1: Django
python manage.py runserver

# Terminal 2: Celery
celery -A config worker -l info

# Terminal 3: FastAPI
python main.py

# Terminal 4: Frontend
npm run dev
```

### Production
```bash
# Use Docker Compose
docker-compose up -d

# Or deploy separately:
# - Django: Gunicorn + Nginx
# - Celery: Supervisor
# - FastAPI: Uvicorn + Nginx
# - Frontend: Vercel/Netlify
```

## Conclusion

This architecture provides:
- ✅ **Scalability**: Handles 1800+ courses
- ✅ **Reliability**: Fault-tolerant with retries
- ✅ **Performance**: <1s response time
- ✅ **Observability**: Real-time progress tracking
- ✅ **Maintainability**: Clear separation of concerns
