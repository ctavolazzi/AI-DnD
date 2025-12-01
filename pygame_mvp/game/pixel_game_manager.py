"""
Pixel Game Manager - Integrated with Nano Banana Games-style UI

This is the "brain transplant" version that uses the new Pixel UI components
instead of the old UIManager.

Features:
- PixelGameHUD for HP/MP bars and minimap
- PixelInventoryScreen for full inventory management
- PixelDialogueBox for NPC conversations
- Full integration with existing RPG systems (combat, quests, save/load)
"""

from enum import Enum
import random
from typing import Dict, Optional, Tuple, List

import pygame

from pygame_mvp.config import SCREEN_WIDTH, SCREEN_HEIGHT, PADDING
from pygame_mvp.game.tile_map import (
    TileMap,
    PointOfInterest,
    create_tavern_map,
    create_forest_map,
    create_level_1,
    create_level_2,
    create_level_3,
)
from pygame_mvp.game.systems import (
    Player,
    CharacterClass,
    CombatSystem,
    Item,
    ItemType,
    Stats,
    create_enemy,
)
from pygame_mvp.game.quests import (
    QuestTracker,
    ObjectiveType,
    create_main_story_quests,
    create_side_quests,
)
from pygame_mvp.game.save_system import SaveSystem

# New Pixel UI components
from pygame_mvp.ui.pixel_hud import PixelGameHUD
from pygame_mvp.ui.pixel_inventory import PixelInventoryScreen
from pygame_mvp.ui.pixel_dialogue import PixelDialogueBox, DialogueSequence
from pygame_mvp.ui.pixel_theme import get_pixel_theme


class GamePhase(Enum):
    EXPLORATION = "exploration"
    COMBAT = "combat"
    DIALOGUE = "dialogue"


class PixelGameManager:
    """
    Top-level game coordinator with Pixel UI integration.
    
    Manages:
    - Map navigation and rendering
    - Player movement and collision
    - Combat encounters
    - Quest tracking
    - Save/Load system
    - All Pixel UI overlays (HUD, Inventory, Dialogue)
    """

    def __init__(self, screen: pygame.Surface, image_provider=None):
        self.screen = screen
        self.image_provider = image_provider
        self.theme = get_pixel_theme()
        self.phase = GamePhase.EXPLORATION
        
        # --- Map Management ---
        self.map_builders: Dict[str, callable] = {
            "tavern": create_tavern_map,
            "forest": create_forest_map,
            "level_1": create_level_1,
            "level_2": create_level_2,
            "level_3": create_level_3,
        }
        self.map_labels: Dict[str, str] = {
            "tavern": "Starting Tavern",
            "forest": "Dark Forest",
            "level_1": "Village Outskirts",
            "level_2": "Goblin Caves",
            "level_3": "Dragon's Lair",
        }
        self.map_connections: Dict[str, Dict[str, Tuple[str, int, int]]] = {
            "tavern": {"default": ("level_1", 1, 5)},
            "forest": {"Forest Entrance": ("tavern", 8, 5)},
            "level_1": {
                "Village Gate": ("tavern", 8, 5),
                "Forest Trail": ("level_2", 1, 5),
            },
            "level_2": {
                "Cave Entrance": ("level_1", 15, 5),
                "Dark Descent": ("level_3", 1, 5),
            },
            "level_3": {
                "Cavern Entrance": ("level_2", 15, 5),
                "Victory Portal": ("tavern", 8, 5),
            },
        }
        
        self.current_map_name = "tavern"
        self.current_map: Optional[TileMap] = None
        
        # --- Player ---
        self.player: Optional[Player] = None
        self.player_grid: List[int] = [8, 5]
        
        # --- Quest & Save Systems ---
        self.quest_tracker = QuestTracker()
        self.save_system = SaveSystem("saves")
        
        # --- Combat State ---
        self.combat_enemy: Optional[object] = None
        self.enemy_sprite_cache: Dict[str, pygame.Surface] = {}
        
        # --- Game Log ---
        self.log_lines: List[str] = []
        
        # --- Fonts ---
        pygame.font.init()
        self.hud_font = pygame.font.Font(None, 20)
        self.big_font = pygame.font.Font(None, 32)
        
        # --- Pixel UI Components ---
        self.hud = PixelGameHUD(screen)
        self.inventory_screen = PixelInventoryScreen(screen)
        self.dialogue_box = PixelDialogueBox(screen)
        self.dialogue_sequence: Optional[DialogueSequence] = None
        
        # Wire inventory callbacks
        self.inventory_screen.on_item_use = self._on_item_use
        self.inventory_screen.on_close = self._close_inventory
        
        # --- Map rendering config ---
        self.map_offset_x = 50
        self.map_offset_y = 80
        self.tile_size = 32

    # ========================================================================
    # GAME INITIALIZATION
    # ========================================================================
    
    def start_new_game(self, player_name: str = "Hero", 
                       player_class: CharacterClass = CharacterClass.FIGHTER) -> None:
        """Initialize a new game with fresh state."""
        self._log("Starting new adventure...")
        
        # Create player
        self.player = Player(player_name, player_class)
        self.player.gold = random.randint(20, 50)
        
        # Give starting equipment
        starter_weapon = Item(
            "Rusty Sword", ItemType.WEAPON, value=10,
            damage_min=2, damage_max=5,
            description="A well-worn blade. Still sharp enough."
        )
        self.player.equip(starter_weapon)
        
        # Add starting items
        self.player.inventory = [
            Item("Health Potion", ItemType.POTION, value=50,
                 description="Restores 30 HP. Tastes like cherries."),
            Item("Mana Potion", ItemType.POTION, value=50,
                 description="Restores 20 MP. Glows faintly blue."),
        ]
        
        # Initialize map
        self.current_map_name = "tavern"
        self.current_map = self.map_builders[self.current_map_name]()
        self.player_grid = list(self.current_map.start_pos)
        
        # Setup quests
        self._register_default_quests()
        
        # Initialize HUD
        self._sync_hud()
        
        # Start with welcome dialogue
        self._trigger_welcome_dialogue()
        
        self._log(f"Welcome, {player_name} the {player_class.value}!")
        self._log("Use WASD or arrows to move. [I] for inventory.")

    def load_game(self, slot: int = 1) -> bool:
        """Load game from save slot."""
        save_data = self.save_system.load_game(slot)
        if not save_data:
            self._log("No save found in slot.")
            return False
        
        try:
            data = save_data.get("game_data", {})
            
            # Restore player
            player_data = data.get("player")
            if player_data:
                self.player = self._deserialize_player(player_data)
            
            # Restore map
            self.current_map_name = data.get("map", "tavern")
            if self.current_map_name in self.map_builders:
                self.current_map = self.map_builders[self.current_map_name]()
            
            self.player_grid = data.get("player_grid", [8, 5])
            
            # Restore quests
            quests_state = data.get("quests")
            if quests_state:
                self.quest_tracker.from_dict(quests_state)
            
            self._sync_hud()
            self._log("Game loaded successfully!")
            return True
            
        except Exception as e:
            self._log(f"Failed to load: {e}")
            return False

    # ========================================================================
    # INPUT HANDLING
    # ========================================================================
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle input events with priority system.
        
        Priority order:
        1. Dialogue (blocks all input when active)
        2. Inventory overlay
        3. Combat controls
        4. Exploration controls
        """
        # 1. Dialogue has highest priority
        if self.dialogue_box.visible:
            return self.dialogue_box.handle_event(event)
        
        # 2. Inventory overlay
        if self.inventory_screen.visible:
            if self.inventory_screen.handle_event(event):
                return True
            # Check for close key
            if event.type == pygame.KEYDOWN and event.key == pygame.K_i:
                self._close_inventory()
                return True
            return False
        
        # 3. Handle by phase
        if event.type == pygame.KEYDOWN:
            # Global shortcuts
            if event.key == pygame.K_i:
                self._open_inventory()
                return True
            
            # Quick save/load
            mods = pygame.key.get_mods()
            if event.key == pygame.K_s and (mods & pygame.KMOD_CTRL):
                self._save_game(slot=1, name="Quick Save")
                return True
            if event.key == pygame.K_l and (mods & pygame.KMOD_CTRL):
                self.load_game(slot=1)
                return True
            
            # Phase-specific controls
            if self.phase == GamePhase.COMBAT:
                return self._handle_combat_input(event)
            else:
                return self._handle_exploration_input(event)
        
        return False

    def _handle_exploration_input(self, event: pygame.event.Event) -> bool:
        """Handle movement and interaction in exploration mode."""
        if event.type != pygame.KEYDOWN:
            return False
        
        dx, dy = 0, 0
        if event.key in (pygame.K_UP, pygame.K_w):
            dy = -1
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            dy = 1
        elif event.key in (pygame.K_LEFT, pygame.K_a):
            dx = -1
        elif event.key in (pygame.K_RIGHT, pygame.K_d):
            dx = 1
        elif event.key == pygame.K_t:
            # Debug: trigger test dialogue
            self._trigger_test_dialogue()
            return True
        
        if dx or dy:
            self._attempt_move(dx, dy)
            return True
        
        return False

    def _handle_combat_input(self, event: pygame.event.Event) -> bool:
        """Handle combat controls."""
        if event.type != pygame.KEYDOWN:
            return False
        
        if event.key == pygame.K_SPACE:
            self._player_attack()
            return True
        elif event.key == pygame.K_ESCAPE:
            self._flee_combat()
            return True
        
        return False

    # ========================================================================
    # UPDATE LOOP
    # ========================================================================
    
    def update(self) -> None:
        """Update game state each frame."""
        # Update dialogue animation
        if self.dialogue_box.visible:
            self.dialogue_box.update()
        
        # Update HUD animations (HP/MP bar smoothing)
        self.hud.update()
        
        # Sync HUD values
        if self.player:
            self.hud.set_hp(self.player.current_hp, self.player.max_hp)
            self.hud.set_mp(self.player.current_mana, self.player.max_mana)
            self.hud.set_player_pos(*self.player_grid)

    # ========================================================================
    # RENDERING
    # ========================================================================
    
    def render(self) -> None:
        """Render the complete game screen."""
        # 1. Background
        self.screen.fill((20, 18, 15))
        
        # 2. Render based on phase
        if self.phase == GamePhase.COMBAT:
            self._render_combat()
        else:
            self._render_exploration()
        
        # 3. HUD (always visible)
        self.hud.render()
        
        # 4. Game log (bottom)
        self._render_log()
        
        # 5. Overlays
        if self.inventory_screen.visible:
            self.inventory_screen.render()
        
        if self.dialogue_box.visible:
            self.dialogue_box.render()

    def _render_exploration(self) -> None:
        """Render the exploration/map view."""
        if not self.current_map:
            return
        
        # Render tile map
        self._render_map()
        
        # Render player
        self._render_player()
        
        # Map label
        map_name = self.map_labels.get(self.current_map_name, self.current_map_name)
        label = self.hud_font.render(f"Location: {map_name}", True, (200, 180, 140))
        self.screen.blit(label, (PADDING, SCREEN_HEIGHT - 100))

    def _render_map(self) -> None:
        """Render the tile map."""
        if not self.current_map:
            return
        
        # Get tile data for minimap
        tiles = []
        for y in range(self.current_map.height):
            row = []
            for x in range(self.current_map.width):
                tile = self.current_map.get_tile(x, y)
                row.append(0 if tile and tile.walkable else 1)
            tiles.append(row)
        
        self.hud.set_map_tiles(tiles, self.current_map.width, self.current_map.height)
        
        # Render visible tiles
        for y in range(self.current_map.height):
            for x in range(self.current_map.width):
                tile = self.current_map.get_tile(x, y)
                if not tile:
                    continue
                
                screen_x = self.map_offset_x + x * self.tile_size
                screen_y = self.map_offset_y + y * self.tile_size
                
                # Skip if off screen
                if screen_x < -self.tile_size or screen_x > SCREEN_WIDTH + self.tile_size:
                    continue
                if screen_y < -self.tile_size or screen_y > SCREEN_HEIGHT + self.tile_size:
                    continue
                
                # Tile color
                if not tile.walkable:
                    color = (60, 55, 50)  # Wall
                else:
                    color = (180, 160, 100) if (x + y) % 2 == 0 else (170, 150, 90)
                
                pygame.draw.rect(self.screen, color,
                               (screen_x, screen_y, self.tile_size - 1, self.tile_size - 1))
                
                # Stone texture for walls
                if not tile.walkable:
                    pygame.draw.rect(self.screen, (50, 45, 40),
                                   (screen_x, screen_y, self.tile_size - 1, self.tile_size - 1), 2)
        
        # Render POIs
        for poi in self.current_map.pois:
            if poi.triggered:
                continue
            screen_x = self.map_offset_x + poi.x * self.tile_size + self.tile_size // 2
            screen_y = self.map_offset_y + poi.y * self.tile_size + self.tile_size // 2
            
            # Glowing indicator
            color = (255, 215, 0) if poi.event_type == "treasure" else (100, 200, 255)
            pygame.draw.circle(self.screen, color, (screen_x, screen_y), 6)
            pygame.draw.circle(self.screen, (255, 255, 255), (screen_x, screen_y), 3)

    def _render_player(self) -> None:
        """Render the player character sprite."""
        px, py = self.player_grid
        screen_x = self.map_offset_x + px * self.tile_size + self.tile_size // 2
        screen_y = self.map_offset_y + py * self.tile_size + self.tile_size // 2
        
        # Body
        pygame.draw.rect(self.screen, (70, 140, 170),
                        (screen_x - 10, screen_y - 6, 20, 24), border_radius=3)
        
        # Head
        pygame.draw.circle(self.screen, (230, 190, 150), (screen_x, screen_y - 14), 10)
        
        # Hair
        pygame.draw.ellipse(self.screen, (100, 70, 40),
                          (screen_x - 10, screen_y - 26, 20, 14))
        
        # Sword
        pygame.draw.rect(self.screen, (180, 180, 200),
                        (screen_x + 10, screen_y - 12, 5, 20))
        pygame.draw.rect(self.screen, (139, 90, 43),
                        (screen_x + 8, screen_y + 6, 9, 4))

    def _render_combat(self) -> None:
        """Render the combat screen."""
        # Combat background
        combat_rect = pygame.Rect(50, 80, SCREEN_WIDTH - 100, SCREEN_HEIGHT - 200)
        pygame.draw.rect(self.screen, (30, 15, 15), combat_rect, border_radius=8)
        pygame.draw.rect(self.screen, (139, 90, 43), combat_rect, 3, border_radius=8)
        
        # Enemy info
        if self.combat_enemy:
            # Enemy name
            name_text = self.big_font.render(self.combat_enemy.name, True, (255, 200, 100))
            self.screen.blit(name_text, (combat_rect.centerx - name_text.get_width() // 2, 
                                        combat_rect.top + 20))
            
            # Enemy HP bar
            hp_pct = self.combat_enemy.current_hp / self.combat_enemy.max_hp
            bar_width = 200
            bar_x = combat_rect.centerx - bar_width // 2
            bar_y = combat_rect.top + 60
            
            pygame.draw.rect(self.screen, (60, 20, 20), (bar_x, bar_y, bar_width, 20), border_radius=3)
            pygame.draw.rect(self.screen, (200, 60, 60), 
                           (bar_x, bar_y, int(bar_width * hp_pct), 20), border_radius=3)
            
            hp_text = self.hud_font.render(f"HP: {self.combat_enemy.current_hp}/{self.combat_enemy.max_hp}",
                                          True, (255, 255, 255))
            self.screen.blit(hp_text, (bar_x + bar_width // 2 - hp_text.get_width() // 2, bar_y + 2))
            
            # Simple enemy sprite placeholder
            enemy_center = (combat_rect.centerx, combat_rect.centery)
            pygame.draw.circle(self.screen, (100, 150, 80), enemy_center, 40)
            pygame.draw.circle(self.screen, (60, 90, 50), enemy_center, 40, 3)
            
            # Eyes
            pygame.draw.circle(self.screen, (200, 50, 50), 
                             (enemy_center[0] - 12, enemy_center[1] - 10), 6)
            pygame.draw.circle(self.screen, (200, 50, 50), 
                             (enemy_center[0] + 12, enemy_center[1] - 10), 6)
        
        # Combat controls hint
        hint = self.hud_font.render("[SPACE] Attack  |  [ESC] Flee", True, (180, 170, 140))
        self.screen.blit(hint, (combat_rect.centerx - hint.get_width() // 2, 
                               combat_rect.bottom - 40))

    def _render_log(self) -> None:
        """Render the game log at bottom of screen."""
        y = SCREEN_HEIGHT - 80
        for line in self.log_lines[-3:]:
            text = self.hud_font.render(line, True, (200, 190, 170))
            self.screen.blit(text, (PADDING, y))
            y += 22

    # ========================================================================
    # MOVEMENT & MAP
    # ========================================================================
    
    def _attempt_move(self, dx: int, dy: int) -> None:
        """Attempt to move player by delta."""
        if not self.current_map:
            return
        
        new_x = self.player_grid[0] + dx
        new_y = self.player_grid[1] + dy
        
        # Check walkability
        if not self.current_map.is_walkable(new_x, new_y):
            return
        
        self.player_grid = [new_x, new_y]
        
        # Check for POI
        poi = self.current_map.get_poi(new_x, new_y)
        if poi and not poi.triggered:
            self._handle_poi(poi)
            return
        
        # Random encounter chance
        if random.random() < 0.08:
            enemies = ["Goblin Scout", "Forest Wolf", "Skeleton Warrior"]
            self._start_combat(random.choice(enemies))

    def _handle_poi(self, poi: PointOfInterest) -> None:
        """Handle stepping on a Point of Interest."""
        self._log(f"★ {poi.name}")
        
        if poi.event_type == "treasure":
            gold = random.randint(15, 50)
            self.player.gold += gold
            self._log(f"Found {gold} gold!")
            self.current_map.trigger_poi(poi)
            self._update_quests(ObjectiveType.COLLECT, poi.name)
            
        elif poi.event_type == "npc":
            self._trigger_npc_dialogue(poi.name, poi.description)
            self.current_map.trigger_poi(poi)
            self._update_quests(ObjectiveType.TALK, poi.name)
            
        elif poi.event_type == "encounter":
            self.current_map.trigger_poi(poi)
            self._start_combat(poi.name)
            
        elif poi.event_type == "exit":
            self._handle_exit(poi)

    def _handle_exit(self, poi: PointOfInterest) -> None:
        """Handle map transition."""
        connections = self.map_connections.get(self.current_map_name, {})
        
        if poi.name in connections:
            dest_map, dest_x, dest_y = connections[poi.name]
        elif "default" in connections:
            dest_map, dest_x, dest_y = connections["default"]
        else:
            self._log("The path is blocked.")
            return
        
        if dest_map in self.map_builders:
            self.current_map_name = dest_map
            self.current_map = self.map_builders[dest_map]()
            self.player_grid = [dest_x, dest_y]
            
            label = self.map_labels.get(dest_map, dest_map)
            self._log(f"Traveling to {label}...")
            self._update_quests(ObjectiveType.REACH, label)

    # ========================================================================
    # COMBAT
    # ========================================================================
    
    def _start_combat(self, enemy_name: str) -> None:
        """Start a combat encounter."""
        self.phase = GamePhase.COMBAT
        self.combat_enemy = create_enemy(enemy_name, base_hp=random.randint(12, 25))
        self._log(f"⚔️ Combat with {enemy_name}!")

    def _player_attack(self) -> None:
        """Player attacks the enemy."""
        if not self.combat_enemy or not self.player:
            return
        
        result = CombatSystem.calculate_attack(self.player, self.combat_enemy)
        self._log(f"You attack: {result['msg']}")
        
        if self.combat_enemy.current_hp <= 0:
            self._end_combat(victory=True)
            return
        
        # Enemy counterattack
        retaliation = CombatSystem.calculate_attack(self.combat_enemy, self.player)
        self._log(f"Enemy strikes: {retaliation['msg']}")
        
        if self.player.current_hp <= 0:
            self._log("You have been defeated...")
            self._end_combat(victory=False)

    def _flee_combat(self) -> None:
        """Attempt to flee from combat."""
        if random.random() < 0.6:  # 60% flee chance
            self._log("You escaped!")
            self._end_combat(victory=False)
        else:
            self._log("Couldn't escape!")
            # Enemy gets a free attack
            if self.combat_enemy and self.player:
                result = CombatSystem.calculate_attack(self.combat_enemy, self.player)
                self._log(f"Enemy attacks as you flee: {result['msg']}")

    def _end_combat(self, victory: bool) -> None:
        """End combat and return to exploration."""
        if victory and self.combat_enemy:
            xp_gain = random.randint(10, 25)
            gold_gain = random.randint(5, 20)
            self.player.xp += xp_gain
            self.player.gold += gold_gain
            self._log(f"Victory! +{xp_gain} XP, +{gold_gain} gold")
            self._update_quests(ObjectiveType.KILL, self.combat_enemy.name)
        
        self.phase = GamePhase.EXPLORATION
        self.combat_enemy = None

    # ========================================================================
    # INVENTORY & ITEMS
    # ========================================================================
    
    def _open_inventory(self) -> None:
        """Open the inventory screen."""
        if self.player:
            self.inventory_screen.set_player(self.player)
        self.inventory_screen.show()

    def _close_inventory(self) -> None:
        """Close the inventory screen."""
        self.inventory_screen.hide()

    def _on_item_use(self, item: Item) -> None:
        """Handle using an item from inventory."""
        if not self.player:
            return
        
        if item.item_type == ItemType.POTION:
            if "Health" in item.name:
                heal = 30
                old_hp = self.player.current_hp
                self.player.current_hp += heal
                actual_heal = self.player.current_hp - old_hp
                self._log(f"Used {item.name}! +{actual_heal} HP")
                
            elif "Mana" in item.name:
                restore = 20
                old_mana = self.player.current_mana
                self.player.current_mana += restore
                actual_restore = self.player.current_mana - old_mana
                self._log(f"Used {item.name}! +{actual_restore} MP")
            
            # Remove item from inventory
            if item in self.player.inventory:
                self.player.inventory.remove(item)
                self.inventory_screen.set_player(self.player)

    # ========================================================================
    # DIALOGUE
    # ========================================================================
    
    def _trigger_welcome_dialogue(self) -> None:
        """Show welcome dialogue sequence."""
        self.dialogue_sequence = DialogueSequence(self.dialogue_box)
        self.dialogue_sequence.add_line(
            "TAVERN KEEPER",
            "Welcome, adventurer! Rest here before your journey.",
            portrait_color=(139, 90, 43)
        )
        self.dialogue_sequence.add_line(
            "TAVERN KEEPER",
            "The village needs someone brave to clear the goblin caves.",
            portrait_color=(139, 90, 43)
        )
        self.dialogue_sequence.start()

    def _trigger_npc_dialogue(self, npc_name: str, description: str) -> None:
        """Trigger dialogue for an NPC."""
        self.dialogue_sequence = DialogueSequence(self.dialogue_box)
        self.dialogue_sequence.add_line(
            npc_name.upper(),
            f'"{description}"',
            portrait_color=(100, 100, 180)
        )
        self.dialogue_sequence.start()

    def _trigger_test_dialogue(self) -> None:
        """Debug: trigger test dialogue."""
        self.dialogue_sequence = DialogueSequence(self.dialogue_box)
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
        self.dialogue_sequence.start()

    # ========================================================================
    # QUESTS
    # ========================================================================
    
    def _register_default_quests(self) -> None:
        """Register starting quests."""
        for quest in create_main_story_quests() + create_side_quests():
            self.quest_tracker.register_quest(quest)
        
        self.quest_tracker.start_quest("main_01")
        self.quest_tracker.start_quest("side_01")

    def _update_quests(self, objective_type: ObjectiveType, target: str, count: int = 1) -> None:
        """Update quest progress."""
        completed = self.quest_tracker.update_objectives(objective_type, target, count)
        
        for quest, obj in completed:
            self._log(f"✓ {obj.description}")
        
        # Check for completed quests
        for quest in list(self.quest_tracker.get_active_quests()):
            if quest.is_complete:
                rewards = self.quest_tracker.complete_quest(quest.id)
                self._log(f"🎉 Quest complete: {quest.name}")
                if rewards:
                    self._log(f"Rewards: {rewards.xp} XP, {rewards.gold} gold")
                    if self.player:
                        self.player.xp += rewards.xp
                        self.player.gold += rewards.gold

    # ========================================================================
    # SAVE/LOAD
    # ========================================================================
    
    def _save_game(self, slot: int, name: str) -> None:
        """Save current game state."""
        if not self.player:
            self._log("Nothing to save!")
            return
        
        data = {
            "map": self.current_map_name,
            "player_grid": self.player_grid,
            "player": self._serialize_player(self.player),
            "quests": self.quest_tracker.to_dict(),
        }
        meta = {
            "player_name": self.player.name,
            "player_level": self.player.level,
            "location": self.current_map_name,
            "playtime_seconds": 0,
            "turn_count": 0,
        }
        
        success = self.save_system.save_game(slot=slot, save_name=name, 
                                            game_data=data, metadata=meta)
        self._log("Game saved!" if success else "Save failed.")

    def _serialize_player(self, player: Player) -> dict:
        """Convert player to saveable dict."""
        return {
            "name": player.name,
            "class": player.char_class.value,
            "level": player.level,
            "hp": player.current_hp,
            "max_hp": player.max_hp,
            "mana": player.current_mana,
            "max_mana": player.max_mana,
            "xp": player.xp,
            "gold": player.gold,
            "inventory": [
                {
                    "name": item.name,
                    "item_type": item.item_type.value,
                    "value": item.value,
                    "damage_min": item.damage_min,
                    "damage_max": item.damage_max,
                    "description": item.description,
                }
                for item in player.inventory
            ],
        }

    def _deserialize_player(self, data: dict) -> Player:
        """Rebuild player from save data."""
        try:
            char_class = CharacterClass(data.get("class", "Fighter"))
        except ValueError:
            char_class = CharacterClass.FIGHTER
        
        player = Player(data.get("name", "Hero"), char_class)
        player.level = data.get("level", 1)
        player.current_hp = data.get("hp", player.max_hp)
        player.max_hp = data.get("max_hp", player.max_hp)
        player.current_mana = data.get("mana", player.max_mana)
        player.max_mana = data.get("max_mana", player.max_mana)
        player.xp = data.get("xp", 0)
        player.gold = data.get("gold", 0)
        
        # Rebuild inventory
        player.inventory = []
        for item_data in data.get("inventory", []):
            item = Item(
                name=item_data.get("name", "Item"),
                item_type=ItemType(item_data.get("item_type", "Potion")),
                value=item_data.get("value", 0),
                damage_min=item_data.get("damage_min", 0),
                damage_max=item_data.get("damage_max", 0),
                description=item_data.get("description", ""),
            )
            player.inventory.append(item)
        
        return player

    # ========================================================================
    # HELPERS
    # ========================================================================
    
    def _sync_hud(self) -> None:
        """Sync HUD with current player state."""
        if not self.player:
            return
        
        self.hud.set_hp(self.player.current_hp, self.player.max_hp)
        self.hud.set_mp(self.player.current_mana, self.player.max_mana)
        self.hud.set_player_pos(*self.player_grid)

    def _log(self, message: str) -> None:
        """Add a message to the game log."""
        self.log_lines.append(message)
        # Keep log manageable
        if len(self.log_lines) > 50:
            self.log_lines = self.log_lines[-30:]

