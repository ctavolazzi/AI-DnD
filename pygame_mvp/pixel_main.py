#!/usr/bin/env python3
"""
Quest for the Golden Bunch - Main Entry Point

A pixel art RPG with Nano Banana Games-inspired UI.

Features:
- Animated title screen with menu navigation
- Full pixel art HUD (HP/MP bars, minimap)
- Category-based inventory system
- NPC dialogue with typewriter effect
- Turn-based combat system
- Quest tracking
- Save/Load system

Controls:
- WASD / Arrows: Move / Navigate menus
- Enter / Space: Select / Advance dialogue
- I: Open inventory
- T: Talk (debug dialogue)
- Ctrl+S: Quick save
- Ctrl+L: Quick load
- ESC: Menu / Close overlays
"""

import sys
from pathlib import Path
from enum import Enum

# Add project root to path for module imports
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import pygame

from pygame_mvp.config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, GAME_TITLE
from pygame_mvp.ui.title_screen import TitleScreen
from pygame_mvp.game.pixel_game_manager import PixelGameManager
from pygame_mvp.game.systems import CharacterClass


class AppState(Enum):
    """Application state machine states."""
    TITLE = "title"
    GAME = "game"
    GAME_OVER = "game_over"


class PixelRPGApp:
    """
    Main application class managing state transitions and main loop.
    """

    def __init__(self):
        # Initialize Pygame
        pygame.init()
        pygame.font.init()

        # Create window
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Quest for the Golden Bunch")

        self.clock = pygame.time.Clock()
        self.running = True
        self.state = AppState.TITLE

        # Initialize components
        self._setup_title_screen()
        self._setup_game_manager()

        # Print welcome message
        self._print_welcome()

    def _setup_title_screen(self) -> None:
        """Initialize the title screen."""
        self.title_screen = TitleScreen(self.screen)

        # Wire callbacks
        self.title_screen.on_new_game = self._start_new_game
        self.title_screen.on_load_game = self._load_game
        self.title_screen.on_options = self._show_options
        self.title_screen.on_quit = self._quit_game

    def _setup_game_manager(self) -> None:
        """Initialize the game manager."""
        self.game_manager = PixelGameManager(self.screen)

    def _print_welcome(self) -> None:
        """Print welcome message to console."""
        print("""
╔══════════════════════════════════════════════════════════════╗
║          Quest for the Golden Bunch - Pixel RPG              ║
╠══════════════════════════════════════════════════════════════╣
║  Controls:                                                   ║
║    [WASD/Arrows] - Move / Navigate                           ║
║    [Enter/Space] - Select / Advance                          ║
║    [I]           - Inventory                                 ║
║    [T]           - Talk (debug dialogue)                     ║
║    [Ctrl+S]      - Quick Save                                ║
║    [Ctrl+L]      - Quick Load                                ║
║    [ESC]         - Menu / Close                              ║
╚══════════════════════════════════════════════════════════════╝
        """)

    # ========================================================================
    # STATE TRANSITIONS
    # ========================================================================

    def _start_new_game(self) -> None:
        """Start a new game."""
        print("Starting new game...")

        # TODO: Add character creation screen
        # For now, use default character
        self.game_manager.start_new_game(
            player_name="Hero",
            player_class=CharacterClass.FIGHTER
        )

        self.state = AppState.GAME

    def _load_game(self) -> None:
        """Load a saved game."""
        print("Loading game...")

        if self.game_manager.load_game(slot=1):
            self.state = AppState.GAME
        else:
            # No save found, start new game
            print("No save found, starting new game...")
            self._start_new_game()

    def _show_options(self) -> None:
        """Show options menu."""
        print("Options menu not yet implemented")
        # TODO: Implement options screen

    def _quit_game(self) -> None:
        """Quit the application."""
        print("Goodbye!")
        self.running = False

    def _return_to_title(self) -> None:
        """Return to title screen."""
        self.state = AppState.TITLE

    # ========================================================================
    # MAIN LOOP
    # ========================================================================

    def run(self) -> None:
        """Main application loop."""
        while self.running:
            # Handle events
            self._handle_events()

            # Update state
            self._update()

            # Render
            self._render()

            # Flip display
            pygame.display.flip()

            # Cap framerate
            self.clock.tick(FPS)

        # Cleanup
        pygame.quit()

    def _handle_events(self) -> None:
        """Process all pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                continue

            # Route events based on state
            if self.state == AppState.TITLE:
                self.title_screen.handle_event(event)

            elif self.state == AppState.GAME:
                # Check for return to title
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    # If no overlays are open, return to title
                    if not self.game_manager.dialogue_box.visible and \
                       not self.game_manager.inventory_screen.visible:
                        self._return_to_title()
                        continue

                self.game_manager.handle_event(event)

    def _update(self) -> None:
        """Update game state."""
        if self.state == AppState.TITLE:
            self.title_screen.update()

        elif self.state == AppState.GAME:
            self.game_manager.update()

    def _render(self) -> None:
        """Render current state."""
        if self.state == AppState.TITLE:
            self.title_screen.render()

        elif self.state == AppState.GAME:
            self.game_manager.render()


def main():
    """Application entry point."""
    app = PixelRPGApp()
    app.run()


if __name__ == "__main__":
    main()

