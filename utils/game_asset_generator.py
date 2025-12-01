#!/usr/bin/env python3
"""
Game Asset Generator - Automated D&D Asset Creation with PixelLab

This utility helps generate complete character sprite sets for the AI-DnD game,
including 8-directional sprites, walking animations, and action animations.

Usage:
    python utils/game_asset_generator.py --character "elven ranger" --output assets/characters/
    python utils/game_asset_generator.py --npc "goblin warrior" --animations walk,attack
    python utils/game_asset_generator.py --batch characters.json
"""

import argparse
import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

# Add parent directory to path for imports
SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPT_DIR.parent
sys.path.insert(0, str(ROOT_DIR))

from pixellab_integration.pixellab_client import PixelLabClient, create_8_directional_character
from PIL import Image

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GameAssetGenerator:
    """Generate complete game-ready pixel art assets using PixelLab."""

    def __init__(self, api_key: str, output_dir: str = "assets"):
        """
        Initialize the asset generator.

        Args:
            api_key: PixelLab API key
            output_dir: Base directory for saving generated assets
        """
        self.client = PixelLabClient(api_key=api_key, auto_save=False)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Asset generator initialized. Output: {self.output_dir}")

    def generate_character_set(
        self,
        description: str,
        character_name: str,
        size: int = 64,
        include_animations: bool = True,
        animation_types: Optional[List[str]] = None
    ) -> Dict[str, Path]:
        """
        Generate a complete character asset set.

        Args:
            description: Character description for AI generation
            character_name: Name for organizing files
            size: Sprite size (width and height)
            include_animations: Whether to generate animations
            animation_types: List of animation types (walk, run, attack, idle)

        Returns:
            Dictionary mapping asset types to file paths
        """
        if animation_types is None:
            animation_types = ["walk", "idle"]

        char_dir = self.output_dir / character_name.lower().replace(" ", "_")
        char_dir.mkdir(parents=True, exist_ok=True)

        generated_assets = {}

        logger.info(f"Generating 8-directional sprites for '{description}'...")

        # Generate 8-directional sprites
        directions = {
            'north': 'north',
            'northeast': 'northeast',
            'east': 'east',
            'southeast': 'southeast',
            'south': 'south',
            'southwest': 'southwest',
            'west': 'west',
            'northwest': 'northwest'
        }

        direction_images = {}
        for direction, dir_name in directions.items():
            logger.info(f"  Generating {direction} facing sprite...")
            sprite = self.client.generate_character(
                description=description,
                width=size,
                height=size,
                direction=direction,
                no_background=True
            )

            sprite_path = char_dir / f"{direction}.png"
            sprite.save(sprite_path, "PNG")
            direction_images[direction] = sprite
            generated_assets[f"sprite_{direction}"] = sprite_path
            logger.info(f"    Saved: {sprite_path}")

        # Create sprite sheet
        logger.info("Creating sprite sheet...")
        sprite_sheet = self._create_8_direction_sheet(direction_images, size)
        sheet_path = char_dir / "spritesheet_8dir.png"
        sprite_sheet.save(sheet_path, "PNG")
        generated_assets["spritesheet_8dir"] = sheet_path
        logger.info(f"  Saved: {sheet_path}")

        # Generate animations if requested
        if include_animations:
            for action in animation_types:
                logger.info(f"Generating {action} animation...")
                anim_dir = char_dir / "animations" / action
                anim_dir.mkdir(parents=True, exist_ok=True)

                try:
                    # Use south-facing sprite as reference for animations
                    frames = self.client.animate_character_text(
                        reference_image=direction_images['south'],
                        description=description,
                        action=action,
                        n_frames=4,
                        width=size,
                        height=size,
                        direction='south',
                        view='side'
                    )

                    frame_paths = []
                    for i, frame in enumerate(frames):
                        frame_path = anim_dir / f"frame_{i:02d}.png"
                        frame.save(frame_path, "PNG")
                        frame_paths.append(frame_path)

                    # Create animation sprite sheet
                    anim_sheet = self.client.create_sprite_sheet(
                        frames=frames,
                        columns=4,
                        filename=f"{action}_animation.png"
                    )
                    anim_sheet_path = anim_dir / "spritesheet.png"
                    anim_sheet.save(anim_sheet_path, "PNG")

                    generated_assets[f"animation_{action}"] = anim_sheet_path
                    generated_assets[f"animation_{action}_frames"] = frame_paths
                    logger.info(f"  Saved: {anim_sheet_path}")

                except Exception as e:
                    logger.error(f"  Failed to generate {action} animation: {e}")

        # Create metadata file
        metadata = {
            "character_name": character_name,
            "description": description,
            "size": size,
            "generated_at": datetime.utcnow().isoformat(),
            "assets": {k: str(v) for k, v in generated_assets.items()}
        }

        metadata_path = char_dir / "metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)

        logger.info(f"✅ Character set complete! Assets saved to: {char_dir}")
        return generated_assets

    def _create_8_direction_sheet(
        self,
        direction_images: Dict[str, Image.Image],
        sprite_size: int
    ) -> Image.Image:
        """
        Create a sprite sheet with 8-directional sprites arranged in a grid.

        Layout:
        NW  N  NE
        W   -  E
        SW  S  SE
        """
        sheet_width = sprite_size * 3
        sheet_height = sprite_size * 3

        sheet = Image.new('RGBA', (sheet_width, sheet_height), (0, 0, 0, 0))

        positions = {
            'northwest': (0, 0),
            'north': (sprite_size, 0),
            'northeast': (sprite_size * 2, 0),
            'west': (0, sprite_size),
            'east': (sprite_size * 2, sprite_size),
            'southwest': (0, sprite_size * 2),
            'south': (sprite_size, sprite_size * 2),
            'southeast': (sprite_size * 2, sprite_size * 2),
        }

        for direction, (x, y) in positions.items():
            if direction in direction_images:
                sheet.paste(direction_images[direction], (x, y))

        return sheet

    def generate_npc_batch(self, npc_definitions: List[Dict]) -> Dict[str, Dict]:
        """
        Generate assets for multiple NPCs from a batch definition.

        Args:
            npc_definitions: List of NPC definition dicts with keys:
                - name: NPC name
                - description: Character description
                - size: Optional sprite size (default: 64)
                - animations: Optional list of animation types

        Returns:
            Dictionary mapping NPC names to their generated assets
        """
        results = {}

        for i, npc in enumerate(npc_definitions, 1):
            name = npc.get('name', f'npc_{i}')
            description = npc.get('description', 'generic character')
            size = npc.get('size', 64)
            animations = npc.get('animations', ['walk'])

            logger.info(f"\n[{i}/{len(npc_definitions)}] Generating assets for: {name}")

            try:
                assets = self.generate_character_set(
                    description=description,
                    character_name=name,
                    size=size,
                    include_animations=True,
                    animation_types=animations
                )
                results[name] = {
                    'status': 'success',
                    'assets': assets
                }
            except Exception as e:
                logger.error(f"Failed to generate {name}: {e}")
                results[name] = {
                    'status': 'error',
                    'error': str(e)
                }

        return results


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Generate game-ready pixel art assets for AI-DnD'
    )

    parser.add_argument(
        '--character',
        help='Generate a player character (e.g., "elven ranger")'
    )

    parser.add_argument(
        '--npc',
        help='Generate an NPC (e.g., "goblin warrior")'
    )

    parser.add_argument(
        '--batch',
        help='Path to JSON file with batch character definitions'
    )

    parser.add_argument(
        '--output',
        default='assets/generated',
        help='Output directory for generated assets'
    )

    parser.add_argument(
        '--size',
        type=int,
        default=64,
        help='Sprite size in pixels (default: 64)'
    )

    parser.add_argument(
        '--animations',
        default='walk,idle',
        help='Comma-separated list of animations (default: walk,idle)'
    )

    parser.add_argument(
        '--api-key',
        default=os.getenv('PIXELLAB_API_KEY'),
        help='PixelLab API key (or set PIXELLAB_API_KEY env var)'
    )

    args = parser.parse_args()

    if not args.api_key:
        logger.error("❌ PIXELLAB_API_KEY not found. Set it in .env or use --api-key")
        return 1

    generator = GameAssetGenerator(
        api_key=args.api_key,
        output_dir=args.output
    )

    animation_list = [a.strip() for a in args.animations.split(',')]

    if args.batch:
        # Batch mode
        batch_file = Path(args.batch)
        if not batch_file.exists():
            logger.error(f"❌ Batch file not found: {batch_file}")
            return 1

        with open(batch_file, 'r') as f:
            npc_definitions = json.load(f)

        logger.info(f"🚀 Starting batch generation of {len(npc_definitions)} characters...")
        results = generator.generate_npc_batch(npc_definitions)

        # Print summary
        successful = sum(1 for r in results.values() if r['status'] == 'success')
        logger.info(f"\n✅ Batch complete: {successful}/{len(results)} successful")

    elif args.character or args.npc:
        # Single character mode
        description = args.character or args.npc
        char_type = 'character' if args.character else 'npc'
        name = description.replace(' ', '_')

        logger.info(f"🚀 Generating {char_type}: {description}")
        generator.generate_character_set(
            description=description,
            character_name=name,
            size=args.size,
            include_animations=True,
            animation_types=animation_list
        )
    else:
        parser.print_help()
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
