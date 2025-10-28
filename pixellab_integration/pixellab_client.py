#!/usr/bin/env python3
"""
PixelLab API Client - Complete Integration
Full-featured wrapper for PixelLab's AI pixel art generation API
"""

import logging
from pathlib import Path
from typing import Optional, Dict, List, Union
from PIL import Image
import pixellab
from pixellab import (
    ImageSize, Outline, Shading, Detail,
    CameraView, Direction, SkeletonFrame
)


logger = logging.getLogger(__name__)


class PixelLabClient:
    """
    Complete PixelLab API client with all available methods.

    This client provides access to all PixelLab AI-powered pixel art generation
    features including character generation, animation, tilesets, rotation,
    inpainting, and more.
    """

    def __init__(self, api_key: str, auto_save: bool = True, save_dir: str = "outputs"):
        """
        Initialize PixelLab client.

        Args:
            api_key: Your PixelLab API key from https://www.pixellab.ai
            auto_save: Automatically save generated images
            save_dir: Directory to save images to
        """
        self.client = pixellab.Client(secret=api_key)
        self.auto_save = auto_save
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"PixelLab client initialized. Save directory: {self.save_dir}")

    def get_balance(self) -> dict:
        """
        Check your current API credit balance.

        Returns:
            dict: Balance information
        """
        response = self.client.get_balance()
        return {
            "credits": response.credits,
            "status": "success"
        }

    # ========== IMAGE GENERATION ==========

    def generate_character(
        self,
        description: str,
        width: int = 64,
        height: int = 64,
        **kwargs
    ) -> Image.Image:
        """
        Generate a pixel art character using PixFlux.

        Args:
            description: Text description of the character
            width: Image width in pixels
            height: Image height in pixels
            **kwargs: Additional parameters:
                - negative_description: What to avoid in the generation
                - text_guidance_scale: How closely to follow the text (default: 8)
                - outline: Outline style (None, 'thin', 'thick')
                - shading: Shading style (None, 'flat', 'smooth')
                - detail: Detail level (None, 'low', 'medium', 'high')
                - view: Camera view ('side', 'front', 'back', '3/4')
                - direction: Direction facing ('north', 'south', 'east', 'west')
                - isometric: Use isometric projection
                - no_background: Generate without background
                - seed: Random seed for reproducibility

        Returns:
            PIL.Image.Image: Generated character image
        """
        image_size = {"width": width, "height": height}

        response = self.client.generate_image_pixflux(
            description=description,
            image_size=image_size,
            **kwargs
        )

        image = response.image.pil_image()

        if self.auto_save:
            filename = f"character_{description.replace(' ', '_')[:30]}.png"
            self._save_image(image, filename)

        return image

    def generate_with_style(
        self,
        description: str,
        style_image: Image.Image,
        width: int = 64,
        height: int = 64,
        style_strength: float = 0.7,
        **kwargs
    ) -> Image.Image:
        """
        Generate pixel art using BitForge with a reference style image.

        Args:
            description: Text description
            style_image: Reference image for style matching
            width: Image width
            height: Image height
            style_strength: How strongly to apply the style (0.0-1.0)
            **kwargs: Additional BitForge parameters

        Returns:
            Generated image matching the style
        """
        image_size = {"width": width, "height": height}

        response = self.client.generate_image_bitforge(
            description=description,
            image_size=image_size,
            style_image=style_image,
            style_strength=style_strength,
            **kwargs
        )

        image = response.image.pil_image()

        if self.auto_save:
            filename = f"styled_{description.replace(' ', '_')[:30]}.png"
            self._save_image(image, filename)

        return image

    # ========== ANIMATION ==========

    def animate_character_text(
        self,
        reference_image: Image.Image,
        description: str,
        action: str,
        width: int = 64,
        height: int = 64,
        n_frames: int = 4,
        view: str = 'side',
        direction: str = 'east',
        **kwargs
    ) -> List[Image.Image]:
        """
        Animate a character using text descriptions.

        Args:
            reference_image: The character to animate
            description: Character description
            action: Animation action (e.g., "walk", "run", "idle", "attack")
            width: Frame width
            height: Frame height
            n_frames: Number of animation frames
            view: Camera view
            direction: Direction facing
            **kwargs: Additional animation parameters

        Returns:
            List of animation frames as PIL Images
        """
        image_size = ImageSize(width=width, height=height)

        response = self.client.animate_with_text(
            image_size=image_size,
            description=description,
            action=action,
            reference_image=reference_image,
            view=view,
            direction=direction,
            n_frames=n_frames,
            **kwargs
        )

        frames = [frame.pil_image() for frame in response.images]

        if self.auto_save:
            for i, frame in enumerate(frames):
                filename = f"animation_{action}_frame{i:02d}.png"
                self._save_image(frame, filename)

        return frames

    def animate_character_skeleton(
        self,
        skeleton_keypoints: List[SkeletonFrame],
        width: int = 64,
        height: int = 64,
        view: str = 'side',
        direction: str = 'east',
        reference_image: Optional[Image.Image] = None,
        **kwargs
    ) -> List[Image.Image]:
        """
        Animate a character using skeleton keypoints.

        Args:
            skeleton_keypoints: List of skeleton frames defining the animation
            width: Frame width
            height: Frame height
            view: Camera view
            direction: Direction facing
            reference_image: Optional reference character image
            **kwargs: Additional parameters

        Returns:
            List of animation frames
        """
        image_size = {"width": width, "height": height}

        response = self.client.animate_with_skeleton(
            image_size=image_size,
            skeleton_keypoints=skeleton_keypoints,
            view=view,
            direction=direction,
            reference_image=reference_image,
            **kwargs
        )

        frames = [frame.pil_image() for frame in response.images]

        if self.auto_save:
            for i, frame in enumerate(frames):
                filename = f"skeleton_anim_frame{i:02d}.png"
                self._save_image(frame, filename)

        return frames

    def estimate_skeleton(self, character_image: Image.Image) -> Dict:
        """
        Extract skeleton structure from a character image.

        Args:
            character_image: Character image on transparent background

        Returns:
            Dictionary containing skeleton keypoints
        """
        response = self.client.estimate_skeleton(image=character_image)

        return {
            "skeleton_frame": response.skeleton_frame,
            "confidence": getattr(response, 'confidence', None)
        }

    # ========== IMAGE MANIPULATION ==========

    def rotate_character(
        self,
        image: Image.Image,
        from_view: Optional[str] = None,
        to_view: Optional[str] = None,
        from_direction: Optional[str] = None,
        to_direction: Optional[str] = None,
        width: int = 64,
        height: int = 64,
        **kwargs
    ) -> Image.Image:
        """
        Rotate a character to a different view or direction.

        Args:
            image: Character image to rotate
            from_view: Current view ('side', 'front', 'back', '3/4')
            to_view: Target view
            from_direction: Current direction ('north', 'south', 'east', 'west')
            to_direction: Target direction
            width: Output width
            height: Output height
            **kwargs: Additional rotation parameters

        Returns:
            Rotated character image
        """
        image_size = {"width": width, "height": height}

        response = self.client.rotate(
            image_size=image_size,
            from_image=image,
            from_view=from_view,
            to_view=to_view,
            from_direction=from_direction,
            to_direction=to_direction,
            **kwargs
        )

        rotated = response.image.pil_image()

        if self.auto_save:
            filename = f"rotated_{to_view or to_direction}.png"
            self._save_image(rotated, filename)

        return rotated

    def inpaint_image(
        self,
        description: str,
        inpainting_image: Image.Image,
        mask_image: Image.Image,
        width: int = 64,
        height: int = 64,
        **kwargs
    ) -> Image.Image:
        """
        Modify specific regions of an image using inpainting.

        Args:
            description: Description of what to paint in the masked region
            inpainting_image: Original image to modify
            mask_image: Mask indicating regions to repaint (white = repaint)
            width: Output width
            height: Output height
            **kwargs: Additional inpainting parameters

        Returns:
            Inpainted image
        """
        image_size = {"width": width, "height": height}

        response = self.client.inpaint(
            description=description,
            image_size=image_size,
            inpainting_image=inpainting_image,
            mask_image=mask_image,
            **kwargs
        )

        result = response.image.pil_image()

        if self.auto_save:
            filename = f"inpainted_{description.replace(' ', '_')[:30]}.png"
            self._save_image(result, filename)

        return result

    # ========== HELPER METHODS ==========

    def _save_image(self, image: Image.Image, filename: str) -> Path:
        """Save an image to the save directory."""
        filepath = self.save_dir / filename
        image.save(filepath, "PNG")
        logger.info(f"Saved image: {filepath}")
        return filepath

    def create_sprite_sheet(
        self,
        frames: List[Image.Image],
        columns: int = 4,
        filename: str = "spritesheet.png"
    ) -> Image.Image:
        """
        Combine animation frames into a sprite sheet.

        Args:
            frames: List of animation frames
            columns: Number of columns in the sprite sheet
            filename: Output filename

        Returns:
            Sprite sheet image
        """
        if not frames:
            raise ValueError("No frames provided")

        frame_width, frame_height = frames[0].size
        rows = (len(frames) + columns - 1) // columns

        sheet_width = frame_width * columns
        sheet_height = frame_height * rows

        sprite_sheet = Image.new('RGBA', (sheet_width, sheet_height), (0, 0, 0, 0))

        for idx, frame in enumerate(frames):
            row = idx // columns
            col = idx % columns
            x = col * frame_width
            y = row * frame_height
            sprite_sheet.paste(frame, (x, y))

        if self.auto_save:
            self._save_image(sprite_sheet, filename)

        return sprite_sheet

    def batch_generate_directions(
        self,
        description: str,
        directions: List[str] = ['north', 'south', 'east', 'west'],
        width: int = 64,
        height: int = 64,
        **kwargs
    ) -> Dict[str, Image.Image]:
        """
        Generate a character facing multiple directions.

        Args:
            description: Character description
            directions: List of directions to generate
            width: Image width
            height: Image height
            **kwargs: Additional generation parameters

        Returns:
            Dictionary mapping directions to images
        """
        results = {}

        for direction in directions:
            logger.info(f"Generating character facing {direction}...")
            image = self.generate_character(
                description=description,
                width=width,
                height=height,
                direction=direction,
                **kwargs
            )
            results[direction] = image

        return results


# ========== CONVENIENCE FUNCTIONS ==========

def create_walking_animation(
    client: PixelLabClient,
    description: str,
    n_frames: int = 4,
    **kwargs
) -> List[Image.Image]:
    """
    Quick helper to create a walking animation.

    Args:
        client: PixelLabClient instance
        description: Character description
        n_frames: Number of frames
        **kwargs: Additional parameters

    Returns:
        List of walking animation frames
    """
    # First generate the base character
    base_character = client.generate_character(description, **kwargs)

    # Then animate it walking
    frames = client.animate_character_text(
        reference_image=base_character,
        description=description,
        action="walk",
        n_frames=n_frames,
        **kwargs
    )

    return frames


def create_8_directional_character(
    client: PixelLabClient,
    description: str,
    width: int = 64,
    height: int = 64,
    **kwargs
) -> Dict[str, Image.Image]:
    """
    Create a character with all 8 cardinal and ordinal directions.

    Args:
        client: PixelLabClient instance
        description: Character description
        width: Image width
        height: Image height
        **kwargs: Additional parameters

    Returns:
        Dictionary with all 8 directional views
    """
    directions = ['north', 'northeast', 'east', 'southeast',
                  'south', 'southwest', 'west', 'northwest']

    return client.batch_generate_directions(
        description=description,
        directions=directions,
        width=width,
        height=height,
        **kwargs
    )
