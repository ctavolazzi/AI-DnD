"""
Game Screens

Assembles UI components into complete game screens.
"""

import pygame
from typing import Optional, Callable, List, Dict

# Use absolute imports for standalone execution
try:
    from pygame_mvp.config import (
        SCREEN_WIDTH,
        SCREEN_HEIGHT,
        MARGIN,
        PADDING,
        SCENE_VIEWER_X,
        SCENE_VIEWER_Y,
        SCENE_VIEWER_WIDTH,
        SCENE_VIEWER_HEIGHT,
        SCENE_IMAGE_WIDTH,
        SCENE_IMAGE_HEIGHT,
        ADVENTURE_LOG_X,
        ADVENTURE_LOG_Y,
        ADVENTURE_LOG_WIDTH,
        ADVENTURE_LOG_HEIGHT,
        MAP_PANEL_X,
        MAP_PANEL_Y,
        MAP_PANEL_WIDTH,
        MAP_PANEL_HEIGHT,
        MAP_THUMB_WIDTH,
        MAP_THUMB_HEIGHT,
        NAV_PANEL_X,
        NAV_PANEL_Y,
        NAV_PANEL_WIDTH,
        NAV_PANEL_HEIGHT,
        CHARACTER_PANEL_X,
        CHARACTER_PANEL_Y,
        CHARACTER_PANEL_WIDTH,
        CHARACTER_PANEL_HEIGHT,
        INVENTORY_PANEL_X,
        INVENTORY_PANEL_Y,
        INVENTORY_PANEL_WIDTH,
        INVENTORY_PANEL_HEIGHT,
        QUEST_PANEL_X,
        QUEST_PANEL_Y,
        QUEST_PANEL_WIDTH,
        QUEST_PANEL_HEIGHT,
        BOTTOM_BAR_Y,
        ACTION_BUTTON_WIDTH,
        ACTION_BUTTON_HEIGHT,
        ACTION_BUTTON_SPACING,
        PORTRAIT_WIDTH,
        PORTRAIT_HEIGHT,
        STAT_BAR_WIDTH,
        STAT_BAR_HEIGHT,
        INVENTORY_SLOTS_PER_ROW,
        INVENTORY_SLOT_SIZE,
        INVENTORY_SLOT_SPACING,
        CENTER_X,
        CENTER_WIDTH
    )
    from pygame_mvp.game.game_state import GameState, CharacterState
    from pygame_mvp.services.image_provider import ImageProvider, MockImageProvider
    from pygame_mvp.ui.components import (
        Panel,
        Button,
        TextBox,
        ImageFrame,
        StatBar,
        InventoryGrid
    )
    from pygame_mvp.ui.theme import get_theme
except ImportError:
    from config import (
        SCREEN_WIDTH,
        SCREEN_HEIGHT,
        MARGIN,
        PADDING,
        SCENE_VIEWER_X,
        SCENE_VIEWER_Y,
        SCENE_VIEWER_WIDTH,
        SCENE_VIEWER_HEIGHT,
        SCENE_IMAGE_WIDTH,
        SCENE_IMAGE_HEIGHT,
        ADVENTURE_LOG_X,
        ADVENTURE_LOG_Y,
        ADVENTURE_LOG_WIDTH,
        ADVENTURE_LOG_HEIGHT,
        MAP_PANEL_X,
        MAP_PANEL_Y,
        MAP_PANEL_WIDTH,
        MAP_PANEL_HEIGHT,
        MAP_THUMB_WIDTH,
        MAP_THUMB_HEIGHT,
        NAV_PANEL_X,
        NAV_PANEL_Y,
        NAV_PANEL_WIDTH,
        NAV_PANEL_HEIGHT,
        CHARACTER_PANEL_X,
        CHARACTER_PANEL_Y,
        CHARACTER_PANEL_WIDTH,
        CHARACTER_PANEL_HEIGHT,
        INVENTORY_PANEL_X,
        INVENTORY_PANEL_Y,
        INVENTORY_PANEL_WIDTH,
        INVENTORY_PANEL_HEIGHT,
        QUEST_PANEL_X,
        QUEST_PANEL_Y,
        QUEST_PANEL_WIDTH,
        QUEST_PANEL_HEIGHT,
        BOTTOM_BAR_Y,
        ACTION_BUTTON_WIDTH,
        ACTION_BUTTON_HEIGHT,
        ACTION_BUTTON_SPACING,
        PORTRAIT_WIDTH,
        PORTRAIT_HEIGHT,
        STAT_BAR_WIDTH,
        STAT_BAR_HEIGHT,
        INVENTORY_SLOTS_PER_ROW,
        INVENTORY_SLOT_SIZE,
        INVENTORY_SLOT_SPACING,
        CENTER_X,
        CENTER_WIDTH
    )
    from game.game_state import GameState, CharacterState
    from services.image_provider import ImageProvider, MockImageProvider
    from ui.components import (
        Panel,
        Button,
        TextBox,
        ImageFrame,
        StatBar,
        InventoryGrid
    )
    from ui.theme import get_theme


class MainGameScreen:
    """
    Main game screen with all UI panels assembled.

    Layout:
    - Left sidebar: Map, Navigation
    - Center: Scene Viewer, Adventure Log
    - Right sidebar: Character Stats, Inventory, Quest
    - Bottom: Action Buttons
    """

    def __init__(
        self,
        game_state: GameState,
        image_provider: Optional[ImageProvider] = None
    ):
        self.state = game_state
        self.image_provider = image_provider or MockImageProvider()

        # Action callbacks
        self.on_next_turn: Optional[Callable] = None
        self.on_attack: Optional[Callable] = None
        self.on_cast_spell: Optional[Callable] = None
        self.on_use_item: Optional[Callable] = None

        # Build UI components
        self._build_panels()
        self._build_buttons()

    def _build_panels(self) -> None:
        """Create all UI panels."""
        # Scene Viewer (center top)
        self.scene_panel = Panel(
            SCENE_VIEWER_X, SCENE_VIEWER_Y,
            SCENE_VIEWER_WIDTH, SCENE_VIEWER_HEIGHT,
            title="Scene"
        )
        self.scene_image = ImageFrame(
            SCENE_VIEWER_X + PADDING,
            SCENE_VIEWER_Y + 28,
            SCENE_IMAGE_WIDTH,
            SCENE_IMAGE_HEIGHT
        )
        self.scene_panel.add_child(self.scene_image)

        # Adventure Log (center bottom)
        self.log_panel = Panel(
            ADVENTURE_LOG_X, ADVENTURE_LOG_Y,
            ADVENTURE_LOG_WIDTH, ADVENTURE_LOG_HEIGHT,
            title="Adventure Log"
        )
        self.log_text = TextBox(
            ADVENTURE_LOG_X + PADDING,
            ADVENTURE_LOG_Y + 28,
            ADVENTURE_LOG_WIDTH - PADDING * 2,
            ADVENTURE_LOG_HEIGHT - 36
        )
        self.log_panel.add_child(self.log_text)

        # Map Panel (left top)
        self.map_panel = Panel(
            MAP_PANEL_X, MAP_PANEL_Y,
            MAP_PANEL_WIDTH, MAP_PANEL_HEIGHT,
            title="Map"
        )
        self.map_image = ImageFrame(
            MAP_PANEL_X + PADDING,
            MAP_PANEL_Y + 28,
            MAP_THUMB_WIDTH,
            MAP_THUMB_HEIGHT - 10
        )
        self.map_panel.add_child(self.map_image)

        # Navigation Panel (left bottom)
        self.nav_panel = Panel(
            NAV_PANEL_X, NAV_PANEL_Y,
            NAV_PANEL_WIDTH, NAV_PANEL_HEIGHT,
            title="Navigation"
        )

        # Character Panel (right top)
        self.char_panel = Panel(
            CHARACTER_PANEL_X, CHARACTER_PANEL_Y,
            CHARACTER_PANEL_WIDTH, CHARACTER_PANEL_HEIGHT,
            title="Character"
        )

        # Character portrait
        self.char_portrait = ImageFrame(
            CHARACTER_PANEL_X + PADDING,
            CHARACTER_PANEL_Y + 32,
            PORTRAIT_WIDTH,
            PORTRAIT_HEIGHT
        )
        self.char_panel.add_child(self.char_portrait)

        # HP Bar
        self.hp_bar = StatBar(
            CHARACTER_PANEL_X + PORTRAIT_WIDTH + PADDING * 2,
            CHARACTER_PANEL_Y + 40,
            STAT_BAR_WIDTH,
            STAT_BAR_HEIGHT,
            bar_color="hp_bar",
            bg_color="hp_bar_bg",
            label="HP"
        )
        self.char_panel.add_child(self.hp_bar)

        # Mana Bar
        self.mana_bar = StatBar(
            CHARACTER_PANEL_X + PORTRAIT_WIDTH + PADDING * 2,
            CHARACTER_PANEL_Y + 62,
            STAT_BAR_WIDTH,
            STAT_BAR_HEIGHT,
            bar_color="mana_bar",
            bg_color="mana_bar_bg",
            label="MP"
        )
        self.char_panel.add_child(self.mana_bar)

        # Inventory Panel (right middle)
        self.inv_panel = Panel(
            INVENTORY_PANEL_X, INVENTORY_PANEL_Y,
            INVENTORY_PANEL_WIDTH, INVENTORY_PANEL_HEIGHT,
            title="Inventory"
        )

        # Inventory grid
        grid_x = INVENTORY_PANEL_X + PADDING
        grid_y = INVENTORY_PANEL_Y + 32
        self.inv_grid = InventoryGrid(
            grid_x, grid_y,
            slots_per_row=INVENTORY_SLOTS_PER_ROW,
            num_slots=15,
            slot_size=INVENTORY_SLOT_SIZE,
            spacing=INVENTORY_SLOT_SPACING
        )
        self.inv_panel.add_child(self.inv_grid)

        # Quest Panel (right bottom)
        self.quest_panel = Panel(
            QUEST_PANEL_X, QUEST_PANEL_Y,
            QUEST_PANEL_WIDTH, QUEST_PANEL_HEIGHT,
            title="Quest"
        )
        self.quest_text = TextBox(
            QUEST_PANEL_X + PADDING,
            QUEST_PANEL_Y + 28,
            QUEST_PANEL_WIDTH - PADDING * 2,
            QUEST_PANEL_HEIGHT - 36
        )
        self.quest_panel.add_child(self.quest_text)

        # Collect all panels
        self.panels = [
            self.scene_panel,
            self.log_panel,
            self.map_panel,
            self.nav_panel,
            self.char_panel,
            self.inv_panel,
            self.quest_panel
        ]

    def _build_buttons(self) -> None:
        """Create action buttons."""
        # Calculate button positions (centered in bottom bar)
        total_width = 4 * ACTION_BUTTON_WIDTH + 3 * ACTION_BUTTON_SPACING
        start_x = CENTER_X + (CENTER_WIDTH - total_width) // 2
        button_y = BOTTOM_BAR_Y + 8

        self.btn_next_turn = Button(
            start_x,
            button_y,
            ACTION_BUTTON_WIDTH,
            ACTION_BUTTON_HEIGHT,
            "Next Turn",
            callback=self._on_next_turn
        )

        self.btn_attack = Button(
            start_x + ACTION_BUTTON_WIDTH + ACTION_BUTTON_SPACING,
            button_y,
            ACTION_BUTTON_WIDTH,
            ACTION_BUTTON_HEIGHT,
            "Attack",
            callback=self._on_attack
        )

        self.btn_cast = Button(
            start_x + 2 * (ACTION_BUTTON_WIDTH + ACTION_BUTTON_SPACING),
            button_y,
            ACTION_BUTTON_WIDTH,
            ACTION_BUTTON_HEIGHT,
            "Cast Spell",
            callback=self._on_cast_spell
        )

        self.btn_item = Button(
            start_x + 3 * (ACTION_BUTTON_WIDTH + ACTION_BUTTON_SPACING),
            button_y,
            ACTION_BUTTON_WIDTH,
            ACTION_BUTTON_HEIGHT,
            "Use Item",
            callback=self._on_use_item
        )

        self.buttons = [
            self.btn_next_turn,
            self.btn_attack,
            self.btn_cast,
            self.btn_item
        ]

    def _on_next_turn(self) -> None:
        """Handle next turn button."""
        if self.on_next_turn:
            self.on_next_turn()

    def _on_attack(self) -> None:
        """Handle attack button."""
        if self.on_attack:
            self.on_attack()

    def _on_cast_spell(self) -> None:
        """Handle cast spell button."""
        if self.on_cast_spell:
            self.on_cast_spell()

    def _on_use_item(self) -> None:
        """Handle use item button."""
        if self.on_use_item:
            self.on_use_item()

    def update_from_state(self) -> None:
        """Update UI components from game state."""
        # Update scene image
        scene_img = self.image_provider.get_scene_image(
            self.state.location.name,
            SCENE_IMAGE_WIDTH,
            SCENE_IMAGE_HEIGHT
        )
        self.scene_image.set_image(scene_img)

        # Update map image
        map_img = self.image_provider.get_map_image(
            self.state.location.name,
            MAP_THUMB_WIDTH,
            MAP_THUMB_HEIGHT - 10
        )
        self.map_image.set_image(map_img)

        # Update adventure log
        self.log_text.set_lines(self.state.get_recent_log(20))

        # Update character stats
        player = self.state.get_current_player()
        if player:
            # Update portrait
            portrait = self.image_provider.get_character_portrait(
                player.name,
                player.char_class,
                PORTRAIT_WIDTH,
                PORTRAIT_HEIGHT
            )
            self.char_portrait.set_image(portrait)

            # Update HP/Mana bars
            self.hp_bar.set_value(player.hp, player.max_hp)
            self.mana_bar.set_value(player.mana, player.max_mana)

        # Update quest info
        quest_lines = [
            self.state.quest.title,
            "",
            self.state.quest.description
        ]
        self.quest_text.set_lines(quest_lines)

        # Update inventory (simplified - just show gold for now)
        self.inv_grid.clear_all()
        # TODO: Populate from actual inventory

    def render(self, surface: pygame.Surface) -> None:
        """Render the entire game screen."""
        # Update from state
        self.update_from_state()

        # Render all panels
        for panel in self.panels:
            panel.render(surface)

        # Render all buttons
        for button in self.buttons:
            button.render(surface)

        # Render turn counter and status
        self._render_status(surface)

    def _render_status(self, surface: pygame.Surface) -> None:
        """Render game status info."""
        theme = get_theme()
        pygame.font.init()
        font = pygame.font.Font(None, 18)

        # Turn counter
        turn_text = font.render(f"Turn: {self.state.turn_count}", True, theme.text_secondary)
        surface.blit(turn_text, (MARGIN, SCREEN_HEIGHT - 20))

        # Phase indicator
        phase_text = font.render(f"Phase: {self.state.phase.value}", True, theme.text_secondary)
        surface.blit(phase_text, (MARGIN + 100, SCREEN_HEIGHT - 20))

        # Gold counter
        gold_text = font.render(f"Gold: {self.state.inventory.gold}", True, theme.text_highlight)
        surface.blit(gold_text, (SCREEN_WIDTH - 100, SCREEN_HEIGHT - 20))

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle events for all components."""
        # Check buttons first
        for button in self.buttons:
            if button.handle_event(event):
                return True

        # Then check panels
        for panel in self.panels:
            if panel.handle_event(event):
                return True

        return False

