"""
PixelLab Integration for AI-DnD
================================

Complete AI-powered pixel art generation for game development.

Quick Start:
    >>> from pixellab_integration import PixelLabClient
    >>> client = PixelLabClient(api_key="your-key")
    >>> character = client.generate_character("fantasy wizard")

For full documentation, see README.md
"""

from .pixellab_client import (
    PixelLabClient,
    create_walking_animation,
    create_8_directional_character
)

__version__ = "1.0.0"
__all__ = [
    "PixelLabClient",
    "create_walking_animation",
    "create_8_directional_character"
]
