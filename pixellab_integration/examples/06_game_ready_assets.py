#!/usr/bin/env python3
"""
Example 6: Game-Ready Asset Creation
Complete workflow for creating game-ready character assets
"""

import sys
sys.path.insert(0, '..')

from pixellab_client import PixelLabClient
import logging

logging.basicConfig(level=logging.INFO)


def create_complete_character_set(client, description, output_prefix):
    """
    Create a complete set of character assets for a game.

    Returns sprite sheets for:
    - 8 directional idle poses
    - 4 directional walk animations
    - 4 directional run animations
    - Attack animation
    - All combined into one master sheet
    """
    print(f"\nCreating complete asset set for: {description}")
    print("-" * 60)

    all_frames = []

    # Step 1: Generate base character
    print("1. Generating base character...")
    base = client.generate_character(
        description=description,
        width=64,
        height=64,
        no_background=True
    )

    # Step 2: 8-directional idle poses
    print("2. Creating 8-directional idle poses...")
    directions = ['north', 'northeast', 'east', 'southeast',
                  'south', 'southwest', 'west', 'northwest']

    idle_frames = []
    for direction in directions:
        idle = client.generate_character(
            description=description,
            width=64,
            height=64,
            direction=direction,
            no_background=True
        )
        idle_frames.append(idle)

    idle_sheet = client.create_sprite_sheet(
        idle_frames,
        columns=4,
        filename=f"{output_prefix}_idle_8dir.png"
    )
    all_frames.extend(idle_frames)

    # Step 3: Walking animations for 4 directions
    print("3. Creating walking animations...")
    walk_frames = []

    for direction in ['north', 'east', 'south', 'west']:
        frames = client.animate_character_text(
            reference_image=base,
            description=description,
            action="walk",
            direction=direction,
            n_frames=4
        )
        walk_frames.extend(frames)

    walk_sheet = client.create_sprite_sheet(
        walk_frames,
        columns=4,
        filename=f"{output_prefix}_walk_4dir.png"
    )
    all_frames.extend(walk_frames)

    # Step 4: Running animations
    print("4. Creating running animations...")
    run_frames = []

    for direction in ['north', 'east', 'south', 'west']:
        frames = client.animate_character_text(
            reference_image=base,
            description=description,
            action="run",
            direction=direction,
            n_frames=4
        )
        run_frames.extend(frames)

    run_sheet = client.create_sprite_sheet(
        run_frames,
        columns=4,
        filename=f"{output_prefix}_run_4dir.png"
    )
    all_frames.extend(run_frames)

    # Step 5: Special actions
    print("5. Creating special action animations...")

    # Attack
    attack_frames = client.animate_character_text(
        reference_image=base,
        description=description,
        action="attack",
        n_frames=6
    )

    # Idle breathing
    idle_anim = client.animate_character_text(
        reference_image=base,
        description=description,
        action="idle breathing",
        n_frames=4
    )

    special_frames = attack_frames + idle_anim
    special_sheet = client.create_sprite_sheet(
        special_frames,
        columns=5,
        filename=f"{output_prefix}_special.png"
    )
    all_frames.extend(special_frames)

    # Step 6: Create master sprite sheet
    print("6. Creating master sprite sheet...")
    master_sheet = client.create_sprite_sheet(
        all_frames,
        columns=8,
        filename=f"{output_prefix}_MASTER.png"
    )

    print(f"\n✓ Complete asset set created!")
    print(f"  - Total frames: {len(all_frames)}")
    print(f"  - Idle poses: 8")
    print(f"  - Walk frames: 16 (4 per direction)")
    print(f"  - Run frames: 16 (4 per direction)")
    print(f"  - Special: {len(special_frames)}")

    return {
        'idle': idle_frames,
        'walk': walk_frames,
        'run': run_frames,
        'special': special_frames,
        'all': all_frames
    }


def main():
    API_KEY = "your-api-key-here"
    client = PixelLabClient(
        api_key=API_KEY,
        auto_save=True,
        save_dir="outputs/game_assets"
    )

    print("=" * 60)
    print("PIXELLAB - GAME-READY ASSET CREATION")
    print("=" * 60)

    # Example 1: Complete Hero Character
    print("\n" + "=" * 60)
    print("CREATING HERO CHARACTER ASSET SET")
    print("=" * 60)

    hero_assets = create_complete_character_set(
        client,
        description="pixel art hero knight with sword and shield",
        output_prefix="hero_knight"
    )

    # Example 2: Complete Enemy Character
    print("\n" + "=" * 60)
    print("CREATING ENEMY CHARACTER ASSET SET")
    print("=" * 60)

    enemy_assets = create_complete_character_set(
        client,
        description="pixel art goblin enemy with club",
        output_prefix="goblin_enemy"
    )

    # Example 3: NPC Character
    print("\n" + "=" * 60)
    print("CREATING NPC CHARACTER ASSET SET")
    print("=" * 60)

    npc_assets = create_complete_character_set(
        client,
        description="pixel art merchant NPC with robes",
        output_prefix="merchant_npc"
    )

    print("\n" + "=" * 60)
    print("ASSET CREATION COMPLETE!")
    print("=" * 60)
    print("\n✓ All game-ready assets saved to: outputs/game_assets/")
    print("\nEach character includes:")
    print("  - 8-directional idle poses")
    print("  - 4-directional walk animations (16 frames)")
    print("  - 4-directional run animations (16 frames)")
    print("  - Special action animations")
    print("  - Master sprite sheet with all frames")
    print("\nReady to import into your game engine!")
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
