import asyncio
import logging
import json
from typing import Dict, Optional, Any, Callable, List
from concurrent.futures import ThreadPoolExecutor
from functools import partial

from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..models import GameSession, Character as DBCharacter
from ..core.providers import InstantTimeProvider, LogProvider
from ..models.log_event import LogEvent

# Import the unified game engine
# We need to add the project root to sys.path if not already done in main
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from dnd_game import DnDGame, Character

class DatabaseLogProvider(LogProvider):
    """
    Log provider that writes events to the SQLite database queue
    instead of direct file I/O.
    """
    def __init__(self, session_id: str):
        self.session_id = session_id

    def log(self, level: int, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        # Map integer level to string
        level_name = logging.getLevelName(level)

        # Create a new DB session for this log entry to ensure it's committed immediately
        db = SessionLocal()
        try:
            log_event = LogEvent(
                session_id=self.session_id,
                level=level_name,
                message=message,
                log_metadata=extra or {},
                status="pending"
            )
            db.add(log_event)
            db.commit()
        except Exception as e:
            print(f"CRITICAL: Failed to write log to DB: {e}")
        finally:
            db.close()

class GameService:
    """
    Service to manage DnDGame instances, handle rehydration from DB,
    and execute actions in a thread pool to avoid blocking the async loop.
    """
    _instance: Optional['GameService'] = None

    def __init__(self):
        self._executor = ThreadPoolExecutor(max_workers=4)
        # In-memory cache of active games: session_id -> DnDGame
        self._active_games: Dict[str, DnDGame] = {}

    @classmethod
    def get_instance(cls) -> 'GameService':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    async def execute_action(self, session_id: str, action_fn: Callable[[DnDGame], Any]) -> Any:
        """
        Execute a function against a DnDGame instance in a separate thread.
        Handles loading/caching the game instance.
        """
        # Run the blocking logic in the thread pool
        return await asyncio.get_running_loop().run_in_executor(
            self._executor,
            partial(self._run_action_sync, session_id, action_fn)
        )

    def _run_action_sync(self, session_id: str, action_fn: Callable[[DnDGame], Any]) -> Any:
        """Synchronous worker method"""
        game = self._get_or_load_game(session_id)
        if not game:
            raise ValueError(f"Game session {session_id} not found")

        # Execute the action
        result = action_fn(game)

        # Snapshot state back to DB (Characters only for now, as full state is complex)
        # In a full implementation, we'd serialize the entire DnDGame state
        self._snapshot_characters(session_id, game)

        return result

    def _get_or_load_game(self, session_id: str) -> Optional[DnDGame]:
        """
        Get game from cache or rehydrate from DB.
        This runs inside the thread pool.
        """
        if session_id in self._active_games:
            return self._active_games[session_id]

        # Rehydration Logic
        db = SessionLocal()
        try:
            session = db.query(GameSession).filter(GameSession.id == session_id).first()
            if not session:
                return None

            # Create providers
            time_provider = InstantTimeProvider()
            log_provider = DatabaseLogProvider(session_id)

            # Initialize Game
            # NOTE: DnDGame currently initializes fresh characters in __init__
            # We need to refactor DnDGame to allow empty init or loading from state
            # For now, we create it and then overwrite characters from DB

            game = DnDGame(
                auto_create_characters=False,
                time_provider=time_provider,
                log_provider=log_provider
            )

            # Load characters from DB
            db_characters = db.query(DBCharacter).filter(
                DBCharacter.session_id == session_id,
                DBCharacter.deleted_at == None
            ).all()

            game.players = []
            game.enemies = []

            for db_char in db_characters:
                # Convert DB model back to Game Character
                # Include identifiers and extended stats so combat lookups work
                char_data = {
                    "id": db_char.id,
                    "name": db_char.name,
                    "char_class": db_char.char_class,
                    "hp": db_char.hp,
                    "max_hp": db_char.max_hp,
                    "attack": db_char.attack,
                    "defense": db_char.defense,
                    "team": db_char.team,
                    "alive": db_char.alive,
                    "mana": db_char.mana,
                    "max_mana": db_char.max_mana,
                    "ability_scores": db_char.ability_scores,
                    "status_effects": db_char.status_effects,
                    "inventory": db_char.inventory,
                    "spells": db_char.spells,
                    "proficiency_bonus": db_char.proficiency_bonus,
                    "skill_proficiencies": db_char.skill_proficiencies,
                }
                character = Character.from_db_dict(char_data)

                if character.team == "players":
                    game.players.append(character)
                else:
                    game.enemies.append(character)

            # Cache it
            self._active_games[session_id] = game
            return game

        finally:
            db.close()

    def _snapshot_characters(self, session_id: str, game: DnDGame):
        """Save updated character state to DB"""
        db = SessionLocal()
        try:
            all_chars = game.players + game.enemies
            for char in all_chars:
                # Find DB record (assuming name match for now, ideally use ID)
                db_char = db.query(DBCharacter).filter(
                    DBCharacter.session_id == session_id,
                    DBCharacter.name == char.name
                ).first()

                if db_char:
                    db_char.hp = char.hp
                    db_char.alive = char.alive
                    # Update other stats
            db.commit()
        except Exception as e:
            print(f"Error snapshotting characters: {e}")
        finally:
            db.close()

    def invalidate_cache(self, session_id: str):
        """Remove session from cache (e.g. after deletion)"""
        if session_id in self._active_games:
            del self._active_games[session_id]

    def clear_cache(self, session_id: Optional[str] = None):
        """Clear cache for a specific session or all sessions."""
        if session_id:
            self.invalidate_cache(session_id)
        else:
            self._active_games.clear()


# Shared singleton instance for modules that prefer direct import
game_service = GameService.get_instance()
