# game_state.py
"""
DEPRECATED: This file is deprecated. Use unified_gamestate.GameState instead.

This file is maintained for backward compatibility only.
All new code should import from unified_gamestate.

Migration:
    OLD: from game_state import GameState
    NEW: from unified_gamestate import GameState
"""

import warnings
from unified_gamestate import GameState as UnifiedGameState

# For backward compatibility, provide the old class name
# but emit a deprecation warning
class GameState(UnifiedGameState):
    """
    Deprecated: Use unified_gamestate.GameState instead.

    This class will be removed in a future version.
    """
    def __init__(self, *args, **kwargs):
        warnings.warn(
            "game_state.GameState is deprecated. "
            "Use unified_gamestate.GameState instead.",
            DeprecationWarning,
            stacklevel=2
        )
        # Initialize with backward-compatible defaults if no args
        if not args and not kwargs:
            super().__init__()
            # Set legacy attributes for compatibility
            self.player_character = None
            self.characers = []  # Note: typo preserved for compatibility
        else:
            super().__init__(*args, **kwargs)

