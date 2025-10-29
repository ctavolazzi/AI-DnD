"""
DEPRECATED: This legacy GameStateManager is deprecated.

Use unified_gamestate.GameState instead.

Migration:
    OLD: from legacy.game_state_manager import GameStateManager
    NEW: from unified_gamestate import GameState

    OLD: manager = GameStateManager()
    NEW: state = GameState(run_id="your_id")

This file is maintained for reference only and will be removed in a future version.
"""

import warnings
from character_state import CharacterState
from world import World

warnings.warn(
    "legacy.game_state_manager.GameStateManager is deprecated. "
    "Use unified_gamestate.GameState instead. "
    "This file will be removed in a future version.",
    DeprecationWarning,
    stacklevel=2
)

class GameStateManager:
    """
    DEPRECATED: Use unified_gamestate.GameState instead.

    This class is maintained for backward compatibility only.
    """
    def __init__(self):
        warnings.warn(
            "GameStateManager is deprecated. Use unified_gamestate.GameState instead.",
            DeprecationWarning,
            stacklevel=2
        )
        self.state = {}

    def load_game_state(self, filepath):
        """DEPRECATED: Use GameState.from_save_state() instead."""
        warnings.warn(
            "load_game_state is deprecated. Use GameState.from_save_state() instead.",
            DeprecationWarning,
            stacklevel=2
        )
        # Logic to load game state from file
        pass

    def save_game_state(self, filepath):
        """DEPRECATED: Use GameState.to_save_state_dict() instead."""
        warnings.warn(
            "save_game_state is deprecated. Use GameState.to_save_state_dict() instead.",
            DeprecationWarning,
            stacklevel=2
        )
        # Logic to save game state to file
        pass

    def update_character_position(self, position):
        """DEPRECATED: Use GameState methods instead."""
        warnings.warn(
            "update_character_position is deprecated. Use GameState methods instead.",
            DeprecationWarning,
            stacklevel=2
        )
        if position in self.world_state.locations:
            self.character_state.position = position
            return self.world_state.locations[position]
        else:
            return None