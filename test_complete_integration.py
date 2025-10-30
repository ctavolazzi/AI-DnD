"""Complete integration test: Character + Inventory + GameState + WorldManager + Validation"""

from dnd_game import Character
from unified_gamestate import GameState
from world_builder import WorldManager


def test_complete_integration():
    """Test full integration: Character → GameState → WorldManager → Validation"""
    print("=== Complete Integration Test ===\n")

    # 1. Create Character with inventory
    char = Character("Hero", "Fighter")
    char.inventory.gold = 100
    char.inventory.add_item('health_potion', 3)
    char.inventory.equip('longsword')

    print("1. Character created with inventory ✅")

    # 2. Validate Character
    char_issues = char.validate()
    assert len(char_issues) == 0, f"Character should be valid: {char_issues}"
    print("2. Character validation passed ✅")

    # 3. Create GameState
    gs = GameState(run_id="integration_test")
    print("3. GameState created ✅")

    # 4. Add Character to GameState
    gs.add_character("hero1", char.to_dict())
    assert "hero1" in gs.characters, "Character should be in GameState"
    print("4. Character added to GameState ✅")

    # 5. Integrate WorldManager
    wm = WorldManager()
    gs.sync_with_world_manager(wm)
    assert len(gs.locations) == len(wm.locations), "Locations should be synced"
    assert gs.current_location_id == wm.current_location_id, "Current location should match"
    print("5. WorldManager synced with GameState ✅")

    # 6. Validate GameState
    gs_issues = gs.validate()
    assert len(gs_issues) == 0, f"GameState should be valid: {gs_issues}"
    print("6. GameState validation passed ✅")

    # 7. Test persistence round-trip
    # Save state
    state_dict = gs.to_dict()

    # Restore state
    restored = GameState()
    for key, value in state_dict.items():
        if hasattr(restored, key):
            setattr(restored, key, value)

    # Verify restoration
    assert restored.run_id == gs.run_id, "Run ID should match"
    assert "hero1" in restored.characters, "Character should be restored"
    assert restored.current_location_id == gs.current_location_id, "Location should match"

    # Verify character inventory in restored state
    restored_char_data = restored.characters["hero1"]
    assert "inventory" in restored_char_data, "Inventory should be in restored data"
    assert restored_char_data["inventory"]["gold"] == 100, "Gold should be restored"

    print("7. Persistence round-trip passed ✅")

    # 8. Test movement integration
    wm.move("out")  # Move to square
    gs.set_current_location(wm.current_location_id)
    assert gs.current_location_id == wm.current_location_id, "Movement should be synced"
    print("8. Location movement integrated ✅")

    # 9. Final validation
    final_char_issues = char.validate()
    final_gs_issues = gs.validate()
    assert len(final_char_issues) == 0, "Character should still be valid"
    assert len(final_gs_issues) == 0, "GameState should still be valid"
    print("9. Final validation passed ✅")

    print("\n✅ Complete integration test PASSED!")
    print("✅ All systems working together correctly")


if __name__ == "__main__":
    test_complete_integration()

