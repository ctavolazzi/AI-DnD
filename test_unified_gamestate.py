"""Test unified GameState class and conversion methods"""

import json
from unified_gamestate import GameState


def test_basic_creation():
    """Test basic GameState creation"""
    state = GameState(run_id="test_001", turn=5)
    assert state.run_id == "test_001"
    assert state.turn == 5
    assert state.status == "active"
    print("✅ Basic creation test passed")


def test_to_from_dict():
    """Test to_dict() and from_dict() round-trip"""
    original = GameState(run_id="test_002", turn=10)
    original.add_character("char1", {"name": "Aldric", "class": "Wizard"})
    original.add_location("loc1", {"name": "Tavern", "type": "tavern"})

    # Convert to dict
    data = original.to_dict()

    # Create from dict
    restored = GameState()
    for key, value in data.items():
        if hasattr(restored, key):
            setattr(restored, key, value)

    assert restored.run_id == original.run_id
    assert restored.turn == original.turn
    assert "char1" in restored.characters
    assert restored.characters["char1"]["name"] == "Aldric"
    print("✅ to_dict/from_dict round-trip test passed")


def test_to_run_data():
    """Test conversion to dungeon_master.py current_run_data format"""
    state = GameState(run_id="test_003", turn=15)
    state.add_character("char1", {"name": "Aldric"})
    state.add_character("char2", {"name": "Thorin"})
    state.current_quest_id = "quest_001"

    run_data = state.to_run_data()

    assert run_data["run_id"] == "test_003"
    assert run_data["turn_count"] == 15
    assert "Aldric" in run_data["characters"]
    assert "Thorin" in run_data["characters"]
    assert run_data["quest"] == "quest_001"
    print("✅ to_run_data() test passed")


def test_from_run_data():
    """Test conversion from dungeon_master.py current_run_data format"""
    run_data = {
        "run_id": "test_004",
        "start_time": "2025-10-29 12:00:00",
        "status": "active",
        "turn_count": 20,
        "characters": ["Aldric", "Thorin"],
        "events": [{"type": "combat", "message": "Battle!"}],
        "combat": [{"round": 1}],
        "locations": ["tavern", "dungeon"],
        "quest": "quest_002"
    }

    state = GameState.from_run_data(run_data)

    assert state.run_id == "test_004"
    assert state.turn == 20
    assert len(state.characters) == 2
    assert len(state.events) == 1
    assert state.current_quest_id == "quest_002"
    print("✅ from_run_data() test passed")


def test_to_game_state_manager():
    """Test conversion to backend GameStateManager format"""
    state = GameState(run_id="test_005", session_id="sess_001", turn=25)
    state.add_character("char1", {"name": "Aldric", "hp": 50})
    state.add_location("loc1", {"name": "Tavern"})
    state.current_location_id = "loc1"

    manager_dict = state.to_game_state_manager_dict()

    assert manager_dict["session_id"] == "sess_001"
    assert manager_dict["turn"] == 25
    assert "char1" in manager_dict["characters"]
    assert manager_dict["current_location_id"] == "loc1"
    assert "metadata" in manager_dict
    print("✅ to_game_state_manager_dict() test passed")


def test_from_game_state_manager():
    """Test conversion from backend GameStateManager format"""
    manager_state = {
        "session_id": "sess_002",
        "turn": 30,
        "status": "active",
        "current_location_id": "loc2",
        "characters": {
            "char1": {"name": "Aldric", "hp": 50}
        },
        "locations": {
            "loc2": {"name": "Dungeon"}
        },
        "events": [{"type": "move"}],
        "metadata": {
            "created_at": "2025-10-29T12:00:00",
            "updated_at": "2025-10-29T12:30:00"
        }
    }

    state = GameState.from_game_state_manager(manager_state, run_id="test_006")

    assert state.run_id == "test_006"
    assert state.session_id == "sess_002"
    assert state.turn == 30
    assert "char1" in state.characters
    assert state.current_location_id == "loc2"
    print("✅ from_game_state_manager() test passed")


def test_convenience_methods():
    """Test convenience methods"""
    state = GameState(run_id="test_007")

    # Add character
    state.add_character("char1", {"name": "Test"})
    assert "char1" in state.characters

    # Get character
    char = state.get_character("char1")
    assert char["name"] == "Test"

    # Next turn
    assert state.next_turn() == 1
    assert state.turn == 1

    # Set status
    state.set_status("completed")
    assert state.status == "completed"

    # Add event
    state.add_event({"type": "test"})
    assert len(state.events) == 1
    assert "timestamp" in state.events[0]

    print("✅ Convenience methods test passed")


if __name__ == "__main__":
    print("🧪 Testing Unified GameState Class\n")

    test_basic_creation()
    test_to_from_dict()
    test_to_run_data()
    test_from_run_data()
    test_to_game_state_manager()
    test_from_game_state_manager()
    test_convenience_methods()

    print("\n✅ All tests passed!")

