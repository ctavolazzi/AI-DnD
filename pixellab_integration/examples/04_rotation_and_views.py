#!/usr/bin/env python3
"""
Example 4: Rotation and View Changes
Rotate characters and change camera views
"""

import sys
sys.path.insert(0, '..')

from pixellab_client import PixelLabClient
import logging

logging.basicConfig(level=logging.INFO)


def main():
    API_KEY = "your-api-key-here"
    client = PixelLabClient(
        api_key=API_KEY,
        auto_save=True,
        save_dir="outputs/rotations"
    )

    print("=" * 60)
    print("PIXELLAB - ROTATION AND VIEW CHANGES")
    print("=" * 60)

    # Create a base character
    print("\n1. Creating base character (side view, facing east)...")
    base_char = client.generate_character(
        description="pixel art robot character",
        width=64,
        height=64,
        view='side',
        direction='east',
        no_background=True
    )
    print("   Base character created")

    # Example 1: Rotate to different directions
    print("\n2. Rotating to different directions...")

    east = base_char  # Already facing east
    west = client.rotate_character(
        base_char,
        from_direction='east',
        to_direction='west'
    )
    north = client.rotate_character(
        base_char,
        from_direction='east',
        to_direction='north'
    )
    south = client.rotate_character(
        base_char,
        from_direction='east',
        to_direction='south'
    )

    print("   Created all 4 cardinal directions")

    # Create sprite sheet
    direction_frames = [north, east, south, west]
    direction_sheet = client.create_sprite_sheet(
        direction_frames,
        columns=4,
        filename="robot_all_directions.png"
    )

    # Example 2: Change camera views
    print("\n3. Changing camera views...")

    front_view = client.rotate_character(
        base_char,
        from_view='side',
        to_view='front'
    )

    back_view = client.rotate_character(
        base_char,
        from_view='side',
        to_view='back'
    )

    three_quarter = client.rotate_character(
        base_char,
        from_view='side',
        to_view='3/4'
    )

    print("   Created multiple camera views")

    # Create view comparison sheet
    view_frames = [front_view, three_quarter, base_char, back_view]
    view_sheet = client.create_sprite_sheet(
        view_frames,
        columns=4,
        filename="robot_all_views.png"
    )

    # Example 3: Complete rotation set
    print("\n4. Creating complete 360° rotation...")

    rotation_frames = []
    directions = ['north', 'northeast', 'east', 'southeast',
                  'south', 'southwest', 'west', 'northwest']

    current = base_char
    for i, direction in enumerate(directions[1:], 1):  # Skip first (already have it)
        rotated = client.rotate_character(
            current,
            from_direction=directions[i-1],
            to_direction=direction
        )
        rotation_frames.append(rotated)
        current = rotated

    rotation_frames.insert(0, base_char)  # Add original at start

    rotation_sheet = client.create_sprite_sheet(
        rotation_frames,
        columns=4,
        filename="robot_360_rotation.png"
    )
    print(f"   Created 360° rotation with {len(rotation_frames)} frames")

    print("\n✓ All rotations saved to: outputs/rotations/")
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
