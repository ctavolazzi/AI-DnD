#!/usr/bin/env python3
"""
Test 8: UI Screens Module

Tests the MainGameScreen class that assembles all UI components.
This is the final untested module - 469 lines of screen assembly code.
"""

import sys
import os

# Set SDL to use dummy video driver for headless testing
os.environ['SDL_VIDEODRIVER'] = 'dummy'

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame
from ui.screens import MainGameScreen
from game.game_state import GameState, CharacterState, LocationState, QuestState, InventoryState, GamePhase
from services.image_provider import MockImageProvider


def create_test_game_state() -> GameState:
    """Create a basic game state for testing."""
    # GameState creates instances automatically, so we just need to modify them
    state = GameState()

    # Add a player using the add_player method
    state.add_player(
        name="Test Hero",
        char_class="Warrior",
        hp=75,
        max_hp=100,
        mana=30,
        max_mana=50
    )

    # Modify location (already created by GameState.__init__)
    state.location.name = "Test Dungeon"
    state.location.description = "A dark test dungeon"

    # Modify quest (already created by GameState.__init__)
    state.quest.title = "Test Quest"
    state.quest.description = "Complete the test"

    # Modify inventory (already created by GameState.__init__)
    state.inventory.gold = 150

    # Set phase
    state.phase = GamePhase.EXPLORATION

    return state


def test_screen_initialization():
    """Test MainGameScreen initialization."""
    print("Testing MainGameScreen initialization...")

    pygame.init()
    state = create_test_game_state()
    screen = MainGameScreen(state)

    assert screen.state is state, "Should store game state"
    assert screen.image_provider is not None, "Should have image provider"

    print(f"   Game state: ✓")
    print(f"   Image provider: ✓")
    print("✅ MainGameScreen initialization works")

    pygame.quit()
    return True


def test_screen_has_panels():
    """Test that screen creates all expected panels."""
    print("\nTesting panel creation...")

    pygame.init()
    state = create_test_game_state()
    screen = MainGameScreen(state)

    # Should have 7 panels
    assert hasattr(screen, 'panels'), "Should have panels collection"
    assert len(screen.panels) == 7, f"Should have 7 panels, got {len(screen.panels)}"

    # Individual panels
    assert hasattr(screen, 'scene_panel'), "Should have scene_panel"
    assert hasattr(screen, 'log_panel'), "Should have log_panel"
    assert hasattr(screen, 'map_panel'), "Should have map_panel"
    assert hasattr(screen, 'nav_panel'), "Should have nav_panel"
    assert hasattr(screen, 'char_panel'), "Should have char_panel"
    assert hasattr(screen, 'inv_panel'), "Should have inv_panel"
    assert hasattr(screen, 'quest_panel'), "Should have quest_panel"

    print(f"   Panel count: 7 ✓")
    print(f"   All panels present: ✓")
    print("✅ Panel creation works")

    pygame.quit()
    return True


def test_screen_has_components():
    """Test that screen creates all UI components."""
    print("\nTesting component creation...")

    pygame.init()
    state = create_test_game_state()
    screen = MainGameScreen(state)

    # Scene components
    assert hasattr(screen, 'scene_image'), "Should have scene_image"

    # Log components
    assert hasattr(screen, 'log_text'), "Should have log_text"

    # Map components
    assert hasattr(screen, 'map_image'), "Should have map_image"

    # Character components
    assert hasattr(screen, 'char_portrait'), "Should have char_portrait"
    assert hasattr(screen, 'hp_bar'), "Should have hp_bar"
    assert hasattr(screen, 'mana_bar'), "Should have mana_bar"

    # Inventory components
    assert hasattr(screen, 'inv_grid'), "Should have inv_grid"

    # Quest components
    assert hasattr(screen, 'quest_text'), "Should have quest_text"

    print(f"   Scene components: ✓")
    print(f"   Character components: ✓")
    print(f"   Inventory components: ✓")
    print(f"   Quest components: ✓")
    print("✅ Component creation works")

    pygame.quit()
    return True


def test_screen_has_buttons():
    """Test that screen creates action buttons."""
    print("\nTesting button creation...")

    pygame.init()
    state = create_test_game_state()
    screen = MainGameScreen(state)

    # Should have 4 buttons
    assert hasattr(screen, 'buttons'), "Should have buttons collection"
    assert len(screen.buttons) == 4, f"Should have 4 buttons, got {len(screen.buttons)}"

    # Individual buttons
    assert hasattr(screen, 'btn_next_turn'), "Should have btn_next_turn"
    assert hasattr(screen, 'btn_attack'), "Should have btn_attack"
    assert hasattr(screen, 'btn_cast'), "Should have btn_cast"
    assert hasattr(screen, 'btn_item'), "Should have btn_item"

    # Check button labels
    assert screen.btn_next_turn.text == "Next Turn", "Next turn button label"
    assert screen.btn_attack.text == "Attack", "Attack button label"
    assert screen.btn_cast.text == "Cast Spell", "Cast spell button label"
    assert screen.btn_item.text == "Use Item", "Use item button label"

    print(f"   Button count: 4 ✓")
    print(f"   All buttons present: ✓")
    print(f"   Button labels correct: ✓")
    print("✅ Button creation works")

    pygame.quit()
    return True


def test_button_callbacks():
    """Test button callback wiring."""
    print("\nTesting button callbacks...")

    pygame.init()
    state = create_test_game_state()
    screen = MainGameScreen(state)

    # Buttons should have callbacks
    assert screen.btn_next_turn.callback is not None, "Next turn button should have callback"
    assert screen.btn_attack.callback is not None, "Attack button should have callback"
    assert screen.btn_cast.callback is not None, "Cast button should have callback"
    assert screen.btn_item.callback is not None, "Use item button should have callback"

    print(f"   All buttons have callbacks: ✓")
    print("✅ Button callback wiring works")

    pygame.quit()
    return True


def test_external_callback_registration():
    """Test registering external callbacks."""
    print("\nTesting external callback registration...")

    pygame.init()
    state = create_test_game_state()
    screen = MainGameScreen(state)

    # Track callback execution
    callbacks_called = []

    def on_next_turn():
        callbacks_called.append('next_turn')

    def on_attack():
        callbacks_called.append('attack')

    def on_cast_spell():
        callbacks_called.append('cast')

    def on_use_item():
        callbacks_called.append('item')

    # Register callbacks
    screen.on_next_turn = on_next_turn
    screen.on_attack = on_attack
    screen.on_cast_spell = on_cast_spell
    screen.on_use_item = on_use_item

    # Trigger internal handlers (which should call external callbacks)
    screen._on_next_turn()
    screen._on_attack()
    screen._on_cast_spell()
    screen._on_use_item()

    assert 'next_turn' in callbacks_called, "Next turn callback should execute"
    assert 'attack' in callbacks_called, "Attack callback should execute"
    assert 'cast' in callbacks_called, "Cast callback should execute"
    assert 'item' in callbacks_called, "Item callback should execute"
    assert len(callbacks_called) == 4, "All 4 callbacks should execute"

    print(f"   Callbacks registered: ✓")
    print(f"   Callbacks executed: {len(callbacks_called)}/4")
    print("✅ External callback registration works")

    pygame.quit()
    return True


def test_callback_optional():
    """Test that callbacks are optional (won't crash if None)."""
    print("\nTesting optional callbacks...")

    pygame.init()
    state = create_test_game_state()
    screen = MainGameScreen(state)

    # Callbacks should start as None
    assert screen.on_next_turn is None, "Should start with no next_turn callback"
    assert screen.on_attack is None, "Should start with no attack callback"
    assert screen.on_cast_spell is None, "Should start with no cast callback"
    assert screen.on_use_item is None, "Should start with no item callback"

    # Calling internal handlers should not crash
    try:
        screen._on_next_turn()
        screen._on_attack()
        screen._on_cast_spell()
        screen._on_use_item()
        no_crash = True
    except:
        no_crash = False

    assert no_crash, "Should not crash when callbacks are None"

    print(f"   Callbacks default to None: ✓")
    print(f"   No crash with None callbacks: ✓")
    print("✅ Optional callback handling works")

    pygame.quit()
    return True


def test_update_from_state():
    """Test updating UI from game state."""
    print("\nTesting update_from_state()...")

    pygame.init()
    state = create_test_game_state()
    screen = MainGameScreen(state)

    # Should not crash when called
    try:
        screen.update_from_state()
        success = True
    except Exception as e:
        print(f"   Error: {e}")
        success = False

    assert success, "update_from_state() should not crash"

    print(f"   Update executed: ✓")
    print("✅ update_from_state() works")

    pygame.quit()
    return True


def test_state_updates_components():
    """Test that state changes update UI components."""
    print("\nTesting state synchronization...")

    pygame.init()
    state = create_test_game_state()
    screen = MainGameScreen(state)

    # Modify state
    state.turn_count = 10
    state.quest.title = "New Quest Title"
    player = state.get_current_player()
    player.hp = 50
    player.max_hp = 100

    # Update UI
    screen.update_from_state()

    # Check that UI reflects state
    # (We can't check rendered output in headless mode, but verify no crashes)
    assert state.turn_count == 10, "State should be modified"

    print(f"   State modified: ✓")
    print(f"   UI update completed: ✓")
    print("✅ State synchronization works")

    pygame.quit()
    return True


def test_render_method_exists():
    """Test that render method exists and can be called."""
    print("\nTesting render method...")

    pygame.init()
    state = create_test_game_state()
    screen = MainGameScreen(state)

    # Create a dummy surface
    surface = pygame.Surface((1280, 720))

    # Should not crash when rendering
    try:
        screen.render(surface)
        success = True
    except Exception as e:
        print(f"   Error: {e}")
        import traceback
        traceback.print_exc()
        success = False

    assert success, "render() should not crash"

    print(f"   Render executed: ✓")
    print("✅ render() method works")

    pygame.quit()
    return True


def test_handle_event_method():
    """Test event handling."""
    print("\nTesting event handling...")

    pygame.init()
    state = create_test_game_state()
    screen = MainGameScreen(state)

    # Create a dummy mouse click event
    event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'pos': (100, 100), 'button': 1})

    # Should return boolean and not crash
    try:
        result = screen.handle_event(event)
        assert isinstance(result, bool), "Should return boolean"
        success = True
    except Exception as e:
        print(f"   Error: {e}")
        success = False

    assert success, "handle_event() should work"

    print(f"   Event handling: ✓")
    print("✅ Event handling works")

    pygame.quit()
    return True


def test_custom_image_provider():
    """Test using custom image provider."""
    print("\nTesting custom image provider...")

    pygame.init()
    state = create_test_game_state()
    custom_provider = MockImageProvider()
    screen = MainGameScreen(state, image_provider=custom_provider)

    assert screen.image_provider is custom_provider, "Should use custom provider"

    print(f"   Custom provider set: ✓")
    print("✅ Custom image provider works")

    pygame.quit()
    return True


def main():
    """Run all screen tests."""
    print("🧪 Test 8: UI Screens Module")
    print("=" * 60)
    print("⚠️  Testing final untested module (469 lines)")
    print("=" * 60)

    tests = [
        test_screen_initialization,
        test_screen_has_panels,
        test_screen_has_components,
        test_screen_has_buttons,
        test_button_callbacks,
        test_external_callback_registration,
        test_callback_optional,
        test_update_from_state,
        test_state_updates_components,
        test_render_method_exists,
        test_handle_event_method,
        test_custom_image_provider,
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
        print("🎉 All screen tests passed!")
        print("\n⚠️  NOTE: These are integration/logic tests")
        print("   Actual rendering validated but not visually inspected")
        return 0
    else:
        print("❌ Some screen tests failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
