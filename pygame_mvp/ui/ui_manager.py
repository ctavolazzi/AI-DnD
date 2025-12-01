"""
Lightweight UI manager for overlay screens (inventory, character sheet).

This keeps the GameManager loop focused on logic while UI rendering lives here.
"""

from typing import List, Optional

import pygame

# Prefer absolute imports but fall back to relative for script execution
try:  # pragma: no cover - exercised in package mode
    from pygame_mvp.config import SCREEN_WIDTH, SCREEN_HEIGHT, PADDING
    from pygame_mvp.ui.theme import get_theme
except ImportError:  # pragma: no cover
    from config import SCREEN_WIDTH, SCREEN_HEIGHT, PADDING
    from ui.theme import get_theme


class UIManager:
    """Manages toggleable overlay panels for the GameManager loop."""

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.theme = get_theme()
        pygame.font.init()
        self.header_font = pygame.font.Font(None, 26)
        self.body_font = pygame.font.Font(None, 20)
        self.small_font = pygame.font.Font(None, 18)

        # Panels toggle flags
        self.show_inventory = False
        self.show_character = False

        # Layout defaults (right-side overlay)
        self.panel_width = 360
        self.panel_margin = PADDING
        self.anchor_x = SCREEN_WIDTH - self.panel_width - self.panel_margin
        self.anchor_y = self.panel_margin

    # ------------------------------------------------------------------ #
    # Event handling
    # ------------------------------------------------------------------ #
    def handle_key_event(self, event: pygame.event.Event) -> bool:
        """
        Toggle overlay visibility on keypress.

        Returns True if the event was consumed.
        """
        if event.type != pygame.KEYDOWN:
            return False

        if event.key == pygame.K_i:
            self.toggle_inventory()
            return True
        if event.key == pygame.K_c:
            self.toggle_character()
            return True
        return False

    def toggle_inventory(self) -> None:
        """Toggle inventory overlay."""
        self.show_inventory = not self.show_inventory
        if self.show_inventory:
            self.show_character = False  # show one overlay at a time

    def toggle_character(self) -> None:
        """Toggle character sheet overlay."""
        self.show_character = not self.show_character
        if self.show_character:
            self.show_inventory = False

    # ------------------------------------------------------------------ #
    # Rendering
    # ------------------------------------------------------------------ #
    def render(
        self,
        player,
        quests: Optional[object] = None,
        log_lines: Optional[List[str]] = None,
    ) -> None:
        """Render any active overlays on top of the main scene."""
        if self.show_inventory:
            self._render_inventory(player)
        if self.show_character:
            self._render_character(player, quests, log_lines)

    def _render_inventory(self, player) -> None:
        """Render a simple inventory list."""
        panel_height = SCREEN_HEIGHT - self.panel_margin * 2
        rect = pygame.Rect(self.anchor_x, self.anchor_y, self.panel_width, panel_height)
        self._draw_panel(rect, "Inventory")

        y = rect.top + 40
        lines = []

        # Equipment
        lines.append("Equipped:")
        for slot, item in player.equipment.items():
            label = item.name if item else "Empty"
            lines.append(f"  {slot.title()}: {label}")

        lines.append("")  # spacer
        lines.append("Bag:")

        if not player.inventory:
            lines.append("  (Empty)")
        else:
            for item in player.inventory:
                stats = []
                if item.damage_min or item.damage_max:
                    stats.append(f"{item.damage_min}-{item.damage_max} dmg")
                if item.stats_bonus and any(
                    [
                        item.stats_bonus.strength,
                        item.stats_bonus.dexterity,
                        item.stats_bonus.intelligence,
                        item.stats_bonus.constitution,
                    ]
                ):
                    stats.append(
                        f"+{item.stats_bonus.strength} STR "
                        f"+{item.stats_bonus.dexterity} DEX "
                        f"+{item.stats_bonus.intelligence} INT "
                        f"+{item.stats_bonus.constitution} CON"
                    )
                meta = f" ({', '.join(stats)})" if stats else ""
                lines.append(f"  • {item.name} [{item.item_type.value}]{meta}")

        self._blit_lines(lines, start_y=y)

    def _render_character(self, player, quests, log_lines: Optional[List[str]]) -> None:
        """Render character sheet with stats and quest snippets."""
        panel_height = SCREEN_HEIGHT - self.panel_margin * 2
        rect = pygame.Rect(self.anchor_x, self.anchor_y, self.panel_width, panel_height)
        self._draw_panel(rect, "Character")

        y = rect.top + 40
        lines = [
            f"Name: {player.name}",
            f"Class: {getattr(player.char_class, 'value', player.char_class)}",
            f"Level: {getattr(player, 'level', 1)}",
            f"XP: {getattr(player, 'xp', 0)}",
            f"HP: {player.current_hp}/{player.max_hp}",
            "",
            "Stats:",
        ]

        total_stats = getattr(player, "total_stats", None)
        if total_stats:
            lines.extend(
                [
                    f"  STR {total_stats.strength}",
                    f"  DEX {total_stats.dexterity}",
                    f"  INT {total_stats.intelligence}",
                    f"  CON {total_stats.constitution}",
                ]
            )

        # Quest summary if available
        active_quests = getattr(quests, "get_active_quests", lambda: [])()
        if active_quests:
            lines.append("")
            lines.append("Quests:")
            for quest in active_quests[:3]:
                lines.append(f"  • {quest.name} ({int(quest.progress_percent)}%)")

        # Recent log lines (lightweight status recap)
        if log_lines:
            lines.append("")
            lines.append("Recent Log:")
            for entry in log_lines[-5:]:
                lines.append(f"  {entry}")

        self._blit_lines(lines, start_y=y)

    def _draw_panel(self, rect: pygame.Rect, title: str) -> None:
        """Draw a simple framed panel."""
        pygame.draw.rect(self.screen, self.theme.panel_bg, rect, border_radius=8)
        pygame.draw.rect(self.screen, self.theme.panel_border, rect, 2, border_radius=8)

        # Header
        header = self.header_font.render(title, True, self.theme.text_highlight)
        self.screen.blit(header, (rect.left + PADDING, rect.top + PADDING))

    def _blit_lines(self, lines: List[str], start_y: int) -> None:
        """Render text lines with vertical spacing."""
        y = start_y
        for line in lines:
            text = self.body_font.render(line, True, self.theme.text_primary)
            self.screen.blit(text, (self.anchor_x + PADDING, y))
            y += text.get_height() + 4

