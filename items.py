"""
Item and Equipment System for AI D&D Game

Provides items, equipment, loot drops, and inventory management.
"""

from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import random


class ItemType(Enum):
    """Types of items."""
    WEAPON = "weapon"
    ARMOR = "armor"
    CONSUMABLE = "consumable"
    QUEST = "quest"
    TREASURE = "treasure"
    TOOL = "tool"


class ItemRarity(Enum):
    """Item rarity levels."""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"


@dataclass
class ItemEffect:
    """Effects that an item can have."""
    effect_type: str  # heal, buff_attack, buff_defense, damage, etc.
    value: int
    duration: int = 0  # 0 = instant, >0 = turns


class Item:
    """Represents an item in the game."""

    def __init__(
        self,
        item_id: str,
        name: str,
        item_type: ItemType,
        description: str = "",
        value: int = 0,
        rarity: ItemRarity = ItemRarity.COMMON,
        effects: List[ItemEffect] = None,
        stackable: bool = False,
        max_stack: int = 99,
        equippable: bool = False,
        slot: str = None,  # "weapon", "armor", "accessory", etc.
        stats: Dict[str, int] = None  # {"attack": 5, "defense": 2}
    ):
        self.item_id = item_id
        self.name = name
        self.item_type = item_type
        self.description = description
        self.value = value  # Gold value
        self.rarity = rarity
        self.effects = effects or []
        self.stackable = stackable
        self.max_stack = max_stack
        self.equippable = equippable
        self.slot = slot
        self.stats = stats or {}

    def use(self, character) -> str:
        """Use the item on a character."""
        results = []

        for effect in self.effects:
            if effect.effect_type == "heal":
                old_hp = character.hp
                character.hp = min(character.max_hp, character.hp + effect.value)
                healed = character.hp - old_hp
                results.append(f"Healed {healed} HP")

            elif effect.effect_type == "buff_attack":
                character.attack += effect.value
                results.append(f"Attack +{effect.value}")

            elif effect.effect_type == "buff_defense":
                character.defense += effect.value
                results.append(f"Defense +{effect.value}")

        return ", ".join(results) if results else "No effect"

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "item_id": self.item_id,
            "name": self.name,
            "type": self.item_type.value,
            "description": self.description,
            "value": self.value,
            "rarity": self.rarity.value,
            "stackable": self.stackable,
            "equippable": self.equippable,
            "slot": self.slot,
            "stats": self.stats
        }


# ============================================================================
# ITEM DEFINITIONS
# ============================================================================

ITEMS = {
    # Weapons
    "rusty_dagger": Item(
        "rusty_dagger",
        "Rusty Dagger",
        ItemType.WEAPON,
        "A worn dagger, barely sharp enough to cut bread.",
        value=5,
        rarity=ItemRarity.COMMON,
        equippable=True,
        slot="weapon",
        stats={"attack": 2}
    ),

    "iron_sword": Item(
        "iron_sword",
        "Iron Sword",
        ItemType.WEAPON,
        "A reliable iron blade, standard issue for town guards.",
        value=25,
        rarity=ItemRarity.COMMON,
        equippable=True,
        slot="weapon",
        stats={"attack": 5}
    ),

    "steel_longsword": Item(
        "steel_longsword",
        "Steel Longsword",
        ItemType.WEAPON,
        "A well-crafted longsword with a gleaming edge.",
        value=75,
        rarity=ItemRarity.UNCOMMON,
        equippable=True,
        slot="weapon",
        stats={"attack": 8}
    ),

    "enchanted_blade": Item(
        "enchanted_blade",
        "Enchanted Blade",
        ItemType.WEAPON,
        "Runes glow along this magical blade.",
        value=250,
        rarity=ItemRarity.RARE,
        equippable=True,
        slot="weapon",
        stats={"attack": 12, "magic_damage": 5}
    ),

    # Armor
    "leather_armor": Item(
        "leather_armor",
        "Leather Armor",
        ItemType.ARMOR,
        "Simple leather protection, better than nothing.",
        value=20,
        rarity=ItemRarity.COMMON,
        equippable=True,
        slot="armor",
        stats={"defense": 3}
    ),

    "chainmail": Item(
        "chainmail",
        "Chainmail",
        ItemType.ARMOR,
        "Interlocking metal rings provide solid protection.",
        value=60,
        rarity=ItemRarity.UNCOMMON,
        equippable=True,
        slot="armor",
        stats={"defense": 6}
    ),

    "plate_armor": Item(
        "plate_armor",
        "Plate Armor",
        ItemType.ARMOR,
        "Heavy steel plates, the finest protection money can buy.",
        value=200,
        rarity=ItemRarity.RARE,
        equippable=True,
        slot="armor",
        stats={"defense": 10}
    ),

    # Consumables
    "health_potion": Item(
        "health_potion",
        "Health Potion",
        ItemType.CONSUMABLE,
        "A red liquid that restores vitality.",
        value=50,
        rarity=ItemRarity.COMMON,
        stackable=True,
        max_stack=10,
        effects=[ItemEffect("heal", 20)]
    ),

    "greater_health_potion": Item(
        "greater_health_potion",
        "Greater Health Potion",
        ItemType.CONSUMABLE,
        "A concentrated healing draught.",
        value=150,
        rarity=ItemRarity.UNCOMMON,
        stackable=True,
        max_stack=5,
        effects=[ItemEffect("heal", 50)]
    ),

    "strength_elixir": Item(
        "strength_elixir",
        "Strength Elixir",
        ItemType.CONSUMABLE,
        "Increases attack power temporarily.",
        value=100,
        rarity=ItemRarity.UNCOMMON,
        stackable=True,
        max_stack=5,
        effects=[ItemEffect("buff_attack", 3, duration=3)]
    ),

    # Tools
    "lockpicks": Item(
        "lockpicks",
        "Thieves' Tools",
        ItemType.TOOL,
        "A set of picks and probes for opening locks.",
        value=25,
        rarity=ItemRarity.COMMON
    ),

    "rope": Item(
        "rope",
        "Rope (50ft)",
        ItemType.TOOL,
        "Hempen rope, useful for climbing or binding.",
        value=10,
        rarity=ItemRarity.COMMON
    ),

    "torch": Item(
        "torch",
        "Torch",
        ItemType.TOOL,
        "A wooden torch that provides light.",
        value=1,
        rarity=ItemRarity.COMMON,
        stackable=True,
        max_stack=20
    ),

    # Treasure
    "gold_coin": Item(
        "gold_coin",
        "Gold Coin",
        ItemType.TREASURE,
        "A shiny gold coin.",
        value=1,
        rarity=ItemRarity.COMMON,
        stackable=True,
        max_stack=999
    ),

    "ruby": Item(
        "ruby",
        "Ruby",
        ItemType.TREASURE,
        "A precious red gemstone.",
        value=100,
        rarity=ItemRarity.UNCOMMON,
        stackable=True
    ),

    "ancient_coin": Item(
        "ancient_coin",
        "Ancient Coin",
        ItemType.TREASURE,
        "A coin from a forgotten empire.",
        value=50,
        rarity=ItemRarity.RARE,
        stackable=True
    ),

    # Quest Items
    "shattered_rune": Item(
        "shattered_rune",
        "Shattered Rune Fragment",
        ItemType.QUEST,
        "A piece of the broken rune from Emberpeak.",
        value=0,
        rarity=ItemRarity.RARE
    ),

    "miners_note": Item(
        "miners_note",
        "Miner's Note",
        ItemType.QUEST,
        "A hastily scribbled plea for help.",
        value=0,
        rarity=ItemRarity.COMMON
    ),
}


# ============================================================================
# LOOT TABLES
# ============================================================================

class LootTable:
    """Defines what items can drop from enemies/chests."""

    def __init__(self, name: str):
        self.name = name
        self.items: List[Dict[str, Any]] = []
        self.gold_range: tuple = (0, 0)

    def add_item(self, item_id: str, chance: float, quantity: tuple = (1, 1)):
        """
        Add an item to the loot table.

        Args:
            item_id: ID of the item
            chance: Probability (0.0 to 1.0)
            quantity: (min, max) amount to drop
        """
        self.items.append({
            "item_id": item_id,
            "chance": chance,
            "quantity": quantity
        })

    def set_gold(self, min_gold: int, max_gold: int):
        """Set the gold range."""
        self.gold_range = (min_gold, max_gold)

    def roll(self) -> Dict[str, int]:
        """Roll for loot drops."""
        drops = {}

        # Roll gold
        if self.gold_range[1] > 0:
            gold = random.randint(self.gold_range[0], self.gold_range[1])
            if gold > 0:
                drops["gold_coin"] = gold

        # Roll for items
        for item_entry in self.items:
            if random.random() < item_entry["chance"]:
                quantity = random.randint(
                    item_entry["quantity"][0],
                    item_entry["quantity"][1]
                )
                item_id = item_entry["item_id"]
                drops[item_id] = drops.get(item_id, 0) + quantity

        return drops


# Define loot tables for different enemy types
LOOT_TABLES = {
    "goblin": LootTable("goblin"),
    "orc": LootTable("orc"),
    "skeleton": LootTable("skeleton"),
    "bandit": LootTable("bandit"),
    "chest_common": LootTable("chest_common"),
    "chest_rare": LootTable("chest_rare"),
    "boss": LootTable("boss"),
}

# Goblin loot
LOOT_TABLES["goblin"].set_gold(1, 10)
LOOT_TABLES["goblin"].add_item("rusty_dagger", 0.3, (1, 1))
LOOT_TABLES["goblin"].add_item("torch", 0.2, (1, 2))
LOOT_TABLES["goblin"].add_item("health_potion", 0.1, (1, 1))

# Orc loot
LOOT_TABLES["orc"].set_gold(5, 20)
LOOT_TABLES["orc"].add_item("iron_sword", 0.4, (1, 1))
LOOT_TABLES["orc"].add_item("leather_armor", 0.3, (1, 1))
LOOT_TABLES["orc"].add_item("health_potion", 0.2, (1, 2))

# Skeleton loot
LOOT_TABLES["skeleton"].set_gold(0, 5)
LOOT_TABLES["skeleton"].add_item("rusty_dagger", 0.2, (1, 1))
LOOT_TABLES["skeleton"].add_item("ancient_coin", 0.3, (1, 3))

# Bandit loot
LOOT_TABLES["bandit"].set_gold(10, 30)
LOOT_TABLES["bandit"].add_item("iron_sword", 0.5, (1, 1))
LOOT_TABLES["bandit"].add_item("lockpicks", 0.3, (1, 1))
LOOT_TABLES["bandit"].add_item("health_potion", 0.4, (1, 2))
LOOT_TABLES["bandit"].add_item("rope", 0.2, (1, 1))

# Common chest
LOOT_TABLES["chest_common"].set_gold(20, 50)
LOOT_TABLES["chest_common"].add_item("health_potion", 0.8, (1, 3))
LOOT_TABLES["chest_common"].add_item("iron_sword", 0.4, (1, 1))
LOOT_TABLES["chest_common"].add_item("leather_armor", 0.4, (1, 1))
LOOT_TABLES["chest_common"].add_item("torch", 0.6, (2, 5))

# Rare chest
LOOT_TABLES["chest_rare"].set_gold(100, 250)
LOOT_TABLES["chest_rare"].add_item("steel_longsword", 0.6, (1, 1))
LOOT_TABLES["chest_rare"].add_item("chainmail", 0.6, (1, 1))
LOOT_TABLES["chest_rare"].add_item("greater_health_potion", 0.8, (2, 4))
LOOT_TABLES["chest_rare"].add_item("strength_elixir", 0.5, (1, 2))
LOOT_TABLES["chest_rare"].add_item("ruby", 0.3, (1, 3))

# Boss loot
LOOT_TABLES["boss"].set_gold(200, 500)
LOOT_TABLES["boss"].add_item("enchanted_blade", 0.8, (1, 1))
LOOT_TABLES["boss"].add_item("plate_armor", 0.7, (1, 1))
LOOT_TABLES["boss"].add_item("greater_health_potion", 1.0, (3, 5))
LOOT_TABLES["boss"].add_item("ruby", 0.8, (2, 5))
LOOT_TABLES["boss"].add_item("shattered_rune", 1.0, (1, 1))


# ============================================================================
# INVENTORY SYSTEM
# ============================================================================

class Inventory:
    """Manages a character's inventory."""

    def __init__(self, capacity: int = 20):
        self.capacity = capacity
        self.items: Dict[str, int] = {}  # item_id: quantity
        self.equipped: Dict[str, str] = {}  # slot: item_id
        self.gold: int = 0

    def add_item(self, item_id: str, quantity: int = 1) -> bool:
        """
        Add items to inventory.

        Returns:
            True if successful, False if inventory full
        """
        # Handle gold specially
        if item_id == "gold_coin":
            self.gold += quantity
            return True

        item = ITEMS.get(item_id)
        if not item:
            return False

        # Check capacity
        if not item.stackable and len(self.items) >= self.capacity:
            return False

        # Add to existing stack or create new
        if item.stackable:
            current = self.items.get(item_id, 0)
            self.items[item_id] = min(current + quantity, item.max_stack)
        else:
            if item_id not in self.items:
                self.items[item_id] = quantity

        return True

    def remove_item(self, item_id: str, quantity: int = 1) -> bool:
        """
        Remove items from inventory.

        Returns:
            True if successful, False if not enough items
        """
        if item_id == "gold_coin":
            if self.gold >= quantity:
                self.gold -= quantity
                return True
            return False

        if item_id not in self.items or self.items[item_id] < quantity:
            return False

        self.items[item_id] -= quantity
        if self.items[item_id] <= 0:
            del self.items[item_id]
            # Unequip if equipped
            for slot, equipped_id in list(self.equipped.items()):
                if equipped_id == item_id:
                    del self.equipped[slot]

        return True

    def has_item(self, item_id: str, quantity: int = 1) -> bool:
        """Check if inventory has item."""
        if item_id == "gold_coin":
            return self.gold >= quantity
        return self.items.get(item_id, 0) >= quantity

    def equip(self, item_id: str) -> str:
        """
        Equip an item.

        Returns:
            Message describing result
        """
        if not self.has_item(item_id):
            return f"You don't have {item_id}"

        item = ITEMS.get(item_id)
        if not item or not item.equippable:
            return f"{item.name} cannot be equipped"

        # Unequip current item in slot
        if item.slot in self.equipped:
            old_item_id = self.equipped[item.slot]
            old_item = ITEMS[old_item_id]
            self.equipped[item.slot] = item_id
            return f"Equipped {item.name}, unequipped {old_item.name}"

        self.equipped[item.slot] = item_id
        return f"Equipped {item.name}"

    def unequip(self, slot: str) -> str:
        """Unequip item from slot."""
        if slot not in self.equipped:
            return f"Nothing equipped in {slot}"

        item_id = self.equipped[slot]
        item = ITEMS[item_id]
        del self.equipped[slot]
        return f"Unequipped {item.name}"

    def get_equipped_stats(self) -> Dict[str, int]:
        """Get total stats from equipped items."""
        total_stats = {}

        for item_id in self.equipped.values():
            item = ITEMS[item_id]
            for stat, value in item.stats.items():
                total_stats[stat] = total_stats.get(stat, 0) + value

        return total_stats

    def use_item(self, item_id: str, character) -> str:
        """Use a consumable item."""
        if not self.has_item(item_id):
            return f"You don't have {item_id}"

        item = ITEMS.get(item_id)
        if not item:
            return "Unknown item"

        if item.item_type != ItemType.CONSUMABLE:
            return f"{item.name} cannot be used"

        result = item.use(character)
        self.remove_item(item_id, 1)

        return f"Used {item.name}: {result}"

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "capacity": self.capacity,
            "items": {
                item_id: {
                    "quantity": qty,
                    "name": ITEMS[item_id].name
                }
                for item_id, qty in self.items.items()
            },
            "equipped": {
                slot: {
                    "item_id": item_id,
                    "name": ITEMS[item_id].name
                }
                for slot, item_id in self.equipped.items()
            },
            "gold": self.gold
        }


def get_loot_from_enemy(enemy_class: str) -> Dict[str, int]:
    """
    Get loot drops from a defeated enemy.

    Args:
        enemy_class: Class of enemy (Goblin, Orc, etc.)

    Returns:
        Dictionary of item_id: quantity
    """
    loot_table_name = enemy_class.lower()
    loot_table = LOOT_TABLES.get(loot_table_name)

    if not loot_table:
        # Default to gold only
        return {"gold_coin": random.randint(1, 5)}

    return loot_table.roll()
