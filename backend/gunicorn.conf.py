"""
Gunicorn Production Configuration for Django (WSGI)
----------------------------------------------------
Usage:
    cd backend/django
    gunicorn erp.wsgi:application --config ../gunicorn.conf.py

Why Gunicorn over `python manage.py runserver`:
  - Multi-worker (handles N requests in parallel instead of 1)
  - Production-hardened (proper signal handling, graceful restarts)
  - Works behind Nginx / Render / Railway / Fly proxy
  - `runserver` prints a warning: "DO NOT USE IN PRODUCTION" — we listen.

Worker formula: (2 × CPU cores) + 1
  - +1 ensures CPUs are always busy even when workers are context-switching
  - Capped at 9 to prevent RAM exhaustion on small VMs
"""
import multiprocessing
import os

# ── Binding ───────────────────────────────────────────────────────────────────
bind = f"0.0.0.0:{os.getenv('PORT', '8000')}"

# ── Workers ───────────────────────────────────────────────────────────────────
workers = min((multiprocessing.cpu_count() * 2) + 1, 9)

# ── Worker class ─────────────────────────────────────────────────────────────
# 'sync' is the default and safest choice for Django.
# Use 'gevent' or 'gthread' if you have long-polling / streaming views.
worker_class = "sync"

# ── Timeouts ─────────────────────────────────────────────────────────────────
# Kill a worker if it doesn't respond within 30 s (prevents stuck workers)
timeout = 30

# Keep TCP connections alive for 75 s — reduces TLS handshake overhead
# when Nginx/proxy reuses a connection for multiple requests
keepalive = 75

# Graceful shutdown: let in-flight requests finish (up to 30 s)
graceful_timeout = 30

# ── Connection queuing ────────────────────────────────────────────────────────
# Max number of pending connections before OS rejects new ones
backlog = 2048

# ── Performance ──────────────────────────────────────────────────────────────
# Reuse each worker process for up to 1000 requests, then recycle.
# Prevents slow memory leaks from accumulating indefinitely.
max_requests = 1000
max_requests_jitter = 100   # randomise to avoid thundering-herd restarts

# Pre-load app code before forking workers
# Pro: Workers start instantly (no import time per restart)
# Con: Can cause issues with non-fork-safe libraries (signals, file handles)
preload_app = True

# ── Logging ───────────────────────────────────────────────────────────────────
loglevel = os.getenv("LOG_LEVEL", "warning")
accesslog = "-"    # stdout — collected by your logging infrastructure
errorlog  = "-"    # stdout
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s %(D)sµs'

# ── Process name ─────────────────────────────────────────────────────────────
proc_name = "cadence-django"
