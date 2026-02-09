"""
API Routers
Each router handles a specific domain of the application
"""
from .generation import router as generation_router
from .health import router as health_router
from .cache import router as cache_router
from .conflicts import router as conflicts_router
from .websocket import router as websocket_router

__all__ = [
    'generation_router',
    'health_router',
    'cache_router',
    'conflicts_router',
    'websocket_router'
]
