"""Integration tests for WorldManager-GameState integration"""

from world_builder import WorldManager
from unified_gamestate import GameState


def test_worldmanager_gamestate_sync():
    """Test syncing WorldManager with GameState"""
    wm = WorldManager()
    gs = GameState(run_id="test_001")

    # Before sync
    assert gs.current_location_id is None, "Should start with no location"
    assert len(gs.locations) == 0, "Should start with no locations"

    # Sync
    gs.sync_with_world_manager(wm)

    # After sync
    assert gs.current_location_id == wm.current_location_id, "Location ID should match"
    assert len(gs.locations) == len(wm.locations), "All locations should be synced"
    assert gs.current_location_id in gs.locations, "Current location should be in locations"

    print("✅ WorldManager-GameState sync test passed")


def test_location_data_persistence():
    """Test location data is properly stored"""
    wm = WorldManager()
    gs = GameState(run_id="test_002")

    gs.sync_with_world_manager(wm)

    # Get current location from WorldManager
    wm_location = wm.get_current_location()

    # Get same location from GameState
    gs_location_data = gs.get_current_location_data()

    assert gs_location_data is not None, "Should have location data"
    assert gs_location_data["name"] == wm_location.name, "Location name should match"
    assert gs_location_data["id"] == wm_location.location_id, "Location ID should match"

    print("✅ Location data persistence test passed")


def test_location_movement_tracking():
    """Test location changes are tracked in GameState"""
    wm = WorldManager()
    gs = GameState(run_id="test_003")

    gs.sync_with_world_manager(wm)
    initial_location = gs.current_location_id

    # Move in WorldManager
    success, message = wm.move("out")  # From tavern to square
    assert success, "Movement should succeed"

    # Update GameState
    gs.set_current_location(wm.current_location_id)

    # Verify change
    assert gs.current_location_id != initial_location, "Location should change"
    assert gs.current_location_id == wm.current_location_id, "Should match WorldManager"

    # Check visited status
    current_data = gs.get_current_location_data()
    assert current_data is not None, "Should have location data"
    assert current_data.get("visited") is True, "Location should be marked visited"

    print("✅ Location movement tracking test passed")


def test_location_update():
    """Test updating location data in GameState"""
    gs = GameState(run_id="test_004")

    # Add a location
    location_data = {
        "id": "test_location",
        "name": "Test Location",
        "type": "town",
        "description": "A test location",
        "visited": False,
        "cleared": False
    }

    gs.update_location("test_location", location_data)

    # Verify
    assert "test_location" in gs.locations, "Location should be added"
    assert gs.locations["test_location"]["name"] == "Test Location", "Name should match"

    # Update it
    location_data["cleared"] = True
    gs.update_location("test_location", location_data)

    assert gs.locations["test_location"]["cleared"] is True, "Location should be updated"

    print("✅ Location update test passed")


if __name__ == "__main__":
    print("🧪 Testing WorldManager-GameState Integration\n")

    test_worldmanager_gamestate_sync()
    test_location_data_persistence()
    test_location_movement_tracking()
    test_location_update()

    print("\n✅ All WorldManager integration tests passed!")

