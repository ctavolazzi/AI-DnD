#!/usr/bin/env python3
"""
Pygame MVP - Fresh Architecture

Entry point for the Pygame D&D game with placeholder image system.

Features:
- Clean architecture with centralized state
- Placeholder images that show exactly what API calls will be made
- No network calls during development - fast iteration
- Single config change to switch to real API images

Usage:
    python pygame_mvp/main.py

    # Or with real API (when ready)
    python pygame_mvp/main.py --use-api
"""

import sys
import random
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import pygame

from config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, GAME_TITLE, CURRENT_THEME, SHOW_FPS
from game.game_state import GameState, GamePhase
from game.game_loop import GameLoop
from services.image_provider import MockImageProvider, APIImageProvider
from services.narrative import NarrativeService
from ui.screens import MainGameScreen


class PygameMVP:
    """
    Main game application.

    Coordinates game state, UI, and game logic.
    """

    def __init__(self, use_api: bool = False, use_ai_narrative: bool = False):
        # Initialize state
        self.state = GameState()

        # Initialize services
        if use_api:
            self.image_provider = APIImageProvider()
        else:
            self.image_provider = MockImageProvider()

        self.narrative = NarrativeService(use_ai=use_ai_narrative)

        # Initialize game loop
        self.loop = GameLoop(self.state)

        # Initialize screen (after pygame init in run)
        self.screen: MainGameScreen = None

        # FPS tracking
        self.show_fps = SHOW_FPS
        self.fps_font = None

    def setup_game(self) -> None:
        """Set up initial game state."""
        # Create player characters
        self.state.add_player(
            "Hero",
            random.choice(["Fighter", "Wizard", "Rogue", "Cleric"]),
            hp=35, max_hp=35,
            mana=50, max_mana=50,
            attack=12, defense=5
        )
        self.state.add_player(
            "Companion",
            random.choice(["Fighter", "Wizard", "Rogue", "Cleric"]),
            hp=28, max_hp=28,
            mana=40, max_mana=40,
            attack=10, defense=4
        )

        # Create initial enemies
        self.state.add_enemy(
            "Goblin Scout",
            "Goblin",
            hp=15, max_hp=15,
            attack=6, defense=2
        )
        self.state.add_enemy(
            "Goblin Warrior",
            "Goblin",
            hp=20, max_hp=20,
            attack=8, defense=3
        )

        # Set initial location
        self.state.set_location(
            "Starting Tavern",
            "A cozy tavern where adventurers gather. The fire crackles warmly.",
            exits=["Village Square", "Dark Forest"],
            npcs=["Bartender", "Mysterious Stranger"]
        )

        # Set initial quest
        self.state.quest.title = "The Goblin Problem"
        self.state.quest.description = "Clear the goblin camp threatening the village trade route."

        # Add starting gold
        self.state.inventory.gold = random.randint(20, 50)

        # Log game start
        self.state.log("Welcome to the adventure!")
        self.state.log(f"Location: {self.state.location.name}")
        self.state.log(f"Quest: {self.state.quest.title}")
        self.state.log("")
        self.state.log("Your party stands ready...")

    def _on_next_turn(self) -> None:
        """Handle next turn action."""
        self.state.advance_turn()
        self.state.log(f"--- Turn {self.state.turn_count} ---")

        # Simple combat simulation
        if self.state.phase == GamePhase.COMBAT:
            self._process_combat_turn()
        else:
            self._process_exploration_turn()

    def _process_combat_turn(self) -> None:
        """Process a combat turn."""
        # Get alive combatants
        alive_players = self.state.get_alive_players()
        alive_enemies = self.state.get_alive_enemies()

        if not alive_enemies:
            self.state.log("Victory! All enemies defeated!")
            self.state.end_combat()
            return

        if not alive_players:
            self.state.log("Defeat! Your party has fallen...")
            self.state.phase = GamePhase.GAME_OVER
            return

        # Players attack
        for player in alive_players:
            if alive_enemies:
                target = random.choice(alive_enemies)
                damage = max(1, player.attack - target.defense + random.randint(-2, 4))
                target.hp -= damage
                self.state.log(f"{player.name} attacks {target.name} for {damage} damage!")

                if target.hp <= 0:
                    target.alive = False
                    self.state.log(f"{target.name} has been defeated!")
                    alive_enemies = [e for e in alive_enemies if e.alive]

        # Enemies attack
        alive_enemies = self.state.get_alive_enemies()
        for enemy in alive_enemies:
            if alive_players:
                target = random.choice(alive_players)
                damage = max(1, enemy.attack - target.defense + random.randint(-2, 2))
                target.hp -= damage
                self.state.log(f"{enemy.name} attacks {target.name} for {damage} damage!")

                if target.hp <= 0:
                    target.alive = False
                    self.state.log(f"{target.name} has fallen!")
                    alive_players = [p for p in alive_players if p.alive]

    def _process_exploration_turn(self) -> None:
        """Process an exploration turn."""
        # Random events
        if random.random() < 0.3:
            events = [
                "You find a small health potion!",
                "A crow caws ominously in the distance.",
                "You discover some gold coins! (+5 gold)",
                "The path ahead looks treacherous.",
                "You hear rustling in the bushes..."
            ]
            event = random.choice(events)
            self.state.log(event)

            if "+5 gold" in event:
                self.state.inventory.gold += 5

        # Chance of encounter
        if random.random() < 0.2 and not self.state.get_alive_enemies():
            self.state.log("")
            self.state.log("*** ENCOUNTER! ***")
            self.state.add_enemy(
                f"Wild Goblin",
                "Goblin",
                hp=12, max_hp=12,
                attack=5, defense=1
            )
            self.state.start_combat()

    def _on_attack(self) -> None:
        """Handle attack action."""
        if self.state.phase != GamePhase.COMBAT:
            # Start combat if enemies exist
            if self.state.get_alive_enemies():
                self.state.start_combat()
                self.state.log("Combat initiated!")
            else:
                self.state.log("No enemies to attack.")
        else:
            # Process an attack
            self._on_next_turn()

    def _on_cast_spell(self) -> None:
        """Handle cast spell action."""
        player = self.state.get_current_player()
        if player and player.mana >= 10:
            player.mana -= 10

            # Healing spell
            heal_amount = random.randint(5, 15)
            player.hp = min(player.max_hp, player.hp + heal_amount)
            self.state.log(f"{player.name} casts a healing spell for {heal_amount} HP!")
        else:
            self.state.log("Not enough mana!")

    def _on_use_item(self) -> None:
        """Handle use item action."""
        if self.state.inventory.gold >= 10:
            self.state.inventory.gold -= 10
            player = self.state.get_current_player()
            if player:
                player.hp = min(player.max_hp, player.hp + 10)
                self.state.log(f"Used a health potion! {player.name} healed 10 HP.")
        else:
            self.state.log("No usable items!")

    def _on_render(self, surface: pygame.Surface) -> None:
        """Render callback."""
        if self.screen:
            self.screen.render(surface)

        # Render FPS
        if self.show_fps and self.fps_font and self.loop.clock:
            fps = int(self.loop.clock.get_fps())
            fps_text = self.fps_font.render(f"FPS: {fps}", True, (100, 100, 100))
            surface.blit(fps_text, (SCREEN_WIDTH - 70, 5))

    def _on_event(self, event: pygame.event.Event) -> None:
        """Handle events."""
        if self.screen:
            self.screen.handle_event(event)

    def run(self) -> None:
        """Run the game."""
        # Initialize pygame
        if not self.loop.initialize():
            print("Failed to initialize pygame")
            return

        # Initialize fonts for FPS display
        pygame.font.init()
        self.fps_font = pygame.font.Font(None, 20)

        # Create screen
        self.screen = MainGameScreen(self.state, self.image_provider)

        # Set up action callbacks
        self.screen.on_next_turn = self._on_next_turn
        self.screen.on_attack = self._on_attack
        self.screen.on_cast_spell = self._on_cast_spell
        self.screen.on_use_item = self._on_use_item

        # Set up loop callbacks
        self.loop.on_render = self._on_render
        self.loop.on_mouse_down = self._on_event
        self.loop.on_mouse_up = self._on_event
        self.loop.on_mouse_motion = self._on_event

        # Register action shortcuts
        self.loop.register_action("next_turn", self._on_next_turn)
        self.loop.register_action("action_0", self._on_next_turn)
        self.loop.register_action("action_1", self._on_attack)
        self.loop.register_action("action_2", self._on_cast_spell)
        self.loop.register_action("action_3", self._on_use_item)

        # Set up game
        self.setup_game()

        # Run main loop
        self.loop.run()


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Pygame MVP - D&D Adventure Game")
    parser.add_argument("--use-api", action="store_true", help="Use real API for images")
    parser.add_argument("--use-ai", action="store_true", help="Use AI for narrative generation")
    args = parser.parse_args()

    print(f"""
╔══════════════════════════════════════════════════════════════╗
║             Pygame MVP - D&D Adventure Game                  ║
╠══════════════════════════════════════════════════════════════╣
║  Image Provider: {"API (Real Images)" if args.use_api else "Mock (Placeholders)":40} ║
║  Narrative:      {"AI-Generated" if args.use_ai else "Fallback Text":40} ║
╠══════════════════════════════════════════════════════════════╣
║  Controls:                                                   ║
║    [SPACE] - Next Turn                                       ║
║    [1-4]   - Quick Actions                                   ║
║    [ESC]   - Quit                                            ║
║    Mouse   - Click buttons and UI                            ║
╚══════════════════════════════════════════════════════════════╝
    """)

    game = PygameMVP(use_api=args.use_api, use_ai_narrative=args.use_ai)
    game.run()


if __name__ == "__main__":
    main()

