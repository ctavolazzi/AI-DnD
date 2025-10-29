"""
GameState Adapter for seamless migration.

This adapter provides backward compatibility for code that uses
current_run_data dict format while internally using unified GameState.

Usage:
    adapter = GameStateAdapter(run_id="test_001")
    adapter.current_run_data  # Access as dict (backward compatible)
    adapter.gamestate  # Access as unified GameState (new way)
"""

from unified_gamestate import GameState
from typing import Dict, Any, Optional


class GameStateAdapter:
    """
    Adapter that provides backward-compatible current_run_data dict interface
    while using unified GameState internally.

    This allows gradual migration - code can continue using dict access
    patterns while the underlying data is in unified GameState format.
    """

    def __init__(
        self,
        run_id: Optional[str] = None,
        start_time: Optional[str] = None,
        initial_data: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize adapter.

        Args:
            run_id: Optional run ID
            start_time: Optional start time
            initial_data: Optional dict in current_run_data format to initialize from
        """
        if initial_data:
            self.gamestate = GameState.from_run_data(initial_data)
        else:
            self.gamestate = GameState(
                run_id=run_id,
                turn=0,
                status="active",
                start_time=start_time
            )

    @property
    def current_run_data(self) -> Dict[str, Any]:
        """
        Get current_run_data in dict format (backward compatible).

        This property provides seamless dict access for legacy code.
        """
        return self.gamestate.to_run_data()

    @current_run_data.setter
    def current_run_data(self, value: Dict[str, Any]):
        """Update from current_run_data dict"""
        self.gamestate = GameState.from_run_data(value)

    def sync_from_unified(self, gamestate: GameState) -> None:
        """Sync from unified GameState instance"""
        self.gamestate = gamestate

    def update_from_dict(self, updates: Dict[str, Any]) -> None:
        """
        Update game state from dict updates (partial updates).

        This handles cases where code does: current_run_data["turn_count"] = 5
        """
        run_data = self.current_run_data
        run_data.update(updates)
        self.current_run_data = run_data

    # Convenience accessors for common operations
    @property
    def run_id(self) -> str:
        return self.gamestate.run_id

    @property
    def turn_count(self) -> int:
        return self.gamestate.turn

    @turn_count.setter
    def turn_count(self, value: int):
        self.gamestate.turn = value
        self.gamestate.update_timestamp()

    @property
    def status(self) -> str:
        return self.gamestate.status

    @status.setter
    def status(self, value: str):
        self.gamestate.set_status(value)

