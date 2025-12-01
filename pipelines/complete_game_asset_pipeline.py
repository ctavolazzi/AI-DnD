#!/usr/bin/env python3
"""
Complete Game Asset Pipeline

Advanced workflow combining multiple PixelLab API features to create
production-ready game assets including:
- Characters with 8-directional sprites
- Multiple animation sets (walk, idle, attack, run, etc.)
- NPCs and enemies
- Environmental objects with rotation views
- Tilesets and terrain elements

This pipeline demonstrates:
1. Batch character generation
2. Multi-directional sprite creation using rotation
3. Animation generation for all directions
4. Sprite sheet optimization
5. Asset organization and metadata generation

Usage:
    python pipelines/complete_game_asset_pipeline.py --project "my-rpg"
    python pipelines/complete_game_asset_pipeline.py --character "warrior" --animations walk,attack,idle
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from PIL import Image
from dotenv import load_dotenv
from pixellab_integration.pixellab_client import PixelLabClient

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()


class GameAssetPipeline:
    """
    Advanced pipeline for creating complete game asset packages.

    This class orchestrates multiple PixelLab API calls to create
    production-ready game assets with proper organization and metadata.
    """

    # Standard directions for top-down games
    DIRECTIONS_8 = ['north', 'north-east', 'east', 'south-east',
                    'south', 'south-west', 'west', 'north-west']

    DIRECTIONS_4 = ['north', 'east', 'south', 'west']

    def __init__(
        self,
        api_key: str,
        project_name: str = "game_assets",
        output_root: str = "game_assets"
    ):
        """
        Initialize the asset pipeline.

        Args:
            api_key: PixelLab API key
            project_name: Name of the game project
            output_root: Root directory for outputs
        """
        self.client = PixelLabClient(api_key, auto_save=False)
        self.project_name = project_name
        self.output_root = Path(output_root) / project_name
        self.output_root.mkdir(parents=True, exist_ok=True)

        # Create subdirectories
        self.dirs = {
            "characters": self.output_root / "characters",
            "npcs": self.output_root / "npcs",
            "enemies": self.output_root / "enemies",
            "objects": self.output_root / "objects",
            "terrain": self.output_root / "terrain",
            "effects": self.output_root / "effects",
            "spritesheets": self.output_root / "spritesheets"
        }

        for dir_path in self.dirs.values():
            dir_path.mkdir(parents=True, exist_ok=True)

        logger.info(f"Pipeline initialized for project: {project_name}")
        logger.info(f"Output directory: {self.output_root}")

    # ========== CHARACTER GENERATION ==========

    def create_complete_character(
        self,
        name: str,
        description: str,
        animations: List[str] = None,
        size: int = 64,
        directions: int = 8,
        category: str = "characters"
    ) -> Dict:
        """
        Create a complete character with all directions and animations.

        Args:
            name: Character name (used for file naming)
            description: Character description
            animations: List of animations (walk, idle, attack, run, etc.)
            size: Sprite size (16, 32, 64, 128, 256)
            directions: Number of directions (4 or 8)
            category: Asset category (characters, npcs, enemies)

        Returns:
            Dictionary containing all generated assets
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"Creating Complete Character: {name}")
        logger.info(f"{'='*60}")

        animations = animations or ["idle", "walk"]
        direction_list = self.DIRECTIONS_8 if directions == 8 else self.DIRECTIONS_4

        character_dir = self.dirs[category] / name
        character_dir.mkdir(parents=True, exist_ok=True)

        assets = {
            "name": name,
            "description": description,
            "size": size,
            "directions": {},
            "animations": {},
            "spritesheets": {},
            "metadata": {}
        }

        # Step 1: Generate base character facing south
        logger.info(f"Step 1: Generating base character...")
        base_char = self.client.generate_character(
            description=description,
            width=size,
            height=size,
            direction="south",
            no_background=True,
            detail="highly detailed"
        )
        base_path = character_dir / f"{name}_base.png"
        base_char.save(base_path)
        logger.info(f"✓ Base character saved: {base_path}")

        # Step 2: Generate all directional views
        logger.info(f"Step 2: Generating {directions}-directional views...")
        for direction in direction_list:
            if direction == "south":
                assets["directions"][direction] = base_char
                continue

            rotated = self.client.rotate_character(
                image=base_char,
                from_direction="south",
                to_direction=direction,
                width=size,
                height=size
            )
            assets["directions"][direction] = rotated

            # Save individual direction
            dir_path = character_dir / "directions" / f"{name}_{direction}.png"
            dir_path.parent.mkdir(exist_ok=True)
            rotated.save(dir_path)
            logger.info(f"  ✓ {direction}")

        # Create directional sprite sheet
        direction_sheet = self.client.create_sprite_sheet(
            frames=list(assets["directions"].values()),
            columns=4,
            filename="temp.png"
        )
        sheet_path = character_dir / f"{name}_directions.png"
        direction_sheet.save(sheet_path)
        assets["spritesheets"]["directions"] = direction_sheet
        logger.info(f"✓ Direction sprite sheet: {sheet_path}")

        # Step 3: Generate animations
        logger.info(f"Step 3: Generating animations...")
        for animation in animations:
            logger.info(f"  Creating '{animation}' animation...")
            animation_frames = {}

            # For demonstration, we'll create animation for main 4 directions
            for direction in ["north", "east", "south", "west"]:
                logger.info(f"    {animation} - {direction}...")

                frames = self.client.animate_character_text(
                    reference_image=assets["directions"][direction],
                    description=description,
                    action=animation,
                    width=size,
                    height=size,
                    n_frames=4,
                    direction=direction
                )

                animation_frames[direction] = frames

                # Save individual frames
                for i, frame in enumerate(frames):
                    frame_path = character_dir / "animations" / animation / direction / f"frame_{i:02d}.png"
                    frame_path.parent.mkdir(parents=True, exist_ok=True)
                    frame.save(frame_path)

            assets["animations"][animation] = animation_frames

            # Create animation sprite sheet
            all_anim_frames = []
            for direction in ["north", "east", "south", "west"]:
                all_anim_frames.extend(animation_frames[direction])

            anim_sheet = self.client.create_sprite_sheet(
                frames=all_anim_frames,
                columns=4,
                filename="temp.png"
            )
            anim_sheet_path = character_dir / f"{name}_{animation}_sheet.png"
            anim_sheet.save(anim_sheet_path)
            assets["spritesheets"][animation] = anim_sheet
            logger.info(f"  ✓ {animation} sprite sheet: {anim_sheet_path}")

        # Step 4: Generate metadata
        logger.info(f"Step 4: Generating metadata...")
        metadata = {
            "name": name,
            "description": description,
            "size": size,
            "directions": len(direction_list),
            "animations": animations,
            "created": datetime.now().isoformat(),
            "files": {
                "base": str(base_path.relative_to(self.output_root)),
                "direction_sheet": str(sheet_path.relative_to(self.output_root)),
                "animation_sheets": {
                    anim: str((character_dir / f"{name}_{anim}_sheet.png").relative_to(self.output_root))
                    for anim in animations
                }
            },
            "sprite_info": {
                "frame_size": [size, size],
                "directions": direction_list,
                "animations": {
                    anim: {"frames": 4, "directions": 4}
                    for anim in animations
                }
            }
        }

        metadata_path = character_dir / f"{name}_metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        logger.info(f"✓ Metadata saved: {metadata_path}")

        assets["metadata"] = metadata

        logger.info(f"\n✓ Complete! Character '{name}' assets generated")
        logger.info(f"  Location: {character_dir}")
        logger.info(f"  Directions: {directions}")
        logger.info(f"  Animations: {', '.join(animations)}")

        return assets

    # ========== ENVIRONMENT GENERATION ==========

    def create_object_rotations(
        self,
        name: str,
        description: str,
        size: int = 64,
        views: int = 4
    ) -> Dict:
        """
        Create an environmental object with multiple rotation views.

        Args:
            name: Object name
            description: Object description
            size: Sprite size
            views: Number of rotation views

        Returns:
            Dictionary containing generated views
        """
        logger.info(f"\nCreating Object: {name}")

        object_dir = self.dirs["objects"] / name
        object_dir.mkdir(parents=True, exist_ok=True)

        # Generate base object
        logger.info("Generating base object...")
        base = self.client.generate_character(
            description=description,
            width=size,
            height=size,
            no_background=True,
            isometric=True,
            detail="highly detailed"
        )

        views_dict = {"0": base}

        # Generate rotated views
        angles = [90, 180, 270] if views == 4 else [45, 90, 135, 180, 225, 270, 315]

        for angle in angles[:views-1]:
            logger.info(f"  Rotating to {angle}°...")
            rotated = self.client.rotate_character(
                image=base,
                from_direction="south",
                direction_change=angle,
                width=size,
                height=size
            )
            views_dict[str(angle)] = rotated

        # Create sprite sheet
        rotation_sheet = self.client.create_sprite_sheet(
            frames=list(views_dict.values()),
            columns=views,
            filename="temp.png"
        )

        sheet_path = object_dir / f"{name}_rotations.png"
        rotation_sheet.save(sheet_path)

        logger.info(f"✓ Object rotations saved: {sheet_path}")

        return {
            "name": name,
            "views": views_dict,
            "sprite_sheet": rotation_sheet
        }

    # ========== BATCH PROCESSING ==========

    def batch_create_party(
        self,
        party_config: List[Dict]
    ) -> Dict:
        """
        Create a complete party of characters.

        Args:
            party_config: List of character configurations

        Example:
            [
                {"name": "warrior", "description": "knight with sword", "animations": ["walk", "attack"]},
                {"name": "mage", "description": "wizard with staff", "animations": ["walk", "cast"]},
                ...
            ]
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"BATCH: Creating Party of {len(party_config)} Characters")
        logger.info(f"{'='*60}")

        results = {}

        for i, char_config in enumerate(party_config, 1):
            logger.info(f"\n[{i}/{len(party_config)}] Processing: {char_config['name']}")

            try:
                assets = self.create_complete_character(
                    name=char_config["name"],
                    description=char_config["description"],
                    animations=char_config.get("animations", ["walk", "idle"]),
                    size=char_config.get("size", 64),
                    directions=char_config.get("directions", 8),
                    category=char_config.get("category", "characters")
                )
                results[char_config["name"]] = assets
            except Exception as e:
                logger.error(f"Failed to create {char_config['name']}: {e}")
                results[char_config["name"]] = {"error": str(e)}

        # Create party manifest
        manifest = {
            "project": self.project_name,
            "created": datetime.now().isoformat(),
            "characters": len(party_config),
            "party": results
        }

        manifest_path = self.output_root / "party_manifest.json"
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)

        logger.info(f"\n✓ Party creation complete!")
        logger.info(f"  Manifest: {manifest_path}")

        return results

    # ========== UTILITY METHODS ==========

    def check_balance(self):
        """Check API balance before starting."""
        balance = self.client.get_balance()
        logger.info(f"API Balance: ${balance['usd']:.2f} USD")
        return balance


def main():
    """Run the game asset pipeline."""
    parser = argparse.ArgumentParser(description="Complete Game Asset Pipeline")
    parser.add_argument("--project", default="my_game", help="Project name")
    parser.add_argument("--api-key", help="PixelLab API key")
    parser.add_argument("--character", help="Single character to create")
    parser.add_argument("--description", help="Character description")
    parser.add_argument("--animations", default="walk,idle", help="Comma-separated animations")
    parser.add_argument("--size", type=int, default=64, help="Sprite size")
    parser.add_argument("--directions", type=int, default=8, choices=[4, 8], help="Number of directions")
    parser.add_argument("--batch", help="Path to batch config JSON")
    parser.add_argument("--demo", action="store_true", help="Run demo with sample party")

    args = parser.parse_args()

    # Get API key
    api_key = args.api_key or os.getenv("PIXELLAB_API_KEY")
    if not api_key:
        logger.error("No API key provided. Use --api-key or set PIXELLAB_API_KEY")
        sys.exit(1)

    # Initialize pipeline
    pipeline = GameAssetPipeline(api_key, args.project)

    # Check balance
    pipeline.check_balance()

    if args.demo:
        # Run demo with sample party
        logger.info("Running DEMO mode with sample party...")
        party = [
            {
                "name": "hero_warrior",
                "description": "heroic knight in shining armor with sword",
                "animations": ["walk", "attack", "idle"],
                "category": "characters"
            },
            {
                "name": "wizard_npc",
                "description": "old wizard with purple robes and staff",
                "animations": ["walk", "idle"],
                "category": "npcs"
            },
            {
                "name": "goblin_enemy",
                "description": "small green goblin with crude weapon",
                "animations": ["walk", "attack"],
                "size": 48,
                "category": "enemies"
            }
        ]
        pipeline.batch_create_party(party)

    elif args.batch:
        # Batch mode from config file
        with open(args.batch) as f:
            config = json.load(f)
        pipeline.batch_create_party(config)

    elif args.character and args.description:
        # Single character mode
        animations = args.animations.split(",")
        pipeline.create_complete_character(
            name=args.character,
            description=args.description,
            animations=animations,
            size=args.size,
            directions=args.directions
        )

    else:
        logger.error("Please provide either: --character + --description, --batch <file>, or --demo")
        parser.print_help()
        sys.exit(1)

    logger.info(f"\n{'='*60}")
    logger.info(f"Pipeline Complete!")
    logger.info(f"{'='*60}")
    logger.info(f"Assets saved to: {pipeline.output_root}")


if __name__ == "__main__":
    main()
