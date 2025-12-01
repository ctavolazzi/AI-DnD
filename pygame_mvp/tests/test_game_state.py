#!/usr/bin/env python3
"""
Test 2: Game State Module

Tests the centralized game state manager and related data structures.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game.game_state import (
    GameState, GamePhase, CharacterState,
    InventoryState, QuestState, LocationState
)


def test_game_phase_enum():
    """Test GamePhase enum has all required states."""
    print("Testing GamePhase enum...")

    required_phases = ["MENU", "EXPLORATION", "COMBAT", "DIALOGUE", "INVENTORY", "GAME_OVER"]

    for phase_name in required_phases:
        assert hasattr(GamePhase, phase_name), f"Missing phase: {phase_name}"

    print(f"   Found {len(GamePhase)} game phases")
    for phase in GamePhase:
        print(f"   - {phase.name}: {phase.value}")
    print("✅ GamePhase enum valid")
    return True


def test_character_state_creation():
    """Test CharacterState dataclass."""
    print("\nTesting CharacterState creation...")

    char = CharacterState(
        name="Test Hero",
        char_class="Fighter",
        hp=50,
        max_hp=50,
        mana=10,
        max_mana=10,
        attack=15,
        defense=5
    )

    assert char.name == "Test Hero"
    assert char.char_class == "Fighter"
    assert char.hp == 50
    assert char.max_hp == 50
    assert char.mana == 10
    assert char.max_mana == 10
    assert char.attack == 15
    assert char.defense == 5
    assert char.alive is True
    assert char.team == "players"
    assert char.status_effects == []

    print(f"   Character: {char.name} ({char.char_class})")
    print(f"   HP: {char.hp}/{char.max_hp}")
    print(f"   Mana: {char.mana}/{char.max_mana}")
    print(f"   Attack: {char.attack}, Defense: {char.defense}")
    print("✅ CharacterState creation works")
    return True


def test_character_state_properties():
    """Test CharacterState computed properties."""
    print("\nTesting CharacterState properties...")

    char = CharacterState(
        name="Wounded Hero",
        char_class="Fighter",
        hp=25,
        max_hp=100,
        mana=3,
        max_mana=10,
        attack=15,
        defense=5
    )

    # Test hp_percent
    assert char.hp_percent == 0.25, f"HP percent wrong: {char.hp_percent}"

    # Test mana_percent
    assert char.mana_percent == 0.3, f"Mana percent wrong: {char.mana_percent}"

    # Test edge case: 0 max_hp
    char.max_hp = 0
    assert char.hp_percent == 0, "HP percent should be 0 when max_hp is 0"

    # Test edge case: 0 max_mana
    char.max_mana = 0
    assert char.mana_percent == 0, "Mana percent should be 0 when max_mana is 0"

    print(f"   HP percent calculation: ✓")
    print(f"   Mana percent calculation: ✓")
    print(f"   Edge cases handled: ✓")
    print("✅ CharacterState properties work correctly")
    return True


def test_inventory_state():
    """Test InventoryState dataclass."""
    print("\nTesting InventoryState...")

    inventory = InventoryState()

    # Items is now a list (not dict)
    assert inventory.items == []
    assert inventory.equipped == {}
    assert inventory.gold == 0
    assert inventory.capacity == 20

    # Test adding items using the new add_item method
    from pygame_mvp.game.game_state import InventoryItem
    potion = InventoryItem(name="potion", quantity=5)
    sword = InventoryItem(name="sword", quantity=1)
    inventory.add_item(potion)
    inventory.add_item(sword)
    assert len(inventory.items) == 2
    
    # Test get_item
    found_potion = inventory.get_item("potion")
    assert found_potion is not None
    assert found_potion.quantity == 5

    # Test equipping items
    inventory.equipped["weapon"] = "sword"
    assert inventory.equipped["weapon"] == "sword"

    # Test gold
    inventory.gold = 100
    assert inventory.gold == 100

    print(f"   Items: {len(inventory.items)} types")
    print(f"   Equipped: {len(inventory.equipped)} slots")
    print(f"   Gold: {inventory.gold}")
    print(f"   Capacity: {inventory.capacity}")
    print("✅ InventoryState works correctly")
    return True


def test_quest_state():
    """Test QuestState dataclass."""
    print("\nTesting QuestState...")

    quest = QuestState()

    assert quest.title == "No Active Quest"
    assert quest.description == ""
    assert quest.objectives == []
    assert quest.completed is False

    # Test setting quest
    quest.title = "Rescue the Princess"
    quest.description = "Save Princess Zelda from Ganon"
    quest.objectives = [
        {"text": "Enter the castle", "done": True},
        {"text": "Defeat Ganon", "done": False}
    ]

    assert quest.title == "Rescue the Princess"
    assert len(quest.objectives) == 2
    assert quest.objectives[0]["done"] is True
    assert quest.objectives[1]["done"] is False

    print(f"   Quest: {quest.title}")
    print(f"   Objectives: {len(quest.objectives)}")
    print(f"   Completed: {quest.completed}")
    print("✅ QuestState works correctly")
    return True


def test_location_state():
    """Test LocationState dataclass."""
    print("\nTesting LocationState...")

    location = LocationState()

    assert location.name == "Starting Tavern"
    assert location.description == "A cozy tavern where adventurers gather."
    assert location.available_exits == []
    assert location.npcs == []
    assert location.items == []

    # Test modifying location
    location.name = "Dark Forest"
    location.description = "A mysterious forest filled with danger"
    location.available_exits = ["north", "east"]
    location.npcs = ["Wise Old Man", "Merchant"]
    location.items = ["Rusty Sword", "Health Potion"]

    assert location.name == "Dark Forest"
    assert len(location.available_exits) == 2
    assert len(location.npcs) == 2
    assert len(location.items) == 2

    print(f"   Location: {location.name}")
    print(f"   Exits: {len(location.available_exits)}")
    print(f"   NPCs: {len(location.npcs)}")
    print(f"   Items: {len(location.items)}")
    print("✅ LocationState works correctly")
    return True


def test_game_state_initialization():
    """Test GameState initialization."""
    print("\nTesting GameState initialization...")

    game_state = GameState()

    assert game_state.phase == GamePhase.EXPLORATION
    assert game_state.turn_count == 0
    assert game_state.scene_counter == 0
    assert game_state.players == []
    assert game_state.enemies == []
    assert game_state.current_player_index == 0
    assert isinstance(game_state.location, LocationState)
    assert game_state.visited_locations == ["Starting Tavern"]
    assert isinstance(game_state.quest, QuestState)

    print(f"   Phase: {game_state.phase.name}")
    print(f"   Turn count: {game_state.turn_count}")
    print(f"   Players: {len(game_state.players)}")
    print(f"   Enemies: {len(game_state.enemies)}")
    print(f"   Location: {game_state.location.name}")
    print("✅ GameState initialization works")
    return True


def test_game_state_character_management():
    """Test adding and managing characters in GameState."""
    print("\nTesting GameState character management...")

    game_state = GameState()

    # Add players
    player1 = CharacterState(
        name="Hero1", char_class="Fighter",
        hp=100, max_hp=100, mana=20, max_mana=20,
        attack=15, defense=10
    )
    player2 = CharacterState(
        name="Hero2", char_class="Wizard",
        hp=60, max_hp=60, mana=100, max_mana=100,
        attack=8, defense=5
    )

    game_state.players.append(player1)
    game_state.players.append(player2)

    assert len(game_state.players) == 2
    assert game_state.players[0].name == "Hero1"
    assert game_state.players[1].name == "Hero2"

    # Add enemies
    enemy1 = CharacterState(
        name="Goblin", char_class="Enemy",
        hp=30, max_hp=30, mana=0, max_mana=0,
        attack=8, defense=3, team="enemies"
    )

    game_state.enemies.append(enemy1)

    assert len(game_state.enemies) == 1
    assert game_state.enemies[0].name == "Goblin"

    print(f"   Players added: {len(game_state.players)}")
    print(f"   Enemies added: {len(game_state.enemies)}")
    print("✅ Character management works")
    return True


def main():
    """Run all game state tests."""
    print("🧪 Test 2: Game State Module")
    print("=" * 60)

    tests = [
        test_game_phase_enum,
        test_character_state_creation,
        test_character_state_properties,
        test_inventory_state,
        test_quest_state,
        test_location_state,
        test_game_state_initialization,
        test_game_state_character_management,
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

    print("\n" + "=" * 60)
    print(f"Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All game state tests passed!")
        return 0
    else:
        print("❌ Some game state tests failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
