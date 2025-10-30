"""Integration tests for validation system"""

from dnd_game import Character
from unified_gamestate import GameState


def test_character_validation():
    """Test Character validation methods"""
    char = Character("Test", "Fighter")

    # Valid character should have no issues
    issues = char.validate()
    assert len(issues) == 0, f"Valid character should have no issues: {issues}"

    # Create invalid character
    char.hp = -5  # Negative HP
    char.mana = 1000  # Exceeds max
    char.attack = -10  # Negative attack

    issues = char.validate()
    assert len(issues) > 0, "Invalid character should have issues"
    assert any("HP is negative" in issue for issue in issues), "Should detect negative HP"

    # Fix issues
    fixes = char.fix_validation_issues()
    assert len(fixes) > 0, "Should apply fixes"

    # Verify fixed
    issues_after = char.validate()
    assert len(issues_after) == 0, f"After fixes should be valid: {issues_after}"

    print("✅ Character validation test passed")


def test_gamestate_validation():
    """Test GameState validation methods"""
    gs = GameState(run_id="test")

    # Valid state should have no issues
    issues = gs.validate()
    assert len(issues) == 0, f"Valid state should have no issues: {issues}"

    # Create invalid state
    gs.turn = -5  # Negative turn
    gs.status = "invalid_status"  # Invalid status
    gs.current_location_id = "nonexistent"  # Location not in locations

    issues = gs.validate()
    assert len(issues) > 0, "Invalid state should have issues"
    assert any("Turn is negative" in issue for issue in issues), "Should detect negative turn"
    assert any("Status" in issue for issue in issues), "Should detect invalid status"

    # Fix issues
    fixes = gs.fix_validation_issues()
    assert len(fixes) > 0, "Should apply fixes"

    # Verify fixed
    issues_after = gs.validate()
    assert len(issues_after) == 0, f"After fixes should be valid: {issues_after}"

    print("✅ GameState validation test passed")


def test_validation_with_characters():
    """Test validation with characters in GameState"""
    gs = GameState(run_id="test")

    # Add valid character
    char = Character("Hero", "Fighter")
    gs.add_character("char1", char.to_dict())

    issues = gs.validate()
    assert len(issues) == 0, "Valid character should cause no issues"

    # Add invalid character data
    gs.add_character("char2", {"hp": -10})  # Missing name, negative HP

    issues = gs.validate()
    assert len(issues) > 0, "Invalid character should cause issues"
    assert any("missing 'name'" in issue for issue in issues), "Should detect missing name"
    assert any("negative HP" in issue for issue in issues), "Should detect negative HP"

    print("✅ GameState character validation test passed")


if __name__ == "__main__":
    print("🧪 Testing Validation Integration\n")

    test_character_validation()
    test_gamestate_validation()
    test_validation_with_characters()

    print("\n✅ All validation integration tests passed!")

