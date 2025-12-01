"""
Title Screen - Pixel Art Style

Inspired by "Quest for the Golden Bunch" mockup.
Features:
- Animated background
- Large pixel-art title with drop shadow
- Menu navigation with keyboard/mouse
- Decorative banana border frame
"""

import pygame
from typing import Callable, Optional, List, Tuple
from enum import Enum

try:
    from pygame_mvp.config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
    from pygame_mvp.ui.pixel_theme import get_pixel_theme, BANANA_YELLOW, WOOD_DARK
except ImportError:
    from config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
    from ui.pixel_theme import get_pixel_theme, BANANA_YELLOW, WOOD_DARK


class MenuOption(Enum):
    NEW_GAME = "NEW GAME"
    LOAD_GAME = "LOAD GAME"
    OPTIONS = "OPTIONS"
    QUIT = "QUIT"


class TitleScreen:
    """
    Pixel art title screen with animated elements.

    Controls:
    - UP/DOWN or W/S: Navigate menu
    - ENTER/SPACE: Select option
    - Mouse: Click menu items
    """

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.theme = get_pixel_theme()

        # Fonts (pixel-style sizes)
        pygame.font.init()
        self.title_font = pygame.font.Font(None, 72)
        self.subtitle_font = pygame.font.Font(None, 48)
        self.menu_font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

        # Menu state
        self.menu_options = [
            MenuOption.NEW_GAME,
            MenuOption.LOAD_GAME,
            MenuOption.OPTIONS,
            MenuOption.QUIT,
        ]
        self.selected_index = 0
        self.hovered_index = -1

        # Callbacks
        self.on_new_game: Optional[Callable] = None
        self.on_load_game: Optional[Callable] = None
        self.on_options: Optional[Callable] = None
        self.on_quit: Optional[Callable] = None

        # Animation state
        self.animation_frame = 0
        self.title_offset_y = 0

        # Pre-render static elements
        self._create_background()
        self._create_border_frame()
        self._create_title_text()

    def _create_background(self) -> None:
        """Create the background gradient/scene."""
        self.background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

        # Sky gradient (top to middle)
        for y in range(SCREEN_HEIGHT // 2):
            progress = y / (SCREEN_HEIGHT // 2)
            r = int(100 + progress * 50)
            g = int(180 + progress * 30)
            b = int(230 - progress * 30)
            pygame.draw.line(self.background, (r, g, b), (0, y), (SCREEN_WIDTH, y))

        # Ground gradient (middle to bottom)
        for y in range(SCREEN_HEIGHT // 2, SCREEN_HEIGHT):
            progress = (y - SCREEN_HEIGHT // 2) / (SCREEN_HEIGHT // 2)
            r = int(60 + progress * 20)
            g = int(140 - progress * 40)
            b = int(60 - progress * 20)
            pygame.draw.line(self.background, (r, g, b), (0, y), (SCREEN_WIDTH, y))

        # Add some "clouds" (simple ellipses)
        cloud_color = (240, 245, 255, 180)
        cloud_surf = pygame.Surface((200, 60), pygame.SRCALPHA)
        pygame.draw.ellipse(cloud_surf, cloud_color, (0, 10, 80, 40))
        pygame.draw.ellipse(cloud_surf, cloud_color, (40, 0, 100, 50))
        pygame.draw.ellipse(cloud_surf, cloud_color, (100, 15, 90, 35))

        self.background.blit(cloud_surf, (150, 50))
        self.background.blit(cloud_surf, (600, 80))
        self.background.blit(cloud_surf, (900, 40))

        # Add simple pixel-style "ruins" silhouettes
        self._draw_ruins()

        # Add palm tree silhouettes
        self._draw_palm_trees()

    def _draw_ruins(self) -> None:
        """Draw simple ruin silhouettes on background."""
        ruin_color = (80, 90, 70)

        # Left ruin (arch)
        points = [
            (50, SCREEN_HEIGHT - 100),
            (50, SCREEN_HEIGHT - 250),
            (80, SCREEN_HEIGHT - 280),
            (130, SCREEN_HEIGHT - 280),
            (160, SCREEN_HEIGHT - 250),
            (160, SCREEN_HEIGHT - 100),
            (130, SCREEN_HEIGHT - 100),
            (130, SCREEN_HEIGHT - 200),
            (80, SCREEN_HEIGHT - 200),
            (80, SCREEN_HEIGHT - 100),
        ]
        pygame.draw.polygon(self.background, ruin_color, points)

        # Right ruin (pillar)
        pygame.draw.rect(self.background, ruin_color,
                        (SCREEN_WIDTH - 180, SCREEN_HEIGHT - 220, 40, 120))
        pygame.draw.rect(self.background, ruin_color,
                        (SCREEN_WIDTH - 120, SCREEN_HEIGHT - 180, 50, 80))

    def _draw_palm_trees(self) -> None:
        """Draw stylized palm tree silhouettes."""
        trunk_color = (60, 50, 40)
        leaf_color = (40, 100, 50)

        # Palm tree 1 (left side)
        pygame.draw.rect(self.background, trunk_color,
                        (250, SCREEN_HEIGHT - 200, 20, 100))
        # Leaves (simple triangular fronds)
        for angle_offset in [-40, -20, 0, 20, 40]:
            leaf_points = [
                (260, SCREEN_HEIGHT - 200),
                (260 + angle_offset - 30, SCREEN_HEIGHT - 280),
                (260 + angle_offset + 30, SCREEN_HEIGHT - 260),
            ]
            pygame.draw.polygon(self.background, leaf_color, leaf_points)

        # Palm tree 2 (right side)
        pygame.draw.rect(self.background, trunk_color,
                        (SCREEN_WIDTH - 300, SCREEN_HEIGHT - 250, 25, 150))
        for angle_offset in [-50, -25, 0, 25, 50]:
            leaf_points = [
                (SCREEN_WIDTH - 287, SCREEN_HEIGHT - 250),
                (SCREEN_WIDTH - 287 + angle_offset - 35, SCREEN_HEIGHT - 340),
                (SCREEN_WIDTH - 287 + angle_offset + 35, SCREEN_HEIGHT - 315),
            ]
            pygame.draw.polygon(self.background, leaf_color, leaf_points)

    def _create_border_frame(self) -> None:
        """Create decorative banana border frame."""
        self.border_frame = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

        border_width = 40
        frame_color = WOOD_DARK

        # Draw frame edges
        pygame.draw.rect(self.border_frame, frame_color, (0, 0, SCREEN_WIDTH, border_width))
        pygame.draw.rect(self.border_frame, frame_color, (0, SCREEN_HEIGHT - border_width, SCREEN_WIDTH, border_width))
        pygame.draw.rect(self.border_frame, frame_color, (0, 0, border_width, SCREEN_HEIGHT))
        pygame.draw.rect(self.border_frame, frame_color, (SCREEN_WIDTH - border_width, 0, border_width, SCREEN_HEIGHT))

        # Draw vine/leaf pattern along border
        vine_color = (50, 100, 50)
        for i in range(0, SCREEN_WIDTH, 60):
            # Top border decorations
            pygame.draw.ellipse(self.border_frame, vine_color, (i + 10, 5, 40, 25))
            pygame.draw.ellipse(self.border_frame, vine_color, (i + 20, 15, 30, 20))
            # Bottom border decorations
            pygame.draw.ellipse(self.border_frame, vine_color, (i + 10, SCREEN_HEIGHT - 30, 40, 25))

        # Draw banana icons along border
        banana_color = BANANA_YELLOW
        banana_stem = (100, 80, 40)
        for i in range(80, SCREEN_WIDTH - 80, 120):
            # Top bananas
            self._draw_banana(self.border_frame, i, 12, 25)
            # Bottom bananas
            self._draw_banana(self.border_frame, i + 40, SCREEN_HEIGHT - 28, 25)

        # Side bananas
        for j in range(80, SCREEN_HEIGHT - 80, 100):
            self._draw_banana(self.border_frame, 12, j, 22)
            self._draw_banana(self.border_frame, SCREEN_WIDTH - 32, j + 30, 22)

    def _draw_banana(self, surface: pygame.Surface, x: int, y: int, size: int) -> None:
        """Draw a simple banana icon."""
        banana_color = BANANA_YELLOW
        stem_color = (100, 80, 40)

        # Banana body (curved rectangle approximation)
        points = [
            (x, y + size // 3),
            (x + size // 4, y),
            (x + size * 3 // 4, y),
            (x + size, y + size // 3),
            (x + size * 3 // 4, y + size * 2 // 3),
            (x + size // 4, y + size * 2 // 3),
        ]
        pygame.draw.polygon(surface, banana_color, points)

        # Stem
        pygame.draw.rect(surface, stem_color, (x + size // 2 - 2, y - 4, 6, 8))

    def _create_title_text(self) -> None:
        """Create the title text surfaces."""
        # Main title "QUEST FOR THE"
        self.title_line1 = self.subtitle_font.render("QUEST FOR THE", True, self.theme.title_text)
        self.title_line1_shadow = self.subtitle_font.render("QUEST FOR THE", True, self.theme.title_shadow)

        # Big title "GOLDEN BUNCH"
        self.title_line2 = self.title_font.render("GOLDEN BUNCH", True, self.theme.title_text)
        self.title_line2_shadow = self.title_font.render("GOLDEN BUNCH", True, self.theme.title_shadow)

        # Calculate positions
        self.title1_x = (SCREEN_WIDTH - self.title_line1.get_width()) // 2
        self.title2_x = (SCREEN_WIDTH - self.title_line2.get_width()) // 2
        self.title1_y = 100
        self.title2_y = 150

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle input events."""
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected_index = (self.selected_index - 1) % len(self.menu_options)
                return True
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected_index = (self.selected_index + 1) % len(self.menu_options)
                return True
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._select_current_option()
                return True

        elif event.type == pygame.MOUSEMOTION:
            self._update_hover(event.pos)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.hovered_index >= 0:
                    self.selected_index = self.hovered_index
                    self._select_current_option()
                    return True

        return False

    def _update_hover(self, mouse_pos: Tuple[int, int]) -> None:
        """Update which menu item is hovered."""
        menu_y_start = SCREEN_HEIGHT // 2 + 20
        menu_spacing = 50

        self.hovered_index = -1
        for i, option in enumerate(self.menu_options):
            item_y = menu_y_start + i * menu_spacing
            item_rect = pygame.Rect(
                SCREEN_WIDTH // 2 - 100,
                item_y - 15,
                200,
                40
            )
            if item_rect.collidepoint(mouse_pos):
                self.hovered_index = i
                break

    def _select_current_option(self) -> None:
        """Execute the callback for the selected option."""
        option = self.menu_options[self.selected_index]

        if option == MenuOption.NEW_GAME and self.on_new_game:
            self.on_new_game()
        elif option == MenuOption.LOAD_GAME and self.on_load_game:
            self.on_load_game()
        elif option == MenuOption.OPTIONS and self.on_options:
            self.on_options()
        elif option == MenuOption.QUIT and self.on_quit:
            self.on_quit()

    def update(self) -> None:
        """Update animation state."""
        self.animation_frame += 1

        # Subtle title bounce
        self.title_offset_y = int(2 * ((self.animation_frame % 60) / 60 - 0.5) ** 2 * 4)

    def render(self) -> None:
        """Render the title screen."""
        # Draw background
        self.screen.blit(self.background, (0, 0))

        # Draw border frame
        self.screen.blit(self.border_frame, (0, 0))

        # Draw title with shadow
        shadow_offset = 3
        self.screen.blit(self.title_line1_shadow,
                        (self.title1_x + shadow_offset, self.title1_y + self.title_offset_y + shadow_offset))
        self.screen.blit(self.title_line1,
                        (self.title1_x, self.title1_y + self.title_offset_y))

        self.screen.blit(self.title_line2_shadow,
                        (self.title2_x + shadow_offset, self.title2_y + self.title_offset_y + shadow_offset))
        self.screen.blit(self.title_line2,
                        (self.title2_x, self.title2_y + self.title_offset_y))

        # Draw menu
        self._render_menu()

        # Draw "Nano Banana Games" credit
        credit_text = self.small_font.render("Powered by AI-DnD", True, self.theme.text_light)
        self.screen.blit(credit_text,
                        (SCREEN_WIDTH - credit_text.get_width() - 60, SCREEN_HEIGHT - 60))

    def _render_menu(self) -> None:
        """Render the menu options."""
        menu_y_start = SCREEN_HEIGHT // 2 + 20
        menu_spacing = 50

        for i, option in enumerate(self.menu_options):
            is_selected = (i == self.selected_index)
            is_hovered = (i == self.hovered_index)

            # Choose color based on state
            if is_selected or is_hovered:
                color = self.theme.menu_text_selected
                prefix = "> "
                suffix = " <"
            else:
                color = self.theme.menu_text
                prefix = ""
                suffix = ""

            text = f"{prefix}{option.value}{suffix}"
            text_surface = self.menu_font.render(text, True, color)

            x = (SCREEN_WIDTH - text_surface.get_width()) // 2
            y = menu_y_start + i * menu_spacing

            # Draw shadow
            shadow_surface = self.menu_font.render(text, True, self.theme.title_shadow)
            self.screen.blit(shadow_surface, (x + 2, y + 2))

            # Draw text
            self.screen.blit(text_surface, (x, y))

