#!/usr/bin/env python3
"""
Test 4: Game Loop Module

Tests the main game loop, event handling, and callbacks.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Set SDL to use dummy video driver for headless testing
os.environ['SDL_VIDEODRIVER'] = 'dummy'

import pygame
from pygame_mvp.game.game_loop import GameLoop
from pygame_mvp.game.game_state import GameState, GamePhase, CharacterState


def test_game_loop_initialization():
    """Test GameLoop initialization."""
    print("Testing GameLoop initialization...")

    state = GameState()
    loop = GameLoop(state)

    assert loop.state is state, "State should be stored"
    assert loop.running is False, "Should not be running initially"
    assert loop.clock is None, "Clock should be None before init"
    assert loop.screen is None, "Screen should be None before init"
    assert loop.on_quit is None, "Callbacks should be None initially"
    assert loop.action_callbacks == {}, "Action callbacks should be empty"

    print(f"   State: ✓")
    print(f"   Running: {loop.running}")
    print(f"   Callbacks: ✓")
    print("✅ GameLoop initialization works")
    return True


def test_game_loop_pygame_init():
    """Test pygame initialization."""
    print("\nTesting pygame initialization...")

    state = GameState()
    loop = GameLoop(state)

    result = loop.initialize()

    assert result is True, "Initialization should succeed"
    assert loop.screen is not None, "Screen should be created"
    assert loop.clock is not None, "Clock should be created"

    print(f"   Initialization result: {result}")
    print(f"   Screen created: ✓")
    print(f"   Clock created: ✓")
    print("✅ Pygame initialization works")

    # Cleanup
    pygame.quit()
    return True


def test_action_registration():
    """Test action callback registration."""
    print("\nTesting action registration...")

    state = GameState()
    loop = GameLoop(state)

    # Track if callback was called
    callback_called = []

    def test_callback():
        callback_called.append(True)

    # Register action
    loop.register_action("test_action", test_callback)

    assert "test_action" in loop.action_callbacks, "Action should be registered"

    # Trigger action
    loop.trigger_action("test_action")

    assert len(callback_called) == 1, "Callback should be called once"

    print(f"   Action registered: ✓")
    print(f"   Action triggered: ✓")
    print(f"   Callback executed: ✓")
    print("✅ Action registration works")
    return True


def test_action_with_parameters():
    """Test action callbacks with parameters."""
    print("\nTesting actions with parameters...")

    state = GameState()
    loop = GameLoop(state)

    # Track parameters
    received_params = []

    def param_callback(*args, **kwargs):
        received_params.append((args, kwargs))

    # Register and trigger with args
    loop.register_action("param_action", param_callback)
    loop.trigger_action("param_action", 1, 2, 3, key="value")

    assert len(received_params) == 1, "Callback should be called"
    args, kwargs = received_params[0]
    assert args == (1, 2, 3), "Args should match"
    assert kwargs == {"key": "value"}, "Kwargs should match"

    print(f"   Positional args: {args} ✓")
    print(f"   Keyword args: {kwargs} ✓")
    print("✅ Parameterized actions work")
    return True


def test_trigger_nonexistent_action():
    """Test triggering action that doesn't exist."""
    print("\nTesting nonexistent action...")

    state = GameState()
    loop = GameLoop(state)

    # This should not raise an error
    try:
        loop.trigger_action("nonexistent")
        print(f"   No error on missing action: ✓")
        print("✅ Nonexistent action handling works")
        return True
    except Exception as e:
        print(f"❌ Should not raise error: {e}")
        return False


def test_callback_registration():
    """Test event callback registration."""
    print("\nTesting callback registration...")

    state = GameState()
    loop = GameLoop(state)

    called = []

    def on_quit_callback():
        called.append("quit")

    def on_update_callback(dt):
        called.append(f"update:{dt}")

    def on_render_callback(screen):
        called.append("render")

    loop.on_quit = on_quit_callback
    loop.on_update = on_update_callback
    loop.on_render = on_render_callback

    assert loop.on_quit is on_quit_callback, "Quit callback set"
    assert loop.on_update is on_update_callback, "Update callback set"
    assert loop.on_render is on_render_callback, "Render callback set"

    # Test update callback
    loop.update(0.016)
    assert len(called) == 1, "Update callback should be called"
    assert called[0] == "update:0.016", "Update callback should receive dt"

    print(f"   Quit callback: ✓")
    print(f"   Update callback: ✓")
    print(f"   Render callback: ✓")
    print("✅ Callback registration works")
    return True


def test_update_game_over_detection():
    """Test game over detection in update loop."""
    print("\nTesting game over detection...")

    state = GameState()
    loop = GameLoop(state)

    # Create a losing scenario - all players dead
    # CharacterState imported at top of file
    player = CharacterState(
        name="Hero", char_class="Fighter",
        hp=0, max_hp=100, mana=10, max_mana=10,
        attack=10, defense=5, alive=False
    )
    state.players.append(player)

    # Update should detect game over
    loop.update(0.016)

    assert state.phase == GamePhase.GAME_OVER, "Should transition to game over"
    assert "GAME OVER" in state.adventure_log[-1], "Should log game over message"

    print(f"   Game over detected: ✓")
    print(f"   Phase changed: {state.phase.name}")
    print(f"   Log message: ✓")
    print("✅ Game over detection works")
    return True


def test_update_victory_detection():
    """Test victory detection in update loop."""
    print("\nTesting victory detection...")

    state = GameState()
    loop = GameLoop(state)

    # Create a winning scenario - all enemies dead, player alive
    # CharacterState imported at top of file
    player = CharacterState(
        name="Hero", char_class="Fighter",
        hp=50, max_hp=100, mana=10, max_mana=10,
        attack=10, defense=5, alive=True
    )
    state.players.append(player)

    enemy = CharacterState(
        name="Goblin", char_class="Enemy",
        hp=0, max_hp=30, mana=0, max_mana=0,
        attack=5, defense=2, alive=False, team="enemies"
    )
    state.enemies.append(enemy)

    # Update should detect victory
    loop.update(0.016)

    assert len(state.enemies) == 0, "Enemies should be cleared on victory"
    assert "VICTORY" in state.adventure_log[-1], "Should log victory message"

    print(f"   Victory detected: ✓")
    print(f"   Enemies cleared: ✓")
    print(f"   Log message: ✓")
    print("✅ Victory detection works")
    return True


def test_stop_method():
    """Test stop method."""
    print("\nTesting stop method...")

    state = GameState()
    loop = GameLoop(state)

    loop.running = True
    assert loop.running is True, "Should be running"

    loop.stop()
    assert loop.running is False, "Should stop"

    print(f"   Running: True → False ✓")
    print("✅ Stop method works")
    return True


def main():
    """Run all game loop tests."""
    print("🧪 Test 4: Game Loop Module")
    print("=" * 60)

    tests = [
        test_game_loop_initialization,
        test_game_loop_pygame_init,
        test_action_registration,
        test_action_with_parameters,
        test_trigger_nonexistent_action,
        test_callback_registration,
        test_update_game_over_detection,
        test_update_victory_detection,
        test_stop_method,
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
        print("🎉 All game loop tests passed!")
        return 0
    else:
        print("❌ Some game loop tests failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
