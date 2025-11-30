"""
Image Provider System

Abstract interface and implementations for image generation.
- MockImageProvider: Generates labeled placeholder images
- APIImageProvider: Calls real API for AI-generated images
"""

import pygame
from abc import ABC, abstractmethod
from typing import Dict, Tuple, Optional

# Use absolute imports for standalone execution
try:
    from pygame_mvp.config import (
        CURRENT_THEME,
        FONT_SIZE_SMALL,
        FONT_SIZE_NORMAL,
        PADDING
    )
except ImportError:
    from config import (
        CURRENT_THEME,
        FONT_SIZE_SMALL,
        FONT_SIZE_NORMAL,
        PADDING
    )


class ImageProvider(ABC):
    """Abstract base class for image providers."""

    @abstractmethod
    def get_scene_image(self, scene_name: str, width: int, height: int) -> pygame.Surface:
        """Generate or fetch a scene image."""
        pass

    @abstractmethod
    def get_character_portrait(self, name: str, char_class: str, width: int, height: int) -> pygame.Surface:
        """Generate or fetch a character portrait."""
        pass

    @abstractmethod
    def get_item_image(self, item_name: str, width: int, height: int) -> pygame.Surface:
        """Generate or fetch an item icon."""
        pass

    @abstractmethod
    def get_map_image(self, location_name: str, width: int, height: int) -> pygame.Surface:
        """Generate or fetch a map/location image."""
        pass

    def clear_cache(self) -> None:
        """Clear the image cache."""
        pass


class MockImageProvider(ImageProvider):
    """
    Generates labeled placeholder images for development.

    Each placeholder clearly shows:
    - Image type (SCENE, CHARACTER, ITEM, MAP)
    - Name/description
    - Dimensions
    - API call that would be made
    """

    def __init__(self):
        self._cache: Dict[Tuple, pygame.Surface] = {}
        self._font_small: Optional[pygame.font.Font] = None
        self._font_normal: Optional[pygame.font.Font] = None
        self._initialized = False

    def _ensure_initialized(self) -> None:
        """Initialize fonts on first use."""
        if self._initialized:
            return

        pygame.font.init()
        self._font_small = pygame.font.Font(None, FONT_SIZE_SMALL + 2)
        self._font_normal = pygame.font.Font(None, FONT_SIZE_NORMAL + 2)
        self._initialized = True

    def _get_cache_key(self, img_type: str, name: str, width: int, height: int) -> Tuple:
        """Generate a cache key."""
        return (img_type, name, width, height)

    def _create_placeholder(
        self,
        img_type: str,
        name: str,
        width: int,
        height: int,
        bg_color: Tuple[int, int, int],
        api_call: str
    ) -> pygame.Surface:
        """
        Create a labeled placeholder image.

        Args:
            img_type: Type label (SCENE, CHARACTER, ITEM, MAP)
            name: Name to display
            width: Image width
            height: Image height
            bg_color: Background color
            api_call: API endpoint that would be called
        """
        self._ensure_initialized()

        # Check cache
        cache_key = self._get_cache_key(img_type, name, width, height)
        if cache_key in self._cache:
            return self._cache[cache_key]

        # Create surface
        surface = pygame.Surface((width, height))
        surface.fill(bg_color)

        # Draw border
        border_color = tuple(min(c + 40, 255) for c in bg_color)
        pygame.draw.rect(surface, border_color, (0, 0, width, height), 2)

        # Draw corner markers
        corner_size = 10
        pygame.draw.line(surface, border_color, (0, corner_size), (corner_size, 0), 2)
        pygame.draw.line(surface, border_color, (width - corner_size, 0), (width, corner_size), 2)
        pygame.draw.line(surface, border_color, (0, height - corner_size), (corner_size, height), 2)
        pygame.draw.line(surface, border_color, (width - corner_size, height), (width, height - corner_size), 2)

        # Text color
        text_color = (220, 220, 220)
        dim_text_color = (160, 160, 160)

        # Render type label
        type_text = self._font_normal.render(f"[{img_type}]", True, text_color)
        type_rect = type_text.get_rect(centerx=width // 2, top=PADDING)
        surface.blit(type_text, type_rect)

        # Render name (truncate if too long)
        max_name_width = width - PADDING * 4
        name_display = name
        name_text = self._font_normal.render(name_display, True, text_color)
        while name_text.get_width() > max_name_width and len(name_display) > 10:
            name_display = name_display[:-4] + "..."
            name_text = self._font_normal.render(name_display, True, text_color)
        name_rect = name_text.get_rect(centerx=width // 2, top=type_rect.bottom + 4)
        surface.blit(name_text, name_rect)

        # Render dimensions
        dim_text = self._font_small.render(f"{width} x {height} px", True, dim_text_color)
        dim_rect = dim_text.get_rect(centerx=width // 2, centery=height // 2)
        surface.blit(dim_text, dim_rect)

        # Render API call (at bottom)
        api_text = self._font_small.render(f"API: {api_call}", True, dim_text_color)
        # Truncate if needed
        max_api_width = width - PADDING * 2
        api_display = f"API: {api_call}"
        while api_text.get_width() > max_api_width and len(api_display) > 15:
            api_display = api_display[:-4] + "..."
            api_text = self._font_small.render(api_display, True, dim_text_color)
        api_rect = api_text.get_rect(centerx=width // 2, bottom=height - PADDING)
        surface.blit(api_text, api_rect)

        # Draw center crosshair
        cross_color = tuple(min(c + 20, 255) for c in bg_color)
        cx, cy = width // 2, height // 2
        cross_size = 15
        pygame.draw.line(surface, cross_color, (cx - cross_size, cy), (cx + cross_size, cy), 1)
        pygame.draw.line(surface, cross_color, (cx, cy - cross_size), (cx, cy + cross_size), 1)

        # Cache and return
        self._cache[cache_key] = surface
        return surface

    def get_scene_image(self, scene_name: str, width: int, height: int) -> pygame.Surface:
        """Generate a scene placeholder."""
        return self._create_placeholder(
            img_type="SCENE",
            name=scene_name,
            width=width,
            height=height,
            bg_color=CURRENT_THEME["placeholder_scene"],
            api_call="generate_scene"
        )

    def get_character_portrait(self, name: str, char_class: str, width: int, height: int) -> pygame.Surface:
        """Generate a character portrait placeholder."""
        return self._create_placeholder(
            img_type="CHARACTER",
            name=f"{name} ({char_class})",
            width=width,
            height=height,
            bg_color=CURRENT_THEME["placeholder_character"],
            api_call="generate_portrait"
        )

    def get_item_image(self, item_name: str, width: int, height: int) -> pygame.Surface:
        """Generate an item icon placeholder."""
        return self._create_placeholder(
            img_type="ITEM",
            name=item_name,
            width=width,
            height=height,
            bg_color=CURRENT_THEME["placeholder_item"],
            api_call="generate_item"
        )

    def get_map_image(self, location_name: str, width: int, height: int) -> pygame.Surface:
        """Generate a map placeholder."""
        return self._create_placeholder(
            img_type="MAP",
            name=location_name,
            width=width,
            height=height,
            bg_color=CURRENT_THEME["placeholder_scene"],
            api_call="generate_map"
        )

    def clear_cache(self) -> None:
        """Clear the image cache."""
        self._cache.clear()


class APIImageProvider(ImageProvider):
    """
    Real image provider that calls the FastAPI backend.

    Note: This is a stub for future implementation.
    Switch to this provider when ready for real API calls.
    """

    def __init__(self, api_url: str = "http://localhost:8000/api/v1"):
        self.api_url = api_url
        self._cache: Dict[Tuple, pygame.Surface] = {}
        self._fallback = MockImageProvider()

    def _fetch_image(self, endpoint: str, params: dict, width: int, height: int) -> pygame.Surface:
        """
        Fetch image from API.

        TODO: Implement actual API call
        - POST to endpoint with params
        - Receive base64 image
        - Decode to pygame.Surface
        - Handle errors with fallback
        """
        # For now, return fallback placeholder
        return self._fallback.get_scene_image(params.get("name", "Unknown"), width, height)

    def get_scene_image(self, scene_name: str, width: int, height: int) -> pygame.Surface:
        """Fetch scene image from API."""
        return self._fetch_image(
            f"{self.api_url}/images/scene",
            {"name": scene_name, "width": width, "height": height},
            width, height
        )

    def get_character_portrait(self, name: str, char_class: str, width: int, height: int) -> pygame.Surface:
        """Fetch character portrait from API."""
        return self._fetch_image(
            f"{self.api_url}/images/portrait",
            {"name": name, "char_class": char_class, "width": width, "height": height},
            width, height
        )

    def get_item_image(self, item_name: str, width: int, height: int) -> pygame.Surface:
        """Fetch item image from API."""
        return self._fetch_image(
            f"{self.api_url}/images/item",
            {"name": item_name, "width": width, "height": height},
            width, height
        )

    def get_map_image(self, location_name: str, width: int, height: int) -> pygame.Surface:
        """Fetch map image from API."""
        return self._fetch_image(
            f"{self.api_url}/images/map",
            {"name": location_name, "width": width, "height": height},
            width, height
        )

    def clear_cache(self) -> None:
        """Clear the image cache."""
        self._cache.clear()

