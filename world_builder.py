"""
World Building System for AI D&D Game

Defines locations, connections, NPCs, and encounter tables.
"""

from typing import Dict, List, Optional, Set, Tuple
from enum import Enum
import random


class LocationType(Enum):
    """Types of locations."""
    TOWN = "town"
    WILDERNESS = "wilderness"
    DUNGEON = "dungeon"
    CAVE = "cave"
    RUINS = "ruins"
    TAVERN = "tavern"
    SHOP = "shop"
    TEMPLE = "temple"


class Location:
    """Represents a location in the game world."""

    def __init__(
        self,
        location_id: str,
        name: str,
        location_type: LocationType,
        description: str,
        connections: Dict[str, str] = None,  # direction: location_id
        encounter_chance: float = 0.0,
        encounter_table: str = None,
        npcs: List[str] = None,
        services: List[str] = None,  # ["shop", "inn", "temple"]
        items: List[str] = None,  # Item IDs that can be found here
        visited: bool = False,
        cleared: bool = False,
        coordinates: Tuple[int, int] = None  # For map display
    ):
        self.location_id = location_id
        self.name = name
        self.location_type = location_type
        self.description = description
        self.connections = connections or {}
        self.encounter_chance = encounter_chance
        self.encounter_table = encounter_table
        self.npcs = npcs or []
        self.services = services or []
        self.items = items or []
        self.visited = visited
        self.cleared = cleared
        self.coordinates = coordinates

    def get_available_directions(self) -> List[str]:
        """Get list of directions player can travel."""
        return list(self.connections.keys())

    def get_connected_location(self, direction: str) -> Optional[str]:
        """Get the location ID in a given direction."""
        return self.connections.get(direction)

    def mark_visited(self):
        """Mark location as visited."""
        self.visited = True

    def mark_cleared(self):
        """Mark location as cleared of enemies."""
        self.cleared = True

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.location_id,
            "name": self.name,
            "type": self.location_type.value,
            "description": self.description,
            "connections": self.connections,
            "encounter_chance": self.encounter_chance,
            "npcs": self.npcs,
            "services": self.services,
            "visited": self.visited,
            "cleared": self.cleared,
            "coordinates": self.coordinates
        }


# ============================================================================
# WORLD MAP DEFINITION
# ============================================================================

def create_emberpeak_world() -> Dict[str, Location]:
    """Create the Emberpeak region world map."""

    locations = {}

    # ========================================================================
    # THORNHAVEN VILLAGE (Starting Area)
    # ========================================================================

    locations["thornhaven_tavern"] = Location(
        "thornhaven_tavern",
        "The Rusty Axe Tavern",
        LocationType.TAVERN,
        "A warm, dimly lit tavern filled with the smell of roasted meat and ale. "
        "Adventurers and locals gather here to share tales and rumors. "
        "A crackling fireplace illuminates wanted posters on the wall.",
        connections={"out": "thornhaven_square"},
        npcs=["innkeeper_mara", "rogue_companion", "fighter_companion"],
        services=["inn", "rumors"],
        coordinates=(3, 2)
    )

    locations["thornhaven_square"] = Location(
        "thornhaven_square",
        "Thornhaven Village Square",
        LocationType.TOWN,
        "The heart of Thornhaven village. Merchants hawk their wares while "
        "villagers go about their daily business. A stone well sits in the center. "
        "To the north lies the blacksmith, east leads to the temple, south to the tavern, "
        "and west toward the town gates.",
        connections={
            "north": "thornhaven_blacksmith",
            "south": "thornhaven_tavern",
            "east": "thornhaven_temple",
            "west": "thornhaven_gates"
        },
        npcs=["merchant_todd", "village_elder"],
        services=["fountain"],
        coordinates=(3, 1)
    )

    locations["thornhaven_blacksmith"] = Location(
        "thornhaven_blacksmith",
        "Ironforge Smithy",
        LocationType.SHOP,
        "The clang of hammer on anvil rings out from this sweltering workshop. "
        "Weapons and armor line the walls, and the smell of hot metal fills the air. "
        "The blacksmith eyes you appraisingly.",
        connections={"south": "thornhaven_square"},
        npcs=["blacksmith_grim"],
        services=["shop", "repair"],
        items=["iron_sword", "leather_armor", "chainmail"],
        coordinates=(3, 0)
    )

    locations["thornhaven_temple"] = Location(
        "thornhaven_temple",
        "Temple of the Dawning Light",
        LocationType.TEMPLE,
        "A small but well-kept temple. Candles flicker before a statue of the dawn goddess. "
        "The air smells of incense, and you feel a sense of peace here. "
        "A priestess kneels in prayer.",
        connections={"west": "thornhaven_square"},
        npcs=["priestess_elena"],
        services=["healing", "blessing"],
        coordinates=(4, 1)
    )

    locations["thornhaven_gates"] = Location(
        "thornhaven_gates",
        "Thornhaven Village Gates",
        LocationType.TOWN,
        "The western edge of Thornhaven. Wooden gates mark the boundary between "
        "civilization and the wild frontier. Guards eye travelers suspiciously. "
        "Beyond lies Darkwood Forest to the west, and paths north and south.",
        connections={
            "east": "thornhaven_square",
            "west": "darkwood_forest",
            "north": "northern_crossroads",
            "south": "southern_path"
        },
        npcs=["guard_captain"],
        coordinates=(2, 1)
    )

    # ========================================================================
    # WILDERNESS AREAS
    # ========================================================================

    locations["darkwood_forest"] = Location(
        "darkwood_forest",
        "Darkwood Forest",
        LocationType.WILDERNESS,
        "Ancient trees block out most of the sunlight, creating an eerie twilight. "
        "Strange sounds echo from deeper in the woods. The path is barely visible, "
        "winding between massive tree trunks covered in moss.",
        connections={
            "east": "thornhaven_gates",
            "west": "forest_clearing",
            "north": "forest_depths"
        },
        encounter_chance=0.3,
        encounter_table="forest",
        coordinates=(1, 1)
    )

    locations["forest_clearing"] = Location(
        "forest_clearing",
        "Forest Clearing",
        LocationType.WILDERNESS,
        "A circular clearing where sunlight breaks through the canopy. Wildflowers "
        "bloom in the grass, and you can hear a stream nearby. This seems like a "
        "safe place to rest.",
        connections={
            "east": "darkwood_forest",
            "north": "hidden_grove"
        },
        items=["health_potion", "rope"],
        coordinates=(0, 1)
    )

    locations["forest_depths"] = Location(
        "forest_depths",
        "Deep Forest",
        LocationType.WILDERNESS,
        "The forest grows darker and more threatening here. Gnarled roots threaten "
        "to trip you with every step. You hear growling in the distance.",
        connections={
            "south": "darkwood_forest",
            "west": "goblin_camp"
        },
        encounter_chance=0.5,
        encounter_table="forest",
        coordinates=(1, 0)
    )

    locations["hidden_grove"] = Location(
        "hidden_grove",
        "Hidden Grove",
        LocationType.WILDERNESS,
        "A mystical clearing pulses with magical energy. Ancient stones form a circle, "
        "covered in glowing runes. The air shimmers with power. This place feels sacred.",
        connections={
            "south": "forest_clearing"
        },
        npcs=["hermit_sage"],
        items=["ancient_coin", "strength_elixir"],
        coordinates=(0, 0)
    )

    locations["goblin_camp"] = Location(
        "goblin_camp",
        "Goblin Camp",
        LocationType.WILDERNESS,
        "Crude tents and campfires mark this goblin encampment. The smell of rotten "
        "meat hangs in the air. Goblins scramble about, sharpening weapons and arguing "
        "in their harsh tongue.",
        connections={
            "east": "forest_depths"
        },
        encounter_chance=0.8,
        encounter_table="goblin_camp",
        cleared=False,
        items=["chest_common"],
        coordinates=(0, 0)
    )

    # ========================================================================
    # NORTHERN AREA
    # ========================================================================

    locations["northern_crossroads"] = Location(
        "northern_crossroads",
        "Northern Crossroads",
        LocationType.WILDERNESS,
        "Four paths meet at this windswept crossroads. A weathered signpost points "
        "in different directions: Village to the south, Mountains to the north, "
        "Forest to the west, Ruins to the east.",
        connections={
            "south": "thornhaven_gates",
            "north": "mountain_pass",
            "east": "ancient_ruins",
            "west": "darkwood_forest"
        },
        encounter_chance=0.2,
        encounter_table="wilderness",
        coordinates=(2, 0)
    )

    locations["mountain_pass"] = Location(
        "mountain_pass",
        "Mountain Pass",
        LocationType.WILDERNESS,
        "A narrow path winds up the mountainside. Loose rocks make footing treacherous. "
        "The air grows cold, and snow dusts the higher peaks. You can see Emberpeak Mine "
        "ahead, dark and foreboding.",
        connections={
            "south": "northern_crossroads",
            "north": "emberpeak_entrance"
        },
        encounter_chance=0.3,
        encounter_table="mountain",
        coordinates=(2, -1)
    )

    locations["ancient_ruins"] = Location(
        "ancient_ruins",
        "Ancient Ruins",
        LocationType.RUINS,
        "Crumbling stone walls are all that remain of some forgotten civilization. "
        "Strange symbols are carved into the weathered stones. You sense magic here, "
        "old and dangerous.",
        connections={
            "west": "northern_crossroads",
            "down": "ruins_crypt"
        },
        encounter_chance=0.4,
        encounter_table="undead",
        items=["ancient_coin", "chest_common"],
        coordinates=(3, 0)
    )

    # ========================================================================
    # SOUTHERN AREA
    # ========================================================================

    locations["southern_path"] = Location(
        "southern_path",
        "Southern Trading Path",
        LocationType.WILDERNESS,
        "A well-traveled road leads south from the village. Wagon tracks mark the "
        "dirt path. You can see farmland in the distance.",
        connections={
            "north": "thornhaven_gates",
            "south": "riverside_farm",
            "east": "bandit_hideout"
        },
        encounter_chance=0.2,
        encounter_table="wilderness",
        coordinates=(2, 2)
    )

    locations["riverside_farm"] = Location(
        "riverside_farm",
        "Riverside Farm",
        LocationType.TOWN,
        "A peaceful farm sits beside a gently flowing river. Crops grow in neat rows, "
        "and chickens peck at the ground. The farmer looks worried.",
        connections={
            "north": "southern_path"
        },
        npcs=["farmer_bran"],
        items=["health_potion"],
        coordinates=(2, 3)
    )

    locations["bandit_hideout"] = Location(
        "bandit_hideout",
        "Bandit Hideout",
        LocationType.CAVE,
        "A cave entrance hidden by thick brush. You can hear voices and laughter "
        "from within. This is clearly a bandit camp - stolen goods are piled near "
        "the entrance.",
        connections={
            "west": "southern_path"
        },
        encounter_chance=0.9,
        encounter_table="bandits",
        cleared=False,
        items=["chest_rare"],
        coordinates=(3, 2)
    )

    # ========================================================================
    # EMBERPEAK MINES DUNGEON (Main Quest Location)
    # ========================================================================

    locations["emberpeak_entrance"] = Location(
        "emberpeak_entrance",
        "Emberpeak Mine Entrance",
        LocationType.DUNGEON,
        "The entrance to Emberpeak Mine yawns before you like a hungry mouth. "
        "Broken mine carts and rusted tools litter the area. You can hear faint "
        "cries for help echoing from the depths.",
        connections={
            "south": "mountain_pass",
            "down": "mine_shaft"
        },
        npcs=["wounded_miner"],
        coordinates=(2, -2)
    )

    locations["mine_shaft"] = Location(
        "mine_shaft",
        "Main Mine Shaft",
        LocationType.DUNGEON,
        "Support beams creak ominously as you descend into darkness. Your torch "
        "flickers, casting dancing shadows on the rough-hewn walls. Multiple tunnels "
        "branch off in different directions.",
        connections={
            "up": "emberpeak_entrance",
            "north": "collapsed_tunnel",
            "east": "storage_cavern",
            "south": "deep_mines"
        },
        encounter_chance=0.4,
        encounter_table="mine",
        coordinates=(2, -2)
    )

    locations["collapsed_tunnel"] = Location(
        "collapsed_tunnel",
        "Collapsed Tunnel",
        LocationType.DUNGEON,
        "This tunnel has partially collapsed. You can hear voices on the other side "
        "of the rubble - the trapped miners! But something moves in the shadows...",
        connections={
            "south": "mine_shaft"
        },
        encounter_chance=0.7,
        encounter_table="mine",
        npcs=["trapped_miners"],
        coordinates=(2, -3)
    )

    locations["storage_cavern"] = Location(
        "storage_cavern",
        "Storage Cavern",
        LocationType.DUNGEON,
        "Old mining equipment and supplies are stored here. Crates and barrels "
        "are stacked against the walls. Some have been broken open and looted.",
        connections={
            "west": "mine_shaft"
        },
        items=["chest_common", "health_potion", "torch"],
        coordinates=(3, -2)
    )

    locations["deep_mines"] = Location(
        "deep_mines",
        "Deep Mines",
        LocationType.DUNGEON,
        "The deepest part of the mine. The air is hot and oppressive. Glowing "
        "crystals embedded in the walls pulse with an unnatural light. You sense "
        "powerful magic ahead.",
        connections={
            "north": "mine_shaft",
            "south": "rune_chamber"
        },
        encounter_chance=0.6,
        encounter_table="mine",
        coordinates=(2, -1)
    )

    locations["rune_chamber"] = Location(
        "rune_chamber",
        "Chamber of the Shattered Rune",
        LocationType.DUNGEON,
        "A massive chamber opens before you. In the center, a glowing rune hovers "
        "in the air, cracked and pulsing with dark energy. This is the source of "
        "the corruption! A massive creature guards it...",
        connections={
            "north": "deep_mines"
        },
        encounter_chance=1.0,
        encounter_table="boss",
        items=["shattered_rune", "chest_rare"],
        coordinates=(2, 0)
    )

    # Underground ruins
    locations["ruins_crypt"] = Location(
        "ruins_crypt",
        "Ancient Crypt",
        LocationType.DUNGEON,
        "Stone sarcophagi line the walls of this underground crypt. Ancient bones "
        "and grave goods rest in eternal silence. Or do they? You hear scraping sounds...",
        connections={
            "up": "ancient_ruins"
        },
        encounter_chance=0.8,
        encounter_table="undead",
        items=["chest_rare", "ancient_coin"],
        coordinates=(3, 1)
    )

    return locations


# ============================================================================
# ENCOUNTER TABLES
# ============================================================================

ENCOUNTER_TABLES = {
    "forest": [
        {"enemies": [("Goblin", 2)], "weight": 3},
        {"enemies": [("Goblin", 3)], "weight": 2},
        {"enemies": [("Goblin", 1), ("Orc", 1)], "weight": 1},
    ],

    "wilderness": [
        {"enemies": [("Bandit", 2)], "weight": 3},
        {"enemies": [("Goblin", 2)], "weight": 2},
        {"enemies": [("Bandit", 1)], "weight": 2},
    ],

    "mountain": [
        {"enemies": [("Orc", 2)], "weight": 3},
        {"enemies": [("Orc", 3)], "weight": 2},
        {"enemies": [("Skeleton", 2)], "weight": 1},
    ],

    "undead": [
        {"enemies": [("Skeleton", 3)], "weight": 3},
        {"enemies": [("Skeleton", 2)], "weight": 2},
        {"enemies": [("Skeleton", 4)], "weight": 1},
    ],

    "goblin_camp": [
        {"enemies": [("Goblin", 4)], "weight": 2},
        {"enemies": [("Goblin", 3), ("Orc", 1)], "weight": 2},
        {"enemies": [("Goblin", 5)], "weight": 1},
    ],

    "bandits": [
        {"enemies": [("Bandit", 3)], "weight": 3},
        {"enemies": [("Bandit", 2)], "weight": 2},
        {"enemies": [("Bandit", 4)], "weight": 1},
    ],

    "mine": [
        {"enemies": [("Skeleton", 2)], "weight": 3},
        {"enemies": [("Skeleton", 3)], "weight": 2},
        {"enemies": [("Goblin", 2), ("Skeleton", 1)], "weight": 2},
    ],

    "boss": [
        {"enemies": [("Orc", 1)], "weight": 1, "boss": True},  # Placeholder - should be special boss
    ],
}


def get_random_encounter(encounter_table_name: str) -> List[Tuple[str, int]]:
    """
    Get a random encounter from a table.

    Args:
        encounter_table_name: Name of the encounter table

    Returns:
        List of (enemy_class, count) tuples
    """
    table = ENCOUNTER_TABLES.get(encounter_table_name, [])
    if not table:
        return [("Goblin", 1)]  # Default

    # Weighted random selection
    total_weight = sum(e["weight"] for e in table)
    rand = random.uniform(0, total_weight)

    current = 0
    for encounter in table:
        current += encounter["weight"]
        if rand <= current:
            return encounter["enemies"]

    return table[0]["enemies"]  # Fallback


# ============================================================================
# WORLD MANAGER
# ============================================================================

class WorldManager:
    """Manages the game world and player location."""

    def __init__(self):
        self.locations = create_emberpeak_world()
        self.current_location_id = "thornhaven_tavern"

    def get_current_location(self) -> Location:
        """Get the current location object."""
        return self.locations[self.current_location_id]

    def move(self, direction: str) -> Tuple[bool, str]:
        """
        Attempt to move in a direction.

        Returns:
            (success, message)
        """
        current = self.get_current_location()
        new_location_id = current.get_connected_location(direction)

        if not new_location_id:
            return False, f"You can't go {direction} from here."

        if new_location_id not in self.locations:
            return False, f"That path leads nowhere."

        # Move successful
        self.current_location_id = new_location_id
        new_location = self.get_current_location()
        new_location.mark_visited()

        return True, f"You travel {direction} to {new_location.name}."

    def get_available_directions(self) -> List[str]:
        """Get available movement directions from current location."""
        return self.get_current_location().get_available_directions()

    def check_for_encounter(self) -> Optional[List[Tuple[str, int]]]:
        """
        Check if an encounter occurs at current location.

        Returns:
            List of (enemy_class, count) or None
        """
        current = self.get_current_location()

        if current.cleared:
            return None

        if random.random() < current.encounter_chance:
            if current.encounter_table:
                return get_random_encounter(current.encounter_table)

        return None

    def get_map_state(self) -> Dict:
        """
        Get the current state of the world map for display.

        Returns:
            Dictionary with location data for map rendering
        """
        map_data = {
            "current_location": self.current_location_id,
            "locations": {}
        }

        for loc_id, location in self.locations.items():
            if location.visited or loc_id == self.current_location_id:
                map_data["locations"][loc_id] = {
                    "name": location.name,
                    "type": location.location_type.value,
                    "coordinates": location.coordinates,
                    "cleared": location.cleared,
                    "current": loc_id == self.current_location_id
                }

        return map_data
