"""
Tile-based Map System

Grid-based map with different terrain types, collision detection,
and point-of-interest event triggers.
"""

import pygame
from typing import List, Dict, Tuple, Optional, Callable
from enum import Enum
from dataclasses import dataclass


class TileType(Enum):
    """Types of tiles in the map."""
    FLOOR = "floor"
    WALL = "wall"
    WATER = "water"
    PATH = "path"
    GRASS = "grass"
    DOOR = "door"


@dataclass
class PointOfInterest:
    """A location on the map that triggers an event."""
    grid_x: int
    grid_y: int
    name: str
    description: str
    event_type: str  # "encounter", "treasure", "npc", "exit", "story"
    triggered: bool = False
    repeatable: bool = False

    def can_trigger(self) -> bool:
        return not self.triggered or self.repeatable


# Tile colors for rendering
TILE_COLORS = {
    TileType.FLOOR: (60, 50, 40),      # Dark brown floor
    TileType.WALL: (40, 35, 30),       # Darker walls
    TileType.WATER: (30, 60, 90),      # Dark blue water
    TileType.PATH: (90, 75, 55),       # Light brown path
    TileType.GRASS: (40, 70, 40),      # Dark green grass
    TileType.DOOR: (120, 80, 40),      # Golden door
}

# Which tiles can be walked on
WALKABLE_TILES = {TileType.FLOOR, TileType.PATH, TileType.GRASS, TileType.DOOR}


class TileMap:
    """
    A grid-based tile map with collision and events.
    """

    def __init__(self, width: int, height: int, tile_size: int = 12):
        self.width = width  # tiles
        self.height = height  # tiles
        self.tile_size = tile_size

        # Initialize with floor tiles
        self.tiles: List[List[TileType]] = [
            [TileType.FLOOR for _ in range(width)]
            for _ in range(height)
        ]

        # Points of interest
        self.pois: List[PointOfInterest] = []

        # Event callback
        self.on_poi_triggered: Optional[Callable[[PointOfInterest], None]] = None

        # Pixel dimensions
        self.pixel_width = width * tile_size
        self.pixel_height = height * tile_size

    def set_tile(self, x: int, y: int, tile_type: TileType) -> None:
        """Set a tile at grid position."""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.tiles[y][x] = tile_type

    def get_tile(self, x: int, y: int) -> TileType:
        """Get tile at grid position."""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles[y][x]
        return TileType.WALL  # Out of bounds = wall

    def is_walkable(self, grid_x: int, grid_y: int) -> bool:
        """Check if a grid position can be walked on."""
        tile = self.get_tile(grid_x, grid_y)
        return tile in WALKABLE_TILES

    def pixel_to_grid(self, px: int, py: int) -> Tuple[int, int]:
        """Convert pixel coordinates to grid coordinates."""
        return px // self.tile_size, py // self.tile_size

    def grid_to_pixel(self, gx: int, gy: int) -> Tuple[int, int]:
        """Convert grid coordinates to pixel coordinates (top-left of tile)."""
        return gx * self.tile_size, gy * self.tile_size

    def can_move_to_pixel(self, px: int, py: int, sprite_size: int) -> bool:
        """Check if a sprite can move to pixel position."""
        # Check all four corners of the sprite
        corners = [
            (px, py),                              # Top-left
            (px + sprite_size - 1, py),            # Top-right
            (px, py + sprite_size - 1),            # Bottom-left
            (px + sprite_size - 1, py + sprite_size - 1)  # Bottom-right
        ]

        for cx, cy in corners:
            gx, gy = self.pixel_to_grid(cx, cy)
            if not self.is_walkable(gx, gy):
                return False
        return True

    def add_poi(self, poi: PointOfInterest) -> None:
        """Add a point of interest to the map."""
        self.pois.append(poi)

    def check_poi_collision(self, grid_x: int, grid_y: int) -> Optional[PointOfInterest]:
        """Check if position triggers a POI."""
        for poi in self.pois:
            if poi.grid_x == grid_x and poi.grid_y == grid_y:
                if poi.can_trigger():
                    return poi
        return None

    def trigger_poi(self, poi: PointOfInterest) -> None:
        """Mark a point of interest as triggered (consumed)."""
        if not poi.repeatable:
            poi.triggered = True

    def render(self, surface: pygame.Surface, offset_x: int, offset_y: int) -> None:
        """Render the tile map."""
        for gy in range(self.height):
            for gx in range(self.width):
                tile = self.tiles[gy][gx]
                color = TILE_COLORS.get(tile, (50, 50, 50))

                rect = pygame.Rect(
                    offset_x + gx * self.tile_size,
                    offset_y + gy * self.tile_size,
                    self.tile_size - 1,  # -1 for grid lines
                    self.tile_size - 1
                )
                pygame.draw.rect(surface, color, rect)

        # Render POIs
        for poi in self.pois:
            if not poi.triggered or poi.repeatable:
                self._render_poi(surface, poi, offset_x, offset_y)

    def _render_poi(self, surface: pygame.Surface, poi: PointOfInterest,
                    offset_x: int, offset_y: int) -> None:
        """Render a point of interest marker."""
        px = offset_x + poi.grid_x * self.tile_size + self.tile_size // 2
        py = offset_y + poi.grid_y * self.tile_size + self.tile_size // 2

        # Different colors for different event types
        colors = {
            "encounter": (200, 50, 50),    # Red - danger
            "treasure": (255, 215, 0),     # Gold - treasure
            "npc": (100, 200, 100),        # Green - friendly
            "exit": (100, 150, 255),       # Blue - exit
            "story": (200, 150, 255),      # Purple - story
        }
        color = colors.get(poi.event_type, (255, 255, 255))

        # Pulsing effect based on time
        pulse = abs((pygame.time.get_ticks() % 1000) - 500) / 500
        radius = int(3 + pulse * 2)

        # Glow effect
        glow_surf = pygame.Surface((radius * 4, radius * 4), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*color, 80), (radius * 2, radius * 2), radius * 2)
        surface.blit(glow_surf, (px - radius * 2, py - radius * 2))

        # Core
        pygame.draw.circle(surface, color, (px, py), radius)


def create_tavern_map() -> TileMap:
    """Create the starting tavern map."""
    # 18x12 tiles fits nicely in the map panel
    tilemap = TileMap(18, 10, tile_size=12)

    # Fill with floor
    for y in range(10):
        for x in range(18):
            tilemap.set_tile(x, y, TileType.FLOOR)

    # Walls around edges
    for x in range(18):
        tilemap.set_tile(x, 0, TileType.WALL)
        tilemap.set_tile(x, 9, TileType.WALL)
    for y in range(10):
        tilemap.set_tile(0, y, TileType.WALL)
        tilemap.set_tile(17, y, TileType.WALL)

    # Interior walls / bar counter
    for x in range(2, 7):
        tilemap.set_tile(x, 3, TileType.WALL)

    # Tables (small wall sections)
    tilemap.set_tile(10, 2, TileType.WALL)
    tilemap.set_tile(10, 6, TileType.WALL)
    tilemap.set_tile(14, 4, TileType.WALL)

    # Door to outside
    tilemap.set_tile(9, 9, TileType.DOOR)

    # Path to door
    for y in range(7, 9):
        tilemap.set_tile(9, y, TileType.PATH)

    # Add points of interest
    tilemap.add_poi(PointOfInterest(
        grid_x=4, grid_y=2,
        name="Bartender",
        description="A grizzled dwarf polishes mugs behind the counter.",
        event_type="npc",
        repeatable=True
    ))

    tilemap.add_poi(PointOfInterest(
        grid_x=14, grid_y=3,
        name="Mysterious Stranger",
        description="A hooded figure sits alone, nursing a dark drink.",
        event_type="story"
    ))

    tilemap.add_poi(PointOfInterest(
        grid_x=2, grid_y=7,
        name="Coin Pouch",
        description="Someone left a small pouch of coins under the table!",
        event_type="treasure"
    ))

    tilemap.add_poi(PointOfInterest(
        grid_x=9, grid_y=8,
        name="Tavern Exit",
        description="The door leads to the village square.",
        event_type="exit",
        repeatable=True
    ))

    tilemap.add_poi(PointOfInterest(
        grid_x=15, grid_y=7,
        name="Suspicious Character",
        description="A shifty-looking goblin in disguise! It attacks!",
        event_type="encounter"
    ))

    return tilemap


def create_forest_map() -> TileMap:
    """Create a forest exploration map."""
    tilemap = TileMap(18, 10, tile_size=12)
    
    # Fill with grass
    for y in range(10):
        for x in range(18):
            tilemap.set_tile(x, y, TileType.GRASS)
    
    # Dense forest edges (walls)
    for x in range(18):
        tilemap.set_tile(x, 0, TileType.WALL)
        tilemap.set_tile(x, 9, TileType.WALL)
    for y in range(10):
        tilemap.set_tile(0, y, TileType.WALL)
        tilemap.set_tile(17, y, TileType.WALL)
    
    # Path through forest
    for x in range(1, 9):
        tilemap.set_tile(x, 5, TileType.PATH)
    for y in range(3, 8):
        tilemap.set_tile(9, y, TileType.PATH)
    for x in range(9, 17):
        tilemap.set_tile(x, 3, TileType.PATH)
    
    # Water (pond)
    for x in range(12, 15):
        for y in range(6, 9):
            tilemap.set_tile(x, y, TileType.WATER)
    
    # Trees (walls) scattered
    trees = [(3, 2), (5, 7), (7, 3), (11, 5), (15, 6), (4, 8), (14, 2)]
    for tx, ty in trees:
        tilemap.set_tile(tx, ty, TileType.WALL)
    
    # POIs
    tilemap.add_poi(PointOfInterest(
        grid_x=2, grid_y=5,
        name="Forest Entrance",
        description="The path leads back to the village.",
        event_type="exit",
        repeatable=True
    ))
    
    tilemap.add_poi(PointOfInterest(
        grid_x=16, grid_y=3,
        name="Goblin Camp",
        description="You've found the goblin camp! Enemies attack!",
        event_type="encounter"
    ))
    
    tilemap.add_poi(PointOfInterest(
        grid_x=6, grid_y=2,
        name="Old Chest",
        description="An old chest hidden among the roots. Inside: 15 gold!",
        event_type="treasure"
    ))
    
    tilemap.add_poi(PointOfInterest(
        grid_x=11, grid_y=7,
        name="Healing Spring",
        description="The spring's waters have restorative properties.",
        event_type="story",
        repeatable=True
    ))
    
    return tilemap


# =============================================================================
# LEVEL MAPS - Progressive difficulty dungeons
# =============================================================================

def create_level_1() -> TileMap:
    """
    Level 1: The Village Outskirts
    
    A peaceful starting area with gentle introduction to exploration.
    Easy encounters, helpful NPCs, basic treasure.
    """
    tilemap = TileMap(18, 10, tile_size=12)
    
    # Fill with grass (outdoor area)
    for y in range(10):
        for x in range(18):
            tilemap.set_tile(x, y, TileType.GRASS)
    
    # Border walls (hedges/fences)
    for x in range(18):
        tilemap.set_tile(x, 0, TileType.WALL)
        tilemap.set_tile(x, 9, TileType.WALL)
    for y in range(10):
        tilemap.set_tile(0, y, TileType.WALL)
        tilemap.set_tile(17, y, TileType.WALL)
    
    # Main path from entrance to exit
    for x in range(1, 17):
        tilemap.set_tile(x, 5, TileType.PATH)
    
    # Side paths
    for y in range(2, 5):
        tilemap.set_tile(5, y, TileType.PATH)
    for y in range(6, 8):
        tilemap.set_tile(12, y, TileType.PATH)
    
    # Small pond
    tilemap.set_tile(3, 2, TileType.WATER)
    tilemap.set_tile(4, 2, TileType.WATER)
    tilemap.set_tile(3, 3, TileType.WATER)
    
    # Decorative rocks/obstacles
    obstacles = [(7, 3), (10, 7), (14, 2), (2, 7)]
    for ox, oy in obstacles:
        tilemap.set_tile(ox, oy, TileType.WALL)
    
    # Small house
    for x in range(14, 17):
        tilemap.set_tile(x, 7, TileType.WALL)
        tilemap.set_tile(x, 8, TileType.WALL)
    tilemap.set_tile(15, 7, TileType.DOOR)
    
    # === POINTS OF INTEREST ===
    
    # Entrance (from tavern)
    tilemap.add_poi(PointOfInterest(
        grid_x=1, grid_y=5,
        name="Village Gate",
        description="The path leads back to the tavern.",
        event_type="exit",
        repeatable=True
    ))
    
    # Exit to Level 2
    tilemap.add_poi(PointOfInterest(
        grid_x=16, grid_y=5,
        name="Forest Trail",
        description="A dark trail leads deeper into the wilderness...",
        event_type="exit",
        repeatable=True
    ))
    
    # Friendly NPC
    tilemap.add_poi(PointOfInterest(
        grid_x=5, grid_y=2,
        name="Old Farmer",
        description="'Watch yourself out there, adventurer. Goblins been spotted near the caves!'",
        event_type="npc",
        repeatable=True
    ))
    
    # Easy treasure
    tilemap.add_poi(PointOfInterest(
        grid_x=12, grid_y=7,
        name="Forgotten Satchel",
        description="Someone dropped their coin purse! Lucky find!",
        event_type="treasure"
    ))
    
    # Very easy encounter
    tilemap.add_poi(PointOfInterest(
        grid_x=10, grid_y=3,
        name="Wild Rat",
        description="A giant rat lunges from the bushes!",
        event_type="encounter"
    ))
    
    # House NPC
    tilemap.add_poi(PointOfInterest(
        grid_x=15, grid_y=7,
        name="Herbalist's Hut",
        description="An old woman offers you a healing potion. 'Take this, you'll need it.'",
        event_type="story"
    ))
    
    return tilemap


def create_level_2() -> TileMap:
    """
    Level 2: The Goblin Caves
    
    Underground cave system. Medium difficulty with tighter corridors,
    more enemies, and better loot.
    """
    tilemap = TileMap(18, 10, tile_size=12)
    
    # Fill with walls (underground)
    for y in range(10):
        for x in range(18):
            tilemap.set_tile(x, y, TileType.WALL)
    
    # Carve out cave system
    # Main entrance corridor
    for x in range(1, 6):
        tilemap.set_tile(x, 5, TileType.FLOOR)
        tilemap.set_tile(x, 4, TileType.FLOOR)
    
    # Central chamber
    for x in range(5, 10):
        for y in range(3, 7):
            tilemap.set_tile(x, y, TileType.FLOOR)
    
    # Northern passage
    for x in range(7, 12):
        tilemap.set_tile(x, 2, TileType.FLOOR)
        tilemap.set_tile(x, 1, TileType.FLOOR)
    
    # Eastern corridor
    for x in range(9, 15):
        tilemap.set_tile(x, 4, TileType.FLOOR)
        tilemap.set_tile(x, 5, TileType.FLOOR)
    
    # Treasure room (north)
    for x in range(11, 14):
        for y in range(1, 3):
            tilemap.set_tile(x, y, TileType.FLOOR)
    
    # Boss chamber (east)
    for x in range(14, 17):
        for y in range(3, 7):
            tilemap.set_tile(x, y, TileType.FLOOR)
    
    # Southern secret passage
    for y in range(5, 9):
        tilemap.set_tile(3, y, TileType.FLOOR)
    for x in range(3, 8):
        tilemap.set_tile(x, 8, TileType.FLOOR)
    
    # Underground stream
    tilemap.set_tile(6, 4, TileType.WATER)
    tilemap.set_tile(7, 4, TileType.WATER)
    tilemap.set_tile(7, 5, TileType.WATER)
    
    # Doors
    tilemap.set_tile(9, 4, TileType.DOOR)  # To boss chamber
    tilemap.set_tile(11, 2, TileType.DOOR)  # To treasure room
    
    # === POINTS OF INTEREST ===
    
    # Entrance
    tilemap.add_poi(PointOfInterest(
        grid_x=1, grid_y=5,
        name="Cave Entrance",
        description="Daylight streams in from outside.",
        event_type="exit",
        repeatable=True
    ))
    
    # Exit to Level 3
    tilemap.add_poi(PointOfInterest(
        grid_x=16, grid_y=5,
        name="Dark Descent",
        description="Stairs lead deeper into the mountain...",
        event_type="exit",
        repeatable=True
    ))
    
    # Goblin patrol
    tilemap.add_poi(PointOfInterest(
        grid_x=7, grid_y=5,
        name="Goblin Scout",
        description="A goblin spots you and raises the alarm!",
        event_type="encounter"
    ))
    
    # Goblin patrol 2
    tilemap.add_poi(PointOfInterest(
        grid_x=10, grid_y=2,
        name="Goblin Archers",
        description="Two goblin archers loose arrows at you!",
        event_type="encounter"
    ))
    
    # Mini-boss
    tilemap.add_poi(PointOfInterest(
        grid_x=15, grid_y=5,
        name="Goblin Chieftain",
        description="The goblin chief charges with a rusty sword!",
        event_type="encounter"
    ))
    
    # Treasure chest
    tilemap.add_poi(PointOfInterest(
        grid_x=12, grid_y=1,
        name="Iron Chest",
        description="A heavy chest filled with goblin plunder!",
        event_type="treasure"
    ))
    
    # Secret treasure
    tilemap.add_poi(PointOfInterest(
        grid_x=5, grid_y=8,
        name="Hidden Cache",
        description="You found a secret stash behind loose rocks!",
        event_type="treasure"
    ))
    
    # Healing pool
    tilemap.add_poi(PointOfInterest(
        grid_x=7, grid_y=4,
        name="Underground Spring",
        description="The cool water has healing properties.",
        event_type="story",
        repeatable=True
    ))
    
    # Prisoner NPC
    tilemap.add_poi(PointOfInterest(
        grid_x=8, grid_y=3,
        name="Captured Merchant",
        description="'Thank the gods! The goblins took everything, but I can tell you about the caves ahead.'",
        event_type="npc"
    ))
    
    return tilemap


def create_level_3() -> TileMap:
    """
    Level 3: The Dragon's Lair
    
    Deep dungeon with the final boss. Difficult layout with multiple
    hazards, strong enemies, and legendary treasure.
    """
    tilemap = TileMap(18, 10, tile_size=12)
    
    # Fill with walls
    for y in range(10):
        for x in range(18):
            tilemap.set_tile(x, y, TileType.WALL)
    
    # Entry chamber
    for x in range(1, 5):
        for y in range(4, 7):
            tilemap.set_tile(x, y, TileType.FLOOR)
    
    # Lava moat (water = lava visually, still blocks)
    for x in range(4, 6):
        for y in range(3, 8):
            tilemap.set_tile(x, y, TileType.WATER)
    # Bridge across
    tilemap.set_tile(5, 5, TileType.PATH)
    
    # Winding corridor
    for x in range(5, 9):
        tilemap.set_tile(x, 5, TileType.FLOOR)
    for y in range(2, 6):
        tilemap.set_tile(8, y, TileType.FLOOR)
    for x in range(8, 12):
        tilemap.set_tile(x, 2, TileType.FLOOR)
    
    # Guard chamber
    for x in range(10, 13):
        for y in range(1, 4):
            tilemap.set_tile(x, y, TileType.FLOOR)
    
    # More lava
    for y in range(4, 8):
        tilemap.set_tile(10, y, TileType.WATER)
        tilemap.set_tile(11, y, TileType.WATER)
    
    # Southern passage (around lava)
    for x in range(7, 10):
        tilemap.set_tile(x, 8, TileType.FLOOR)
    for y in range(6, 9):
        tilemap.set_tile(9, y, TileType.FLOOR)
    
    # Dragon's throne room
    for x in range(12, 17):
        for y in range(3, 8):
            tilemap.set_tile(x, y, TileType.FLOOR)
    
    # Treasure alcoves
    tilemap.set_tile(16, 2, TileType.FLOOR)
    tilemap.set_tile(16, 8, TileType.FLOOR)
    
    # Throne platform (path = golden floor)
    tilemap.set_tile(15, 5, TileType.PATH)
    tilemap.set_tile(14, 5, TileType.PATH)
    tilemap.set_tile(15, 4, TileType.PATH)
    tilemap.set_tile(15, 6, TileType.PATH)
    
    # Doors
    tilemap.set_tile(12, 5, TileType.DOOR)
    
    # === POINTS OF INTEREST ===
    
    # Entrance
    tilemap.add_poi(PointOfInterest(
        grid_x=1, grid_y=5,
        name="Cavern Entrance",
        description="You can retreat to the goblin caves.",
        event_type="exit",
        repeatable=True
    ))
    
    # Victory exit
    tilemap.add_poi(PointOfInterest(
        grid_x=16, grid_y=5,
        name="Victory Portal",
        description="A magical portal appears after defeating the dragon!",
        event_type="exit",
        repeatable=True
    ))
    
    # Elite guard
    tilemap.add_poi(PointOfInterest(
        grid_x=8, grid_y=3,
        name="Dragonkin Guard",
        description="A fearsome dragonkin warrior blocks the path!",
        event_type="encounter"
    ))
    
    # More guards
    tilemap.add_poi(PointOfInterest(
        grid_x=11, grid_y=2,
        name="Dragon Cultists",
        description="Cultists chant dark magic and attack!",
        event_type="encounter"
    ))
    
    # THE BOSS
    tilemap.add_poi(PointOfInterest(
        grid_x=15, grid_y=5,
        name="Vermithrax the Red",
        description="THE DRAGON AWAKENS! Vermithrax roars and breathes fire!",
        event_type="encounter"
    ))
    
    # Legendary treasure
    tilemap.add_poi(PointOfInterest(
        grid_x=16, grid_y=2,
        name="Dragon's Hoard",
        description="Mountains of gold and a legendary weapon!",
        event_type="treasure"
    ))
    
    # More treasure
    tilemap.add_poi(PointOfInterest(
        grid_x=16, grid_y=8,
        name="Ancient Artifact",
        description="A glowing artifact of immense power!",
        event_type="treasure"
    ))
    
    # Trapped adventurer
    tilemap.add_poi(PointOfInterest(
        grid_x=9, grid_y=7,
        name="Dying Knight",
        description="'The dragon... too strong... take my sword... avenge me...'",
        event_type="story"
    ))
    
    # Healing shrine
    tilemap.add_poi(PointOfInterest(
        grid_x=3, grid_y=5,
        name="Ancient Shrine",
        description="An ancient shrine pulses with healing energy.",
        event_type="story",
        repeatable=True
    ))
    
    return tilemap


# =============================================================================
# MAP REGISTRY - Easy access to all maps
# =============================================================================

ALL_MAPS = {
    "tavern": create_tavern_map,
    "forest": create_forest_map,
    "level_1": create_level_1,
    "level_2": create_level_2,
    "level_3": create_level_3,
}

def get_map(name: str) -> TileMap:
    """Get a map by name."""
    if name in ALL_MAPS:
        return ALL_MAPS[name]()
    raise ValueError(f"Unknown map: {name}")

