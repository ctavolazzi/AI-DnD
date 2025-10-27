#!/usr/bin/env python3
"""
Interactive Pygame D&D Game

This is a truly interactive version where you can:
- Control characters directly with mouse clicks
- Move around a game world
- Take actions in real-time
- Explore and interact with the environment
- Fight enemies with direct control

Usage:
    python3 pygame_dnd_interactive.py
"""

import pygame
import sys
import os
import logging
import argparse
import time
import random
import math
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# Import existing game components
from dnd_game import DnDGame, Character, GameError
from narrative_engine import NarrativeEngine
from items import Inventory, Item
from spells import SpellBook, Spell

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 1000
FPS = 60

# Game world constants
WORLD_WIDTH = 2000
WORLD_HEIGHT = 2000
TILE_SIZE = 32

# Colors
COLORS = {
    'background': (20, 30, 20),        # Dark forest green
    'panel': (40, 50, 40),            # Dark panel
    'border': (139, 69, 19),          # Brown border
    'text': (255, 255, 255),          # White text
    'text_secondary': (200, 200, 200), # Gray text
    'accent': (255, 215, 0),          # Gold accent
    'health': (0, 255, 0),            # Green health
    'mana': (0, 150, 255),            # Blue mana
    'damage': (255, 50, 50),          # Red damage
    'button': (60, 70, 60),           # Button background
    'button_hover': (90, 100, 90),    # Button hover
    'button_pressed': (40, 50, 40),   # Button pressed
    'success': (0, 200, 100),         # Success messages
    'warning': (255, 200, 0),         # Warning messages
    'error': (255, 100, 100),         # Error messages
    'grass': (34, 139, 34),           # Grass tiles
    'stone': (105, 105, 105),         # Stone tiles
    'water': (0, 100, 200),           # Water tiles
    'player': (0, 255, 0),            # Player color
    'enemy': (255, 0, 0),             # Enemy color
    'npc': (255, 255, 0),             # NPC color
    'item': (255, 165, 0),            # Item color
}

class GameState(Enum):
    """Game states."""
    EXPLORING = "exploring"
    COMBAT = "combat"
    INVENTORY = "inventory"
    SPELLS = "spells"
    DIALOGUE = "dialogue"

class TileType(Enum):
    """Tile types for the world."""
    GRASS = "grass"
    STONE = "stone"
    WATER = "water"
    TREE = "tree"
    MOUNTAIN = "mountain"

@dataclass
class Tile:
    """Represents a tile in the game world."""
    x: int
    y: int
    tile_type: TileType
    walkable: bool = True
    has_item: bool = False
    item: Optional[Item] = None

@dataclass
class GameEntity:
    """Base class for game entities."""
    x: float
    y: float
    width: int
    height: int
    color: Tuple[int, int, int]
    name: str
    character: Optional[Character] = None

class Player(GameEntity):
    """Player character entity."""
    def __init__(self, x: float, y: float, character: Character):
        super().__init__(x, y, 24, 24, COLORS['player'], character.name, character)
        self.selected = False
        self.moving = False
        self.target_x = x
        self.target_y = y
        self.speed = 2.0

class Enemy(GameEntity):
    """Enemy entity."""
    def __init__(self, x: float, y: float, character: Character):
        super().__init__(x, y, 20, 20, COLORS['enemy'], character.name, character)
        self.aggro_range = 100
        self.attack_range = 30
        self.last_attack_time = 0
        self.attack_cooldown = 2000  # 2 seconds in milliseconds

class NPC(GameEntity):
    """NPC entity."""
    def __init__(self, x: float, y: float, name: str, dialogue: str = ""):
        super().__init__(x, y, 22, 22, COLORS['npc'], name)
        self.dialogue = dialogue

class ItemEntity(GameEntity):
    """Item entity on the ground."""
    def __init__(self, x: float, y: float, item: Item):
        super().__init__(x, y, 16, 16, COLORS['item'], item.name)
        self.item = item

class InteractiveDnDGame:
    """Interactive D&D game with real-time gameplay."""

    def __init__(self, vault_path: str = "character-journal-test-vault", model: str = "mistral"):
        """Initialize the interactive game."""
        self.vault_path = vault_path
        self.model = model

        # Initialize pygame
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Interactive AI D&D Game - Click to Play!")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)

        # Game state
        self.game_state = GameState.EXPLORING
        self.running = True
        self.camera_x = 0
        self.camera_y = 0

        # World
        self.world_tiles = self._generate_world()
        self.entities = []
        self.players = []
        self.enemies = []
        self.npcs = []
        self.items = []

        # UI
        self.selected_entity = None
        self.hovered_entity = None
        self.ui_panels = []
        self.buttons = []

        # Game components
        self.narrative_engine = NarrativeEngine(model)
        self.game_log = []

        # Initialize game world
        self._setup_world()
        self._setup_ui()

        # Logging
        self.logger = logging.getLogger("interactive_dnd_game")
        logging.basicConfig(level=logging.INFO)

        self.logger.info("Interactive D&D Game initialized")

    def _generate_world(self) -> List[List[Tile]]:
        """Generate the game world."""
        tiles = []
        for y in range(WORLD_HEIGHT // TILE_SIZE):
            row = []
            for x in range(WORLD_WIDTH // TILE_SIZE):
                # Simple world generation
                if random.random() < 0.1:
                    tile_type = TileType.WATER
                    walkable = False
                elif random.random() < 0.05:
                    tile_type = TileType.STONE
                    walkable = True
                else:
                    tile_type = TileType.GRASS
                    walkable = True

                tile = Tile(x * TILE_SIZE, y * TILE_SIZE, tile_type, walkable)
                row.append(tile)
            tiles.append(row)
        return tiles

    def _setup_world(self):
        """Setup the game world with entities."""
        # Create player characters
        game = DnDGame(auto_create_characters=True, model=self.model)

        for i, char in enumerate(game.players):
            x = 400 + i * 100
            y = 400 + i * 50
            player = Player(x, y, char)
            self.players.append(player)
            self.entities.append(player)

        # Create enemies
        for i, char in enumerate(game.enemies):
            x = 800 + i * 150
            y = 600 + i * 100
            enemy = Enemy(x, y, char)
            self.enemies.append(enemy)
            self.entities.append(enemy)

        # Create NPCs
        npcs_data = [
            ("Merchant", "Welcome to my shop! I have the finest wares."),
            ("Guard", "Halt! Who goes there?"),
            ("Wizard", "I sense great magic in you, young adventurer."),
            ("Innkeeper", "Need a place to rest? We have rooms available.")
        ]

        for i, (name, dialogue) in enumerate(npcs_data):
            x = 200 + i * 200
            y = 300 + i * 150
            npc = NPC(x, y, name, dialogue)
            self.npcs.append(npc)
            self.entities.append(npc)

        # Create some items on the ground
        item_locations = [(500, 500), (700, 300), (900, 800), (300, 700)]
        for i, (x, y) in enumerate(item_locations):
            # Create a simple item
            item = Item(f"item_{i}", f"Magic Item {i+1}", "treasure", f"A mysterious item found on the ground")
            item_entity = ItemEntity(x, y, item)
            self.items.append(item_entity)
            self.entities.append(item_entity)

        # Set camera to focus on first player and auto-select it
        if self.players:
            self.camera_x = self.players[0].x - SCREEN_WIDTH // 2
            self.camera_y = self.players[0].y - SCREEN_HEIGHT // 2
            self.selected_entity = self.players[0]  # Auto-select first player

    def _setup_ui(self):
        """Setup the UI elements."""
        # Create UI panels and buttons
        self._create_ui_elements()

    def _create_ui_elements(self):
        """Create UI elements."""
        # This will be implemented with the UI system
        pass

    def _world_to_screen(self, world_x: float, world_y: float) -> Tuple[int, int]:
        """Convert world coordinates to screen coordinates."""
        screen_x = int(world_x - self.camera_x)
        screen_y = int(world_y - self.camera_y)
        return screen_x, screen_y

    def _screen_to_world(self, screen_x: int, screen_y: int) -> Tuple[float, float]:
        """Convert screen coordinates to world coordinates."""
        world_x = screen_x + self.camera_x
        world_y = screen_y + self.camera_y
        return world_x, world_y

    def _get_tile_at(self, world_x: float, world_y: float) -> Optional[Tile]:
        """Get the tile at world coordinates."""
        tile_x = int(world_x // TILE_SIZE)
        tile_y = int(world_y // TILE_SIZE)

        if 0 <= tile_y < len(self.world_tiles) and 0 <= tile_x < len(self.world_tiles[tile_y]):
            return self.world_tiles[tile_y][tile_x]
        return None

    def _is_walkable(self, world_x: float, world_y: float) -> bool:
        """Check if a position is walkable."""
        tile = self._get_tile_at(world_x, world_y)
        if not tile:
            return False

        # Check if any entity is blocking the position (except items)
        for entity in self.entities:
            if (abs(entity.x - world_x) < entity.width and
                abs(entity.y - world_y) < entity.height and
                entity != self.selected_entity and
                not isinstance(entity, ItemEntity)):
                return False

        return tile.walkable

    def _get_entity_at(self, world_x: float, world_y: float) -> Optional[GameEntity]:
        """Get the entity at world coordinates."""
        for entity in self.entities:
            if (entity.x <= world_x <= entity.x + entity.width and
                entity.y <= world_y <= entity.y + entity.height):
                return entity
        return None

    def _move_entity(self, entity: GameEntity, target_x: float, target_y: float):
        """Move an entity towards a target position."""
        # Simple movement - just move directly to target
        dx = target_x - entity.x
        dy = target_y - entity.y
        distance = math.sqrt(dx*dx + dy*dy)

        if distance > 0:
            # Normalize and apply speed
            dx = (dx / distance) * entity.speed
            dy = (dy / distance) * entity.speed

            new_x = entity.x + dx
            new_y = entity.y + dy

            # Check if new position is walkable
            if self._is_walkable(new_x, new_y):
                entity.x = new_x
                entity.y = new_y
                return True
            else:
                # Try to move in just X or just Y direction
                if self._is_walkable(new_x, entity.y):
                    entity.x = new_x
                    return True
                elif self._is_walkable(entity.x, new_y):
                    entity.y = new_y
                    return True

        return False

    def _update_camera(self):
        """Update camera position to follow selected player."""
        if self.selected_entity and isinstance(self.selected_entity, Player):
            target_camera_x = self.selected_entity.x - SCREEN_WIDTH // 2
            target_camera_y = self.selected_entity.y - SCREEN_HEIGHT // 2

            # Smooth camera movement
            self.camera_x += (target_camera_x - self.camera_x) * 0.1
            self.camera_y += (target_camera_y - self.camera_y) * 0.1

    def _handle_click(self, screen_x: int, screen_y: int):
        """Handle mouse click."""
        world_x, world_y = self._screen_to_world(screen_x, screen_y)
        entity = self._get_entity_at(world_x, world_y)

        if entity:
            if isinstance(entity, Player):
                # Select player
                self.selected_entity = entity
                self._add_log(f"Selected {entity.name}")
            elif isinstance(entity, Enemy):
                # Attack enemy if player selected
                if self.selected_entity and isinstance(self.selected_entity, Player):
                    self._attack_entity(self.selected_entity, entity)
            elif isinstance(entity, NPC):
                # Talk to NPC
                self._talk_to_npc(entity)
            elif isinstance(entity, ItemEntity):
                # Pick up item
                if self.selected_entity and isinstance(self.selected_entity, Player):
                    self._pickup_item(self.selected_entity, entity)
        else:
            # Move selected player to location
            if self.selected_entity and isinstance(self.selected_entity, Player):
                # Check if the target location is walkable
                if self._is_walkable(world_x, world_y):
                    self.selected_entity.target_x = world_x
                    self.selected_entity.target_y = world_y
                    self.selected_entity.moving = True
                    self._add_log(f"Moving {self.selected_entity.name} to ({int(world_x)}, {int(world_y)})")
                else:
                    self._add_log(f"Cannot move to ({int(world_x)}, {int(world_y)}) - blocked!", "warning")

    def _attack_entity(self, attacker: Player, target: Enemy):
        """Attack an entity."""
        if not attacker.character or not target.character:
            return

        # Check if in range
        distance = math.sqrt((attacker.x - target.x)**2 + (attacker.y - target.y)**2)
        if distance > attacker.character.attack * 10:  # Attack range based on attack stat
            self._add_log(f"{attacker.name} is too far to attack {target.name}")
            return

        # Perform attack
        result = attacker.character.attack_target(target.character)
        damage = result.get("damage_dealt", 0)

        self._add_log(f"{attacker.name} attacks {target.name} for {damage} damage!", "combat")

        if not target.character.alive:
            self._add_log(f"{target.name} has been defeated!", "success")
            # Remove enemy from game
            if target in self.enemies:
                self.enemies.remove(target)
            if target in self.entities:
                self.entities.remove(target)

    def _talk_to_npc(self, npc: NPC):
        """Talk to an NPC."""
        self._add_log(f"Talking to {npc.name}: {npc.dialogue}", "narrative")

    def _pickup_item(self, player: Player, item_entity: ItemEntity):
        """Pick up an item."""
        if not player.character:
            return

        # Add item to inventory
        if player.character.inventory.add_item(item_entity.item.item_id, 1):
            self._add_log(f"{player.name} picked up {item_entity.item.name}!", "success")
            # Remove item from world
            if item_entity in self.items:
                self.items.remove(item_entity)
            if item_entity in self.entities:
                self.entities.remove(item_entity)
        else:
            self._add_log(f"{player.name}'s inventory is full!", "warning")

    def _attack_nearest_enemy(self):
        """Attack the nearest enemy to the selected player."""
        if not self.selected_entity or not isinstance(self.selected_entity, Player):
            return

        player = self.selected_entity
        nearest_enemy = None
        min_distance = float('inf')

        for enemy in self.enemies:
            if enemy.character and enemy.character.alive:
                distance = math.sqrt((player.x - enemy.x)**2 + (player.y - enemy.y)**2)
                if distance < min_distance and distance <= 50:  # Attack range
                    min_distance = distance
                    nearest_enemy = enemy

        if nearest_enemy:
            self._attack_entity(player, nearest_enemy)
        else:
            self._add_log("No enemies in range to attack!", "warning")

    def _interact_nearest_entity(self):
        """Interact with the nearest entity to the selected player."""
        if not self.selected_entity or not isinstance(self.selected_entity, Player):
            return

        player = self.selected_entity
        nearest_entity = None
        min_distance = float('inf')

        for entity in self.entities:
            if entity != player and entity.character and entity.character.alive:
                distance = math.sqrt((player.x - entity.x)**2 + (player.y - entity.y)**2)
                if distance < min_distance and distance <= 40:  # Interaction range
                    min_distance = distance
                    nearest_entity = entity

        if nearest_entity:
            if isinstance(nearest_entity, NPC):
                self._talk_to_npc(nearest_entity)
            elif isinstance(nearest_entity, ItemEntity):
                self._pickup_item(player, nearest_entity)
            elif isinstance(nearest_entity, Enemy):
                self._attack_entity(player, nearest_entity)
        else:
            self._add_log("Nothing nearby to interact with!", "info")

    def _add_log(self, message: str, message_type: str = "info"):
        """Add a message to the game log."""
        self.game_log.append({
            'message': message,
            'type': message_type,
            'time': time.time()
        })

        # Keep only last 20 messages
        if len(self.game_log) > 20:
            self.game_log = self.game_log[-20:]

    def _update_entities(self):
        """Update all entities."""
        current_time = time.time() * 1000  # Convert to milliseconds

        # Update player movement
        for player in self.players:
            if player.moving:
                # Check if reached target
                distance = math.sqrt((player.x - player.target_x)**2 + (player.y - player.target_y)**2)
                if distance < 5:
                    player.moving = False
                else:
                    # Continue moving towards target
                    self._move_entity(player, player.target_x, player.target_y)

        # Update enemy AI
        for enemy in self.enemies:
            if not enemy.character or not enemy.character.alive:
                continue

            # Simple AI: move towards nearest player
            nearest_player = None
            min_distance = float('inf')

            for player in self.players:
                if player.character and player.character.alive:
                    distance = math.sqrt((enemy.x - player.x)**2 + (enemy.y - player.y)**2)
                    if distance < min_distance:
                        min_distance = distance
                        nearest_player = player

            if nearest_player and min_distance < enemy.aggro_range:
                # Move towards player
                if min_distance > enemy.attack_range:
                    self._move_entity(enemy, nearest_player.x, nearest_player.y)
                else:
                    # Attack if in range
                    if current_time - enemy.last_attack_time > enemy.attack_cooldown:
                        self._attack_entity(enemy, nearest_player)
                        enemy.last_attack_time = current_time

    def _draw_world(self):
        """Draw the game world."""
        # Draw tiles
        start_x = int(self.camera_x // TILE_SIZE)
        start_y = int(self.camera_y // TILE_SIZE)
        end_x = start_x + (SCREEN_WIDTH // TILE_SIZE) + 2
        end_y = start_y + (SCREEN_HEIGHT // TILE_SIZE) + 2

        for y in range(max(0, start_y), min(len(self.world_tiles), end_y)):
            for x in range(max(0, start_x), min(len(self.world_tiles[y]), end_x)):
                tile = self.world_tiles[y][x]
                screen_x, screen_y = self._world_to_screen(tile.x, tile.y)

                # Choose color based on tile type
                if tile.tile_type == TileType.GRASS:
                    color = COLORS['grass']
                elif tile.tile_type == TileType.STONE:
                    color = COLORS['stone']
                elif tile.tile_type == TileType.WATER:
                    color = COLORS['water']
                else:
                    color = COLORS['grass']

                pygame.draw.rect(self.screen, color, (screen_x, screen_y, TILE_SIZE, TILE_SIZE))
                pygame.draw.rect(self.screen, (0, 0, 0), (screen_x, screen_y, TILE_SIZE, TILE_SIZE), 1)

    def _draw_entities(self):
        """Draw all entities."""
        for entity in self.entities:
            screen_x, screen_y = self._world_to_screen(entity.x, entity.y)

            # Only draw if on screen
            if -entity.width <= screen_x <= SCREEN_WIDTH and -entity.height <= screen_y <= SCREEN_HEIGHT:
                # Draw entity
                pygame.draw.rect(self.screen, entity.color, (screen_x, screen_y, entity.width, entity.height))

                # Draw border
                border_color = COLORS['accent'] if entity == self.selected_entity else (0, 0, 0)
                pygame.draw.rect(self.screen, border_color, (screen_x, screen_y, entity.width, entity.height), 2)

                # Draw name
                name_surface = self.small_font.render(entity.name, True, COLORS['text'])
                name_rect = name_surface.get_rect(center=(screen_x + entity.width // 2, screen_y - 10))
                self.screen.blit(name_surface, name_rect)

                # Draw health bar for characters
                if entity.character and entity.character.alive:
                    hp_ratio = entity.character.hp / entity.character.max_hp
                    bar_width = entity.width
                    bar_height = 4
                    bar_x = screen_x
                    bar_y = screen_y + entity.height + 2

                    # Background
                    pygame.draw.rect(self.screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))

                    # Health
                    health_width = int(bar_width * hp_ratio)
                    health_color = COLORS['health'] if hp_ratio > 0.5 else (255, 255, 0) if hp_ratio > 0.25 else COLORS['damage']
                    pygame.draw.rect(self.screen, health_color, (bar_x, bar_y, health_width, bar_height))

    def _draw_ui(self):
        """Draw the UI."""
        # Draw game log
        log_x = 10
        log_y = SCREEN_HEIGHT - 200
        log_width = 400
        log_height = 190

        # Background
        pygame.draw.rect(self.screen, COLORS['panel'], (log_x, log_y, log_width, log_height))
        pygame.draw.rect(self.screen, COLORS['border'], (log_x, log_y, log_width, log_height), 2)

        # Title
        title_surface = self.font.render("Game Log", True, COLORS['accent'])
        self.screen.blit(title_surface, (log_x + 10, log_y + 10))

        # Messages
        y_offset = 40
        for message_data in self.game_log[-8:]:  # Show last 8 messages
            message = message_data['message']
            msg_type = message_data['type']

            # Choose color based on type
            color = COLORS['text']
            if msg_type == "combat":
                color = COLORS['damage']
            elif msg_type == "narrative":
                color = COLORS['accent']
            elif msg_type == "success":
                color = COLORS['success']
            elif msg_type == "warning":
                color = COLORS['warning']
            elif msg_type == "error":
                color = COLORS['error']

            # Wrap long messages
            words = message.split()
            lines = []
            current_line = ""

            for word in words:
                test_line = current_line + " " + word if current_line else word
                if self.small_font.size(test_line)[0] < log_width - 20:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word

            if current_line:
                lines.append(current_line)

            for line in lines:
                if y_offset < log_height - 20:
                    message_surface = self.small_font.render(line, True, color)
                    self.screen.blit(message_surface, (log_x + 10, log_y + y_offset))
                    y_offset += 20

        # Draw selected entity info
        if self.selected_entity and self.selected_entity.character:
            info_x = SCREEN_WIDTH - 300
            info_y = 10
            info_width = 290
            info_height = 150

            # Background
            pygame.draw.rect(self.screen, COLORS['panel'], (info_x, info_y, info_width, info_height))
            pygame.draw.rect(self.screen, COLORS['border'], (info_x, info_y, info_width, info_height), 2)

            # Character info
            char = self.selected_entity.character
            y_offset = 20

            # Name and class
            name_surface = self.font.render(f"{char.name} ({char.char_class})", True, COLORS['accent'])
            self.screen.blit(name_surface, (info_x + 10, info_y + y_offset))
            y_offset += 30

            # Stats
            stats = [
                f"HP: {char.hp}/{char.max_hp}",
                f"Mana: {char.mana}/{char.max_mana}",
                f"Attack: {char.attack}",
                f"Defense: {char.defense}"
            ]

            for stat in stats:
                stat_surface = self.small_font.render(stat, True, COLORS['text'])
                self.screen.blit(stat_surface, (info_x + 10, info_y + y_offset))
                y_offset += 20

        # Draw instructions
        instructions = [
            "CONTROLS:",
            "• 1/2: Select player 1/2",
            "• WASD/Arrows: Move character",
            "• SPACE: Attack nearest enemy",
            "• E: Interact with nearest entity",
            "• Shift+WASD: Move camera",
            "• ESC: Quit game"
        ]

        if self.selected_entity:
            instructions.append(f"SELECTED: {self.selected_entity.name}")
        else:
            instructions.append("Press 1 or 2 to select a character!")

        inst_x = 10
        inst_y = 10
        for instruction in instructions:
            inst_surface = self.small_font.render(instruction, True, COLORS['text_secondary'])
            self.screen.blit(inst_surface, (inst_x, inst_y))
            inst_y += 20

    def _handle_events(self):
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self._handle_click(event.pos[0], event.pos[1])

            elif event.type == pygame.KEYDOWN:
                # Character movement with WASD/Arrow keys
                if self.selected_entity and isinstance(self.selected_entity, Player):
                    move_distance = 32  # Move one tile at a time

                    if event.key == pygame.K_w or event.key == pygame.K_UP:
                        new_y = self.selected_entity.y - move_distance
                        if self._is_walkable(self.selected_entity.x, new_y):
                            self.selected_entity.y = new_y
                            self._add_log(f"{self.selected_entity.name} moves north")

                    elif event.key == pygame.K_s or event.key == pygame.K_DOWN:
                        new_y = self.selected_entity.y + move_distance
                        if self._is_walkable(self.selected_entity.x, new_y):
                            self.selected_entity.y = new_y
                            self._add_log(f"{self.selected_entity.name} moves south")

                    elif event.key == pygame.K_a or event.key == pygame.K_LEFT:
                        new_x = self.selected_entity.x - move_distance
                        if self._is_walkable(new_x, self.selected_entity.y):
                            self.selected_entity.x = new_x
                            self._add_log(f"{self.selected_entity.name} moves west")

                    elif event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                        new_x = self.selected_entity.x + move_distance
                        if self._is_walkable(new_x, self.selected_entity.y):
                            self.selected_entity.x = new_x
                            self._add_log(f"{self.selected_entity.name} moves east")

                # Camera movement (when no character selected or with Shift)
                keys = pygame.key.get_pressed()
                if not self.selected_entity or keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                    if event.key == pygame.K_w or event.key == pygame.K_UP:
                        self.camera_y -= 50
                    elif event.key == pygame.K_s or event.key == pygame.K_DOWN:
                        self.camera_y += 50
                    elif event.key == pygame.K_a or event.key == pygame.K_LEFT:
                        self.camera_x -= 50
                    elif event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                        self.camera_x += 50

                # Other controls
                elif event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    # Attack nearest enemy
                    if self.selected_entity and isinstance(self.selected_entity, Player):
                        self._attack_nearest_enemy()
                elif event.key == pygame.K_e:
                    # Interact with nearest entity
                    if self.selected_entity and isinstance(self.selected_entity, Player):
                        self._interact_nearest_entity()
                elif event.key == pygame.K_1:
                    # Select first player
                    if self.players:
                        self.selected_entity = self.players[0]
                        self._add_log(f"Selected {self.players[0].name}")
                elif event.key == pygame.K_2:
                    # Select second player
                    if len(self.players) > 1:
                        self.selected_entity = self.players[1]
                        self._add_log(f"Selected {self.players[1].name}")

    def _draw(self):
        """Draw everything."""
        # Clear screen
        self.screen.fill(COLORS['background'])

        # Draw world
        self._draw_world()

        # Draw entities
        self._draw_entities()

        # Draw UI
        self._draw_ui()

        # Update display
        pygame.display.flip()

    def run(self):
        """Main game loop."""
        self.logger.info("Starting Interactive D&D Game")
        self._add_log("Welcome to the Interactive D&D Game!", "narrative")
        self._add_log("Click on players to select them, then click to move or attack!", "info")

        while self.running:
            # Handle events
            self._handle_events()

            # Update game state
            self._update_entities()
            self._update_camera()

            # Draw everything
            self._draw()

            # Control frame rate
            self.clock.tick(FPS)

        pygame.quit()
        self.logger.info("Game ended")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Run Interactive D&D game')
    parser.add_argument('--vault', type=str, default='character-journal-test-vault',
                      help='Path to Obsidian vault')
    parser.add_argument('--model', type=str, default='mistral',
                      help='Model to use for generation')
    args = parser.parse_args()

    try:
        # Create and run the game
        game = InteractiveDnDGame(vault_path=args.vault, model=args.model)
        game.run()

    except Exception as e:
        print(f"Error running game: {e}")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
