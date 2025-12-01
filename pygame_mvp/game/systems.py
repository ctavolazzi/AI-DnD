"""
Core RPG systems: stats, items, characters, and basic combat math.

This module is intentionally UI-agnostic. It defines the numerical rules
that higher-level managers and renderers can consume.
"""

import random
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class CharacterClass(Enum):
    FIGHTER = "Fighter"
    WIZARD = "Wizard"
    ROGUE = "Rogue"
    CLERIC = "Cleric"


class ItemType(Enum):
    WEAPON = "Weapon"
    ARMOR = "Armor"
    POTION = "Potion"


@dataclass
class Stats:
    """Base attribute block."""

    strength: int = 10
    dexterity: int = 10
    intelligence: int = 10
    constitution: int = 10

    def __add__(self, other: "Stats") -> "Stats":
        return Stats(
            self.strength + other.strength,
            self.dexterity + other.dexterity,
            self.intelligence + other.intelligence,
            self.constitution + other.constitution,
        )

    @classmethod
    def zero(cls) -> "Stats":
        """Create a Stats object with all zeros (useful for bonuses)."""
        return cls(0, 0, 0, 0)

    @classmethod
    def bonus(cls, strength: int = 0, dexterity: int = 0,
              intelligence: int = 0, constitution: int = 0) -> "Stats":
        """Create a bonus Stats object (defaults to 0 instead of 10)."""
        return cls(strength, dexterity, intelligence, constitution)


@dataclass
class Item:
    """Generic item with optional stat and combat bonuses."""

    name: str
    item_type: ItemType
    value: int
    stats_bonus: Stats = field(default_factory=Stats)
    damage_min: int = 0
    damage_max: int = 0
    description: str = ""


class Character:
    """Base character model used by both players and simple enemies."""

    def __init__(self, name: str, level: int = 1, max_hp: int = 20):
        self.name = name
        self.level = level
        self.base_stats = Stats()
        self._max_hp = max_hp
        self._current_hp = max_hp
        self.inventory: List[Item] = []
        self.equipment: Dict[str, Optional[Item]] = {"weapon": None, "armor": None}

    @property
    def max_hp(self) -> int:
        return self._max_hp

    @max_hp.setter
    def max_hp(self, value: int) -> None:
        """Clamp max HP to a minimum of 1 and keep current HP in range."""
        self._max_hp = max(1, value)
        self._current_hp = min(self._current_hp, self._max_hp)

    @property
    def current_hp(self) -> int:
        return self._current_hp

    @current_hp.setter
    def current_hp(self, value: int) -> None:
        """Clamp HP between 0 and max_hp."""
        self._current_hp = max(0, min(value, self._max_hp))

    def equip(self, item: Item) -> None:
        """Equip a weapon or armor, replacing the current item in that slot."""
        if item.item_type == ItemType.WEAPON:
            self.equipment["weapon"] = item
        elif item.item_type == ItemType.ARMOR:
            self.equipment["armor"] = item

    @property
    def total_stats(self) -> Stats:
        """Aggregate base stats with equipment bonuses."""
        total = Stats(
            self.base_stats.strength,
            self.base_stats.dexterity,
            self.base_stats.intelligence,
            self.base_stats.constitution,
        )
        for item in self.equipment.values():
            if item:
                total += item.stats_bonus
        return total


CLASS_BASE_STATS = {
    CharacterClass.FIGHTER: {"stats": Stats(14, 10, 8, 12), "hp": 30},
    CharacterClass.WIZARD: {"stats": Stats(6, 10, 16, 8), "hp": 18},
    CharacterClass.ROGUE: {"stats": Stats(10, 14, 10, 10), "hp": 24},
    CharacterClass.CLERIC: {"stats": Stats(10, 8, 14, 12), "hp": 26},
}


class Player(Character):
    """Player character with class-specific baselines."""

    def __init__(self, name: str, char_class: CharacterClass):
        super().__init__(name)
        self.char_class = char_class
        self.xp: int = 0

        # Class baselines (data-driven)
        cfg = CLASS_BASE_STATS.get(char_class, {"stats": Stats(), "hp": 20})
        self.base_stats = cfg["stats"]
        self.max_hp = cfg["hp"]
        self.current_hp = self.max_hp


class CombatSystem:
    """Lightweight combat math for turn-based encounters."""

    @staticmethod
    def calculate_attack(attacker: Character, defender: Character) -> Dict[str, object]:
        """
        Resolve a single attack roll.

        Returns:
            dict with keys: damage (int), hit (bool), crit (bool), msg (str)
        """
        result = {"damage": 0, "hit": False, "crit": False, "msg": "Missed!"}

        # 1) Hit chance (dexterity-driven)
        hit_chance = 80 + attacker.total_stats.dexterity * 2 - defender.total_stats.dexterity
        if random.randint(1, 100) > max(5, min(95, hit_chance)):
            return result

        # 2) Base damage (weapon + strength)
        weapon = attacker.equipment.get("weapon")
        base_dmg = random.randint(weapon.damage_min, weapon.damage_max) if weapon else 1
        bonus = attacker.total_stats.strength // 3
        total = base_dmg + bonus

        # 3) Crit chance
        crit_chance = 5 + attacker.total_stats.dexterity // 5
        if random.randint(1, 100) <= crit_chance:
            total = int(total * 1.5)
            result["crit"] = True

        # 4) Apply damage
        defender.current_hp -= total
        result.update({"damage": total, "hit": True, "msg": f"Hit for {total}!"})
        if result["crit"]:
            result["msg"] += " (Crit!)"
        return result


def create_enemy(name: str, base_hp: int = 15) -> Character:
    """Convenience helper to create a simple enemy using the Character model."""
    enemy = Character(name)
    enemy.current_hp = base_hp
    enemy.max_hp = base_hp
    enemy.base_stats = Stats(10, 10, 8, 10)
    return enemy
