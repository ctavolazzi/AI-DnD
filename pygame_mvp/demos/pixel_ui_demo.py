#!/usr/bin/env python3
"""
Pixel UI Demo - Showcasing Nano Banana Games-inspired UI

Run this to see all the new pixel art UI components in action:
- Title Screen (press any key to continue)
- Game Screen with HUD and Dialogue
- Inventory Screen (press I)

Controls:
- Arrow keys / WASD: Navigate menus
- Enter / Space: Select
- I: Toggle inventory
- ESC: Back / Quit
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import pygame
from enum import Enum

from pygame_mvp.config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, GAME_TITLE
from pygame_mvp.ui.pixel_theme import get_pixel_theme, PARCHMENT_LIGHT
from pygame_mvp.ui.title_screen import TitleScreen
from pygame_mvp.ui.pixel_inventory import PixelInventoryScreen
from pygame_mvp.ui.pixel_dialogue import PixelDialogueBox, DialogueSequence
from pygame_mvp.ui.pixel_hud import PixelGameHUD
from pygame_mvp.game.systems import Player, CharacterClass, Item, ItemType, Stats


class DemoState(Enum):
    TITLE = "title"
    GAME = "game"


class PixelUIDemo:
    """Demo application for pixel art UI components."""

    def __init__(self):
        pygame.init()
        pygame.display.set_caption(f"{GAME_TITLE} - Pixel UI Demo")

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = DemoState.TITLE

        # Create demo player
        self.player = Player("Hero", CharacterClass.FIGHTER)
        self.player.current_hp = 85
        self.player.inventory = [
            Item("Health Potion", ItemType.POTION, value=50,
                 description="Restores 50 HP. Tastes faintly of... synthetic banana."),
            Item("Mana Potion", ItemType.POTION, value=50,
                 description="Restores 30 MP. Glows with arcane energy."),
            Item("Iron Sword", ItemType.WEAPON, value=100, damage_min=3, damage_max=8,
                 stats_bonus=Stats.bonus(strength=2),
                 description="A sturdy blade forged in the village smithy."),
            Item("Leather Tunic", ItemType.ARMOR, value=75,
                 stats_bonus=Stats.bonus(constitution=1),
                 description="Light armor that allows freedom of movement."),
        ]

        # Initialize UI components
        self._setup_title_screen()
        self._setup_game_ui()

        # Demo state
        self.player_grid_pos = [10, 7]
        self.demo_map_tiles = self._create_demo_map()

    def _setup_title_screen(self) -> None:
        """Set up the title screen."""
        self.title_screen = TitleScreen(self.screen)
        self.title_screen.on_new_game = self._start_game
        self.title_screen.on_load_game = self._start_game  # Same for demo
        self.title_screen.on_options = lambda: print("Options not implemented in demo")
        self.title_screen.on_quit = self._quit

    def _setup_game_ui(self) -> None:
        """Set up game UI components."""
        # HUD
        self.hud = PixelGameHUD(self.screen)
        self.hud.set_hp(self.player.current_hp, self.player.max_hp)
        self.hud.set_mp(50, 100)  # Demo mana

        # Inventory
        self.inventory = PixelInventoryScreen(self.screen)
        self.inventory.set_player(self.player)
        self.inventory.on_item_use = self._on_item_use

        # Dialogue
        self.dialogue = PixelDialogueBox(self.screen)
        self.dialogue_sequence = DialogueSequence(self.dialogue)

        # Pre-load demo dialogue
        self._setup_demo_dialogue()

    def _setup_demo_dialogue(self) -> None:
        """Set up demo dialogue sequence."""
        self.dialogue_sequence.add_line(
            "WIZARD",
            '"Watch out! This dungeon floor is slippery with... peels?"',
            portrait_color=(100, 100, 180)
        )
        self.dialogue_sequence.add_line(
            "WIZARD",
            '"The ancient texts speak of a Golden Bunch hidden in these ruins."',
            portrait_color=(100, 100, 180)
        )
        self.dialogue_sequence.add_line(
            "WIZARD",
            '"Be careful, adventurer. The banana guardians do not take kindly to thieves."',
            portrait_color=(100, 100, 180)
        )

    def _create_demo_map(self) -> list:
        """Create a simple demo map for the minimap."""
        # 0 = floor, 1 = wall
        tiles = []
        for y in range(15):
            row = []
            for x in range(20):
                # Border walls
                if x == 0 or x == 19 or y == 0 or y == 14:
                    row.append(1)
                # Some interior walls
                elif (x in [5, 14] and y < 10) or (y == 7 and 7 < x < 12):
                    row.append(1)
                else:
                    row.append(0)
            tiles.append(row)
        return tiles

    def _start_game(self) -> None:
        """Transition to game state."""
        self.state = DemoState.GAME

        # Start dialogue after brief delay
        self.dialogue_started = False
        self.dialogue_delay = 60  # frames

    def _quit(self) -> None:
        """Quit the demo."""
        self.running = False

    def _on_item_use(self, item: Item) -> None:
        """Handle item use."""
        if item.item_type == ItemType.POTION:
            if "Health" in item.name:
                self.player.current_hp = min(self.player.max_hp, self.player.current_hp + 50)
                self.hud.set_hp(self.player.current_hp, self.player.max_hp)
                print(f"Used {item.name}! HP restored to {self.player.current_hp}")

    def run(self) -> None:
        """Main demo loop."""
        while self.running:
            self._handle_events()
            self._update()
            self._render()

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()

    def _handle_events(self) -> None:
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                continue

            if self.state == DemoState.TITLE:
                self.title_screen.handle_event(event)

            elif self.state == DemoState.GAME:
                # Check dialogue first
                if self.dialogue.visible:
                    if self.dialogue.handle_event(event):
                        continue

                # Check inventory
                if self.inventory.visible:
                    if self.inventory.handle_event(event):
                        continue

                # Game controls
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.inventory.visible:
                            self.inventory.hide()
                        else:
                            self.state = DemoState.TITLE

                    elif event.key == pygame.K_i:
                        self.inventory.toggle()

                    # Player movement (demo)
                    elif event.key in (pygame.K_UP, pygame.K_w):
                        self.player_grid_pos[1] = max(1, self.player_grid_pos[1] - 1)
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        self.player_grid_pos[1] = min(13, self.player_grid_pos[1] + 1)
                    elif event.key in (pygame.K_LEFT, pygame.K_a):
                        self.player_grid_pos[0] = max(1, self.player_grid_pos[0] - 1)
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        self.player_grid_pos[0] = min(18, self.player_grid_pos[0] + 1)

                    # Trigger dialogue with D
                    elif event.key == pygame.K_t:
                        self.dialogue_sequence.start()

    def _update(self) -> None:
        """Update game state."""
        if self.state == DemoState.TITLE:
            self.title_screen.update()

        elif self.state == DemoState.GAME:
            self.hud.update()
            self.dialogue.update()

            # Update minimap
            self.hud.set_player_pos(*self.player_grid_pos)
            self.hud.set_map_tiles(self.demo_map_tiles, 20, 15)

            # Auto-start dialogue once
            if not self.dialogue_started:
                self.dialogue_delay -= 1
                if self.dialogue_delay <= 0:
                    self.dialogue_sequence.start()
                    self.dialogue_started = True

    def _render(self) -> None:
        """Render current state."""
        if self.state == DemoState.TITLE:
            self.title_screen.render()

        elif self.state == DemoState.GAME:
            self._render_game()

    def _render_game(self) -> None:
        """Render the game screen."""
        # Background (dark dungeon)
        self.screen.fill((20, 18, 15))

        # Draw simple dungeon floor
        self._render_dungeon_floor()

        # Draw player character
        self._render_player()

        # HUD (HP/MP bars, minimap)
        self.hud.render()

        # Dialogue box (if active)
        self.dialogue.render()

        # Inventory overlay (if active)
        self.inventory.render()

        # Controls hint
        self._render_controls_hint()

    def _render_dungeon_floor(self) -> None:
        """Render a simple dungeon floor."""
        tile_size = 40
        offset_x = (SCREEN_WIDTH - 20 * tile_size) // 2
        offset_y = 60

        # Draw visible area
        view_range = 8
        px, py = self.player_grid_pos

        for dy in range(-view_range, view_range + 1):
            for dx in range(-view_range, view_range + 1):
                tx = px + dx
                ty = py + dy

                if 0 <= tx < 20 and 0 <= ty < 15:
                    screen_x = offset_x + tx * tile_size
                    screen_y = offset_y + ty * tile_size

                    # Check if on screen
                    if screen_x < -tile_size or screen_x > SCREEN_WIDTH + tile_size:
                        continue
                    if screen_y < -tile_size or screen_y > SCREEN_HEIGHT + tile_size:
                        continue

                    tile = self.demo_map_tiles[ty][tx]

                    if tile == 1:
                        # Wall
                        color = (60, 55, 50)
                        pygame.draw.rect(self.screen, color,
                                       (screen_x, screen_y, tile_size - 1, tile_size - 1))
                        # Stone texture
                        pygame.draw.rect(self.screen, (50, 45, 40),
                                       (screen_x, screen_y, tile_size - 1, tile_size - 1), 2)
                    else:
                        # Floor
                        color = (180, 160, 100) if (tx + ty) % 2 == 0 else (170, 150, 90)
                        pygame.draw.rect(self.screen, color,
                                       (screen_x, screen_y, tile_size - 1, tile_size - 1))

    def _render_player(self) -> None:
        """Render the player character."""
        tile_size = 40
        offset_x = (SCREEN_WIDTH - 20 * tile_size) // 2
        offset_y = 60

        px, py = self.player_grid_pos
        screen_x = offset_x + px * tile_size + tile_size // 2
        screen_y = offset_y + py * tile_size + tile_size // 2

        # Simple character sprite
        # Body
        pygame.draw.rect(self.screen, (70, 140, 170),
                        (screen_x - 12, screen_y - 8, 24, 28), border_radius=4)

        # Head
        pygame.draw.circle(self.screen, (230, 190, 150), (screen_x, screen_y - 18), 12)

        # Hair
        pygame.draw.ellipse(self.screen, (100, 70, 40),
                          (screen_x - 12, screen_y - 32, 24, 16))

        # Sword
        pygame.draw.rect(self.screen, (180, 180, 200),
                        (screen_x + 12, screen_y - 15, 6, 25))
        pygame.draw.rect(self.screen, (139, 90, 43),
                        (screen_x + 10, screen_y + 8, 10, 5))

    def _render_controls_hint(self) -> None:
        """Render controls hint at bottom."""
        if self.inventory.visible or self.dialogue.visible:
            return

        font = pygame.font.Font(None, 20)
        hints = "[WASD/Arrows] Move  [I] Inventory  [T] Talk  [ESC] Menu"
        text = font.render(hints, True, (150, 140, 120))

        x = (SCREEN_WIDTH - text.get_width()) // 2
        y = SCREEN_HEIGHT - 30

        self.screen.blit(text, (x, y))


def main():
    """Run the pixel UI demo."""
    print("""
╔══════════════════════════════════════════════════════════════╗
║            Pixel Art UI Demo - Nano Banana Style             ║
╠══════════════════════════════════════════════════════════════╣
║  Controls:                                                   ║
║    [WASD/Arrows] - Navigate / Move                           ║
║    [Enter/Space] - Select / Advance dialogue                 ║
║    [I]           - Toggle Inventory                          ║
║    [T]           - Trigger Dialogue                          ║
║    [ESC]         - Back / Quit                               ║
╚══════════════════════════════════════════════════════════════╝
    """)

    demo = PixelUIDemo()
    demo.run()


if __name__ == "__main__":
    main()

