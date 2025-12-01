#!/usr/bin/env python3
"""
Test 5: Narrative Service Module

Tests the narrative service wrapper with fallback text generation.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.narrative import NarrativeService


def test_narrative_service_initialization():
    """Test NarrativeService initialization."""
    print("Testing NarrativeService initialization...")

    # Test without AI
    service = NarrativeService(use_ai=False)
    assert service.use_ai is False, "Should not use AI"
    assert service._engine is None, "Engine should be None"

    # Test with AI (will likely fall back since narrative_engine may not exist)
    service_ai = NarrativeService(use_ai=True)
    assert service_ai.use_ai is True, "Should attempt to use AI"

    print(f"   AI disabled: ✓")
    print(f"   AI enabled (fallback expected): ✓")
    print("✅ NarrativeService initialization works")
    return True


def test_describe_scene_fallback():
    """Test scene description with fallback text."""
    print("\nTesting scene description (fallback)...")

    service = NarrativeService(use_ai=False)

    # Test with characters
    result = service.describe_scene("Dark Forest", ["Hero", "Wizard"])
    assert "Dark Forest" in result, "Should include location"
    assert "Hero" in result or "Wizard" in result, "Should include characters"

    print(f"   Location included: ✓")
    print(f"   Characters included: ✓")
    print(f"   Generated: \"{result}\"")

    # Test with no characters
    result_empty = service.describe_scene("Empty Cave", [])
    assert "Empty Cave" in result_empty, "Should include location"
    assert "no one" in result_empty or "empty" in result_empty.lower(), "Should handle empty character list"

    print(f"   Empty character list: ✓")
    print("✅ Scene description works")
    return True


def test_describe_combat_fallback():
    """Test combat description with fallback text."""
    print("\nTesting combat description (fallback)...")

    service = NarrativeService(use_ai=False)

    # Test with damage
    result = service.describe_combat("Hero", "Goblin", "strikes", damage=15)
    assert "Hero" in result, "Should include attacker"
    assert "Goblin" in result, "Should include defender"
    assert "strikes" in result, "Should include action"
    assert "15" in result, "Should include damage"

    print(f"   Combat with damage: \"{result}\" ✓")

    # Test without damage
    result_no_dmg = service.describe_combat("Wizard", "Dragon", "casts fireball")
    assert "Wizard" in result_no_dmg, "Should include attacker"
    assert "Dragon" in result_no_dmg, "Should include defender"
    assert "fireball" in result_no_dmg, "Should include action"

    print(f"   Combat without damage: \"{result_no_dmg}\" ✓")
    print("✅ Combat description works")
    return True


def test_generate_quest_fallback():
    """Test quest generation with fallback text."""
    print("\nTesting quest generation (fallback)...")

    service = NarrativeService(use_ai=False)

    # Test easy quest
    easy_quest = service.generate_quest("easy")
    assert isinstance(easy_quest, str), "Should return string"
    assert len(easy_quest) > 0, "Should not be empty"

    # Test medium quest
    medium_quest = service.generate_quest("medium")
    assert isinstance(medium_quest, str), "Should return string"
    assert len(medium_quest) > 0, "Should not be empty"

    # Test hard quest
    hard_quest = service.generate_quest("hard")
    assert isinstance(hard_quest, str), "Should return string"
    assert len(hard_quest) > 0, "Should not be empty"

    # Test unknown difficulty (should default to medium)
    default_quest = service.generate_quest("unknown")
    assert isinstance(default_quest, str), "Should return string"
    assert len(default_quest) > 0, "Should not be empty"

    print(f"   Easy: \"{easy_quest[:40]}...\"")
    print(f"   Medium: \"{medium_quest[:40]}...\"")
    print(f"   Hard: \"{hard_quest[:40]}...\"")
    print(f"   Default fallback: ✓")
    print("✅ Quest generation works")
    return True


def test_handle_action_fallback():
    """Test player action handling with fallback text."""
    print("\nTesting player action handling (fallback)...")

    service = NarrativeService(use_ai=False)

    result = service.handle_action("Hero", "search the room", "dungeon")
    assert "Hero" in result, "Should include player name"
    assert "search" in result.lower(), "Should include action"

    print(f"   Action handling: \"{result}\" ✓")
    print("✅ Player action handling works")
    return True


def test_generate_encounter_fallback():
    """Test encounter generation with fallback text."""
    print("\nTesting encounter generation (fallback)...")

    service = NarrativeService(use_ai=False)

    # Generate multiple encounters to test randomness
    encounters = set()
    for _ in range(10):
        encounter = service.generate_encounter(5, "forest")
        assert isinstance(encounter, str), "Should return string"
        assert len(encounter) > 0, "Should not be empty"
        encounters.add(encounter)

    print(f"   Generated {len(encounters)} unique encounters from 10 attempts")
    print(f"   Sample: \"{list(encounters)[0]}\"")
    print("✅ Encounter generation works")
    return True


def test_all_methods_work_without_ai():
    """Test that all methods work without AI engine."""
    print("\nTesting all methods without AI...")

    service = NarrativeService(use_ai=False)

    # All these should work with fallback text
    scene = service.describe_scene("Test Location", ["Character"])
    combat = service.describe_combat("A", "B", "attacks", 10)
    quest = service.generate_quest()
    action = service.handle_action("Player", "test", "context")
    encounter = service.generate_encounter(1, "test")

    assert isinstance(scene, str) and len(scene) > 0
    assert isinstance(combat, str) and len(combat) > 0
    assert isinstance(quest, str) and len(quest) > 0
    assert isinstance(action, str) and len(action) > 0
    assert isinstance(encounter, str) and len(encounter) > 0

    print(f"   describe_scene: ✓")
    print(f"   describe_combat: ✓")
    print(f"   generate_quest: ✓")
    print(f"   handle_action: ✓")
    print(f"   generate_encounter: ✓")
    print("✅ All methods work without AI engine")
    return True


def test_encounter_randomness():
    """Test that encounter generation provides variety."""
    print("\nTesting encounter randomness...")

    service = NarrativeService(use_ai=False)

    encounters = [service.generate_encounter(5, "dungeon") for _ in range(20)]

    unique_count = len(set(encounters))

    # Should have at least 2 different encounters in 20 attempts
    assert unique_count >= 2, f"Should have variety, got {unique_count} unique"

    print(f"   20 generations produced {unique_count} unique encounters")
    print(f"   Variety confirmed: ✓")
    print("✅ Encounter randomness works")
    return True


def main():
    """Run all narrative service tests."""
    print("🧪 Test 5: Narrative Service Module")
    print("=" * 60)

    tests = [
        test_narrative_service_initialization,
        test_describe_scene_fallback,
        test_describe_combat_fallback,
        test_generate_quest_fallback,
        test_handle_action_fallback,
        test_generate_encounter_fallback,
        test_all_methods_work_without_ai,
        test_encounter_randomness,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            if test():
                passed += 1
        except AssertionError as e:
            print(f"❌ Test failed: {e}")
        except Exception as e:
            print(f"❌ Test error: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 60)
    print(f"Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All narrative service tests passed!")
        return 0
    else:
        print("❌ Some narrative service tests failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
