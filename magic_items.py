"""
Diablo 2-Style Magic Item System
Supports affixes, rarity tiers, sockets, gems, runes, set items, and unique items.
"""

import random
from typing import Dict, List, Optional, Any
from enum import Enum
from items import Item, ItemType


class ItemRarity(Enum):
    """Item rarity tiers (Diablo 2 style)."""
    COMMON = ("Common", "white", 1.0)
    MAGIC = ("Magic", "blue", 0.3)
    RARE = ("Rare", "yellow", 0.1)
    SET = ("Set", "green", 0.05)
    UNIQUE = ("Unique", "gold", 0.03)
    LEGENDARY = ("Legendary", "orange", 0.01)

    def __init__(self, display_name, color, drop_chance):
        self.display_name = display_name
        self.color = color
        self.drop_chance = drop_chance


class StatType(Enum):
    """Types of stat modifiers."""
    # Primary stats
    STRENGTH = "strength"
    DEXTERITY = "dexterity"
    CONSTITUTION = "constitution"
    INTELLIGENCE = "intelligence"
    WISDOM = "wisdom"
    CHARISMA = "charisma"

    # Combat stats
    ATTACK = "attack"
    DEFENSE = "defense"
    DAMAGE = "damage"
    CRIT_CHANCE = "crit_chance"
    CRIT_DAMAGE = "crit_damage"

    # Resistances
    FIRE_RES = "fire_resistance"
    ICE_RES = "ice_resistance"
    LIGHTNING_RES = "lightning_resistance"
    POISON_RES = "poison_resistance"

    # Other
    MAX_HP = "max_hp"
    MAX_MANA = "max_mana"
    HP_REGEN = "hp_regen"
    MANA_REGEN = "mana_regen"
    SPEED = "speed"
    MAGIC_FIND = "magic_find"


class Affix:
    """Represents a prefix or suffix that can modify an item."""

    def __init__(
        self,
        affix_id: str,
        name: str,
        is_prefix: bool,
        min_level: int,
        stats: Dict[StatType, tuple]  # StatType: (min, max)
    ):
        self.affix_id = affix_id
        self.name = name
        self.is_prefix = is_prefix
        self.min_level = min_level
        self.stats = stats

    def roll_stats(self) -> Dict[StatType, int]:
        """Roll random values for this affix's stats."""
        rolled = {}
        for stat_type, (min_val, max_val) in self.stats.items():
            rolled[stat_type] = random.randint(min_val, max_val)
        return rolled


# ============================================================================
# AFFIX DEFINITIONS
# ============================================================================

# PREFIXES (appear before item name)
PREFIXES = [
    # Damage/Attack prefixes
    Affix("sharp", "Sharp", True, 1, {StatType.ATTACK: (1, 3)}),
    Affix("deadly", "Deadly", True, 5, {StatType.ATTACK: (4, 6), StatType.CRIT_CHANCE: (5, 10)}),
    Affix("vicious", "Vicious", True, 10, {StatType.ATTACK: (7, 10), StatType.DAMAGE: (2, 4)}),
    Affix("savage", "Savage", True, 15, {StatType.ATTACK: (11, 15), StatType.CRIT_DAMAGE: (20, 30)}),

    # Defense prefixes
    Affix("sturdy", "Sturdy", True, 1, {StatType.DEFENSE: (1, 3)}),
    Affix("reinforced", "Reinforced", True, 5, {StatType.DEFENSE: (4, 7)}),
    Affix("fortified", "Fortified", True, 10, {StatType.DEFENSE: (8, 12)}),
    Affix("impenetrable", "Impenetrable", True, 15, {StatType.DEFENSE: (13, 18)}),

    # Elemental damage prefixes
    Affix("flaming", "Flaming", True, 3, {StatType.DAMAGE: (2, 5)}),
    Affix("freezing", "Freezing", True, 3, {StatType.DAMAGE: (2, 5)}),
    Affix("shocking", "Shocking", True, 3, {StatType.DAMAGE: (2, 5)}),
    Affix("infernal", "Infernal", True, 10, {StatType.DAMAGE: (6, 10), StatType.FIRE_RES: (10, 20)}),
    Affix("arctic", "Arctic", True, 10, {StatType.DAMAGE: (6, 10), StatType.ICE_RES: (10, 20)}),
    Affix("voltaic", "Voltaic", True, 10, {StatType.DAMAGE: (6, 10), StatType.LIGHTNING_RES: (10, 20)}),

    # Stat prefixes
    Affix("strong", "Strong", True, 1, {StatType.STRENGTH: (1, 3)}),
    Affix("agile", "Agile", True, 1, {StatType.DEXTERITY: (1, 3)}),
    Affix("wise", "Wise", True, 1, {StatType.WISDOM: (1, 3)}),
    Affix("brilliant", "Brilliant", True, 1, {StatType.INTELLIGENCE: (1, 3)}),
    Affix("mighty", "Mighty", True, 5, {StatType.STRENGTH: (4, 7), StatType.MAX_HP: (10, 20)}),
    Affix("nimble", "Nimble", True, 5, {StatType.DEXTERITY: (4, 7), StatType.SPEED: (5, 10)}),
]

# SUFFIXES (appear after item name)
SUFFIXES = [
    # Resistance suffixes
    Affix("of_fire", "of Fire", False, 3, {StatType.FIRE_RES: (10, 20)}),
    Affix("of_ice", "of Ice", False, 3, {StatType.ICE_RES: (10, 20)}),
    Affix("of_lightning", "of Lightning", False, 3, {StatType.LIGHTNING_RES: (10, 20)}),
    Affix("of_warding", "of Warding", False, 8, {
        StatType.FIRE_RES: (5, 10),
        StatType.ICE_RES: (5, 10),
        StatType.LIGHTNING_RES: (5, 10)
    }),

    # Combat suffixes
    Affix("of_power", "of Power", False, 5, {StatType.ATTACK: (3, 6)}),
    Affix("of_protection", "of Protection", False, 5, {StatType.DEFENSE: (3, 6)}),
    Affix("of_might", "of Might", False, 10, {StatType.STRENGTH: (5, 10), StatType.ATTACK: (3, 5)}),
    Affix("of_precision", "of Precision", False, 10, {StatType.DEXTERITY: (5, 10), StatType.CRIT_CHANCE: (10, 15)}),

    # HP/Mana suffixes
    Affix("of_life", "of Life", False, 1, {StatType.MAX_HP: (10, 20)}),
    Affix("of_mana", "of Mana", False, 1, {StatType.MAX_MANA: (10, 20)}),
    Affix("of_vitality", "of Vitality", False, 5, {StatType.MAX_HP: (21, 40), StatType.HP_REGEN: (1, 2)}),
    Affix("of_energy", "of Energy", False, 5, {StatType.MAX_MANA: (21, 40), StatType.MANA_REGEN: (1, 2)}),

    # Stat suffixes
    Affix("of_the_bear", "of the Bear", False, 8, {StatType.STRENGTH: (5, 10)}),
    Affix("of_the_falcon", "of the Falcon", False, 8, {StatType.DEXTERITY: (5, 10)}),
    Affix("of_the_wolf", "of the Wolf", False, 8, {StatType.CONSTITUTION: (5, 10)}),
    Affix("of_the_sage", "of the Sage", False, 8, {StatType.INTELLIGENCE: (5, 10)}),

    # Special suffixes
    Affix("of_fortune", "of Fortune", False, 12, {StatType.MAGIC_FIND: (10, 25)}),
    Affix("of_greed", "of Greed", False, 10, {StatType.MAGIC_FIND: (5, 15)}),
]


# ============================================================================
# GEMS AND RUNES
# ============================================================================

class Gem:
    """Represents a gem that can be socketed into items."""

    def __init__(self, gem_id: str, name: str, tier: int, stats: Dict[StatType, int]):
        self.gem_id = gem_id
        self.name = name
        self.tier = tier  # 1-5 (Chipped, Flawed, Normal, Flawless, Perfect)
        self.stats = stats


GEMS = {
    # Ruby - Fire damage and fire resistance
    "ruby_1": Gem("ruby_1", "Chipped Ruby", 1, {StatType.FIRE_RES: 5, StatType.DAMAGE: 1}),
    "ruby_2": Gem("ruby_2", "Flawed Ruby", 2, {StatType.FIRE_RES: 8, StatType.DAMAGE: 2}),
    "ruby_3": Gem("ruby_3", "Ruby", 3, {StatType.FIRE_RES: 12, StatType.DAMAGE: 3}),
    "ruby_4": Gem("ruby_4", "Flawless Ruby", 4, {StatType.FIRE_RES: 17, StatType.DAMAGE: 5}),
    "ruby_5": Gem("ruby_5", "Perfect Ruby", 5, {StatType.FIRE_RES: 25, StatType.DAMAGE: 8}),

    # Sapphire - Ice resistance and mana
    "sapphire_1": Gem("sapphire_1", "Chipped Sapphire", 1, {StatType.ICE_RES: 5, StatType.MAX_MANA: 10}),
    "sapphire_3": Gem("sapphire_3", "Sapphire", 3, {StatType.ICE_RES: 12, StatType.MAX_MANA: 30}),
    "sapphire_5": Gem("sapphire_5", "Perfect Sapphire", 5, {StatType.ICE_RES: 25, StatType.MAX_MANA: 60}),

    # Topaz - Lightning resistance and magic find
    "topaz_1": Gem("topaz_1", "Chipped Topaz", 1, {StatType.LIGHTNING_RES: 5, StatType.MAGIC_FIND: 2}),
    "topaz_3": Gem("topaz_3", "Topaz", 3, {StatType.LIGHTNING_RES: 12, StatType.MAGIC_FIND: 8}),
    "topaz_5": Gem("topaz_5", "Perfect Topaz", 5, {StatType.LIGHTNING_RES: 25, StatType.MAGIC_FIND: 15}),

    # Emerald - Defense and poison resistance
    "emerald_1": Gem("emerald_1", "Chipped Emerald", 1, {StatType.DEFENSE: 2, StatType.POISON_RES: 5}),
    "emerald_3": Gem("emerald_3", "Emerald", 3, {StatType.DEFENSE: 6, StatType.POISON_RES: 12}),
    "emerald_5": Gem("emerald_5", "Perfect Emerald", 5, {StatType.DEFENSE: 12, StatType.POISON_RES: 25}),

    # Diamond - All resistances
    "diamond_1": Gem("diamond_1", "Chipped Diamond", 1, {
        StatType.FIRE_RES: 3, StatType.ICE_RES: 3, StatType.LIGHTNING_RES: 3, StatType.POISON_RES: 3
    }),
    "diamond_5": Gem("diamond_5", "Perfect Diamond", 5, {
        StatType.FIRE_RES: 12, StatType.ICE_RES: 12, StatType.LIGHTNING_RES: 12, StatType.POISON_RES: 12
    }),

    # Skull - Life and mana leech
    "skull_1": Gem("skull_1", "Chipped Skull", 1, {StatType.MAX_HP: 10}),
    "skull_3": Gem("skull_3", "Skull", 3, {StatType.MAX_HP: 30}),
    "skull_5": Gem("skull_5", "Perfect Skull", 5, {StatType.MAX_HP: 60}),
}


class Rune:
    """Represents a rune that can be socketed or used in runewords."""

    def __init__(self, rune_id: str, name: str, level: int, stats: Dict[StatType, int]):
        self.rune_id = rune_id
        self.name = name
        self.level = level  # 1-33 like Diablo 2
        self.stats = stats


RUNES = {
    # Low level runes
    "el": Rune("el", "El Rune", 1, {StatType.ATTACK: 1, StatType.DEFENSE: 1}),
    "eld": Rune("eld", "Eld Rune", 2, {StatType.SPEED: 5}),
    "tir": Rune("tir", "Tir Rune", 3, {StatType.MANA_REGEN: 2}),
    "nef": Rune("nef", "Nef Rune", 4, {StatType.DEFENSE: 3}),

    # Mid level runes
    "eth": Rune("eth", "Eth Rune", 5, {StatType.MANA_REGEN: 3}),
    "ith": Rune("ith", "Ith Rune", 6, {StatType.DAMAGE: 3}),
    "tal": Rune("tal", "Tal Rune", 7, {StatType.POISON_RES: 15}),
    "ral": Rune("ral", "Ral Rune", 8, {StatType.FIRE_RES: 15}),
    "ort": Rune("ort", "Ort Rune", 9, {StatType.LIGHTNING_RES: 15}),
    "thul": Rune("thul", "Thul Rune", 10, {StatType.ICE_RES: 15}),

    # Higher level runes
    "shael": Rune("shael", "Shael Rune", 13, {StatType.SPEED: 20}),
    "pul": Rune("pul", "Pul Rune", 21, {StatType.MAGIC_FIND: 25}),
    "um": Rune("um", "Um Rune", 22, {StatType.FIRE_RES: 22, StatType.ICE_RES: 22, StatType.LIGHTNING_RES: 22}),
    "ist": Rune("ist", "Ist Rune", 24, {StatType.MAGIC_FIND: 40}),
    "ber": Rune("ber", "Ber Rune", 30, {StatType.DAMAGE: 20}),
    "jah": Rune("jah", "Jah Rune", 31, {StatType.MAX_HP: 100}),
    "cham": Rune("cham", "Cham Rune", 32, {StatType.MAGIC_FIND: 50}),
    "zod": Rune("zod", "Zod Rune", 33, {StatType.DEFENSE: 30}),
}


# ============================================================================
# SET ITEMS
# ============================================================================

class SetItem:
    """An item that belongs to a set."""

    def __init__(
        self,
        item_id: str,
        set_id: str,
        name: str,
        slot: str,
        base_stats: Dict[StatType, int],
        set_bonuses: Dict[int, Dict[StatType, int]]  # pieces_worn: stats
    ):
        self.item_id = item_id
        self.set_id = set_id
        self.name = name
        self.slot = slot
        self.base_stats = base_stats
        self.set_bonuses = set_bonuses


# Example: "Sigon's Complete Steel" set (warrior set)
SIGONS_SET = {
    "sigons_helm": SetItem(
        "sigons_helm",
        "sigons",
        "Sigon's Visor",
        "head",
        {StatType.DEFENSE: 15, StatType.ATTACK: 5},
        {}
    ),
    "sigons_armor": SetItem(
        "sigons_armor",
        "sigons",
        "Sigon's Shelter",
        "armor",
        {StatType.DEFENSE: 25, StatType.MAX_HP: 40},
        {2: {StatType.DEFENSE: 10}}  # 2-piece bonus
    ),
    "sigons_weapon": SetItem(
        "sigons_weapon",
        "sigons",
        "Sigon's Gage",
        "weapon",
        {StatType.ATTACK: 12, StatType.DAMAGE: 5},
        {
            2: {StatType.ATTACK: 5},  # 2-piece bonus
            3: {StatType.ATTACK: 10, StatType.MAX_HP: 50}  # Full set bonus
        }
    ),
}

# Example: "Tancred's Battlegear" set (offensive set)
TANCREDS_SET = {
    "tancreds_helm": SetItem(
        "tancreds_helm",
        "tancreds",
        "Tancred's Skull",
        "head",
        {StatType.DEFENSE: 10, StatType.ATTACK: 8},
        {}
    ),
    "tancreds_armor": SetItem(
        "tancreds_armor",
        "tancreds",
        "Tancred's Spine",
        "armor",
        {StatType.DEFENSE: 20, StatType.FIRE_RES: 15},
        {2: {StatType.DAMAGE: 5}}
    ),
    "tancreds_boots": SetItem(
        "tancreds_boots",
        "tancreds",
        "Tancred's Hobnails",
        "feet",
        {StatType.DEFENSE: 8, StatType.SPEED: 10},
        {
            2: {StatType.SPEED: 10},
            3: {StatType.ATTACK: 15, StatType.CRIT_CHANCE: 10}
        }
    ),
}

ALL_SET_ITEMS = {**SIGONS_SET, **TANCREDS_SET}


# ============================================================================
# UNIQUE ITEMS
# ============================================================================

class UniqueItem:
    """A unique item with fixed properties."""

    def __init__(
        self,
        item_id: str,
        name: str,
        slot: str,
        level_req: int,
        stats: Dict[StatType, int],
        special: str = ""
    ):
        self.item_id = item_id
        self.name = name
        self.slot = slot
        self.level_req = level_req
        self.stats = stats
        self.special = special


UNIQUE_ITEMS = {
    # Unique weapons
    "the_reaper": UniqueItem(
        "the_reaper",
        "The Reaper's Toll",
        "weapon",
        15,
        {
            StatType.ATTACK: 25,
            StatType.DAMAGE: 15,
            StatType.CRIT_CHANCE: 20,
            StatType.STRENGTH: 10
        },
        "Slain enemies rest in pieces"
    ),
    "windforce": UniqueItem(
        "windforce",
        "Windforce",
        "weapon",
        20,
        {
            StatType.ATTACK: 30,
            StatType.DAMAGE: 20,
            StatType.DEXTERITY: 15,
            StatType.CRIT_DAMAGE: 50
        },
        "Knockback on hit"
    ),

    # Unique armor
    "shako": UniqueItem(
        "shako",
        "Harlequin Crest",
        "head",
        15,
        {
            StatType.MAX_HP: 100,
            StatType.MAX_MANA: 100,
            StatType.DEFENSE: 20,
            StatType.MAGIC_FIND: 50
        },
        "The jester's crown"
    ),
    "enigma": UniqueItem(
        "enigma",
        "Enigma",
        "armor",
        25,
        {
            StatType.DEFENSE: 40,
            StatType.STRENGTH: 20,
            StatType.MAX_HP: 80,
            StatType.MAGIC_FIND: 30,
            StatType.SPEED: 30
        },
        "Grants teleportation"
    ),
    "skulders": UniqueItem(
        "skulders",
        "Skullder's Ire",
        "armor",
        18,
        {
            StatType.DEFENSE: 35,
            StatType.MAGIC_FIND: 100,
            StatType.MAX_HP: 60
        },
        "For the greedy adventurer"
    ),
}


# ============================================================================
# MAGIC ITEM GENERATOR
# ============================================================================

class MagicItemGenerator:
    """Generates magic items with affixes."""

    @staticmethod
    def generate_magic_item(base_item_id: str, item_level: int) -> Dict[str, Any]:
        """
        Generate a magic item with 1-2 affixes.

        Args:
            base_item_id: The base item to enhance
            item_level: Level of the item (affects affix quality)

        Returns:
            Dict with item data including affixes and stats
        """
        # Select affixes
        available_prefixes = [p for p in PREFIXES if p.min_level <= item_level]
        available_suffixes = [s for s in SUFFIXES if s.min_level <= item_level]

        num_affixes = random.choices([1, 2], weights=[0.6, 0.4])[0]

        prefix = random.choice(available_prefixes) if num_affixes >= 1 and random.random() < 0.5 else None
        suffix = random.choice(available_suffixes) if num_affixes >= 1 else None

        # Ensure we have at least one affix
        if not prefix and not suffix:
            if random.random() < 0.5 and available_prefixes:
                prefix = random.choice(available_prefixes)
            elif available_suffixes:
                suffix = random.choice(available_suffixes)

        # Build name
        name_parts = []
        if prefix:
            name_parts.append(prefix.name)
        name_parts.append(base_item_id.replace("_", " ").title())
        if suffix:
            name_parts.append(suffix.name)

        item_name = " ".join(name_parts)

        # Roll stats
        stats = {}
        if prefix:
            stats.update(prefix.roll_stats())
        if suffix:
            suffix_stats = suffix.roll_stats()
            for stat_type, value in suffix_stats.items():
                stats[stat_type] = stats.get(stat_type, 0) + value

        return {
            "item_id": f"magic_{base_item_id}_{random.randint(1000, 9999)}",
            "name": item_name,
            "rarity": ItemRarity.MAGIC,
            "base_item": base_item_id,
            "prefix": prefix.affix_id if prefix else None,
            "suffix": suffix.affix_id if suffix else None,
            "stats": {k.value: v for k, v in stats.items()},
            "sockets": 0
        }

    @staticmethod
    def generate_rare_item(base_item_id: str, item_level: int) -> Dict[str, Any]:
        """Generate a rare item with 3-6 affixes."""
        available_prefixes = [p for p in PREFIXES if p.min_level <= item_level]
        available_suffixes = [s for s in SUFFIXES if s.min_level <= item_level]

        # Rare items have 2-3 prefixes and 1-3 suffixes
        num_prefixes = random.randint(1, min(3, len(available_prefixes)))
        num_suffixes = random.randint(1, min(3, len(available_suffixes)))

        prefixes = random.sample(available_prefixes, num_prefixes)
        suffixes = random.sample(available_suffixes, num_suffixes)

        # Generate a unique rare name (not just prefix + base + suffix)
        rare_first_names = ["Doom", "Grim", "Soul", "Death", "Shadow", "Blood", "Storm", "Plague"]
        rare_last_names = ["Reaver", "Bringer", "Seeker", "Render", "Splitter", "Cleaver", "Slayer"]

        item_name = f"{random.choice(rare_first_names)} {random.choice(rare_last_names)}"

        # Roll stats from all affixes
        stats = {}
        for affix in prefixes + suffixes:
            for stat_type, value in affix.roll_stats().items():
                stats[stat_type] = stats.get(stat_type, 0) + value

        return {
            "item_id": f"rare_{base_item_id}_{random.randint(1000, 9999)}",
            "name": item_name,
            "rarity": ItemRarity.RARE,
            "base_item": base_item_id,
            "affixes": [a.affix_id for a in prefixes + suffixes],
            "stats": {k.value: v for k, v in stats.items()},
            "sockets": random.randint(0, 2) if random.random() < 0.3 else 0
        }

    @staticmethod
    def add_sockets(item: Dict[str, Any], num_sockets: int) -> Dict[str, Any]:
        """Add sockets to an item."""
        item["sockets"] = num_sockets
        item["socketed_gems"] = []
        return item

    @staticmethod
    def socket_gem(item: Dict[str, Any], gem_id: str) -> bool:
        """Socket a gem into an item."""
        if "sockets" not in item or item["sockets"] <= 0:
            return False
        if "socketed_gems" not in item:
            item["socketed_gems"] = []
        if len(item["socketed_gems"]) >= item["sockets"]:
            return False

        item["socketed_gems"].append(gem_id)
        return True


def generate_random_item(item_level: int, base_item_id: str = "longsword") -> Dict[str, Any]:
    """
    Generate a random item with rarity based on drop chances.

    Args:
        item_level: Level of the item
        base_item_id: Base item type

    Returns:
        Generated item dict
    """
    # Roll for rarity
    roll = random.random()

    if roll < ItemRarity.LEGENDARY.drop_chance:
        # Return a random unique item
        unique = random.choice(list(UNIQUE_ITEMS.values()))
        return {
            "item_id": unique.item_id,
            "name": unique.name,
            "rarity": ItemRarity.UNIQUE,
            "stats": {k.value: v for k, v in unique.stats.items()},
            "special": unique.special,
            "sockets": 0
        }
    elif roll < ItemRarity.UNIQUE.drop_chance:
        # Return a random unique item (not legendary, so lower tier unique)
        unique = random.choice(list(UNIQUE_ITEMS.values()))
        return {
            "item_id": unique.item_id,
            "name": unique.name,
            "rarity": ItemRarity.UNIQUE,
            "stats": {k.value: v for k, v in unique.stats.items()},
            "special": unique.special,
            "sockets": 0
        }
    elif roll < ItemRarity.SET.drop_chance:
        # Return a random set item
        set_item = random.choice(list(ALL_SET_ITEMS.values()))
        return {
            "item_id": set_item.item_id,
            "name": set_item.name,
            "rarity": ItemRarity.SET,
            "set_id": set_item.set_id,
            "stats": {k.value: v for k, v in set_item.base_stats.items()},
            "sockets": 0
        }
    elif roll < ItemRarity.RARE.drop_chance:
        return MagicItemGenerator.generate_rare_item(base_item_id, item_level)
    elif roll < ItemRarity.MAGIC.drop_chance:
        return MagicItemGenerator.generate_magic_item(base_item_id, item_level)
    else:
        # Common item - just return base
        return {
            "item_id": base_item_id,
            "name": base_item_id.replace("_", " ").title(),
            "rarity": ItemRarity.COMMON,
            "stats": {},
            "sockets": 0
        }
