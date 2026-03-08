"""
uvicorn Production Configuration
---------------------------------
Usage:
    uvicorn main:app --config uvicorn.conf.py

- Auto-detects CPU count for worker count
- HTTP/1.1 keep-alive enabled by default in uvicorn
- Structured access log for observability
- No reload in production (saves ~80 MB RAM per worker)
"""
import multiprocessing
import os

# ── Server binding ────────────────────────────────────────────────────────────
host = "0.0.0.0"
port = int(os.getenv("FASTAPI_PORT", "8001"))

# ── Workers: (2 × CPU cores) + 1  — standard Gunicorn formula ────────────────
# Capped at 8 to avoid over-subscription on I/O-heavy workloads
workers = min((multiprocessing.cpu_count() * 2) + 1, 8)

# ── Async event loop ─────────────────────────────────────────────────────────
# uvloop is ~2-4× faster than asyncio's default loop on Linux
# Falls back to asyncio on Windows (uvloop not supported)
loop = "uvloop" if os.name != "nt" else "asyncio"

# ── HTTP implementation ───────────────────────────────────────────────────────
# httptools is faster than h11 for HTTP/1.1 parsing
http = "httptools"

# ── Performance tuning ───────────────────────────────────────────────────────
# Keep TCP connections alive for 75 s — avoids repeated handshakes from Django proxy
timeout_keep_alive = 75

# Graceful shutdown: wait up to 30 s for in-flight requests to finish
timeout_graceful_shutdown = 30

# ── Logging ──────────────────────────────────────────────────────────────────
log_level = os.getenv("LOG_LEVEL", "warning")   # info in dev, warning in prod
access_log = True

# ── No reloader in production ─────────────────────────────────────────────────
reload = False
