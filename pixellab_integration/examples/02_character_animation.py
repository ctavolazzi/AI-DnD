#!/usr/bin/env python3
"""
Example 2: Character Animation
Demonstrates creating animated sprites with various actions
"""

import sys
import os
sys.path.insert(0, '..')

from pixellab_client import PixelLabClient, create_walking_animation
import logging

logging.basicConfig(level=logging.INFO)


def main():
    API_KEY = os.getenv("PIXELLAB_API_KEY")
    if not API_KEY:
        raise ValueError(
            "PIXELLAB_API_KEY environment variable not set.\n"
            "Get your API key from https://www.pixellab.ai/vibe-coding\n"
            "Then set it: export PIXELLAB_API_KEY=your-api-key"
        )
    client = PixelLabClient(
        api_key=API_KEY,
        auto_save=True,
        save_dir="outputs/animations"
    )

    print("=" * 60)
    print("PIXELLAB - CHARACTER ANIMATION")
    print("=" * 60)

    # First, create a base character
    print("\n1. Creating base character...")
    base_character = client.generate_character(
        description="pixel art hero character",
        width=64,
        height=64,
        no_background=True
    )
    print("   Base character created")

    # Example 1: Walking animation
    print("\n2. Creating walking animation...")
    walk_frames = client.animate_character_text(
        reference_image=base_character,
        description="pixel art hero character",
        action="walk",
        n_frames=4,
        view='side',
        direction='east'
    )
    print(f"   Generated {len(walk_frames)} frames")

    # Create sprite sheet from walking animation
    walk_sheet = client.create_sprite_sheet(
        walk_frames,
        columns=4,
        filename="walk_spritesheet.png"
    )
    print("   Sprite sheet created")

    # Example 2: Running animation
    print("\n3. Creating running animation...")
    run_frames = client.animate_character_text(
        reference_image=base_character,
        description="pixel art hero character",
        action="run",
        n_frames=4,
        view='side',
        direction='east'
    )
    print(f"   Generated {len(run_frames)} frames")

    # Example 3: Attack animation
    print("\n4. Creating attack animation...")
    attack_frames = client.animate_character_text(
        reference_image=base_character,
        description="pixel art hero character",
        action="attack with sword",
        n_frames=6,
        view='side',
        direction='east'
    )
    print(f"   Generated {len(attack_frames)} frames")

    # Example 4: Idle animation
    print("\n5. Creating idle animation...")
    idle_frames = client.animate_character_text(
        reference_image=base_character,
        description="pixel art hero character",
        action="idle breathing",
        n_frames=4,
        view='side',
        direction='east'
    )
    print(f"   Generated {len(idle_frames)} frames")

    # Example 5: Create complete animation set
    print("\n6. Creating complete animation sprite sheet...")
    all_frames = walk_frames + run_frames + attack_frames + idle_frames
    complete_sheet = client.create_sprite_sheet(
        all_frames,
        columns=6,
        filename="complete_animations.png"
    )
    print(f"   Complete sprite sheet created with {len(all_frames)} frames")

    print("\n✓ All animations saved to: outputs/animations/")
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
