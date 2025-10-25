"""API endpoints"""
from .images import router as images_router
from .scenes import router as scenes_router
from .maintenance import router as maintenance_router
from .migrate import router as migrate_router
from .game import router as game_router

__all__ = [
    "images_router",
    "scenes_router",
    "maintenance_router",
    "migrate_router",
    "game_router"
]
