"""In-memory game state manager with JSON serialization"""
import json
import hashlib
from typing import Dict, List, Optional, Any
from datetime import datetime
from copy import deepcopy


class GameStateManager:
    """
    Manages game state in memory with automatic JSON serialization.

    Features:
    - Fast in-memory access
    - Automatic JSON conversion
    - State snapshots for save/load
    - Integrity checksums
    - Event sourcing support
    """

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.state = {
            "session_id": session_id,
            "turn": 0,
            "status": "active",
            "current_location_id": None,
            "characters": {},  # char_id -> character data
            "locations": {},   # loc_id -> location data
            "events": [],      # event list (most recent)
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
        }

    def get_state(self) -> Dict[str, Any]:
        """Get complete game state as dictionary"""
        return deepcopy(self.state)

    def to_json(self) -> str:
        """Serialize state to JSON string"""
        return json.dumps(self.state, indent=2)

    def from_json(self, json_str: str) -> None:
        """Load state from JSON string"""
        self.state = json.loads(json_str)
        self.state["metadata"]["updated_at"] = datetime.now().isoformat()

    def snapshot(self) -> Dict[str, Any]:
        """
        Create a state snapshot for database persistence.
        Includes checksum for integrity verification.
        """
        snapshot = self.get_state()
        checksum = self.calculate_checksum(snapshot)
        return {
            "snapshot": snapshot,
            "checksum": checksum,
            "timestamp": datetime.now().isoformat()
        }

    def calculate_checksum(self, data: Dict[str, Any]) -> str:
        """Calculate SHA-256 checksum of state data"""
        json_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(json_str.encode()).hexdigest()

    def verify_integrity(self, snapshot: Dict[str, Any], checksum: str) -> bool:
        """Verify snapshot integrity using checksum"""
        calculated = self.calculate_checksum(snapshot)
        return calculated == checksum

    # Character Management
    def add_character(self, char_id: str, char_data: Dict[str, Any]) -> None:
        """Add or update a character"""
        self.state["characters"][char_id] = char_data
        self._update_timestamp()

    def get_character(self, char_id: str) -> Optional[Dict[str, Any]]:
        """Get character data by ID"""
        return self.state["characters"].get(char_id)

    def update_character(self, char_id: str, updates: Dict[str, Any]) -> None:
        """Update specific character fields"""
        if char_id in self.state["characters"]:
            self.state["characters"][char_id].update(updates)
            self._update_timestamp()

    def remove_character(self, char_id: str) -> None:
        """Remove a character"""
        if char_id in self.state["characters"]:
            del self.state["characters"][char_id]
            self._update_timestamp()

    def get_all_characters(self) -> Dict[str, Dict[str, Any]]:
        """Get all characters"""
        return deepcopy(self.state["characters"])

    def get_alive_characters(self) -> List[Dict[str, Any]]:
        """Get all alive characters"""
        return [
            char for char in self.state["characters"].values()
            if char.get("alive", False)
        ]

    # Location Management
    def add_location(self, loc_id: str, loc_data: Dict[str, Any]) -> None:
        """Add or update a location"""
        self.state["locations"][loc_id] = loc_data
        self._update_timestamp()

    def get_location(self, loc_id: str) -> Optional[Dict[str, Any]]:
        """Get location data by ID"""
        return self.state["locations"].get(loc_id)

    def update_location(self, loc_id: str, updates: Dict[str, Any]) -> None:
        """Update specific location fields"""
        if loc_id in self.state["locations"]:
            self.state["locations"][loc_id].update(updates)
            self._update_timestamp()

    def get_current_location(self) -> Optional[Dict[str, Any]]:
        """Get current location"""
        loc_id = self.state.get("current_location_id")
        if loc_id:
            return self.get_location(loc_id)
        return None

    def set_current_location(self, loc_id: str) -> None:
        """Set current location"""
        self.state["current_location_id"] = loc_id
        self._update_timestamp()

    # Event Management
    def add_event(self, event_data: Dict[str, Any]) -> None:
        """Add an event to the timeline"""
        event_data["timestamp"] = datetime.now().isoformat()
        self.state["events"].append(event_data)

        # Keep only last 100 events in memory (older ones in DB)
        if len(self.state["events"]) > 100:
            self.state["events"] = self.state["events"][-100:]

        self._update_timestamp()

    def get_recent_events(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most recent events"""
        return self.state["events"][-limit:]

    def get_events_by_turn(self, turn: int) -> List[Dict[str, Any]]:
        """Get all events for a specific turn"""
        return [
            event for event in self.state["events"]
            if event.get("turn_number") == turn
        ]

    # Turn Management
    def next_turn(self) -> int:
        """Increment turn counter and return new turn number"""
        self.state["turn"] += 1
        self._update_timestamp()
        return self.state["turn"]

    def get_turn(self) -> int:
        """Get current turn number"""
        return self.state["turn"]

    # Status Management
    def set_status(self, status: str) -> None:
        """Set game status (active, paused, completed, failed)"""
        self.state["status"] = status
        self._update_timestamp()

    def get_status(self) -> str:
        """Get current game status"""
        return self.state["status"]

    # Utility
    def _update_timestamp(self) -> None:
        """Update the last modified timestamp"""
        self.state["metadata"]["updated_at"] = datetime.now().isoformat()

    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of current game state"""
        return {
            "session_id": self.session_id,
            "turn": self.state["turn"],
            "status": self.state["status"],
            "character_count": len(self.state["characters"]),
            "alive_character_count": len(self.get_alive_characters()),
            "location_count": len(self.state["locations"]),
            "event_count": len(self.state["events"]),
            "current_location": self.state.get("current_location_id"),
            "updated_at": self.state["metadata"]["updated_at"]
        }


# Global registry of active game sessions
_active_sessions: Dict[str, GameStateManager] = {}


def get_session(session_id: str) -> Optional[GameStateManager]:
    """Get an active game session"""
    return _active_sessions.get(session_id)


def create_session(session_id: str) -> GameStateManager:
    """Create and register a new game session"""
    manager = GameStateManager(session_id)
    _active_sessions[session_id] = manager
    return manager


def delete_session(session_id: str) -> bool:
    """Delete an active game session"""
    if session_id in _active_sessions:
        del _active_sessions[session_id]
        return True
    return False


def get_all_active_sessions() -> List[str]:
    """Get list of all active session IDs"""
    return list(_active_sessions.keys())
