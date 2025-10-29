#!/usr/bin/env python3
"""
Example 3: Multi-Directional Characters
Create characters facing different directions for top-down games
"""

import sys
sys.path.insert(0, '..')

from pixellab_client import PixelLabClient, create_8_directional_character
import logging

logging.basicConfig(level=logging.INFO)


def main():
    API_KEY = "your-api-key-here"
    client = PixelLabClient(
        api_key=API_KEY,
        auto_save=True,
        save_dir="outputs/directional"
    )

    print("=" * 60)
    print("PIXELLAB - MULTI-DIRECTIONAL CHARACTERS")
    print("=" * 60)

    # Example 1: 4-directional character (cardinal directions)
    print("\n1. Creating 4-directional character...")
    directions_4 = client.batch_generate_directions(
        description="pixel art knight character",
        directions=['north', 'south', 'east', 'west'],
        width=64,
        height=64,
        no_background=True
    )
    print(f"   Generated {len(directions_4)} directional views")

    # Create a sprite sheet with all directions
    frames_4 = list(directions_4.values())
    sheet_4 = client.create_sprite_sheet(
        frames_4,
        columns=4,
        filename="knight_4directions.png"
    )
    print("   4-direction sprite sheet created")

    # Example 2: 8-directional character (all directions)
    print("\n2. Creating 8-directional character...")
    directions_8 = create_8_directional_character(
        client,
        description="pixel art wizard character",
        width=64,
        height=64
    )
    print(f"   Generated {len(directions_8)} directional views")

    # Create sprite sheet
    frames_8 = list(directions_8.values())
    sheet_8 = client.create_sprite_sheet(
        frames_8,
        columns=4,
        filename="wizard_8directions.png"
    )
    print("   8-direction sprite sheet created")

    # Example 3: Directional walking animations
    print("\n3. Creating directional walking animations...")

    # Generate base character
    base = client.generate_character(
        description="pixel art archer character",
        width=64,
        height=64,
        no_background=True
    )

    # Animate in each cardinal direction
    all_walk_frames = []
    for direction in ['north', 'east', 'south', 'west']:
        print(f"   Animating walk {direction}...")
        frames = client.animate_character_text(
            reference_image=base,
            description="pixel art archer character",
            action="walk",
            direction=direction,
            n_frames=4
        )
        all_walk_frames.extend(frames)

    # Create complete directional walk sprite sheet
    walk_sheet = client.create_sprite_sheet(
        all_walk_frames,
        columns=4,
        filename="archer_directional_walks.png"
    )
    print(f"   Created sprite sheet with {len(all_walk_frames)} frames")

    print("\n✓ All directional sprites saved to: outputs/directional/")
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
