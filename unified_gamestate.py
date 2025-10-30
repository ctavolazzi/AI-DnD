"""
Unified GameState class - Single source of truth for game state management.

This class consolidates all GameState definitions:
- dungeon_master.py current_run_data
- backend/app/services/game_state_manager.py GameStateManager
- save_state.py game_state structure
- game_state.py basic class

Design Philosophy:
- Canonical representation of all game state
- Conversion methods for each existing system
- Maintains backward compatibility during migration
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from copy import deepcopy
import json


class GameState:
    """
    Unified game state class - canonical representation of all game state.

    This class consolidates multiple GameState definitions into a single
    source of truth, following the same pattern as Character consolidation (Task 1).

    Attributes:
        run_id: Unique identifier for this game run/session
        session_id: Backend session identifier (may equal run_id)
        turn: Current turn number (0-based)
        status: Game status ("active", "completed", "error", "paused")
        start_time: ISO timestamp of game start
        created_at: ISO timestamp of state creation
        updated_at: ISO timestamp of last update

        # Core game data
        characters: Dict[str, dict] - Character data by char_id
        locations: Dict[str, dict] - Location data by loc_id
        events: List[dict] - Event history (most recent)
        combat: List[dict] - Combat encounter history

        # Quest system
        current_quest_id: Optional[str] - Active quest ID
        quests: Dict[str, dict] - Quest data by quest_id

        # Location tracking
        current_location_id: Optional[str] - Current location ID

        # Obsidian integration
        obsidian_data: Optional[dict] - Obsidian vault references

        # Session management
        sessions: List[str] - Session references

        # Conclusion
        conclusion: Optional[str] - Game conclusion text
        error_details: Optional[str] - Error information if status is "error"
    """

    def __init__(
        self,
        run_id: Optional[str] = None,
        session_id: Optional[str] = None,
        turn: int = 0,
        status: str = "active",
        start_time: Optional[str] = None,
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None
    ):
        """Initialize unified GameState"""
        # Identifiers
        self.run_id = run_id or datetime.now().strftime("%Y%m%d%H%M%S")
        self.session_id = session_id or self.run_id

        # Turn and status
        self.turn = turn
        self.status = status

        # Timestamps
        now = datetime.now().isoformat()
        self.start_time = start_time or now
        self.created_at = created_at or now
        self.updated_at = updated_at or now

        # Core game data
        self.characters: Dict[str, dict] = {}  # char_id -> character_data
        self.locations: Dict[str, dict] = {}   # loc_id -> location_data
        self.events: List[dict] = []           # Event history
        self.combat: List[dict] = []            # Combat history

        # Quest system
        self.current_quest_id: Optional[str] = None
        self.quests: Dict[str, dict] = {}

        # Location tracking
        self.current_location_id: Optional[str] = None

        # Obsidian integration
        self.obsidian_data: Optional[dict] = None

        # Session management
        self.sessions: List[str] = []

        # Conclusion
        self.conclusion: Optional[str] = None
        self.error_details: Optional[str] = None

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp"""
        self.updated_at = datetime.now().isoformat()

    # ========== Conversion Methods ==========

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to standard dictionary format for JSON serialization.

        Returns:
            Complete game state as dictionary
        """
        return {
            "run_id": self.run_id,
            "session_id": self.session_id,
            "turn": self.turn,
            "status": self.status,
            "start_time": self.start_time,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "characters": deepcopy(self.characters),
            "locations": deepcopy(self.locations),
            "events": deepcopy(self.events),
            "combat": deepcopy(self.combat),
            "current_quest_id": self.current_quest_id,
            "quests": deepcopy(self.quests),
            "current_location_id": self.current_location_id,
            "obsidian_data": deepcopy(self.obsidian_data) if self.obsidian_data else None,
            "sessions": deepcopy(self.sessions),
            "conclusion": self.conclusion,
            "error_details": self.error_details
        }

    def to_run_data(self) -> Dict[str, Any]:
        """
        Convert to dungeon_master.py current_run_data format.

        This format uses lists for characters/events/combat/locations instead of dicts,
        and stores character names rather than full data.

        Returns:
            Dictionary in current_run_data format
        """
        # Extract character names/references from character dict
        character_refs = []
        for char_id, char_data in self.characters.items():
            # Try to get name, otherwise use char_id
            name = char_data.get("name") if isinstance(char_data, dict) else str(char_data)
            character_refs.append(name or char_id)

        # Extract location IDs
        location_refs = list(self.locations.keys())

        return {
            "run_id": self.run_id,
            "start_time": self.start_time,
            "status": self.status,
            "turn_count": self.turn,
            "characters": character_refs,
            "events": deepcopy(self.events),
            "combat": deepcopy(self.combat),
            "locations": location_refs,
            "sessions": deepcopy(self.sessions),
            "quest": self.current_quest_id,
            "conclusion": self.conclusion,
            "error_details": self.error_details
        }

    @classmethod
    def from_run_data(cls, data: Dict[str, Any]) -> 'GameState':
        """
        Create GameState from dungeon_master.py current_run_data format.

        Args:
            data: Dictionary in current_run_data format

        Returns:
            New GameState instance
        """
        state = cls(
            run_id=data.get("run_id"),
            turn=data.get("turn_count", 0),
            status=data.get("status", "active"),
            start_time=data.get("start_time")
        )

        # Convert character refs to dict (will need character data from elsewhere)
        # For now, store as minimal entries
        for char_ref in data.get("characters", []):
            if isinstance(char_ref, str):
                state.characters[char_ref] = {"name": char_ref}

        # Events and combat are already dicts
        state.events = data.get("events", [])
        state.combat = data.get("combat", [])

        # Locations - convert list to dict with minimal entries
        for loc_ref in data.get("locations", []):
            if isinstance(loc_ref, str):
                state.locations[loc_ref] = {"id": loc_ref, "name": loc_ref}

        state.sessions = data.get("sessions", [])
        state.current_quest_id = data.get("quest")
        state.conclusion = data.get("conclusion")
        state.error_details = data.get("error_details")

        return state

    def to_game_state_manager_dict(self) -> Dict[str, Any]:
        """
        Convert to backend GameStateManager.state format.

        Returns:
            Dictionary in GameStateManager format
        """
        return {
            "session_id": self.session_id,
            "turn": self.turn,
            "status": self.status,
            "current_location_id": self.current_location_id,
            "characters": deepcopy(self.characters),
            "locations": deepcopy(self.locations),
            "events": deepcopy(self.events),
            "metadata": {
                "created_at": self.created_at,
                "updated_at": self.updated_at
            }
        }

    @classmethod
    def from_game_state_manager(cls, manager_state: Dict[str, Any], run_id: Optional[str] = None) -> 'GameState':
        """
        Create GameState from backend GameStateManager.state.

        Args:
            manager_state: Dictionary from GameStateManager.get_state()
            run_id: Optional run_id (will use session_id if not provided)

        Returns:
            New GameState instance
        """
        metadata = manager_state.get("metadata", {})

        state = cls(
            run_id=run_id or manager_state.get("session_id"),
            session_id=manager_state.get("session_id"),
            turn=manager_state.get("turn", 0),
            status=manager_state.get("status", "active"),
            created_at=metadata.get("created_at"),
            updated_at=metadata.get("updated_at")
        )

        state.characters = manager_state.get("characters", {})
        state.locations = manager_state.get("locations", {})
        state.events = manager_state.get("events", [])
        state.current_location_id = manager_state.get("current_location_id")

        return state

    def to_save_state_dict(self) -> Dict[str, Any]:
        """
        Convert to save_state.py format for persistence.

        Returns:
            Dictionary in save_state format
        """
        # Convert characters to players/enemies based on team
        players = []
        enemies = []

        for char_id, char_data in self.characters.items():
            team = char_data.get("team", "player") if isinstance(char_data, dict) else "player"
            char_dict = char_data if isinstance(char_data, dict) else {"id": char_id}

            if team == "enemy":
                enemies.append(char_dict)
            else:
                players.append(char_dict)

        quest_data = None
        if self.current_quest_id and self.current_quest_id in self.quests:
            quest_data = self.quests[self.current_quest_id]

        return {
            "game_state": {
                "quest": quest_data,
                "obsidian_data": deepcopy(self.obsidian_data),
                "players": players,
                "enemies": enemies,
                "location": self.current_location_id or "Unknown",
                "run_id": self.run_id,
                "start_time": self.start_time
            }
        }

    @classmethod
    def from_save_state(cls, save_data: Dict[str, Any]) -> 'GameState':
        """
        Create GameState from save_state.py format.

        Args:
            save_data: Dictionary from load_game_from_file()

        Returns:
            New GameState instance
        """
        game_state = save_data.get("game_state", {})

        state = cls(
            run_id=game_state.get("run_id"),
            turn=save_data.get("current_turn", 0),
            status="active",
            start_time=game_state.get("start_time")
        )

        # Combine players and enemies into characters dict
        for player in game_state.get("players", []):
            char_id = player.get("id") or player.get("name", "unknown")
            state.characters[char_id] = player
            if "team" not in state.characters[char_id]:
                state.characters[char_id]["team"] = "player"

        for enemy in game_state.get("enemies", []):
            char_id = enemy.get("id") or enemy.get("name", "unknown")
            state.characters[char_id] = enemy
            if "team" not in state.characters[char_id]:
                state.characters[char_id]["team"] = "enemy"

        state.current_location_id = game_state.get("location")

        quest_data = game_state.get("quest")
        if quest_data:
            quest_id = quest_data.get("quest_id") or "main_quest"
            state.quests[quest_id] = quest_data
            state.current_quest_id = quest_id

        state.obsidian_data = game_state.get("obsidian_data")

        return state

    # ========== Convenience Methods ==========

    def next_turn(self) -> int:
        """Increment turn counter and return new turn number"""
        self.turn += 1
        self.update_timestamp()
        return self.turn

    def add_character(self, char_id: str, character_data: dict) -> None:
        """Add or update a character"""
        self.characters[char_id] = character_data
        self.update_timestamp()

    def get_character(self, char_id: str) -> Optional[dict]:
        """Get character data by ID"""
        return self.characters.get(char_id)

    def add_location(self, loc_id: str, location_data: dict) -> None:
        """Add or update a location"""
        self.locations[loc_id] = location_data
        self.update_timestamp()

    def get_location(self, loc_id: str) -> Optional[dict]:
        """Get location data by ID"""
        return self.locations.get(loc_id)

    def add_event(self, event_data: dict) -> None:
        """Add an event to the timeline"""
        event_data["timestamp"] = datetime.now().isoformat()
        self.events.append(event_data)

        # Keep only last 100 events in memory
        if len(self.events) > 100:
            self.events = self.events[-100:]

        self.update_timestamp()

    def set_status(self, status: str) -> None:
        """Set game status"""
        self.status = status
        self.update_timestamp()

    def to_json(self) -> str:
        """Serialize to JSON string"""
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> 'GameState':
        """Create from JSON string"""
        data = json.loads(json_str)
        state = cls()
        for key, value in data.items():
            if hasattr(state, key):
                setattr(state, key, value)
        return state

    # ========== Validation Methods ==========

    def validate(self) -> List[str]:
        """
        Validate game state and return list of issues found.

        Returns:
            List of issue descriptions (empty if valid)
        """
        issues = []

        # Turn validation
        if self.turn < 0:
            issues.append(f"Invalid: Turn is negative ({self.turn})")

        # Status validation
        valid_statuses = ["active", "completed", "error", "paused"]
        if self.status not in valid_statuses:
            issues.append(f"Invalid: Status '{self.status}' not in {valid_statuses}")

        # Current location validation
        if self.current_location_id and self.current_location_id not in self.locations:
            issues.append(f"Invalid: current_location_id '{self.current_location_id}' not in locations")

        # Character validation (basic - detailed validation should use Character.validate())
        for char_id, char_data in self.characters.items():
            if not isinstance(char_data, dict):
                issues.append(f"Invalid: Character {char_id} data is not a dict")
                continue

            # Check required fields
            if "name" not in char_data:
                issues.append(f"Invalid: Character {char_id} missing 'name' field")
            if "hp" in char_data and char_data["hp"] < 0:
                issues.append(f"Invalid: Character {char_id} has negative HP ({char_data['hp']})")

        # Location validation
        for loc_id, loc_data in self.locations.items():
            if not isinstance(loc_data, dict):
                issues.append(f"Invalid: Location {loc_id} data is not a dict")
                continue
            if "name" not in loc_data:
                issues.append(f"Invalid: Location {loc_id} missing 'name' field")

        return issues

    def fix_validation_issues(self) -> List[str]:
        """
        Automatically fix common validation issues.

        Returns:
            List of fixes applied
        """
        fixes = []

        # Fix turn
        if self.turn < 0:
            self.turn = 0
            fixes.append("Fixed: Set negative turn to 0")

        # Fix status
        valid_statuses = ["active", "completed", "error", "paused"]
        if self.status not in valid_statuses:
            self.status = "active"
            fixes.append(f"Fixed: Reset invalid status to 'active'")

        # Remove invalid current_location_id reference
        if self.current_location_id and self.current_location_id not in self.locations:
            fixes.append(f"Fixed: Removed invalid current_location_id reference ({self.current_location_id})")
            self.current_location_id = None

        return fixes

    # ========== WorldManager Integration Methods ==========

    def sync_with_world_manager(self, world_manager) -> None:
        """
        Synchronize GameState with WorldManager.

        Updates current_location_id and adds all WorldManager locations to GameState.

        Args:
            world_manager: WorldManager instance with locations
        """
        self.current_location_id = world_manager.current_location_id

        # Add all locations from WorldManager to GameState
        for loc_id, location in world_manager.locations.items():
            if hasattr(location, 'to_dict'):
                self.locations[loc_id] = location.to_dict()
            else:
                # Fallback if location doesn't have to_dict
                self.locations[loc_id] = {
                    "id": loc_id,
                    "name": getattr(location, 'name', loc_id),
                    "type": getattr(location, 'location_type', {}).value if hasattr(getattr(location, 'location_type', None), 'value') else "unknown"
                }

        self.update_timestamp()

    def get_current_location_data(self) -> Optional[dict]:
        """
        Get current location data from locations dict.

        Returns:
            Location dict or None if not found
        """
        if self.current_location_id:
            return self.locations.get(self.current_location_id)
        return None

    def update_location(self, location_id: str, location_data: dict) -> None:
        """
        Update location data in GameState.

        Args:
            location_id: Location identifier
            location_data: Location data dict (from Location.to_dict())
        """
        self.locations[location_id] = location_data
        self.update_timestamp()

    def set_current_location(self, location_id: str) -> None:
        """
        Set current location and mark as visited.

        Args:
            location_id: Location identifier
        """
        self.current_location_id = location_id

        # Mark location as visited if it exists
        if location_id in self.locations:
            if "visited" not in self.locations[location_id]:
                self.locations[location_id]["visited"] = False
            self.locations[location_id]["visited"] = True

        self.update_timestamp()

