"""
Centralized Game State Manager

Single source of truth for all game state.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class GamePhase(Enum):
    """Current phase of the game."""
    MENU = "menu"
    EXPLORATION = "exploration"
    COMBAT = "combat"
    DIALOGUE = "dialogue"
    INVENTORY = "inventory"
    GAME_OVER = "game_over"


@dataclass
class CharacterState:
    """State for a single character."""
    name: str
    char_class: str
    hp: int
    max_hp: int
    mana: int
    max_mana: int
    attack: int
    defense: int
    alive: bool = True
    team: str = "players"
    status_effects: List[str] = field(default_factory=list)
    ability_scores: Dict[str, int] = field(default_factory=dict)

    @property
    def hp_percent(self) -> float:
        return self.hp / self.max_hp if self.max_hp > 0 else 0

    @property
    def mana_percent(self) -> float:
        return self.mana / self.max_mana if self.max_mana > 0 else 0


@dataclass
class InventoryState:
    """State for inventory."""
    items: Dict[str, int] = field(default_factory=dict)  # item_id: quantity
    equipped: Dict[str, str] = field(default_factory=dict)  # slot: item_id
    gold: int = 0
    capacity: int = 20


@dataclass
class QuestState:
    """State for current quest."""
    title: str = "No Active Quest"
    description: str = ""
    objectives: List[Dict[str, Any]] = field(default_factory=list)
    completed: bool = False


@dataclass
class LocationState:
    """State for current location."""
    name: str = "Starting Tavern"
    description: str = "A cozy tavern where adventurers gather."
    available_exits: List[str] = field(default_factory=list)
    npcs: List[str] = field(default_factory=list)
    items: List[str] = field(default_factory=list)


class GameState:
    """
    Centralized game state manager.

    All game state flows through this class. UI components read from here,
    and game logic writes updates here.
    """

    def __init__(self):
        # Game phase
        self.phase: GamePhase = GamePhase.EXPLORATION
        self.turn_count: int = 0
        self.scene_counter: int = 0

        # Characters
        self.players: List[CharacterState] = []
        self.enemies: List[CharacterState] = []
        self.current_player_index: int = 0

        # World state
        self.location: LocationState = LocationState()
        self.visited_locations: List[str] = ["Starting Tavern"]

        # Quest state
        self.quest: QuestState = QuestState()

        # Inventory (party shared)
        self.inventory: InventoryState = InventoryState()

        # Adventure log
        self.adventure_log: List[str] = []
        self.max_log_entries: int = 100

        # UI state
        self.selected_panel: Optional[str] = None
        self.selected_item_index: Optional[int] = None
        self.hovered_button: Optional[str] = None

        # Combat state
        self.combat_queue: List[CharacterState] = []
        self.current_combatant_index: int = 0

    # =========================================================================
    # Character Management
    # =========================================================================

    def add_player(self, name: str, char_class: str, **kwargs) -> CharacterState:
        """Add a player character."""
        player = CharacterState(
            name=name,
            char_class=char_class,
            hp=kwargs.get("hp", 30),
            max_hp=kwargs.get("max_hp", 30),
            mana=kwargs.get("mana", 50),
            max_mana=kwargs.get("max_mana", 50),
            attack=kwargs.get("attack", 10),
            defense=kwargs.get("defense", 5),
            team="players",
            ability_scores=kwargs.get("ability_scores", {
                "STR": 10, "DEX": 10, "CON": 10,
                "INT": 10, "WIS": 10, "CHA": 10
            })
        )
        self.players.append(player)
        return player

    def add_enemy(self, name: str, char_class: str, **kwargs) -> CharacterState:
        """Add an enemy character."""
        enemy = CharacterState(
            name=name,
            char_class=char_class,
            hp=kwargs.get("hp", 20),
            max_hp=kwargs.get("max_hp", 20),
            mana=kwargs.get("mana", 0),
            max_mana=kwargs.get("max_mana", 0),
            attack=kwargs.get("attack", 8),
            defense=kwargs.get("defense", 3),
            team="enemies"
        )
        self.enemies.append(enemy)
        return enemy

    def get_current_player(self) -> Optional[CharacterState]:
        """Get the currently active player."""
        if self.players and 0 <= self.current_player_index < len(self.players):
            return self.players[self.current_player_index]
        return None

    def get_alive_players(self) -> List[CharacterState]:
        """Get all alive players."""
        return [p for p in self.players if p.alive]

    def get_alive_enemies(self) -> List[CharacterState]:
        """Get all alive enemies."""
        return [e for e in self.enemies if e.alive]

    # =========================================================================
    # Adventure Log
    # =========================================================================

    def log(self, message: str) -> None:
        """Add a message to the adventure log."""
        self.adventure_log.append(message)
        if len(self.adventure_log) > self.max_log_entries:
            self.adventure_log.pop(0)

    def get_recent_log(self, count: int = 10) -> List[str]:
        """Get recent log entries."""
        return self.adventure_log[-count:] if self.adventure_log else []

    # =========================================================================
    # Inventory
    # =========================================================================

    def add_item(self, item_id: str, quantity: int = 1) -> bool:
        """Add item to inventory."""
        if item_id == "gold_coin":
            self.inventory.gold += quantity
            return True

        current = self.inventory.items.get(item_id, 0)
        self.inventory.items[item_id] = current + quantity
        return True

    def remove_item(self, item_id: str, quantity: int = 1) -> bool:
        """Remove item from inventory."""
        if item_id == "gold_coin":
            if self.inventory.gold >= quantity:
                self.inventory.gold -= quantity
                return True
            return False

        current = self.inventory.items.get(item_id, 0)
        if current >= quantity:
            self.inventory.items[item_id] = current - quantity
            if self.inventory.items[item_id] <= 0:
                del self.inventory.items[item_id]
            return True
        return False

    # =========================================================================
    # Game Flow
    # =========================================================================

    def advance_turn(self) -> None:
        """Advance to the next turn."""
        self.turn_count += 1
        self.scene_counter += 1

    def start_combat(self) -> None:
        """Enter combat phase."""
        self.phase = GamePhase.COMBAT
        # Build combat queue from all alive characters
        self.combat_queue = self.get_alive_players() + self.get_alive_enemies()
        self.current_combatant_index = 0

    def end_combat(self) -> None:
        """Exit combat phase."""
        self.phase = GamePhase.EXPLORATION
        self.combat_queue = []
        self.current_combatant_index = 0

    def is_game_over(self) -> bool:
        """Check if game is over."""
        return not any(p.alive for p in self.players)

    def is_victory(self) -> bool:
        """Check if players won (all enemies dead)."""
        return self.enemies and not any(e.alive for e in self.enemies)

    # =========================================================================
    # Location
    # =========================================================================

    def set_location(self, name: str, description: str = "", **kwargs) -> None:
        """Set current location."""
        self.location = LocationState(
            name=name,
            description=description,
            available_exits=kwargs.get("exits", []),
            npcs=kwargs.get("npcs", []),
            items=kwargs.get("items", [])
        )
        if name not in self.visited_locations:
            self.visited_locations.append(name)

    # =========================================================================
    # Serialization
    # =========================================================================

    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary for saving."""
        return {
            "phase": self.phase.value,
            "turn_count": self.turn_count,
            "scene_counter": self.scene_counter,
            "players": [
                {
                    "name": p.name,
                    "char_class": p.char_class,
                    "hp": p.hp,
                    "max_hp": p.max_hp,
                    "mana": p.mana,
                    "max_mana": p.max_mana,
                    "attack": p.attack,
                    "defense": p.defense,
                    "alive": p.alive,
                    "ability_scores": p.ability_scores
                }
                for p in self.players
            ],
            "enemies": [
                {
                    "name": e.name,
                    "char_class": e.char_class,
                    "hp": e.hp,
                    "max_hp": e.max_hp,
                    "attack": e.attack,
                    "defense": e.defense,
                    "alive": e.alive
                }
                for e in self.enemies
            ],
            "location": {
                "name": self.location.name,
                "description": self.location.description
            },
            "inventory": {
                "items": self.inventory.items,
                "gold": self.inventory.gold
            },
            "adventure_log": self.adventure_log[-50:],  # Save last 50 entries
            "quest": {
                "title": self.quest.title,
                "description": self.quest.description,
                "completed": self.quest.completed
            }
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GameState":
        """Create state from dictionary."""
        state = cls()

        state.phase = GamePhase(data.get("phase", "exploration"))
        state.turn_count = data.get("turn_count", 0)
        state.scene_counter = data.get("scene_counter", 0)

        for p_data in data.get("players", []):
            state.add_player(
                p_data["name"],
                p_data["char_class"],
                hp=p_data.get("hp", 30),
                max_hp=p_data.get("max_hp", 30),
                mana=p_data.get("mana", 50),
                max_mana=p_data.get("max_mana", 50),
                attack=p_data.get("attack", 10),
                defense=p_data.get("defense", 5),
                ability_scores=p_data.get("ability_scores", {})
            )

        for e_data in data.get("enemies", []):
            state.add_enemy(
                e_data["name"],
                e_data["char_class"],
                hp=e_data.get("hp", 20),
                max_hp=e_data.get("max_hp", 20),
                attack=e_data.get("attack", 8),
                defense=e_data.get("defense", 3)
            )

        loc_data = data.get("location", {})
        state.set_location(
            loc_data.get("name", "Starting Tavern"),
            loc_data.get("description", "")
        )

        inv_data = data.get("inventory", {})
        state.inventory.items = inv_data.get("items", {})
        state.inventory.gold = inv_data.get("gold", 0)

        state.adventure_log = data.get("adventure_log", [])

        quest_data = data.get("quest", {})
        state.quest.title = quest_data.get("title", "No Active Quest")
        state.quest.description = quest_data.get("description", "")
        state.quest.completed = quest_data.get("completed", False)

        return state

