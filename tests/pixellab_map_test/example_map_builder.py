#!/usr/bin/env python3
"""
Example: Build a Complete Game Map
Demonstrates creating a full game map with PixelLab-generated tiles
"""

import sys
sys.path.insert(0, '../../pixellab_integration')

from pixellab_client import PixelLabClient
from PIL import Image
import logging

logging.basicConfig(level=logging.INFO)


class MapBuilder:
    """Helper class for building game maps with PixelLab tiles."""

    def __init__(self, client: PixelLabClient, tile_size: int = 32):
        self.client = client
        self.tile_size = tile_size
        self.tile_cache = {}

    def generate_tile(self, description: str, cache_key: str = None) -> Image.Image:
        """Generate a tile with caching."""
        if cache_key is None:
            cache_key = description

        if cache_key in self.tile_cache:
            logging.info(f"Using cached tile: {cache_key}")
            return self.tile_cache[cache_key]

        logging.info(f"Generating tile: {description}")
        tile = self.client.generate_character(
            description=description,
            width=self.tile_size,
            height=self.tile_size,
            no_background=True
        )

        self.tile_cache[cache_key] = tile
        return tile

    def create_map(self, layout: list, tile_definitions: dict) -> Image.Image:
        """
        Create a map from a layout and tile definitions.

        Args:
            layout: 2D list of tile keys
            tile_definitions: Dict mapping tile keys to descriptions

        Returns:
            PIL Image of the complete map
        """
        height = len(layout)
        width = len(layout[0])

        map_image = Image.new(
            'RGBA',
            (width * self.tile_size, height * self.tile_size),
            (0, 0, 0, 0)
        )

        # Generate all unique tiles
        for tile_key, description in tile_definitions.items():
            self.generate_tile(description, tile_key)

        # Compose map
        for y, row in enumerate(layout):
            for x, tile_key in enumerate(row):
                if tile_key in self.tile_cache:
                    tile = self.tile_cache[tile_key]
                    map_image.paste(tile, (x * self.tile_size, y * self.tile_size))

        return map_image


def example_rpg_overworld():
    """Generate an RPG overworld map."""
    print("\n" + "="*60)
    print("EXAMPLE: RPG Overworld Map")
    print("="*60 + "\n")

    API_KEY = "your-api-key-here"
    client = PixelLabClient(
        api_key=API_KEY,
        auto_save=True,
        save_dir="map_outputs/rpg_overworld"
    )

    builder = MapBuilder(client, tile_size=32)

    # Define tile types
    tiles = {
        'G': "grass terrain pixel art top-down view",
        'W': "water terrain pixel art top-down view",
        'M': "mountain terrain pixel art top-down view",
        'F': "forest with trees pixel art top-down view",
        'P': "stone path pixel art top-down view",
        'T': "small town buildings pixel art top-down view",
        'C': "castle pixel art top-down view"
    }

    # Create map layout (12x12)
    layout = [
        ['W', 'W', 'W', 'M', 'M', 'M', 'M', 'F', 'F', 'G', 'G', 'G'],
        ['W', 'W', 'G', 'G', 'M', 'M', 'F', 'F', 'F', 'G', 'G', 'G'],
        ['G', 'G', 'G', 'P', 'P', 'M', 'F', 'F', 'G', 'G', 'T', 'G'],
        ['G', 'G', 'P', 'P', 'G', 'G', 'F', 'G', 'G', 'P', 'P', 'P'],
        ['G', 'F', 'P', 'G', 'G', 'G', 'G', 'G', 'P', 'P', 'G', 'G'],
        ['G', 'F', 'F', 'G', 'G', 'G', 'G', 'P', 'P', 'G', 'G', 'G'],
        ['G', 'G', 'F', 'G', 'C', 'C', 'P', 'P', 'G', 'G', 'F', 'F'],
        ['G', 'G', 'G', 'P', 'C', 'C', 'P', 'G', 'G', 'F', 'F', 'F'],
        ['G', 'G', 'P', 'P', 'P', 'P', 'G', 'G', 'G', 'G', 'F', 'F'],
        ['G', 'P', 'P', 'G', 'G', 'G', 'G', 'W', 'W', 'G', 'G', 'G'],
        ['G', 'P', 'G', 'G', 'T', 'G', 'G', 'W', 'W', 'W', 'G', 'G'],
        ['G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'W', 'W', 'W', 'W']
    ]

    print("Generating RPG overworld map (12x12 tiles)...")
    print("This will take a few minutes...\n")

    map_image = builder.create_map(layout, tiles)

    output_path = "map_outputs/rpg_overworld_map.png"
    map_image.save(output_path, "PNG")

    print(f"\n✓ Map generated successfully!")
    print(f"  Size: 12x12 tiles (384x384 pixels)")
    print(f"  Saved to: {output_path}")
    print(f"  Tiles generated: {len(tiles)}")


def example_dungeon_floor():
    """Generate a dungeon floor map."""
    print("\n" + "="*60)
    print("EXAMPLE: Dungeon Floor")
    print("="*60 + "\n")

    API_KEY = "your-api-key-here"
    client = PixelLabClient(
        api_key=API_KEY,
        auto_save=True,
        save_dir="map_outputs/dungeon"
    )

    builder = MapBuilder(client, tile_size=32)

    # Define dungeon tiles
    tiles = {
        '.': "stone dungeon floor pixel art top-down",
        '#': "stone dungeon wall pixel art top-down",
        'D': "wooden dungeon door pixel art top-down",
        'T': "treasure chest pixel art top-down",
        'S': "dungeon stairs pixel art top-down",
        'M': "dungeon monster spawn pixel art top-down"
    }

    # Create dungeon layout (10x10)
    layout = [
        ['#', '#', '#', '#', '#', '#', '#', '#', '#', '#'],
        ['#', '.', '.', '.', '#', 'T', '.', '.', '.', '#'],
        ['#', '.', '.', '.', 'D', '.', '.', 'M', '.', '#'],
        ['#', '.', '.', '.', '#', '.', '.', '.', '.', '#'],
        ['#', '#', 'D', '#', '#', '#', '#', 'D', '#', '#'],
        ['#', '.', '.', '.', '.', '.', '.', '.', '.', '#'],
        ['#', '.', 'M', '.', '.', 'T', '.', '.', '.', '#'],
        ['#', '.', '.', '.', '#', '#', '#', '.', '.', '#'],
        ['#', '.', '.', '.', '.', '.', '.', '.', 'S', '#'],
        ['#', '#', '#', '#', '#', '#', '#', '#', '#', '#']
    ]

    print("Generating dungeon floor map (10x10 tiles)...")
    print("This will take a few minutes...\n")

    map_image = builder.create_map(layout, tiles)

    output_path = "map_outputs/dungeon_floor_map.png"
    map_image.save(output_path, "PNG")

    print(f"\n✓ Dungeon generated successfully!")
    print(f"  Size: 10x10 tiles (320x320 pixels)")
    print(f"  Saved to: {output_path}")
    print(f"  Tiles generated: {len(tiles)}")


def example_platformer_level():
    """Generate a 2D platformer level."""
    print("\n" + "="*60)
    print("EXAMPLE: Platformer Level")
    print("="*60 + "\n")

    API_KEY = "your-api-key-here"
    client = PixelLabClient(
        api_key=API_KEY,
        auto_save=True,
        save_dir="map_outputs/platformer"
    )

    builder = MapBuilder(client, tile_size=32)

    # Define platformer tiles
    tiles = {
        '.': "empty space transparent",
        'G': "grass platform tile side view pixel art",
        'S': "stone platform tile side view pixel art",
        'C': "coin pixel art side view",
        'E': "enemy spawn side view pixel art",
        'F': "flag checkpoint side view pixel art"
    }

    # Create level layout (16x10)
    layout = [
        ['.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.', '.', '.', 'C', '.', '.', '.', '.', '.', '.', 'F', '.'],
        ['.', '.', '.', 'C', '.', '.', 'S', 'S', 'S', '.', '.', '.', 'S', 'S', 'S', 'S'],
        ['.', '.', 'G', 'G', '.', '.', '.', 'E', '.', '.', '.', '.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.', '.', '.', '.', '.', '.', 'C', '.', '.', '.', '.', '.'],
        ['.', 'C', '.', '.', '.', 'S', 'S', 'S', '.', '.', 'G', 'G', '.', '.', '.', '.'],
        ['.', 'G', 'G', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', 'C', '.', '.'],
        ['.', '.', '.', '.', 'E', '.', '.', '.', '.', 'G', 'G', 'G', 'G', 'G', 'G', '.'],
        ['.', '.', '.', 'G', 'G', 'G', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.'],
        ['G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G']
    ]

    print("Generating platformer level (16x10 tiles)...")
    print("This will take a few minutes...\n")

    map_image = builder.create_map(layout, tiles)

    output_path = "map_outputs/platformer_level.png"
    map_image.save(output_path, "PNG")

    print(f"\n✓ Level generated successfully!")
    print(f"  Size: 16x10 tiles (512x320 pixels)")
    print(f"  Saved to: {output_path}")
    print(f"  Tiles generated: {len(tiles)}")


def main():
    """Run all examples."""
    print("\n" + "="*70)
    print("PIXELLAB MAP BUILDER - EXAMPLES")
    print("="*70)
    print("\nThis script demonstrates how to build complete game maps using")
    print("PixelLab-generated tiles.")
    print("\nNOTE: Requires a valid PixelLab API key!")
    print("Get your key at: https://www.pixellab.ai/vibe-coding")
    print("\nUpdate API_KEY in this file, then run:")
    print("  python example_map_builder.py")
    print("="*70 + "\n")

    # Check for API key
    if "your-api-key-here" in open(__file__).read():
        print("⚠️  Please update API_KEY in this file with your actual key")
        print("   Get your key at: https://www.pixellab.ai/vibe-coding")
        return

    # Run examples
    try:
        example_rpg_overworld()
        example_dungeon_floor()
        example_platformer_level()

        print("\n" + "="*70)
        print("ALL EXAMPLES COMPLETE!")
        print("="*70)
        print("\nCheck the map_outputs/ directory for your generated maps.")
        print("Use these maps in your game projects!\n")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
