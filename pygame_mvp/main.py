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

# Add project root so we can import the pygame_mvp package when running as a script.
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import pygame

# Prefer package imports to avoid colliding with root-level modules (e.g., config.py).
from pygame_mvp.config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, GAME_TITLE, CURRENT_THEME, SHOW_FPS,
    MAP_PANEL_X, MAP_PANEL_Y, MAP_PANEL_WIDTH, MAP_PANEL_HEIGHT, PADDING
)
from pygame_mvp.game.tile_map import (
    TileMap, PointOfInterest,
    create_tavern_map, create_forest_map,
    create_level_1, create_level_2, create_level_3,
    get_map, ALL_MAPS
)
from pygame_mvp.game.game_state import GameState, GamePhase
from pygame_mvp.game.game_loop import GameLoop
from pygame_mvp.game.game_manager import GameManager
from pygame_mvp.services.image_provider import MockImageProvider, APIImageProvider
from pygame_mvp.services.narrative import NarrativeService
from pygame_mvp.ui.screens import MainGameScreen


class PlayerSprite:
    """
    A movable player sprite for the map.

    Controlled with arrow keys, uses tile map for collision.
    """

    def __init__(self, x: int, y: int, size: int = 10):
        self.x = x
        self.y = y
        self.size = size
        self.speed = 2  # pixels per frame when held
        self.color = (255, 215, 0)  # Gold
        self.outline_color = (139, 90, 43)  # Brown outline

        # Movement state (for smooth movement while key held)
        self.moving_up = False
        self.moving_down = False
        self.moving_left = False
        self.moving_right = False

        # Map offset (where the tile map is rendered)
        self.map_offset_x = 0
        self.map_offset_y = 0

        # Reference to tile map for collision
        self.tile_map: TileMap = None

        # Last grid position (for POI triggering)
        self.last_grid_x = -1
        self.last_grid_y = -1

    def set_tile_map(self, tile_map: TileMap, offset_x: int, offset_y: int) -> None:
        """Set the tile map for collision detection."""
        self.tile_map = tile_map
        self.map_offset_x = offset_x
        self.map_offset_y = offset_y

    def get_local_pos(self) -> tuple:
        """Get position relative to tile map."""
        return self.x - self.map_offset_x, self.y - self.map_offset_y

    def get_grid_pos(self) -> tuple:
        """Get current grid position."""
        if self.tile_map:
            lx, ly = self.get_local_pos()
            # Use center of sprite for grid position
            cx = lx + self.size // 2
            cy = ly + self.size // 2
            return self.tile_map.pixel_to_grid(cx, cy)
        return 0, 0

    def handle_key_down(self, key: int) -> bool:
        """Handle key press. Returns True if handled."""
        if key == pygame.K_UP or key == pygame.K_w:
            self.moving_up = True
            return True
        elif key == pygame.K_DOWN or key == pygame.K_s:
            self.moving_down = True
            return True
        elif key == pygame.K_LEFT or key == pygame.K_a:
            self.moving_left = True
            return True
        elif key == pygame.K_RIGHT or key == pygame.K_d:
            self.moving_right = True
            return True
        return False

    def handle_key_up(self, key: int) -> bool:
        """Handle key release. Returns True if handled."""
        if key == pygame.K_UP or key == pygame.K_w:
            self.moving_up = False
            return True
        elif key == pygame.K_DOWN or key == pygame.K_s:
            self.moving_down = False
            return True
        elif key == pygame.K_LEFT or key == pygame.K_a:
            self.moving_left = False
            return True
        elif key == pygame.K_RIGHT or key == pygame.K_d:
            self.moving_right = False
            return True
        return False

    def update(self) -> PointOfInterest:
        """Update sprite position. Returns triggered POI if any."""
        triggered_poi = None

        # Try each movement direction with collision check
        if self.moving_up:
            new_y = self.y - self.speed
            if self._can_move_to(self.x, new_y):
                self.y = new_y
        if self.moving_down:
            new_y = self.y + self.speed
            if self._can_move_to(self.x, new_y):
                self.y = new_y
        if self.moving_left:
            new_x = self.x - self.speed
            if self._can_move_to(new_x, self.y):
                self.x = new_x
        if self.moving_right:
            new_x = self.x + self.speed
            if self._can_move_to(new_x, self.y):
                self.x = new_x

        # Check for POI triggers when entering new grid cell
        if self.tile_map:
            gx, gy = self.get_grid_pos()
            if gx != self.last_grid_x or gy != self.last_grid_y:
                self.last_grid_x = gx
                self.last_grid_y = gy
                poi = self.tile_map.check_poi_collision(gx, gy)
                if poi:
                    triggered_poi = poi

        return triggered_poi

    def _can_move_to(self, px: int, py: int) -> bool:
        """Check if sprite can move to pixel position."""
        if not self.tile_map:
            return True

        # Convert to local (tile map) coordinates
        local_x = px - self.map_offset_x
        local_y = py - self.map_offset_y

        # Check boundaries
        if local_x < 0 or local_y < 0:
            return False
        if local_x + self.size > self.tile_map.pixel_width:
            return False
        if local_y + self.size > self.tile_map.pixel_height:
            return False

        # Check tile collision
        return self.tile_map.can_move_to_pixel(local_x, local_y, self.size)

    def set_grid_position(self, grid_x: int, grid_y: int) -> None:
        """Set sprite position to a grid cell."""
        if self.tile_map:
            px, py = self.tile_map.grid_to_pixel(grid_x, grid_y)
            self.x = self.map_offset_x + px + (self.tile_map.tile_size - self.size) // 2
            self.y = self.map_offset_y + py + (self.tile_map.tile_size - self.size) // 2

    def render(self, surface: pygame.Surface) -> None:
        """Render the sprite as a little adventurer icon."""
        # Draw shadow
        shadow_rect = pygame.Rect(self.x + 1, self.y + 1, self.size, self.size)
        pygame.draw.rect(surface, (20, 15, 10), shadow_rect, border_radius=2)

        # Draw body (main square)
        body_rect = pygame.Rect(self.x, self.y, self.size, self.size)
        pygame.draw.rect(surface, self.color, body_rect, border_radius=2)
        pygame.draw.rect(surface, self.outline_color, body_rect, 1, border_radius=2)

        # Draw a little face/direction indicator (if sprite big enough)
        if self.size >= 12:
            center_x = self.x + self.size // 2
            center_y = self.y + self.size // 2
            eye_color = (50, 30, 20)
            pygame.draw.circle(surface, eye_color, (center_x - 2, center_y - 1), 1)
            pygame.draw.circle(surface, eye_color, (center_x + 2, center_y - 1), 1)


class PygameMVP:
    """
    Main game application.

    Coordinates game state, UI, and game logic.
    """

    def __init__(self, use_api: bool = False, use_ai_narrative: bool = False, auto_play: bool = False):
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

        # Auto-play mode
        self.auto_play = auto_play
        self.auto_play_delay = 1500  # ms between actions
        self.last_auto_action = 0
        self.auto_play_turns = 0
        self.max_auto_turns = 25  # Play for 25 turns then stop

        # Tile map system
        self.current_map_name = "tavern"
        self.tile_maps = {
            "tavern": create_tavern_map(),
            "forest": create_forest_map(),
            "level_1": create_level_1(),
            "level_2": create_level_2(),
            "level_3": create_level_3(),
        }
        self.tile_map = self.tile_maps["tavern"]
        
        # Map connections (where exits lead)
        self.map_connections = {
            "tavern": {"default": ("level_1", 1, 5)},
            "forest": {"Forest Entrance": ("tavern", 9, 7)},
            "level_1": {
                "Village Gate": ("tavern", 9, 7),
                "Forest Trail": ("level_2", 1, 5),
            },
            "level_2": {
                "Cave Entrance": ("level_1", 15, 5),
                "Dark Descent": ("level_3", 1, 5),
            },
            "level_3": {
                "Cavern Entrance": ("level_2", 15, 5),
                "Victory Portal": ("tavern", 9, 5),  # Return to start on victory
            },
        }

        # Map rendering offset (inside the map panel)
        self.map_offset_x = MAP_PANEL_X + PADDING
        self.map_offset_y = MAP_PANEL_Y + 28  # Account for title bar

        # Player sprite for map navigation
        self.player_sprite = PlayerSprite(0, 0, size=10)
        self.player_sprite.set_tile_map(self.tile_map, self.map_offset_x, self.map_offset_y)

        # Start player in a walkable position
        self.player_sprite.set_grid_position(8, 5)  # Center of tavern

        # Hook up POI triggers
        self.tile_map.on_poi_triggered = self._on_poi_triggered

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

    def _on_poi_triggered(self, poi: PointOfInterest) -> None:
        """Handle point of interest events."""
        self.state.log("")
        self.state.log(f"★ {poi.name}")
        self.state.log(poi.description)

        if poi.event_type == "treasure":
            # Scale rewards by level
            if self.current_map_name == "level_3":
                if "Hoard" in poi.name:
                    gold_found = random.randint(100, 200)
                    self.state.log(f"💎 LEGENDARY TREASURE! Found {gold_found} gold!")
                elif "Artifact" in poi.name:
                    gold_found = random.randint(75, 150)
                    self.state.log(f"✨ Ancient artifact worth {gold_found} gold!")
                else:
                    gold_found = random.randint(40, 80)
            elif self.current_map_name == "level_2":
                if "Iron Chest" in poi.name:
                    gold_found = random.randint(25, 50)
                else:
                    gold_found = random.randint(15, 35)
            elif self.current_map_name == "level_1":
                gold_found = random.randint(8, 20)
            else:
                gold_found = random.randint(5, 15)
            
            self.state.inventory.gold += gold_found
            if "LEGENDARY" not in self.state.adventure_log[-1] and "Ancient" not in self.state.adventure_log[-1]:
                self.state.log(f"Found {gold_found} gold!")
            self.tile_map.trigger_poi(poi)

        elif poi.event_type == "encounter":
            self.state.log("")
            self.state.log("*** COMBAT! ***")
            
            # Spawn enemies based on level and POI
            self._spawn_encounter_enemies(poi)
            self.state.start_combat()
            self.tile_map.trigger_poi(poi)

        elif poi.event_type == "story":
            # Story events can have special effects
            if "Healing" in poi.name:
                player = self.state.get_current_player()
                if player:
                    heal = min(10, player.max_hp - player.hp)
                    player.hp += heal
                    if heal > 0:
                        self.state.log(f"The waters heal you for {heal} HP!")
                    else:
                        self.state.log("You feel refreshed!")
            self.tile_map.trigger_poi(poi)

        elif poi.event_type == "exit":
            # Switch maps using connection table
            connections = self.map_connections.get(self.current_map_name, {})
            # Try to find specific connection for this POI
            if poi.name in connections:
                dest_map, dest_x, dest_y = connections[poi.name]
            elif "default" in connections:
                dest_map, dest_x, dest_y = connections["default"]
            else:
                # Fallback
                dest_map, dest_x, dest_y = "tavern", 9, 5
            
            self._switch_map(dest_map, dest_x, dest_y)

        elif poi.event_type == "npc":
            # NPC dialogue - just log for now
            self.tile_map.trigger_poi(poi)

    def _spawn_encounter_enemies(self, poi: PointOfInterest) -> None:
        """Spawn enemies appropriate for the encounter and level."""
        # Enemy templates by level
        if self.current_map_name == "level_1":
            # Easy enemies
            if "Rat" in poi.name:
                self.state.add_enemy("Giant Rat", "Beast", hp=8, max_hp=8, attack=4, defense=1)
            else:
                self.state.add_enemy("Goblin Scout", "Goblin", hp=12, max_hp=12, attack=5, defense=2)
                
        elif self.current_map_name == "level_2":
            # Medium enemies
            if "Chieftain" in poi.name:
                self.state.add_enemy("Goblin Chieftain", "Goblin", hp=35, max_hp=35, attack=10, defense=4)
                self.state.add_enemy("Goblin Bodyguard", "Goblin", hp=18, max_hp=18, attack=7, defense=3)
            elif "Archer" in poi.name:
                self.state.add_enemy("Goblin Archer", "Goblin", hp=14, max_hp=14, attack=8, defense=2)
                self.state.add_enemy("Goblin Archer", "Goblin", hp=14, max_hp=14, attack=8, defense=2)
            else:
                self.state.add_enemy("Goblin Warrior", "Goblin", hp=20, max_hp=20, attack=8, defense=3)
                
        elif self.current_map_name == "level_3":
            # Hard enemies
            if "Vermithrax" in poi.name:
                # THE DRAGON BOSS
                self.state.add_enemy("Vermithrax the Red", "Dragon", hp=100, max_hp=100, attack=18, defense=8)
            elif "Dragonkin" in poi.name:
                self.state.add_enemy("Dragonkin Warrior", "Dragonkin", hp=45, max_hp=45, attack=12, defense=6)
            elif "Cultist" in poi.name:
                self.state.add_enemy("Dragon Cultist", "Human", hp=25, max_hp=25, attack=9, defense=3)
                self.state.add_enemy("Dragon Cultist", "Human", hp=25, max_hp=25, attack=9, defense=3)
                self.state.add_enemy("Cult Leader", "Human", hp=35, max_hp=35, attack=11, defense=4)
            else:
                self.state.add_enemy("Fire Elemental", "Elemental", hp=40, max_hp=40, attack=14, defense=5)
        else:
            # Default/tavern/forest enemies
            if "Goblin Camp" in poi.name:
                self.state.add_enemy("Goblin Raider", "Goblin", hp=18, max_hp=18, attack=7, defense=2)
                self.state.add_enemy("Goblin Raider", "Goblin", hp=18, max_hp=18, attack=7, defense=2)
            else:
                self.state.add_enemy("Ambusher", "Goblin", hp=15, max_hp=15, attack=6, defense=2)

    def _switch_map(self, map_name: str, start_x: int, start_y: int) -> None:
        """Switch to a different map."""
        if map_name in self.tile_maps:
            self.current_map_name = map_name
            self.tile_map = self.tile_maps[map_name]
            self.tile_map.on_poi_triggered = self._on_poi_triggered
            self.player_sprite.set_tile_map(self.tile_map, self.map_offset_x, self.map_offset_y)
            self.player_sprite.set_grid_position(start_x, start_y)
            
            # Reset player grid tracking to avoid immediate POI trigger
            self.player_sprite.last_grid_x = start_x
            self.player_sprite.last_grid_y = start_y
            
            # Update game location
            location_names = {
                "tavern": "Starting Tavern",
                "forest": "Dark Forest",
                "level_1": "Village Outskirts",
                "level_2": "Goblin Caves",
                "level_3": "Dragon's Lair",
            }
            
            # Special messages for levels
            level_messages = {
                "level_1": "🌿 The fresh air of the village outskirts greets you.",
                "level_2": "🕯️ The cave air is damp and smells of goblin.",
                "level_3": "🔥 Intense heat radiates from the volcanic depths!",
            }
            
            self.state.log("")
            self.state.log(f"═══ {location_names.get(map_name, map_name)} ═══")
            if map_name in level_messages:
                self.state.log(level_messages[map_name])
            self.state.location.name = location_names.get(map_name, map_name)

    def _auto_play_tick(self) -> None:
        """AI decision-making for auto-play mode."""
        if not self.auto_play:
            return

        current_time = pygame.time.get_ticks()
        if current_time - self.last_auto_action < self.auto_play_delay:
            return

        self.last_auto_action = current_time
        self.auto_play_turns += 1

        # Check for game over conditions
        if self.state.phase == GamePhase.GAME_OVER:
            self.state.log("")
            self.state.log("═══ AUTO-PLAY COMPLETE ═══")
            self.state.log(f"Game ended after {self.auto_play_turns} turns")
            self.auto_play = False
            return

        if self.auto_play_turns >= self.max_auto_turns:
            self.state.log("")
            self.state.log("═══ AUTO-PLAY COMPLETE ═══")
            self.state.log(f"Reached {self.max_auto_turns} turns. Adventure continues...")
            self.auto_play = False
            return

        # AI Decision Making
        player = self.state.get_current_player()
        alive_players = self.state.get_alive_players()
        alive_enemies = self.state.get_alive_enemies()

        # Priority 1: Heal if HP is critical (below 30%)
        if player and player.hp < player.max_hp * 0.3:
            if player.mana >= 10:
                self.state.log(f"🤖 AI: {player.name} is hurt! Casting heal...")
                self._on_cast_spell()
                return
            elif self.state.inventory.gold >= 10:
                self.state.log(f"🤖 AI: {player.name} uses emergency potion!")
                self._on_use_item()
                return

        # Priority 2: Attack if in combat
        if self.state.phase == GamePhase.COMBAT and alive_enemies:
            action = random.choice(["attack", "attack", "attack", "spell"])  # 75% attack, 25% spell
            if action == "spell" and player and player.mana >= 10 and player.hp < player.max_hp * 0.7:
                self.state.log(f"🤖 AI: Tactical healing mid-combat...")
                self._on_cast_spell()
            else:
                self.state.log(f"🤖 AI: Engaging the enemy!")
                self._on_attack()
            return

        # Priority 3: Start combat if enemies exist
        if alive_enemies and self.state.phase != GamePhase.COMBAT:
            self.state.log(f"🤖 AI: Enemies spotted! Initiating combat...")
            self._on_attack()
            return

        # Priority 4: Explore
        self.state.log(f"🤖 AI: Exploring the area...")
        self._on_next_turn()

    def _on_render(self, surface: pygame.Surface) -> None:
        """Render callback."""
        # Run auto-play AI each frame
        self._auto_play_tick()

        # Update player sprite position and check for POI triggers
        triggered_poi = self.player_sprite.update()
        if triggered_poi:
            self._on_poi_triggered(triggered_poi)

        if self.screen:
            self.screen.render(surface)

        # Render tile map (over the placeholder map image)
        self.tile_map.render(surface, self.map_offset_x, self.map_offset_y)

        # Render player sprite on the map
        self.player_sprite.render(surface)

        # Render FPS and auto-play indicator
        if self.show_fps and self.fps_font and self.loop.clock:
            fps = int(self.loop.clock.get_fps())
            fps_text = self.fps_font.render(f"FPS: {fps}", True, (100, 100, 100))
            surface.blit(fps_text, (SCREEN_WIDTH - 70, 5))

        # Auto-play indicator
        if self.auto_play and self.fps_font:
            auto_text = self.fps_font.render(
                f"🤖 AUTO-PLAY ({self.auto_play_turns}/{self.max_auto_turns})",
                True, (50, 200, 50)
            )
            surface.blit(auto_text, (10, 5))

        # Map name and controls hint
        if self.fps_font:
            map_label = self.fps_font.render(
                f"Map: {self.current_map_name.title()}",
                True, (180, 160, 120)
            )
            surface.blit(map_label, (MAP_PANEL_X + PADDING, MAP_PANEL_Y + MAP_PANEL_HEIGHT - 18))

            hint_text = self.fps_font.render(
                "WASD/Arrows: Move | Walk to glowing spots!",
                True, (100, 90, 70)
            )
            surface.blit(hint_text, (MAP_PANEL_X, MAP_PANEL_Y + MAP_PANEL_HEIGHT + 5))

    def _on_event(self, event: pygame.event.Event) -> None:
        """Handle events."""
        if self.screen:
            self.screen.handle_event(event)

    def _on_key_down(self, event: pygame.event.Event) -> None:
        """Handle key down for sprite movement."""
        self.player_sprite.handle_key_down(event.key)

    def _on_key_up(self, event: pygame.event.Event) -> None:
        """Handle key up for sprite movement."""
        self.player_sprite.handle_key_up(event.key)

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
        self.loop.on_key_down = self._on_key_down
        self.loop.on_key_up = self._on_key_up

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


def run_manager_mode(use_api: bool = False) -> None:
    """Run the lightweight GameManager-driven loop."""
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(f"{GAME_TITLE} (Manager Mode)")

    image_provider = APIImageProvider() if use_api else MockImageProvider()
    manager = GameManager(image_provider, screen)
    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                manager.handle_event(event)

        manager.update()
        manager.render()
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Pygame MVP - D&D Adventure Game")
    parser.add_argument("--use-api", action="store_true", help="Use real API for images")
    parser.add_argument("--use-ai", action="store_true", help="Use AI for narrative generation")
    parser.add_argument("--auto-play", action="store_true", help="AI plays the game automatically")
    parser.add_argument("--turns", type=int, default=25, help="Max turns for auto-play (default: 25)")
    parser.add_argument("--manager-mode", action="store_true", help="Run the new GameManager-driven RPG loop")
    args = parser.parse_args()

    if args.manager_mode:
        print("Starting manager mode (RPG systems + PixelLab integration)...")
        run_manager_mode(use_api=args.use_api)
        return

    mode_str = "🤖 AUTO-PLAY MODE" if args.auto_play else "Manual (Human)"

    print(f"""
╔══════════════════════════════════════════════════════════════╗
║             Pygame MVP - D&D Adventure Game                  ║
╠══════════════════════════════════════════════════════════════╣
║  Image Provider: {"API (Real Images)" if args.use_api else "Mock (Placeholders)":40} ║
║  Narrative:      {"AI-Generated" if args.use_ai else "Fallback Text":40} ║
║  Play Mode:      {mode_str:40} ║
╠══════════════════════════════════════════════════════════════╣
║  Controls:                                                   ║
║    [ARROWS/WASD] - Move sprite on map                        ║
║    [SPACE]       - Next Turn                                 ║
║    [1-4]         - Quick Actions                             ║
║    [ESC]         - Quit                                      ║
║    Mouse         - Click buttons and UI                      ║
╚══════════════════════════════════════════════════════════════╝
    """)

    game = PygameMVP(use_api=args.use_api, use_ai_narrative=args.use_ai, auto_play=args.auto_play)
    if args.auto_play:
        game.max_auto_turns = args.turns
    game.run()


if __name__ == "__main__":
    main()
