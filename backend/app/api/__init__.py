"""API endpoints"""
from .images import router as images_router
from .scenes import router as scenes_router
from .maintenance import router as maintenance_router
from .migrate import router as migrate_router
from .game import router as game_router
from .game_logic import router as game_logic_router
from .narrative import router as narrative_router
from .frontend_integration import router as frontend_router
from .character_generation import router as character_generation_router

__all__ = [
    "images_router",
    "scenes_router",
    "maintenance_router",
    "migrate_router",
    "game_router",
    "game_logic_router",
    "narrative_router",
    "frontend_router",
    "character_generation_router"
]
