"""
Game manager: ties together maps, RPG systems, and image generation.

This is a light coordinator that keeps the loop readable. It is intentionally
minimal and can be expanded with richer UI or state persistence later.
"""

from enum import Enum
import random
from typing import Dict, Optional, Tuple

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
    create_enemy,
)
from pygame_mvp.game.quests import (
    QuestTracker,
    ObjectiveType,
    create_main_story_quests,
    create_side_quests,
)
from pygame_mvp.game.save_system import SaveSystem


class GameState(Enum):
    EXPLORATION = "exploration"
    COMBAT = "combat"


class GameManager:
    """Top-level coordinator for movement, encounters, and rendering."""

    def __init__(self, image_provider, screen: pygame.Surface):
        self.image_provider = image_provider
        self.screen = screen
        self.state = GameState.EXPLORATION

        # Map management
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
        self.current_map: TileMap = self.map_builders[self.current_map_name]()

        # Player setup
        self.player = Player("Hero", CharacterClass.FIGHTER)
        starter = Item("Rusty Sword", ItemType.WEAPON, value=10, damage_min=2, damage_max=5)
        self.player.equip(starter)
        self.player_grid = list(self.current_map.start_pos)

        # Quests & saving
        self.quest_tracker = QuestTracker()
        self._register_default_quests()
        self.save_system = SaveSystem("saves")

        # Encounter state
        self.combat_enemy = None
        self.combat_enemy_sprite: Optional[pygame.Surface] = None
        self.enemy_sprite_cache: Dict[str, pygame.Surface] = {}

        # Simple HUD/log
        self.log_lines = [
            "Welcome to the adventure!",
            "Use arrows/WASD to move.",
            "Walk onto glowing POIs or find encounters.",
        ]

        # Rendering config
        self.map_offset_x = PADDING
        self.map_offset_y = PADDING
        self.hud_font = pygame.font.Font(None, 18)
        self.big_font = pygame.font.Font(None, 28)

    # ------------------------------------------------------------------ #
    # Input & Update
    # ------------------------------------------------------------------ #
    def handle_event(self, event: pygame.event.Event) -> None:
        if self.state == GameState.EXPLORATION:
            self._handle_exploration_event(event)
        elif self.state == GameState.COMBAT:
            self._handle_combat_event(event)

    def update(self) -> None:
        """Placeholder for per-frame updates (e.g., animations/timers)."""
        return

    # ------------------------------------------------------------------ #
    # Exploration
    # ------------------------------------------------------------------ #
    def _handle_exploration_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return

        mods = pygame.key.get_mods()
        if event.key == pygame.K_s and (mods & pygame.KMOD_CTRL):
            self._save_game(slot=1, name="Quick Save")
            return
        if event.key == pygame.K_l and (mods & pygame.KMOD_CTRL):
            self._load_game(slot=1)
            return

        dx, dy = 0, 0
        if event.key in (pygame.K_UP, pygame.K_w):
            dy = -1
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            dy = 1
        elif event.key in (pygame.K_LEFT, pygame.K_a):
            dx = -1
        elif event.key in (pygame.K_RIGHT, pygame.K_d):
            dx = 1

        if dx or dy:
            self._attempt_move(dx, dy)

    def _attempt_move(self, dx: int, dy: int) -> None:
        new_x = self.player_grid[0] + dx
        new_y = self.player_grid[1] + dy

        if not self.current_map.is_walkable(new_x, new_y):
            self._log("You bump into an obstacle.")
            return

        self.player_grid = [new_x, new_y]

        # POI check
        poi = self.current_map.get_poi(new_x, new_y)
        if poi:
            self._handle_poi(poi)
            return

        # Random encounter (if enabled)
        if self.current_map.encounters_enabled and random.random() < 0.1:
            self._trigger_combat(random.choice(["Goblin Scout", "Forest Wolf", "Skeleton"]))

    def _handle_poi(self, poi: PointOfInterest) -> None:
        self._log(poi.name)
        self._log(poi.description)

        if poi.event_type == "treasure":
            gold = random.randint(10, 35)
            self._log(f"You find {gold} gold coins!")
            self.current_map.trigger_poi(poi)
            self._update_quests(ObjectiveType.COLLECT, poi.name)
        elif poi.event_type == "npc":
            self._log("You chat with the local.")
            self.current_map.trigger_poi(poi)
            self._update_quests(ObjectiveType.TALK, poi.name)
        elif poi.event_type == "story":
            self._log("A story moment unfolds.")
            self.current_map.trigger_poi(poi)
            self._update_quests(ObjectiveType.REACH, poi.name)
        elif poi.event_type == "encounter":
            self.current_map.trigger_poi(poi)
            self._trigger_combat(poi.name)
        elif poi.event_type == "exit":
            self._switch_map_for_exit(poi)

    def _switch_map_for_exit(self, poi: PointOfInterest) -> None:
        connections = self.map_connections.get(self.current_map_name, {})
        if poi.name in connections:
            dest_map, dest_x, dest_y = connections[poi.name]
        elif "default" in connections:
            dest_map, dest_x, dest_y = connections["default"]
        else:
            return

        if dest_map in self.map_builders:
            self.current_map_name = dest_map
            self.current_map = self.map_builders[dest_map]()
            self.player_grid = [dest_x, dest_y]
            label = self.map_labels.get(dest_map, dest_map.replace("_", " ").title())
            self._log(f"Traveling to {label}...")
            self._update_quests(ObjectiveType.REACH, label)
        else:
            self._log("The way seems blocked.")

    # ------------------------------------------------------------------ #
    # Combat
    # ------------------------------------------------------------------ #
    def _trigger_combat(self, enemy_name: str) -> None:
        self.state = GameState.COMBAT
        self.combat_enemy = create_enemy(enemy_name, base_hp=18)
        self.combat_enemy_sprite = self._get_enemy_sprite(enemy_name)
        self._log(f"Combat started with {enemy_name}!")

    def _handle_combat_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return

        if event.key == pygame.K_SPACE:
            # Player attacks
            outcome = CombatSystem.calculate_attack(self.player, self.combat_enemy)
            self._log(f"You attack: {outcome['msg']}")

            if self.combat_enemy.current_hp <= 0:
                self._end_combat(victory=True)
                return

            # Enemy attacks back
            retaliation = CombatSystem.calculate_attack(self.combat_enemy, self.player)
            self._log(f"Enemy strikes: {retaliation['msg']}")
            if self.player.current_hp <= 0:
                self._log("You fall in battle... Game Over?")
                self._end_combat(victory=False)

        elif event.key == pygame.K_ESCAPE:
            self._log("You flee the encounter.")
            self._end_combat(victory=False)

    def _get_enemy_sprite(self, enemy_name: str) -> pygame.Surface:
        """Fetch enemy art via the image provider (cached)."""
        cache_key = (enemy_name, 128, 128)
        if cache_key in self.enemy_sprite_cache:
            return self.enemy_sprite_cache[cache_key]

        sprite = self.image_provider.get_character_portrait(enemy_name, "Enemy", 128, 128)
        self.enemy_sprite_cache[cache_key] = sprite
        return sprite

    def _end_combat(self, victory: bool) -> None:
        """Cleanup and quest hooks after combat."""
        if victory:
            self._log("Enemy defeated!")
            if self.combat_enemy:
                self._update_quests(ObjectiveType.KILL, self.combat_enemy.name)
        self.state = GameState.EXPLORATION
        self.combat_enemy = None
        self.combat_enemy_sprite = None

    # ------------------------------------------------------------------ #
    # Rendering
    # ------------------------------------------------------------------ #
    def render(self) -> None:
        self.screen.fill((18, 14, 12))

        if self.state == GameState.EXPLORATION:
            self._render_map()
            self._render_player()
        elif self.state == GameState.COMBAT:
            self._render_combat()

        self._render_hud()

    def _render_map(self) -> None:
        self.current_map.render(self.screen, self.map_offset_x, self.map_offset_y)

    def _render_player(self) -> None:
        tile = self.current_map.tile_size
        px = self.map_offset_x + self.player_grid[0] * tile
        py = self.map_offset_y + self.player_grid[1] * tile

        # Shadow
        pygame.draw.rect(self.screen, (20, 15, 10), (px + 1, py + 1, tile, tile), border_radius=2)
        # Body
        pygame.draw.rect(self.screen, (0, 180, 255), (px, py, tile, tile), border_radius=2)

    def _render_combat(self) -> None:
        # Simple combat frame
        frame_rect = pygame.Rect(PADDING, PADDING, SCREEN_WIDTH - PADDING * 2, SCREEN_HEIGHT - PADDING * 2)
        pygame.draw.rect(self.screen, (30, 10, 10), frame_rect)

        if self.combat_enemy_sprite:
            rect = self.combat_enemy_sprite.get_rect(center=frame_rect.center)
            self.screen.blit(self.combat_enemy_sprite, rect)

        # Enemy name/HP
        if self.combat_enemy:
            text = self.big_font.render(
                f"{self.combat_enemy.name} HP: {self.combat_enemy.current_hp}",
                True,
                (240, 210, 190),
            )
            self.screen.blit(text, (frame_rect.centerx - text.get_width() // 2, frame_rect.top + 10))

        # Player HP
        player_text = self.hud_font.render(
            f"Player HP: {self.player.current_hp}/{self.player.max_hp}", True, (200, 220, 200)
        )
        self.screen.blit(player_text, (frame_rect.left + 10, frame_rect.bottom - 30))

        tip_text = self.hud_font.render("[SPACE] Attack | [ESC] Flee", True, (180, 170, 140))
        self.screen.blit(tip_text, (frame_rect.left + 10, frame_rect.bottom - 50))

    def _render_hud(self) -> None:
        # Map label
        map_name = self.map_labels.get(self.current_map_name, self.current_map_name)
        map_label = self.hud_font.render(f"Map: {map_name}", True, (200, 180, 140))
        self.screen.blit(map_label, (PADDING, SCREEN_HEIGHT - 80))

        # Active quests (top 2)
        active = self.quest_tracker.get_active_quests()[:2]
        yq = SCREEN_HEIGHT - 130
        if active:
            quest_label = self.hud_font.render("Quests:", True, (200, 200, 160))
            self.screen.blit(quest_label, (PADDING, yq))
            yq += 18
            for quest in active:
                progress = f"{quest.name} ({int(quest.progress_percent)}%)"
                qt = self.hud_font.render(progress, True, (210, 210, 200))
                self.screen.blit(qt, (PADDING, yq))
                yq += 16

        # Log
        y = SCREEN_HEIGHT - 60
        for line in self.log_lines[-4:]:
            text = self.hud_font.render(line, True, (220, 220, 220))
            self.screen.blit(text, (PADDING, y))
            y += 18

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #
    def _register_default_quests(self) -> None:
        """Load and start initial quests."""
        for quest in create_main_story_quests() + create_side_quests():
            self.quest_tracker.register_quest(quest)
        # Auto-start a couple for visibility
        self.quest_tracker.start_quest("main_01")
        self.quest_tracker.start_quest("side_01")
        self._log("Quests tracked. Check HUD for progress.")

    def _save_game(self, slot: int, name: str) -> None:
        """Persist minimal manager state."""
        data = {
            "map": self.current_map_name,
            "player_grid": self.player_grid,
            "player": self._serialize_player(self.player),
            "quests": self.quest_tracker.to_dict(),
        }
        meta = {
            "player_name": self.player.name,
            "player_level": getattr(self.player, "level", 1),
            "location": self.current_map_name,
            "playtime_seconds": 0,
            "turn_count": 0,
        }
        ok = self.save_system.save_game(slot=slot, save_name=name, game_data=data, metadata=meta)
        self._log("Game saved." if ok else "Save failed.")

    def _load_game(self, slot: int) -> None:
        """Load manager state if available."""
        save = self.save_system.load_game(slot)
        if not save:
            self._log("No save found.")
            return
        try:
            data = save.get("game_data", {})
            player_data = data.get("player")
            if player_data:
                self.player = self._deserialize_player(player_data)
            self.current_map_name = data.get("map", self.current_map_name)
            if self.current_map_name in self.map_builders:
                self.current_map = self.map_builders[self.current_map_name]()
            self.player_grid = data.get("player_grid", self.player_grid)
            quests_state = data.get("quests")
            if quests_state:
                self.quest_tracker.from_dict(quests_state)
            self._log("Game loaded.")
        except Exception as exc:
            self._log(f"Failed to load save: {exc}")

    def _serialize_player(self, player: Player) -> dict:
        """Flatten player data for saving."""
        return {
            "name": player.name,
            "class": player.char_class.value,
            "level": player.level,
            "hp": player.current_hp,
            "max_hp": player.max_hp,
            "xp": getattr(player, "xp", 0),
            "inventory": [
                {
                    "name": item.name,
                    "item_type": item.item_type.value,
                    "value": item.value,
                    "damage_min": item.damage_min,
                    "damage_max": item.damage_max,
                    "stats_bonus": {
                        "str": item.stats_bonus.strength,
                        "dex": item.stats_bonus.dexterity,
                        "int": item.stats_bonus.intelligence,
                        "con": item.stats_bonus.constitution,
                    },
                }
                for item in player.inventory
            ],
            "equipment": {
                slot: {
                    "name": itm.name,
                    "item_type": itm.item_type.value,
                    "value": itm.value,
                    "damage_min": itm.damage_min,
                    "damage_max": itm.damage_max,
                }
                if itm
                else None
                for slot, itm in player.equipment.items()
            },
        }

    def _deserialize_player(self, data: dict) -> Player:
        """Rebuild player from saved data."""
        cls_val = data.get("class", CharacterClass.FIGHTER.value)
        try:
            char_class = CharacterClass(cls_val)
        except ValueError:
            char_class = CharacterClass.FIGHTER
        player = Player(data.get("name", "Hero"), char_class)
        player.level = data.get("level", 1)
        player.current_hp = data.get("hp", player.max_hp)
        player.max_hp = data.get("max_hp", player.max_hp)
        player.xp = data.get("xp", 0)

        # Inventory
        player.inventory = []
        for item_data in data.get("inventory", []):
            itm = Item(
                name=item_data.get("name", "Item"),
                item_type=ItemType(item_data.get("item_type", ItemType.WEAPON.value)),
                value=item_data.get("value", 0),
                damage_min=item_data.get("damage_min", 0),
                damage_max=item_data.get("damage_max", 0),
            )
            player.inventory.append(itm)

        # Equipment
        for slot, item_data in data.get("equipment", {}).items():
            if item_data:
                itm = Item(
                    name=item_data.get("name", "Item"),
                    item_type=ItemType(item_data.get("item_type", ItemType.WEAPON.value)),
                    value=item_data.get("value", 0),
                    damage_min=item_data.get("damage_min", 0),
                    damage_max=item_data.get("damage_max", 0),
                )
                player.equipment[slot] = itm

        return player

    def _update_quests(self, objective_type: ObjectiveType, target: str, count: int = 1) -> None:
        """Update quest objectives and handle completions."""
        completed = self.quest_tracker.update_objectives(objective_type, target, count)
        for quest, obj in completed:
            self._log(f"Objective complete: {obj.description}")

        # Check for quest completions
        for quest in list(self.quest_tracker.get_active_quests()):
            if quest.is_complete:
                rewards = self.quest_tracker.complete_quest(quest.id)
                self._log(f"Quest complete: {quest.name}")
                if rewards:
                    self._log(f"Rewards: {rewards.xp} XP, {rewards.gold} gold")

    def _log(self, message: str) -> None:
        self.log_lines.append(message)
