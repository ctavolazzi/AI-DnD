"""
Main Game Loop

Handles the core game loop, event processing, and state updates.
"""

import pygame
import sys
from typing import Optional, Callable, List

# Use absolute imports for standalone execution
try:
    from pygame_mvp.config import FPS, GAME_TITLE, SCREEN_WIDTH, SCREEN_HEIGHT, CURRENT_THEME
    from pygame_mvp.game.game_state import GameState, GamePhase
except ImportError:
    from config import FPS, GAME_TITLE, SCREEN_WIDTH, SCREEN_HEIGHT, CURRENT_THEME
    from game.game_state import GameState, GamePhase


class GameLoop:
    """
    Main game loop manager.

    Handles initialization, event processing, updates, and rendering.
    """

    def __init__(self, state: GameState):
        self.state = state
        self.running = False
        self.clock: Optional[pygame.time.Clock] = None
        self.screen: Optional[pygame.Surface] = None

        # Callbacks for different events
        self.on_quit: Optional[Callable] = None
        self.on_update: Optional[Callable[[float], None]] = None
        self.on_render: Optional[Callable[[pygame.Surface], None]] = None
        self.on_key_down: Optional[Callable[[pygame.event.Event], None]] = None
        self.on_key_up: Optional[Callable[[pygame.event.Event], None]] = None
        self.on_mouse_down: Optional[Callable[[pygame.event.Event], None]] = None
        self.on_mouse_up: Optional[Callable[[pygame.event.Event], None]] = None
        self.on_mouse_motion: Optional[Callable[[pygame.event.Event], None]] = None

        # Action callbacks (for UI buttons)
        self.action_callbacks: dict[str, Callable] = {}

    def initialize(self) -> bool:
        """Initialize pygame and create window."""
        try:
            pygame.init()
            pygame.display.set_caption(GAME_TITLE)

            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.clock = pygame.time.Clock()

            return True
        except pygame.error as e:
            print(f"Failed to initialize pygame: {e}")
            return False

    def register_action(self, action_name: str, callback: Callable) -> None:
        """Register an action callback."""
        self.action_callbacks[action_name] = callback

    def trigger_action(self, action_name: str, *args, **kwargs) -> None:
        """Trigger a registered action."""
        if action_name in self.action_callbacks:
            self.action_callbacks[action_name](*args, **kwargs)

    def process_events(self) -> None:
        """Process all pending events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                if self.on_quit:
                    self.on_quit()

            elif event.type == pygame.KEYDOWN:
                self._handle_key_down(event)
                if self.on_key_down:
                    self.on_key_down(event)

            elif event.type == pygame.KEYUP:
                if self.on_key_up:
                    self.on_key_up(event)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.on_mouse_down:
                    self.on_mouse_down(event)

            elif event.type == pygame.MOUSEBUTTONUP:
                if self.on_mouse_up:
                    self.on_mouse_up(event)

            elif event.type == pygame.MOUSEMOTION:
                if self.on_mouse_motion:
                    self.on_mouse_motion(event)

    def _handle_key_down(self, event: pygame.event.Event) -> None:
        """Handle built-in key commands."""
        # Escape to quit or go back
        if event.key == pygame.K_ESCAPE:
            if self.state.phase == GamePhase.MENU:
                self.running = False
            else:
                # Could go back to menu or show pause screen
                pass

        # Space to advance turn
        elif event.key == pygame.K_SPACE:
            self.trigger_action("next_turn")

        # Number keys for quick actions
        elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4):
            action_index = event.key - pygame.K_1
            self.trigger_action(f"action_{action_index}")

    def update(self, dt: float) -> None:
        """Update game state."""
        if self.on_update:
            self.on_update(dt)

        # Check for game over conditions
        if self.state.is_game_over():
            self.state.phase = GamePhase.GAME_OVER
            self.state.log("*** GAME OVER ***")
        elif self.state.is_victory():
            self.state.log("*** VICTORY! ***")
            self.state.enemies.clear()

    def render(self) -> None:
        """Render the current frame."""
        if not self.screen:
            return

        # Clear screen with background color
        self.screen.fill(CURRENT_THEME["background"])

        # Call custom render callback
        if self.on_render:
            self.on_render(self.screen)

        # Update display
        pygame.display.flip()

    def run(self) -> None:
        """Run the main game loop."""
        if not self.initialize():
            return

        self.running = True

        while self.running:
            # Calculate delta time
            dt = self.clock.tick(FPS) / 1000.0

            # Process events
            self.process_events()

            # Update game state
            self.update(dt)

            # Render frame
            self.render()

        # Cleanup
        pygame.quit()

    def stop(self) -> None:
        """Stop the game loop."""
        self.running = False

