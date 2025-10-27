#!/usr/bin/env python3
"""
Pygame-based AI D&D Game

This module provides a graphical interface for the AI-driven Dungeons & Dragons game
using pygame. It preserves all existing game mechanics while adding visual elements
like sprites, UI panels, and animations.

Usage:
    python3 pygame_dnd_game.py [--vault VAULT_PATH] [--reset] [--turns N] [--model MODEL_NAME]
"""

import pygame
import sys
import os
import logging
import argparse
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

# Import existing game components
from dnd_game import DnDGame, Character, GameError
from narrative_engine import NarrativeEngine
from items import Inventory, Item
from spells import SpellBook, Spell

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60

# Colors (D&D themed)
COLORS = {
    'background': (20, 20, 20),      # Dark background
    'panel': (40, 40, 40),          # Panel background
    'border': (139, 69, 19),        # Brown border
    'text': (255, 255, 255),        # White text
    'text_secondary': (200, 200, 200), # Gray text
    'accent': (255, 215, 0),        # Gold accent
    'health': (0, 255, 0),          # Green health
    'mana': (0, 100, 255),          # Blue mana
    'damage': (255, 0, 0),          # Red damage
    'button': (70, 70, 70),         # Button background
    'button_hover': (100, 100, 100), # Button hover
    'button_pressed': (50, 50, 50),  # Button pressed
}

@dataclass
class UIElement:
    """Base class for UI elements."""
    x: int
    y: int
    width: int
    height: int
    visible: bool = True

class Button(UIElement):
    """A clickable button."""

    def __init__(self, x: int, y: int, width: int, height: int, text: str,
                 callback=None, font_size: int = 16):
        super().__init__(x, y, width, height)
        self.text = text
        self.callback = callback
        self.font = pygame.font.Font(None, font_size)
        self.hovered = False
        self.pressed = False

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle pygame events. Returns True if event was handled."""
        if not self.visible:
            return False

        if event.type == pygame.MOUSEMOTION:
            mouse_x, mouse_y = event.pos
            self.hovered = (self.x <= mouse_x <= self.x + self.width and
                           self.y <= mouse_y <= self.y + self.height)
            return self.hovered

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.hovered:  # Left click
                self.pressed = True
                return True

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.pressed and self.hovered:
                self.pressed = False
                if self.callback:
                    self.callback()
                return True
            self.pressed = False

        return False

    def draw(self, screen: pygame.Surface):
        """Draw the button."""
        if not self.visible:
            return

        # Choose color based on state
        if self.pressed:
            color = COLORS['button_pressed']
        elif self.hovered:
            color = COLORS['button_hover']
        else:
            color = COLORS['button']

        # Draw button background
        pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, COLORS['border'], (self.x, self.y, self.width, self.height), 2)

        # Draw text
        text_surface = self.font.render(self.text, True, COLORS['text'])
        text_rect = text_surface.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))
        screen.blit(text_surface, text_rect)

class Panel(UIElement):
    """A UI panel with title and content."""

    def __init__(self, x: int, y: int, width: int, height: int, title: str = ""):
        super().__init__(x, y, width, height)
        self.title = title
        self.font = pygame.font.Font(None, 20)
        self.title_font = pygame.font.Font(None, 24)
        self.content = []

    def add_text(self, text: str, color: Tuple[int, int, int] = None):
        """Add text to the panel content."""
        if color is None:
            color = COLORS['text']
        self.content.append((text, color))

    def clear_content(self):
        """Clear panel content."""
        self.content = []

    def draw(self, screen: pygame.Surface):
        """Draw the panel."""
        if not self.visible:
            return

        # Draw panel background
        pygame.draw.rect(screen, COLORS['panel'], (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, COLORS['border'], (self.x, self.y, self.width, self.height), 2)

        # Draw title
        if self.title:
            title_surface = self.title_font.render(self.title, True, COLORS['accent'])
            screen.blit(title_surface, (self.x + 10, self.y + 10))

        # Draw content
        y_offset = 40 if self.title else 10
        for text, color in self.content:
            text_surface = self.font.render(text, True, color)
            screen.blit(text_surface, (self.x + 10, self.y + y_offset))
            y_offset += 25

class CharacterDisplay(UIElement):
    """Displays character information."""

    def __init__(self, x: int, y: int, width: int, height: int, character: Character):
        super().__init__(x, y, width, height)
        self.character = character
        self.font = pygame.font.Font(None, 18)
        self.title_font = pygame.font.Font(None, 22)

    def draw(self, screen: pygame.Surface):
        """Draw character information."""
        if not self.visible or not self.character:
            return

        # Draw background
        pygame.draw.rect(screen, COLORS['panel'], (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, COLORS['border'], (self.x, self.y, self.width, self.height), 2)

        y_offset = 10

        # Character name and class
        name_text = f"{self.character.name} ({self.character.char_class})"
        name_surface = self.title_font.render(name_text, True, COLORS['accent'])
        screen.blit(name_surface, (self.x + 10, self.y + y_offset))
        y_offset += 30

        # HP Bar
        hp_text = f"HP: {self.character.hp}/{self.character.max_hp}"
        hp_surface = self.font.render(hp_text, True, COLORS['text'])
        screen.blit(hp_surface, (self.x + 10, self.y + y_offset))

        # HP Bar visual
        bar_width = 200
        bar_height = 20
        bar_x = self.x + 10
        bar_y = self.y + y_offset + 25

        # Background bar
        pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))

        # Health bar
        hp_ratio = self.character.hp / self.character.max_hp
        health_width = int(bar_width * hp_ratio)
        health_color = COLORS['health'] if hp_ratio > 0.5 else (255, 255, 0) if hp_ratio > 0.25 else COLORS['damage']
        pygame.draw.rect(screen, health_color, (bar_x, bar_y, health_width, bar_height))

        # Border
        pygame.draw.rect(screen, COLORS['border'], (bar_x, bar_y, bar_width, bar_height), 2)
        y_offset += 60

        # Mana Bar
        mana_text = f"Mana: {self.character.mana}/{self.character.max_mana}"
        mana_surface = self.font.render(mana_text, True, COLORS['text'])
        screen.blit(mana_surface, (self.x + 10, self.y + y_offset))

        # Mana Bar visual
        bar_y = self.y + y_offset + 25
        pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))

        mana_ratio = self.character.mana / self.character.max_mana
        mana_width = int(bar_width * mana_ratio)
        pygame.draw.rect(screen, COLORS['mana'], (bar_x, bar_y, mana_width, bar_height))
        pygame.draw.rect(screen, COLORS['border'], (bar_x, bar_y, bar_width, bar_height), 2)
        y_offset += 60

        # Stats
        stats = [
            f"Attack: {self.character.attack}",
            f"Defense: {self.character.defense}",
            f"Level: {getattr(self.character, 'level', 1)}"
        ]

        for stat in stats:
            stat_surface = self.font.render(stat, True, COLORS['text_secondary'])
            screen.blit(stat_surface, (self.x + 10, self.y + y_offset))
            y_offset += 25

class PygameDnDGame:
    """Main pygame-based D&D game class."""

    def __init__(self, vault_path: str = "character-journal-test-vault", model: str = "mistral"):
        """Initialize the pygame D&D game."""
        self.vault_path = vault_path
        self.model = model

        # Initialize pygame
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("AI D&D Game - Pygame Version")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)

        # Initialize game components
        self.game = DnDGame(auto_create_characters=True, model=model)
        self.narrative_engine = NarrativeEngine(model)

        # UI Elements
        self.ui_elements = []
        self.buttons = []
        self.panels = []
        self.character_displays = []

        # Game state
        self.running = True
        self.current_turn = 0
        self.max_turns = 10
        self.game_over = False

        # Setup UI
        self._setup_ui()

        # Logging
        self.logger = logging.getLogger("pygame_dnd_game")
        logging.basicConfig(level=logging.INFO)

    def _setup_ui(self):
        """Setup the user interface."""
        # Main game panel (left side)
        main_panel = Panel(10, 10, 600, 500, "Game Log")
        self.panels.append(main_panel)

        # Character panels (right side)
        char_panel_width = 280
        char_panel_height = 200

        # Player 1
        if len(self.game.players) > 0:
            player1_display = CharacterDisplay(620, 10, char_panel_width, char_panel_height, self.game.players[0])
            self.character_displays.append(player1_display)

        # Player 2
        if len(self.game.players) > 1:
            player2_display = CharacterDisplay(620, 220, char_panel_width, char_panel_height, self.game.players[1])
            self.character_displays.append(player2_display)

        # Enemy 1
        if len(self.game.enemies) > 0:
            enemy1_display = CharacterDisplay(620, 430, char_panel_width, char_panel_height, self.game.enemies[0])
            self.character_displays.append(enemy1_display)

        # Enemy 2
        if len(self.game.enemies) > 1:
            enemy2_display = CharacterDisplay(620, 640, char_panel_width, char_panel_height, self.game.enemies[1])
            self.character_displays.append(enemy2_display)

        # Control buttons
        self.next_turn_button = Button(10, 520, 120, 40, "Next Turn", self.next_turn)
        self.buttons.append(self.next_turn_button)

        self.attack_button = Button(140, 520, 120, 40, "Attack", self.attack_action)
        self.buttons.append(self.attack_button)

        self.cast_spell_button = Button(270, 520, 120, 40, "Cast Spell", self.cast_spell_action)
        self.buttons.append(self.cast_spell_button)

        self.use_item_button = Button(400, 520, 120, 40, "Use Item", self.use_item_action)
        self.buttons.append(self.use_item_button)

        # Status panel
        self.status_panel = Panel(10, 570, 600, 100, "Status")
        self.panels.append(self.status_panel)

        # Inventory panel
        self.inventory_panel = Panel(910, 10, 280, 300, "Inventory")
        self.panels.append(self.inventory_panel)

        # Spell panel
        self.spell_panel = Panel(910, 320, 280, 300, "Spells")
        self.panels.append(self.spell_panel)

        # Quest panel
        self.quest_panel = Panel(910, 630, 280, 150, "Quest")
        self.panels.append(self.quest_panel)

        # Initialize panels with content
        self._update_ui()

    def _update_ui(self):
        """Update UI elements with current game state."""
        # Update main game log
        main_panel = self.panels[0]  # Game Log panel
        main_panel.clear_content()

        # Add current quest
        if hasattr(self.game, 'current_quest') and self.game.current_quest:
            main_panel.add_text(f"Quest: {self.game.current_quest}", COLORS['accent'])
            main_panel.add_text("")  # Empty line

        # Add turn information
        main_panel.add_text(f"Turn: {self.current_turn}/{self.max_turns}")
        main_panel.add_text("")

        # Add character status
        alive_players = [p for p in self.game.players if p.alive]
        alive_enemies = [e for e in self.game.enemies if e.alive]

        main_panel.add_text(f"Players alive: {len(alive_players)}/{len(self.game.players)}")
        main_panel.add_text(f"Enemies alive: {len(alive_enemies)}/{len(self.game.enemies)}")
        main_panel.add_text("")

        # Add recent actions (placeholder)
        main_panel.add_text("Recent actions will appear here...")

        # Update status panel
        self.status_panel.clear_content()
        if self.game_over:
            if any(p.alive for p in self.game.players):
                self.status_panel.add_text("VICTORY! All enemies defeated!", COLORS['health'])
            else:
                self.status_panel.add_text("DEFEAT! All players have fallen!", COLORS['damage'])
        else:
            self.status_panel.add_text("Game in progress...", COLORS['text'])

        # Update inventory panel
        self._update_inventory_panel()

        # Update spell panel
        self._update_spell_panel()

        # Update quest panel
        self._update_quest_panel()

    def _update_inventory_panel(self):
        """Update the inventory panel."""
        self.inventory_panel.clear_content()

        if self.game.players:
            player = self.game.players[0]  # Show first player's inventory
            inventory = player.inventory

            if inventory.items:
                for item_id, quantity in inventory.items.items():
                    item_text = f"{quantity}x {item_id}"
                    self.inventory_panel.add_text(item_text)
            else:
                self.inventory_panel.add_text("No items", COLORS['text_secondary'])

    def _update_spell_panel(self):
        """Update the spell panel."""
        self.spell_panel.clear_content()

        if self.game.players:
            player = self.game.players[0]  # Show first player's spells
            spellbook = player.spellbook

            if spellbook.known_spells:
                for spell_id, spell in spellbook.known_spells.items():
                    if spell:
                        spell_text = f"{spell.name} (Cost: {spell.mana_cost})"
                        self.spell_panel.add_text(spell_text)
            else:
                self.spell_panel.add_text("No spells known", COLORS['text_secondary'])

    def _update_quest_panel(self):
        """Update the quest panel."""
        self.quest_panel.clear_content()

        if hasattr(self.game, 'current_quest') and self.game.current_quest:
            # Split long quest text into multiple lines
            quest_text = self.game.current_quest
            words = quest_text.split()
            lines = []
            current_line = ""

            for word in words:
                if len(current_line + " " + word) <= 40:  # Approximate line length
                    current_line += " " + word if current_line else word
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word

            if current_line:
                lines.append(current_line)

            for line in lines:
                self.quest_panel.add_text(line)
        else:
            self.quest_panel.add_text("No active quest", COLORS['text_secondary'])

    def next_turn(self):
        """Advance to the next turn."""
        if self.game_over:
            return

        self.current_turn += 1

        # Play one turn of the game
        try:
            self.game.play_turn()

            # Check if game is over
            if self.game.is_game_over():
                self.game_over = True
                if any(p.alive for p in self.game.players):
                    self.logger.info("Victory! All enemies defeated!")
                else:
                    self.logger.info("Defeat! All players have fallen!")

            # Check turn limit
            if self.current_turn >= self.max_turns:
                self.game_over = True
                self.logger.info("Game ended due to turn limit")

        except Exception as e:
            self.logger.error(f"Error during turn: {e}")

        self._update_ui()

    def attack_action(self):
        """Handle attack action."""
        # Placeholder for attack logic
        self.logger.info("Attack action selected")

    def cast_spell_action(self):
        """Handle cast spell action."""
        # Placeholder for spell casting logic
        self.logger.info("Cast spell action selected")

    def use_item_action(self):
        """Handle use item action."""
        # Placeholder for item usage logic
        self.logger.info("Use item action selected")

    def handle_events(self):
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            # Handle button events
            for button in self.buttons:
                button.handle_event(event)

    def draw(self):
        """Draw the game."""
        # Clear screen
        self.screen.fill(COLORS['background'])

        # Draw UI elements
        for panel in self.panels:
            panel.draw(self.screen)

        for character_display in self.character_displays:
            character_display.draw(self.screen)

        for button in self.buttons:
            button.draw(self.screen)

        # Update display
        pygame.display.flip()

    def run(self):
        """Main game loop."""
        self.logger.info("Starting Pygame D&D Game")

        # Initial UI update
        self._update_ui()

        while self.running:
            # Handle events
            self.handle_events()

            # Draw everything
            self.draw()

            # Control frame rate
            self.clock.tick(FPS)

        pygame.quit()
        self.logger.info("Game ended")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Run Pygame AI D&D game')
    parser.add_argument('--vault', type=str, default='character-journal-test-vault',
                      help='Path to Obsidian vault')
    parser.add_argument('--reset', action='store_true',
                      help='Reset the vault before running')
    parser.add_argument('--turns', type=int, default=10,
                      help='Number of turns to run')
    parser.add_argument('--model', type=str, default='mistral',
                      help='Model to use for generation')
    args = parser.parse_args()

    try:
        # Create and run the game
        game = PygameDnDGame(vault_path=args.vault, model=args.model)
        game.max_turns = args.turns
        game.run()

    except Exception as e:
        print(f"Error running game: {e}")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
