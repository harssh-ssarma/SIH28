# Smart Classroom & Timetable Scheduler — Project Documentation

> **Version:** 2.0.0 | **Last Updated:** March 2026  
> **Project Type:** SIH (Smart India Hackathon) — Full-Stack Enterprise Web Application  
> **Deployment Target:** `https://sih28.onrender.com`

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [System Architecture](#2-system-architecture)
3. [Technology Stack & Rationale](#3-technology-stack--rationale)
4. [Project Structure](#4-project-structure)
5. [Backend — Django (ERP Layer)](#5-backend--django-erp-layer)
6. [Backend — FastAPI (Timetable Engine)](#6-backend--fastapi-timetable-engine)
7. [Frontend — Next.js](#7-frontend--nextjs)
8. [Database Design](#8-database-design)
9. [Security & Access Control](#9-security--access-control)
10. [Scheduling Algorithm Pipeline](#10-scheduling-algorithm-pipeline)
11. [Key Engineering Practices](#12-key-engineering-practices)
12. [Configuration & Environment](#13-configuration--environment)

---

## 1. Project Overview

The **Smart Classroom & Timetable Scheduler** is an enterprise-grade, full-stack web application designed for higher-education institutions. It automates the highly complex problem of academic timetable generation while adhering to India's **NEP 2020** (National Education Policy) credit-based framework.

### Core Capabilities

| Capability | Description |
|---|---|
| **Automated Timetable Generation** | Multi-stage AI/OR engine produces conflict-free schedules |
| **NEP 2020 Compliance** | Supports open electives, skill enhancement, and credit-based curricula |
| **Multi-Variant Scheduling** | Generates multiple valid timetable alternatives for admin selection |
| **Real-Time Progress Tracking** | WebSocket-driven live generation progress for users |
| **Role-Based Access** | Registrar, Department Head, Coordinator roles with fine-grained permissions |
| **Conflict Detection** | Automatic detection and visualization of scheduling conflicts |
| **Export & Reporting** | PDF, Excel, and Excel-export of finalized timetables |
| **Hardware-Adaptive Engine** | Auto-detects CPU/GPU and scales parallel workers accordingly |

---

## 2. System Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                      FRONTEND (Next.js 14)                      │
│    Port 3000 — TypeScript, Tailwind CSS, Radix UI, Zustand     │
└─────────────────────┬──────────────────────────────────────────┘
                      │  REST + WebSocket
        ┌─────────────┴──────────────────────┐
        │                                    │
┌───────▼────────────────┐    ┌──────────────▼─────────────────┐
│  Django (Port 8000)     │    │  FastAPI Engine (Port 8001)     │
│  ERP / Auth / Data      │    │  Timetable Generation Service   │
│  DRF + Celery + JWT     │    │  CP-SAT + GA + RL + Clustering  │
└───────┬────────────────┘    └──────────────┬─────────────────┘
        │                                    │
        └──────────────┬─────────────────────┘
                       │
              ┌────────▼────────┐
              │   Redis Cache   │  Shared message broker + cache
              └────────┬────────┘
                       │
              ┌────────▼────────┐
              │   PostgreSQL    │  Primary relational data store
              └─────────────────┘
```

The architecture separates concerns into three tiers:
- **Frontend:** React-based SPA served by Next.js, communicating with both backends via REST and WebSocket.
- **Django Backend:** Acts as the authoritative ERP layer — manages users, academic data, timetable metadata, and orchestrates long-running jobs via Celery.
- **FastAPI Engine:** A high-performance microservice dedicated to the computationally intense timetable optimization pipeline.

---

## 3. Technology Stack & Rationale

### 3.1 Backend — Python

**Why Python?**
Python is the industry standard for optimization, machine learning, and data science. The rich ecosystem of solver libraries (`ortools`, `scipy`, `torch`, `deap`) is unmatched and was essential for the multi-stage scheduling engine. Both Django and FastAPI are Python-first frameworks, enabling code and library sharing.

---

#### 3.1.1 Django 5.1.3 — ERP/Data Layer

**Why Django (not pure FastAPI)?**
Django was chosen for the ERP layer because of its mature ORM, built-in admin panel, migration framework, and batteries-included approach to authentication, sessions, and signals. These are critical for managing the academic data that feeds the scheduling engine.

| Library | Purpose | Why |
|---|---|---|
| `Django 5.1.3` | Core ORM, routing, admin | Battle-tested, mature, full-featured web framework |
| `djangorestframework 3.15.2` | REST API serializers/viewsets | De facto Django REST standard |
| `djangorestframework-simplejwt 5.3.0` | JWT Authentication | Stateless auth for SPA frontend |
| `drf-spectacular 0.27.0` | OpenAPI/Swagger docs | Auto-generates API documentation |
| `django-cors-headers 4.6.0` | CORS handling | Required for cross-origin Next.js requests |
| `django-redis 5.4.0` | Redis cache backend | Shared cache layer with FastAPI |
| `django-filter 24.3` | Queryset filtering | Clean URL-based filtering for list endpoints |
| `django-ratelimit 4.1.0` | Request rate limiting | API abuse protection |
| `django-otp 1.3.0` | Two-Factor Authentication | Optional 2FA for admin accounts |
| `django-csp` | Content Security Policy headers | XSS protection |
| `psycopg2-binary` | PostgreSQL adapter | PostgreSQL is the primary DB |
| `argon2-cffi 23.1.0` | Password hashing | Argon2 is the modern recommended hashing algo |
| `celery 5.3.6` | Async task queue | Offloads long-running generation jobs from request/response cycle |
| `kombu 5.3.4` | Celery message transport | Required by Celery for Redis brokering |
| `openpyxl 3.1.5` | Excel read/write | Bulk data import/export |
| `daphne` | ASGI server for WebSockets | Enables Django Channels for real-time updates |
| `channels` | WebSocket support | Real-time generation progress events |

---

#### 3.1.2 FastAPI 0.115.0 — Timetable Engine

**Why FastAPI (separate from Django)?**
The timetable generation is CPU-intensive and long-running (seconds to minutes). FastAPI's async-first design with `uvicorn` gives full control over async execution, parallelism, and streaming responses. Isolating it from Django prevents blocking the ERP layer during generation.

| Library | Purpose | Why |
|---|---|---|
| `fastapi 0.115.0` | API framework | High performance, async, automatic OpenAPI docs |
| `uvicorn[standard] 0.32.0` | ASGI server | Production-grade Uvicorn with watchfiles |
| `pydantic 2.9.2` | Data validation & schemas | Type-safety, request/response modeling |
| `ortools 9.14.6206` | **CP-SAT solver** (Google OR-Tools) | Industrial-strength constraint programming solver |
| `python-constraint 1.4.0` | Lightweight constraint satisfaction | Supplementary constraint solving |
| `numpy` | Numerical arrays | Matrix operations in GA and clustering |
| `networkx 3.2.1` | Graph algorithms | Course dependency and conflict graphs |
| `python-louvain 0.16` | **Louvain community detection** | Stage 1 clustering of courses |
| `scikit-learn` | Machine learning utilities | Feature engineering for RL state representation |
| `torch` | PyTorch deep learning | Neural network components for context engine |
| `deap` | **Genetic Algorithm framework** | Stage 2B evolutionary optimization |
| `scipy` | Scientific computing | Statistical utilities |
| `joblib 1.3.2` | Parallel processing | Parallelizing cluster solving across CPU cores |
| `multiprocess 0.70.15` | Process isolation | Worker process spawning (Windows-safe) |
| `aiohttp` | Async HTTP client | Async callbacks to Django |
| `structlog 23.2.0` | Structured logging | JSON logging for observability |
| `prometheus-client 0.21.0` | Prometheus metrics | Performance monitoring/alerting |
| `prometheus-fastapi-instrumentator` | Auto-metrics for FastAPI | Request latency, throughput metrics |
| `sentry-sdk[fastapi] 2.19.2` | Error tracking | Production error reporting |
| `pulp` | Linear programming | Fallback LP solver |
| `redis[hiredis] 5.2.0` | Shared cache + pub/sub | Progress streaming to Django, result caching |
| `python-jose[cryptography]` | JWT validation | Validates Django-issued JWTs in FastAPI |

---

### 3.2 Frontend — TypeScript / Next.js

**Why TypeScript?**
TypeScript provides compile-time type safety across a complex frontend with many data shapes (timetables, courses, users, conflicts). It catches bugs at build time, improves IDE support, and makes refactoring safer at scale.

**Why Next.js 14?**
Next.js App Router provides file-based routing, server-side rendering (SSR) for SEO, built-in image optimization, and first-class TypeScript support — making it the most productive React framework for this class of application.

| Library | Purpose | Why |
|---|---|---|
| `next 14.0.0` | React framework | SSR, file-system routing, API routes |
| `react 18` + `react-dom 18` | UI library | Component-based rendering |
| `typescript 5` | Type-safe JavaScript | Reduces runtime bugs at scale |
| `tailwindcss 3` | Utility-first CSS | Rapid, consistent styling with design tokens |
| `@radix-ui/*` | Accessible UI primitives | Headless, accessible components (select, dropdown, tabs, etc.) |
| `lucide-react` | Icon library | Clean, consistent SVG icons |
| `zustand 4.4.6` | Global state management | Lightweight, easy-to-use store without boilerplate |
| `swr 2.2.4` | Data fetching + caching | Stale-while-revalidate pattern for API data |
| `react-hook-form 7` | Form state management | Performant forms with minimal re-renders |
| `zod 3` | Schema validation | Runtime type validation for form data and API responses |
| `@hookform/resolvers` | Zod + react-hook-form bridge | Connects Zod schemas to form validation |
| `socket.io-client 4` | Real-time WebSocket client | Receives live generation progress updates |
| `recharts 2` | Charts & data visualization | Dashboard analytics graphs |
| `next-themes 0.2` | Dark/light mode | Theme switching support |
| `dompurify 3` | HTML sanitization | Prevents XSS from user-generated content |
| `html2canvas 1` + `jspdf 3` | PDF export | Client-side timetable PDF generation |
| `file-saver 2` + `xlsx 0.18` | Excel export | Export timetables to spreadsheet |
| `react-hot-toast 2` | Toast notifications | User-facing success/error messages |
| `@sentry/nextjs 7` | Frontend error tracking | Production error monitoring |
| `class-variance-authority` + `clsx` + `tailwind-merge` | Conditional class utilities | Clean Tailwind class composition |

---

## 4. Project Structure

```
Smart-Classroom-and-Timetable-Scheduler/
├── backend/
│   ├── .env                        # Shared environment variables
│   ├── requirements.txt            # All Python dependencies
│   ├── django/                     # ERP + Auth backend (Port 8000)
│   │   ├── manage.py
│   │   ├── core/                   # Shared infrastructure
│   │   └── academics/              # Main application module
│   └── fastapi/                    # Timetable engine (Port 8001)
│       ├── main.py
│       ├── config.py
│       ├── api/                    # HTTP layer
│       ├── core/                   # Enterprise patterns
│       ├── engine/                 # Algorithm pipeline
│       ├── models/                 # Pydantic request/response models
│       ├── utils/                  # Utilities
│       └── tests/                  # Pytest test suite
├── frontend/                       # Next.js app (Port 3000)
│   ├── package.json
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   └── src/
│       ├── app/                    # Next.js App Router pages
│       ├── components/             # Reusable UI components
│       ├── context/                # React context providers
│       ├── hooks/                  # Custom React hooks
│       ├── lib/                    # API clients, utilities
│       └── types/                  # TypeScript type definitions
└── clear.py                        # Dev utility script
```

---

## 5. Backend — Django (ERP Layer)

### 5.1 Module: `core/`

The `core` module provides shared infrastructure used across all Django apps.

| File | Description |
|---|---|
| `rbac.py` | **Role-Based Access Control** — defines `Registrar`, `DeptHead`, `Coordinator` roles and DRF permission classes |
| `permissions.py` | Fine-grained DRF permission classes per action |
| `authentication.py` | JWT authentication backend integrating `simplejwt` |
| `middleware.py` | Custom request middleware (logging, request tracking) |
| `csrf_middleware.py` | Custom CSRF enforcement for SPA integration |
| `cache_service.py` | Redis-backed caching service (read-through, write-through patterns) |
| `audit_logging.py` | Structured audit trail for all create/update/delete operations |
| `hardware_detector.py` | Detects available CPU cores/RAM for adaptive parallelism |
| `health_checks.py` | Health check endpoints for DB, Redis, storage |
| `throttling.py` | Custom DRF throttle classes |
| `storage.py` | File storage abstraction (local / S3 / MinIO) |

### 5.2 Module: `academics/`

The main business domain module.

#### 5.2.1 Models (`academics/models/`)

| Model File | Key Models | Description |
|---|---|---|
| `base.py` | `Organization` | Top-level institutional entity |
| `academic_structure.py` | `School`, `Department`, `Program` | Hierarchical academic org (NEP 2020 compliant with credit fields) |
| `course.py` | `Course` | Course catalog with credit hours, type, lab flags |
| `faculty.py` | `Faculty` | Faculty profiles, department assignments, preferences |
| `student.py` | `Student`, `StudentEnrollment` | Student records and course enrollments |
| `room.py` | `Room` | Rooms with capacity, type, and feature flags |
| `timetable.py` | `Timetable`, `TimetableSlot` | Generated timetable records and individual time slots |
| `timetable_config.py` | `TimetableConfig` | Generation configuration (days, slot times, constraints) |
| `user.py` | `User` | Custom user model with `role` field |

#### 5.2.2 Views (`academics/views/`)

| View File | Description |
|---|---|
| `auth_views.py` | Login, logout, token refresh, 2FA, session management |
| `generation_views.py` | Timetable generation — triggers Celery tasks, returns job IDs |
| `timetable_views.py` | CRUD for timetables (admin, faculty, student views) |
| `timetable_variant_views.py` | Multi-variant timetable comparison and selection |
| `conflict_views.py` | Conflict detection and resolution endpoints |
| `dashboard_views.py` | Analytics — faculty workload, room utilization, statistics |
| `progress_endpoints.py` | Real-time generation progress via SSE/WebSocket |
| `timetable_config_views.py` | Configuration for generation parameters |
| `faculty_viewset.py` | Faculty CRUD (DRF ViewSet) |
| `student_viewset.py` | Student CRUD (DRF ViewSet) |
| `room_viewsets.py` | Room management (DRF ViewSet) |
| `course_viewset.py` | Course catalog management (DRF ViewSet) |
| `academic_viewsets.py` | School/Department/Program management |
| `workflow_views.py` | Timetable approval workflow state machine |
| `password_views.py` | Password reset flow |
| `session_views.py` | Active session listing and revocation |

#### 5.2.3 Supporting Files

| File | Description |
|---|---|
| `celery_tasks.py` | Celery task definitions — async job orchestration for generation |
| `serializers.py` | DRF serializers for all academic models |
| `mixins.py` | Reusable viewset mixins (pagination, filtering, audit) |
| `signals.py` | Django signals for post-save hooks (cache invalidation, notifications) |
| `urls.py` | URL routing for all `academics` endpoints |
| `apps.py` | Django app configuration and ready-signal setup |

---

## 6. Backend — FastAPI (Timetable Engine)

### 6.1 Entry Point & Configuration

| File | Description |
|---|---|
| `main.py` | FastAPI app factory, middleware registration, router inclusion, Windows-safe multiprocessing guard |
| `config.py` | Centralized `Settings` class — all algorithm parameters, timeouts, weights, Redis/Django URLs |

### 6.2 API Layer (`api/`)

#### Routers (`api/routers/`)

| Router | Description |
|---|---|
| `generation.py` | `POST /api/generate` — main timetable generation endpoint |
| `health.py` | `GET /api/health` — liveness and readiness probes |
| `cache.py` | Cache inspection and invalidation for operators |
| `conflicts.py` | Conflict analysis endpoints |
| `websocket.py` | WebSocket endpoint for real-time generation progress streaming |

#### Middleware (`api/middleware/`)

| File | Description |
|---|---|
| `cors.py` | CORS configuration for Django and Next.js origins |
| `error_handler.py` | Global exception handler — normalizes errors to RFC 7807 format |
| `rate_limiting.py` | Per-IP/per-org rate limiting on generation endpoints |

### 6.3 Core Infrastructure (`core/`)

| File / Module | Description |
|---|---|
| `lifespan.py` | FastAPI lifespan manager — startup (Redis ping, hardware detection) and graceful shutdown |
| `logging_config.py` | `structlog` JSON structured logging configuration |
| `memory_monitor.py` | Background memory monitoring, alerts on threshold breaches |
| `cancellation.py` | User-initiated job cancellation, Redis-backed cancel tokens |
| `patterns/circuit_breaker.py` | Circuit Breaker pattern — stops cascading failures on external calls |
| `patterns/bulkhead.py` | Bulkhead pattern — resource isolation between concurrent generation jobs |
| `patterns/saga.py` | Saga pattern — multi-step distributed transaction management |

### 6.4 Scheduling Engine (`engine/`)

The engine runs a **4-stage pipeline**:

```
Input Data
    │
    ▼
Stage 1: Louvain Clustering (stage1_clustering.py)
    │   Graph-based course clustering to reduce problem size
    ▼
Stage 2A: CP-SAT Solver (cpsat/)
    │   Google OR-Tools Constraint Programming for hard constraints
    ▼
Stage 2B: Genetic Algorithm (ga/)
    │   Evolutionary optimization for soft constraints
    ▼
Stage 3: Q-Learning Refinement (rl/)
    │   Reinforcement Learning micro-adjustments
    ▼
Stage 4: Context Engine (context/)
        Multi-dimensional context weighting (temporal, spatial, behavioral)
```

#### Stage 1 — Clustering

| File | Description |
|---|---|
| `stage1_clustering.py` | Builds weighted course conflict graph; applies Louvain community detection to partition courses into clusters for parallel solving |

#### Stage 2A — CP-SAT Solver (`engine/cpsat/`)

| File | Description |
|---|---|
| `solver.py` | Main CP-SAT model builder — encodes all hard constraints as CP-SAT boolean variables |
| `constraints.py` | Hard constraint definitions: no-overlap, room capacity, faculty availability, fixed slots |
| `conflict_constraints.py` | Cross-course conflict constraints (shared students, shared faculty) |
| `dept_solver.py` | Per-department solving with committed-slot registry |
| `cross_dept_solver.py` | Resolves cross-department shared course conflicts |
| `timetable_merger.py` | Merges per-cluster solutions into a unified timetable |
| `committed_registry.py` | Registry of already-committed time slots (prevents double-booking during merging) |
| `strategies.py` | Solver strategy selection (minimize gaps, maximize preference, etc.) |
| `progress.py` | Progress callback hooks for CP-SAT solver |

#### Stage 2B — Genetic Algorithm (`engine/ga/`)

| File | Description |
|---|---|
| `optimizer.py` | GA main loop — population initialization, selection, evolution |
| `fitness.py` | Multi-objective fitness function incorporating all soft constraint weights |
| `operators.py` | Genetic operators — crossover (single-point, two-point), mutation |

#### Stage 3 — Reinforcement Learning (`engine/rl/`)

| File | Description |
|---|---|
| `qlearning.py` | Q-Learning agent — state-action-reward loop for slot micro-optimization |
| `state_manager.py` | State representation of the current partial timetable |
| `reward_calculator.py` | Reward signal computation from constraint satisfaction scores |

#### Supporting Engine Files

| File | Description |
|---|---|
| `adaptive_executor.py` | Detects hardware capabilities and dynamically assigns CPU/GPU workers to clusters |
| `rate_limiter.py` | Per-organization generation rate limiting |
| `engine/__init__.py` | Public engine API — exposes `run_generation_pipeline()` |

### 6.5 Models (Pydantic Schemas) (`models/`)

Pydantic v2 request/response schemas for all API contracts — strict type validation at the boundary.

### 6.6 Utilities (`utils/`)

Helper functions: data normalization, slot time parsing, timetable serialization utilities.

### 6.7 Tests (`tests/`)

Pytest-based test suite covering individual engine stages, API endpoints, and constraint validation.

---

## 7. Frontend — Next.js

### 7.1 App Router Pages (`src/app/`)

| Route | Description |
|---|---|
| `(auth)/` | Login / register pages (grouped route, no shared layout) |
| `(marketing)/` | Public-facing landing/marketing pages |
| `admin/` | Admin portal — full timetable management, conflict resolution, dashboards |
| `faculty/` | Faculty-facing timetable view and schedule viewer |
| `student/` | Student timetable viewer |
| `unauthorized/` | 403 page |

### 7.2 Components (`src/components/`)

| Component / Dir | Description |
|---|---|
| `shell/` | App shell — sidebar, topbar, breadcrumbs, nav |
| `timetables/` | Timetable display grids, slot cards, comparison views |
| `shared/` | Shared components (page headers, data tables, confirm dialogs) |
| `marketing/` | Landing page sections (hero, features, pricing, etc.) |
| `ui/` | Low-level UI primitives (button, input, badge, card wrappers around Radix) |
| `FormFields.tsx` | Reusable form input components (text, select, date) |
| `LoadingSkeletons.tsx` | Loading state skeleton screens for async content |
| `ErrorBoundary.tsx` | React error boundary for graceful degradation |
| `AuthRedirect.tsx` | Client-side guard — redirects unauthenticated users |
| `Toast.tsx` | Toast notification wrapper around `react-hot-toast` |
| `Providers.tsx` | Root provider composition (theme, Zustand, SWR config) |

### 7.3 State Management & Data Fetching

| File/Dir | Description |
|---|---|
| `src/context/` | React Context for session/user state |
| `src/hooks/` | Custom hooks (`useAuth`, `useTimetable`, `useWebSocket`, etc.) |
| `src/lib/` | API client functions, utility helpers, type guards |
| `src/types/` | TypeScript interfaces for Domain models (Timetable, Course, Faculty, Room, User, Conflict) |

### 7.4 Key Frontend Patterns

- **SWR** for all server-state data fetching with automatic revalidation and cache
- **Zustand** for client-side global state (auth session, selected timetable variant)
- **react-hook-form + Zod** for all form data with schema-driven validation
- **socket.io-client** connected to FastAPI WebSocket for live generation progress

---

## 8. Database Design

### Primary Database: PostgreSQL

All academic data is persisted in PostgreSQL. The schema follows a hierarchical model:

```
Organization
  └── School
        └── Department
              └── Program
                    └── Course
Faculty (linked to Department)
Student (linked to Program)
Room (linked to Organization)
Timetable → TimetableSlot (links Course + Faculty + Room + TimeSlot)
TimetableConfig (generation parameters per Organization)
```

### Key Design Decisions

| Decision | Rationale |
|---|---|
| UUID primary keys on all models | Avoids integer ID enumeration attacks, safe for distributed systems |
| Explicit `db_table` names | Prevents Django auto-naming conflicts in multi-app schemas |
| Composite indexes on org+active | Most queries are tenant-scoped; index on `(organization, is_active)` |
| Audit timestamp fields (`created_at`, `updated_at`) on all models | Required for compliance and debug |

### Caching: Redis

Redis is used as a shared cache between Django and FastAPI:

| Use Case | Pattern |
|---|---|
| Timetable generation results | Write-through with TTL |
| Real-time progress state | Pub/Sub channel per job ID |
| Django session cache | Standard session backend |
| Celery broker | Task queue messages |
| Celery result backend | Async task results |
| Rate limiting counters | Atomic increment with TTL |

---

## 9. Security & Access Control

### Authentication

- **JWT tokens** issued by Django (`djangorestframework-simplejwt`)
- RS256 or HS256 signing (configured via env)
- Token refresh via `/api/token/refresh/`
- **Optional 2FA** via `django-otp` (TOTP-based)
- Tokens validated by FastAPI using `python-jose` for engine API calls

### Role-Based Access Control (RBAC)

Three roles with a strict permission matrix:

| Permission | Registrar | Dept Head | Coordinator |
|---|:---:|:---:|:---:|
| Generate timetable | ✅ | ❌ | ❌ |
| Approve timetable | ✅ | ❌ | ❌ |
| Edit timetable | ✅ | ✅ | ❌ |
| View timetable | ✅ | ✅ | ✅ |
| Manage faculty | ✅ | ✅ | ❌ |
| Manage courses | ✅ | ✅ | ❌ |
| Manage rooms | ✅ | ❌ | ❌ |
| Resolve conflicts | ✅ | ✅ | ❌ |

### Security Hardening

| Mechanism | Implementation |
|---|---|
| Password hashing | Argon2 (argon2-cffi) |
| CORS | `django-cors-headers` with explicit origin whitelist |
| Content Security Policy | `django-csp` headers |
| Rate Limiting | `django-ratelimit` (Django) + custom middleware (FastAPI) |
| Input Validation | Pydantic v2 (FastAPI) + Zod (frontend) + DRF serializers (Django) |
| HTML Sanitization | DOMPurify on frontend |
| Audit Logging | All mutations logged to `audit_logging.py` |
| CSRF Protection | Custom `csrf_middleware.py` for SPA cookie flow |
| Error Monitoring | Sentry SDK on both Django and FastAPI + Next.js |

---

## 10. Scheduling Algorithm Pipeline

### Stage 1: Louvain Community Clustering

The Louvain community detection algorithm (via `python-louvain`) partitions courses into clusters based on a weighted conflict graph. Edges are weighted by:
- Shared faculty (`ALPHA_FACULTY = 10.0`)
- Shared student groups (`ALPHA_STUDENT = 10.0`, prioritized for NEP 2020)
- Room competition (`ALPHA_ROOM = 3.0`)

**Why Louvain?** It operates in near-linear time on sparse graphs and produces high-modularity partitions. This reduces the NP-hard timetabling problem into smaller, fully parallelizable subproblems.

### Stage 2A: CP-SAT Constraint Programming

Google OR-Tools CP-SAT solver encodes each cluster's scheduling problem as a Constraint Satisfaction Problem. Hard constraints enforced:
- No faculty double-booking
- No room double-booking
- No student group double-booking
- Room capacity ≥ student enrollment
- Fixed/locked slot assignments honored
- Faculty unavailability windows excluded
- Maximum classes per day per faculty

**Why CP-SAT?** It is one of the fastest industrial CSP solvers available. Unlike pure MIP solvers, CP-SAT excels at combinatorial scheduling with Boolean variables and handles complex disjunctive constraints natively.

### Stage 2B: Genetic Algorithm (DEAP)

A population-based evolutionary optimizer refines CP-SAT solutions for soft constraints:
- Faculty preferred time slots
- Schedule compactness (minimize student gaps)
- Room utilization efficiency
- Faculty workload balance
- Peak-hour spread

Operators: tournament selection, single-point crossover, random mutation. Early termination when quality > 80% or no improvement for 8 generations.

### Stage 3: Q-Learning Refinement

A tabular Q-Learning agent performs final micro-optimizations by treating slot swaps as actions and measuring reward from constraint satisfaction improvement. The Q-table is persisted between runs for incremental learning.

### Stage 4: Context Engine

A multi-dimensional context weighting layer applies learned behavioral and spatial patterns:

| Dimension | Weight | What it considers |
|---|---|---|
| Temporal | 0.25 | Time-of-day effectiveness for subject types |
| Behavioral | 0.25 | Historical pattern learning from past schedules |
| Academic | 0.20 | Curricular coherence and dependency ordering |
| Social | 0.15 | Peer group cohesion for labs/seminars |
| Spatial | 0.15 | Room adjacency and travel time optimization |

### Hardware Adaptation

The `adaptive_executor.py` detects the host hardware at startup and adjusts:
- Number of parallel cluster solver workers
- CP-SAT thread allocation
- GA population size
- whether GPU acceleration is enabled (PyTorch, OpenCL)

---

## 11. Key Engineering Practices

### Code Quality

| Practice | Tool |
|---|---|
| Formatting | `black` (Python), `prettier` (TypeScript) |
| Linting | `flake8` (Python), `eslint` (TypeScript) |
| Import sorting | `isort` (Python) |
| Type checking | `mypy` (Python), `tsc` (TypeScript) |
| Security scanning | `bandit` |
| Test runner | `pytest` with `pytest.ini` config |

### Observability

| Capability | Implementation |
|---|---|
| Structured logging | `structlog` JSON logs (FastAPI), Django logging |
| Error tracking | Sentry SDK (backend + frontend) |
| Metrics | Prometheus + FastAPI instrumentator |
| Celery monitoring | Flower dashboard |
| Health checks | `/api/health` on both services |

### Enterprise Patterns (FastAPI)

| Pattern | File | Purpose |
|---|---|---|
| Circuit Breaker | `core/patterns/circuit_breaker.py` | Prevents cascading failures on Django API calls |
| Bulkhead | `core/patterns/bulkhead.py` | Isolates CPU resources between concurrent jobs |
| Saga | `core/patterns/saga.py` | Manages multi-step generation with rollback |

### Development Practices

- **Environment separation:** `.env` for all secrets and config; `python-decouple` + `python-dotenv` for loading
- **Database migrations:** Django migration files version-controlled for schema traceability
- **API documentation:** Auto-generated OpenAPI/Swagger via `drf-spectacular` (Django) and FastAPI's built-in `/docs`
- **Documentation generation:** `mkdocs` + `mkdocs-material` for technical docs site
- **Profiling:** `py-spy`, `memory-profiler` for performance analysis
- **Remote debugging:** `debugpy` for Docker-based remote debugging

---

## 12. Configuration & Environment

The shared `backend/.env` file configures both Django and FastAPI:

| Variable | Default | Description |
|---|---|---|
| `REDIS_URL` | `redis://localhost:6379/0` | Shared Redis connection |
| `DJANGO_API_BASE_URL` | `http://localhost:8000` | Django base URL (used by FastAPI) |
| `FASTAPI_PORT` | `8001` | FastAPI service port |
| `CELERY_BROKER_URL` | Redis URL | Celery task queue |
| `LOG_LEVEL` | `INFO` | Logging verbosity |
| `SENTRY_DSN` | _(empty)_ | Sentry error reporting DSN |
| `SENTRY_ENVIRONMENT` | `development` | `production` / `development` |

FastAPI algorithm parameters are tuned via `config.py` `Settings` class constants (see [Section 6.1](#61-entry-point--configuration)).

---

*Documentation generated March 2026. For questions, refer to the inline module docstrings or the project maintainers.*
