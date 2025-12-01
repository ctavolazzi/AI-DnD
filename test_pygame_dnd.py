#!/usr/bin/env python3
"""
Test script for pygame D&D game implementation.
This script tests the game logic without opening the GUI window.
"""

import sys
import os
import logging

import pytest

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pygame_dnd_game import PygameDnDGame

def test_game_initialization():
    """Test that the game initializes properly."""
    print("Testing game initialization...")

    try:
        # Create game instance
        game = PygameDnDGame(vault_path="test-vault", model="mistral")

        # Test basic properties
        assert game.game is not None, "Game instance not created"
        assert len(game.game.players) > 0, "No players created"
        assert len(game.game.enemies) > 0, "No enemies created"
        assert len(game.panels) > 0, "No UI panels created"
        assert len(game.buttons) > 0, "No buttons created"

        print("✅ Game initialization successful")
        print(f"   Players: {len(game.game.players)}")
        print(f"   Enemies: {len(game.game.enemies)}")
        print(f"   UI Panels: {len(game.panels)}")
        print(f"   Buttons: {len(game.buttons)}")

    except Exception as exc:  # pragma: no cover - surfaced as pytest failure
        pytest.fail(f"Game initialization failed: {exc}")

def test_character_creation():
    """Test character creation and properties."""
    print("\nTesting character creation...")

    try:
        game = PygameDnDGame(vault_path="test-vault", model="mistral")

        # Test player characters
        for i, player in enumerate(game.game.players):
            assert player.name is not None, f"Player {i} has no name"
            assert player.char_class is not None, f"Player {i} has no class"
            assert player.hp > 0, f"Player {i} has no HP"
            assert player.max_hp > 0, f"Player {i} has no max HP"
            assert player.attack > 0, f"Player {i} has no attack"
            assert player.defense >= 0, f"Player {i} has negative defense"

            print(f"   Player {i+1}: {player.name} ({player.char_class}) - HP: {player.hp}/{player.max_hp}")

        # Test enemy characters
        for i, enemy in enumerate(game.game.enemies):
            assert enemy.name is not None, f"Enemy {i} has no name"
            assert enemy.char_class is not None, f"Enemy {i} has no class"
            assert enemy.hp > 0, f"Enemy {i} has no HP"
            assert enemy.max_hp > 0, f"Enemy {i} has no max HP"

            print(f"   Enemy {i+1}: {enemy.name} ({enemy.char_class}) - HP: {enemy.hp}/{enemy.max_hp}")

        print("✅ Character creation successful")

    except Exception as exc:  # pragma: no cover - surfaced as pytest failure
        pytest.fail(f"Character creation failed: {exc}")

def test_ui_elements():
    """Test UI element creation."""
    print("\nTesting UI elements...")

    try:
        game = PygameDnDGame(vault_path="test-vault", model="mistral")

        # Test panels
        panel_names = [panel.title for panel in game.panels if panel.title]
        expected_panels = ["Game Log", "Status", "Inventory", "Spells", "Quest"]

        for expected in expected_panels:
            assert expected in panel_names, f"Missing panel: {expected}"

        print(f"   Panels: {panel_names}")

        # Test buttons
        button_texts = [button.text for button in game.buttons]
        expected_buttons = ["Next Turn", "Attack", "Cast Spell", "Use Item"]

        for expected in expected_buttons:
            assert expected in button_texts, f"Missing button: {expected}"

        print(f"   Buttons: {button_texts}")

        # Test character displays
        assert len(game.character_displays) > 0, "No character displays created"
        print(f"   Character displays: {len(game.character_displays)}")

        print("✅ UI elements creation successful")

    except Exception as exc:  # pragma: no cover - surfaced as pytest failure
        pytest.fail(f"UI elements test failed: {exc}")

def test_game_mechanics():
    """Test basic game mechanics."""
    print("\nTesting game mechanics...")

    try:
        game = PygameDnDGame(vault_path="test-vault", model="mistral")

        # Test initial game state
        assert not game.game_over, "Game should not be over initially"
        assert game.current_turn == 0, "Game should start at turn 0"

        # Test turn advancement
        initial_turn = game.current_turn
        game.next_turn()
        assert game.current_turn == initial_turn + 1, "Turn should advance"

        print(f"   Initial turn: {initial_turn}")
        print(f"   After next_turn(): {game.current_turn}")

        # Test character stats
        player = game.game.players[0]
        print(f"   Player stats: HP={player.hp}/{player.max_hp}, Attack={player.attack}, Defense={player.defense}")

        print("✅ Game mechanics test successful")

    except Exception as exc:  # pragma: no cover - surfaced as pytest failure
        pytest.fail(f"Game mechanics test failed: {exc}")

def main():
    """Run all tests."""
    print("🧪 Testing Pygame D&D Game Implementation")
    print("=" * 50)

    # Set up logging
    logging.basicConfig(level=logging.WARNING)  # Reduce log noise

    tests = [
        test_game_initialization,
        test_character_creation,
        test_ui_elements,
        test_game_mechanics
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            test()
            passed += 1
        except Exception as exc:
            print(f"❌ {test.__name__} failed: {exc}")

    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Pygame implementation is working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
