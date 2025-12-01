#!/usr/bin/env python3
"""
PixelLab API Examples - Complete Feature Showcase

Demonstrates all available PixelLab API endpoints and features:
- Image Generation (PixFlux and BitForge)
- Text-based Animation
- Skeleton-based Animation
- Character Rotation
- Image Inpainting
- Skeleton Estimation
- Balance Checking

Requirements:
    pip install pixellab pillow python-dotenv

Usage:
    python examples/pixellab_api_examples.py --example all
    python examples/pixellab_api_examples.py --example generation
    python examples/pixellab_api_examples.py --example animation
"""

import argparse
import logging
import os
import sys
from pathlib import Path
from typing import List

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from PIL import Image
from dotenv import load_dotenv
from pixellab_integration.pixellab_client import PixelLabClient

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


class PixelLabExamples:
    """Collection of examples demonstrating PixelLab API capabilities."""

    def __init__(self, api_key: str, output_dir: str = "examples/outputs"):
        """Initialize with API key and output directory."""
        self.client = PixelLabClient(api_key, auto_save=True, save_dir=output_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Examples will save to: {self.output_dir}")

    # ========== EXAMPLE 1: Basic Image Generation (PixFlux) ==========

    def example_basic_generation(self):
        """
        Example 1: Generate basic pixel art images using PixFlux.

        PixFlux features:
        - Supports 32x32 to 400x400 images
        - Text-based generation
        - Transparent backgrounds
        - Custom color palettes
        - Detail and outline control
        """
        logger.info("\n=== Example 1: Basic Image Generation (PixFlux) ===")

        # Simple character generation
        logger.info("Generating a cute dragon...")
        dragon = self.client.generate_character(
            description="cute dragon",
            width=128,
            height=128,
            no_background=True,
            detail="highly detailed",
            outline="single color black outline"
        )
        logger.info("✓ Dragon generated")

        # Character with specific direction
        logger.info("Generating warrior facing east...")
        warrior = self.client.generate_character(
            description="heroic knight in shining armor with sword",
            width=64,
            height=64,
            direction="east",
            detail="medium detail",
            isometric=False
        )
        logger.info("✓ Warrior generated")

        # Isometric building
        logger.info("Generating isometric castle...")
        castle = self.client.generate_character(
            description="medieval castle with towers",
            width=128,
            height=128,
            isometric=True,
            detail="highly detailed",
            no_background=True
        )
        logger.info("✓ Castle generated")

        return {
            "dragon": dragon,
            "warrior": warrior,
            "castle": castle
        }

    # ========== EXAMPLE 2: Style-Based Generation (BitForge) ==========

    def example_style_generation(self):
        """
        Example 2: Generate images using style references with BitForge.

        BitForge features:
        - Maximum 200x200 images
        - Style image references
        - Inpainting support
        - Custom palettes
        """
        logger.info("\n=== Example 2: Style-Based Generation (BitForge) ===")

        # First create a reference style image
        logger.info("Creating style reference...")
        style_reference = self.client.generate_character(
            description="retro 8-bit pixel art character",
            width=64,
            height=64,
            outline="single color black outline"
        )

        # Generate new character matching the style
        logger.info("Generating character with matching style...")
        styled_character = self.client.generate_with_style(
            description="wizard with purple robes and staff",
            style_image=style_reference,
            width=64,
            height=64,
            style_strength=0.8,
            detail="highly detailed"
        )
        logger.info("✓ Styled character generated")

        return {
            "style_reference": style_reference,
            "styled_character": styled_character
        }

    # ========== EXAMPLE 3: Text-Based Animation ==========

    def example_text_animation(self):
        """
        Example 3: Create animations using text descriptions.

        Text Animation features:
        - 64x64 size (currently)
        - 2-20 frames (generates 4 at a time)
        - Multiple actions supported
        - Direction control
        """
        logger.info("\n=== Example 3: Text-Based Animation ===")

        # Generate base character
        logger.info("Generating base character...")
        mage = self.client.generate_character(
            description="human mage in blue robes",
            width=64,
            height=64,
            no_background=True
        )

        # Create walking animation
        logger.info("Creating walking animation...")
        walk_frames = self.client.animate_character_text(
            reference_image=mage,
            description="human mage",
            action="walk",
            width=64,
            height=64,
            n_frames=4,
            view="side",
            direction="south"
        )
        logger.info(f"✓ Generated {len(walk_frames)} walk frames")

        # Create attack animation
        logger.info("Creating attack animation...")
        attack_frames = self.client.animate_character_text(
            reference_image=mage,
            description="human mage",
            action="cast spell",
            width=64,
            height=64,
            n_frames=4,
            view="side",
            direction="south"
        )
        logger.info(f"✓ Generated {len(attack_frames)} attack frames")

        # Create sprite sheet
        logger.info("Creating sprite sheet...")
        all_frames = walk_frames + attack_frames
        sprite_sheet = self.client.create_sprite_sheet(
            frames=all_frames,
            columns=4,
            filename="mage_animations.png"
        )
        logger.info("✓ Sprite sheet created")

        return {
            "base": mage,
            "walk_frames": walk_frames,
            "attack_frames": attack_frames,
            "sprite_sheet": sprite_sheet
        }

    # ========== EXAMPLE 4: Skeleton-Based Animation ==========

    def example_skeleton_animation(self):
        """
        Example 4: Create animations using skeleton keypoints.

        Skeleton Animation features:
        - 16x16 to 256x256
        - Precise pose control
        - Automatic skeleton estimation
        - 4-frame output
        """
        logger.info("\n=== Example 4: Skeleton-Based Animation ===")

        # Generate character
        logger.info("Generating character for skeleton animation...")
        character = self.client.generate_character(
            description="pixel art warrior",
            width=64,
            height=64,
            no_background=True
        )

        # Estimate skeleton
        logger.info("Estimating character skeleton...")
        skeleton_data = self.client.estimate_skeleton(character)
        logger.info(f"✓ Skeleton estimated with {len(skeleton_data.get('skeleton_frame', {}).get('keypoints', []))} keypoints")

        # Note: For actual skeleton animation, you would modify the keypoints
        # to create different poses, then pass them to animate_character_skeleton
        # This is demonstrated in the advanced pipeline

        return {
            "character": character,
            "skeleton_data": skeleton_data
        }

    # ========== EXAMPLE 5: Character Rotation ==========

    def example_rotation(self):
        """
        Example 5: Rotate characters to different views and directions.

        Rotation features:
        - 16x16 to 128x128
        - 8 directions (N, NE, E, SE, S, SW, W, NW)
        - 3 views (side, low top-down, high top-down)
        - Degree-based rotation (-180 to 180)
        """
        logger.info("\n=== Example 5: Character Rotation ===")

        # Generate base character facing south
        logger.info("Generating base character...")
        base_character = self.client.generate_character(
            description="goblin warrior with axe",
            width=64,
            height=64,
            direction="south",
            no_background=True
        )

        # Rotate to different directions
        directions = ["east", "north", "west"]
        rotated_characters = {}

        for direction in directions:
            logger.info(f"Rotating character to face {direction}...")
            rotated = self.client.rotate_character(
                image=base_character,
                from_direction="south",
                to_direction=direction,
                width=64,
                height=64
            )
            rotated_characters[direction] = rotated

        logger.info(f"✓ Created {len(rotated_characters) + 1} directional views")

        # Create sprite sheet with all directions
        all_directions = [base_character] + list(rotated_characters.values())
        direction_sheet = self.client.create_sprite_sheet(
            frames=all_directions,
            columns=4,
            filename="goblin_directions.png"
        )

        return {
            "base": base_character,
            "rotated": rotated_characters,
            "direction_sheet": direction_sheet
        }

    # ========== EXAMPLE 6: Image Inpainting ==========

    def example_inpainting(self):
        """
        Example 6: Modify existing images using inpainting.

        Inpainting features:
        - Maximum 200x200
        - Masked region editing
        - Style preservation
        - Detail control
        """
        logger.info("\n=== Example 6: Image Inpainting ===")

        # Generate base character
        logger.info("Generating base character...")
        base = self.client.generate_character(
            description="simple knight character",
            width=64,
            height=64,
            no_background=True
        )

        # Create a mask for the weapon area (right side of image)
        logger.info("Creating mask for weapon modification...")
        mask = Image.new('L', (64, 64), 0)  # Black background
        # Draw white rectangle on right side where weapon would be
        from PIL import ImageDraw
        draw = ImageDraw.Draw(mask)
        draw.rectangle([40, 20, 60, 50], fill=255)  # White = area to inpaint

        # Inpaint new weapon
        logger.info("Inpainting magic sword...")
        with_sword = self.client.inpaint_image(
            description="glowing magic sword with blue flames",
            inpainting_image=base,
            mask_image=mask,
            width=64,
            height=64,
            detail="highly detailed"
        )
        logger.info("✓ Inpainting complete")

        return {
            "base": base,
            "mask": mask,
            "inpainted": with_sword
        }

    # ========== EXAMPLE 7: Complete Character Set ==========

    def example_complete_character(self):
        """
        Example 7: Create a complete character asset pack.

        Includes:
        - 8 directional views
        - Walking animation for each direction
        - Idle animation
        - Action animation
        """
        logger.info("\n=== Example 7: Complete Character Asset Pack ===")

        description = "elf ranger with bow"

        # Generate 8-directional views
        logger.info("Generating 8-directional character views...")
        directions = ['north', 'north-east', 'east', 'south-east',
                      'south', 'south-west', 'west', 'north-west']

        directional_views = self.client.batch_generate_directions(
            description=description,
            directions=directions,
            width=64,
            height=64,
            no_background=True
        )
        logger.info(f"✓ Generated {len(directional_views)} directional views")

        # Create walking animation for south direction
        logger.info("Creating walking animation...")
        walk_frames = self.client.animate_character_text(
            reference_image=directional_views['south'],
            description=description,
            action="walk",
            width=64,
            height=64,
            n_frames=4,
            direction="south"
        )
        logger.info(f"✓ Generated {len(walk_frames)} walk frames")

        # Create sprite sheets
        logger.info("Creating sprite sheets...")
        direction_sheet = self.client.create_sprite_sheet(
            frames=list(directional_views.values()),
            columns=4,
            filename="elf_directions.png"
        )
        walk_sheet = self.client.create_sprite_sheet(
            frames=walk_frames,
            columns=4,
            filename="elf_walk.png"
        )
        logger.info("✓ Sprite sheets created")

        return {
            "directional_views": directional_views,
            "walk_frames": walk_frames,
            "direction_sheet": direction_sheet,
            "walk_sheet": walk_sheet
        }

    # ========== EXAMPLE 8: Check Balance ==========

    def example_check_balance(self):
        """
        Example 8: Check API credit balance.
        """
        logger.info("\n=== Example 8: Check Balance ===")

        balance = self.client.get_balance()
        logger.info(f"Current balance: ${balance['usd']:.2f} USD")

        return balance


def main():
    """Run PixelLab API examples."""
    parser = argparse.ArgumentParser(description="PixelLab API Examples")
    parser.add_argument(
        "--example",
        choices=[
            "all", "generation", "style", "text-animation",
            "skeleton", "rotation", "inpainting", "complete", "balance"
        ],
        default="all",
        help="Which example to run"
    )
    parser.add_argument(
        "--api-key",
        help="PixelLab API key (or set PIXELLAB_API_KEY env var)"
    )
    parser.add_argument(
        "--output",
        default="examples/outputs",
        help="Output directory for generated images"
    )

    args = parser.parse_args()

    # Get API key
    api_key = args.api_key or os.getenv("PIXELLAB_API_KEY")
    if not api_key:
        logger.error("No API key provided. Use --api-key or set PIXELLAB_API_KEY environment variable")
        sys.exit(1)

    # Create examples instance
    examples = PixelLabExamples(api_key, args.output)

    # Run requested examples
    example_map = {
        "generation": examples.example_basic_generation,
        "style": examples.example_style_generation,
        "text-animation": examples.example_text_animation,
        "skeleton": examples.example_skeleton_animation,
        "rotation": examples.example_rotation,
        "inpainting": examples.example_inpainting,
        "complete": examples.example_complete_character,
        "balance": examples.example_check_balance
    }

    if args.example == "all":
        logger.info("Running ALL examples...")
        for name, func in example_map.items():
            try:
                func()
            except Exception as e:
                logger.error(f"Example '{name}' failed: {e}")
        logger.info("\n✓ All examples complete!")
    else:
        example_map[args.example]()
        logger.info(f"\n✓ Example '{args.example}' complete!")

    logger.info(f"\nOutputs saved to: {examples.output_dir}")


if __name__ == "__main__":
    main()
