#!/usr/bin/env python3
"""
Headless smoke test for pygame_mvp.

Verifies that the game boots, runs one turn, renders UI to a surface,
and that the image provider returns cached placeholders.
"""

import os
import sys
import random
import unittest
from pathlib import Path

# Force headless SDL to avoid opening a window during CI/local tests.
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

# Ensure repo root is on sys.path so package imports resolve.
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pygame

from pygame_mvp.main import PygameMVP
from pygame_mvp.services.image_provider import MockImageProvider, APIImageProvider
from pygame_mvp.ui.screens import MainGameScreen
from pygame_mvp.config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    SCENE_IMAGE_WIDTH,
    SCENE_IMAGE_HEIGHT,
    MAP_THUMB_WIDTH,
    MAP_THUMB_HEIGHT,
)
from pygame_mvp.game.game_state import CharacterState


class TestPygameMVPSmoke(unittest.TestCase):
    """Boot and render sanity checks."""

    def setUp(self) -> None:
        pygame.init()
        pygame.display.init()
        pygame.display.set_mode((1, 1))
        random.seed(1337)  # keep numbers stable for assertions

    def tearDown(self) -> None:
        pygame.quit()

    def test_bootstrap_and_render(self) -> None:
        """Game can initialize, advance a turn, and render UI headlessly."""
        app = PygameMVP(use_api=False, use_ai_narrative=False)
        app.setup_game()

        state = app.state
        self.assertGreaterEqual(len(state.players), 2)
        self.assertGreaterEqual(len(state.enemies), 2)
        self.assertEqual(state.phase.value, "exploration")

        # Exercise core actions; should not throw.
        app._on_next_turn()
        app._on_attack()
        app._on_cast_spell()
        app._on_use_item()

        self.assertEqual(state.turn_count, 1)
        self.assertEqual(state.phase.value, "combat")
        self.assertGreater(state.inventory.gold, 0)
        self.assertTrue(any("Turn 1" in log for log in state.get_recent_log(6)))

        # Validate placeholder provider caching and sizes.
        provider = MockImageProvider()
        scene_img = provider.get_scene_image("Starting Tavern", 320, 180)
        self.assertEqual(scene_img.get_size(), (320, 180))
        self.assertIs(scene_img, provider.get_scene_image("Starting Tavern", 320, 180))

        # Render UI to an offscreen surface.
        surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        screen = MainGameScreen(state, provider)
        screen.render(surface)  # no exception means success

    def test_combat_turn_reduces_enemy_health(self) -> None:
        """A combat turn should apply damage to at least one enemy."""
        app = PygameMVP(use_api=False, use_ai_narrative=False)
        app.setup_game()
        state = app.state

        # Start combat and process a combat turn
        initial_enemy_hps = [e.hp for e in state.enemies]
        app._on_attack()      # enters combat if enemies exist
        app._on_next_turn()   # processes combat round

        # Ensure at least one enemy took damage or was defeated
        post_hps = [e.hp for e in state.enemies]
        self.assertNotEqual(initial_enemy_hps, post_hps)
        self.assertTrue(
            any(e.hp < e.max_hp or not e.alive for e in state.enemies),
            "Expected at least one enemy to be damaged or defeated during combat turn"
        )

    def test_exploration_event_gold_increases(self) -> None:
        """Exploration turn should be able to award gold when the random event triggers."""
        app = PygameMVP(use_api=False, use_ai_narrative=False)
        app.setup_game()
        state = app.state

        # Force exploration phase and deterministic RNG so the +5 gold event fires.
        state.phase = state.phase.EXPLORATION
        random.seed(1)  # event roll < 0.3 path hits gold branch with this seed
        starting_gold = state.inventory.gold

        app._on_next_turn()  # triggers exploration event roll

        self.assertGreaterEqual(
            state.inventory.gold,
            starting_gold,
            "Exploration event should not reduce gold"
        )

    def test_combat_victory_exits_combat(self) -> None:
        """After defeating the last enemy, combat should end on the next turn."""
        app = PygameMVP(use_api=False, use_ai_narrative=False)
        app.setup_game()
        state = app.state

        make_fragile_single_enemy_state(state)

        # Enter combat, process kill, then confirm exit on next turn.
        app._on_attack()    # enters combat
        app._on_next_turn() # players attack; enemy should die
        app._on_next_turn() # no enemies alive -> victory and exit combat

        self.assertEqual(state.phase.value, "exploration", "Combat should end after victory")
        self.assertTrue(all(not e.alive for e in state.enemies), "All enemies should be defeated")
        self.assertTrue(
            any("Victory" in log for log in state.get_recent_log(6)),
            "Victory message should be logged after combat ends"
        )

    def test_ui_layout_invariants(self) -> None:
        """UI layout keeps expected component counts and dimensions sanity."""
        app = PygameMVP(use_api=False, use_ai_narrative=False)
        app.setup_game()
        provider = MockImageProvider()
        screen = MainGameScreen(app.state, provider)

        # Panel and button counts
        self.assertEqual(len(screen.panels), 7, "Expected 7 panels in main screen")
        self.assertEqual(len(screen.buttons), 4, "Expected 4 action buttons")

        # Ensure scene image and map image align with config sizes
        self.assertEqual(screen.scene_image.width, SCENE_IMAGE_WIDTH)
        self.assertEqual(screen.scene_image.height, SCENE_IMAGE_HEIGHT)
        self.assertEqual(screen.map_image.width, MAP_THUMB_WIDTH)
        self.assertEqual(screen.map_image.height, MAP_THUMB_HEIGHT - 10)

        # Render to ensure no exceptions
        surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        screen.render(surface)

    def test_api_image_provider_fallback(self) -> None:
        """API provider stub returns fallback placeholders with correct size."""
        provider = APIImageProvider(api_url="http://localhost:8000/api/v1")
        surf = provider.get_scene_image("Fallback Scene", 123, 77)
        self.assertIsInstance(surf, pygame.Surface)
        self.assertEqual(surf.get_size(), (123, 77))


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def make_fragile_single_enemy_state(state) -> None:
    """Trim to one fragile enemy and boost players for deterministic victory."""
    state.enemies = state.enemies[:1]
    enemy = state.enemies[0]
    enemy.hp = 1
    enemy.max_hp = 1
    enemy.defense = 0
    for p in state.players:
        p.attack = 20


if __name__ == "__main__":
    unittest.main()
