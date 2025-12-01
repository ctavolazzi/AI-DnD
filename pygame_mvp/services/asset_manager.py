"""
Asset Manager

Centralized management of game assets with PixelLab integration.
Handles loading, caching, and on-demand generation of pixel art assets.
"""

import os
import json
import pygame
from pathlib import Path
from typing import Dict, Optional, Tuple, List
from dataclasses import dataclass, field
from enum import Enum


class AssetType(Enum):
    CHARACTER = "character"
    TILESET = "tileset"
    ITEM = "item"
    MAP_OBJECT = "map_object"
    UI = "ui"


@dataclass
class AssetInfo:
    """Metadata for a managed asset."""
    asset_id: str
    asset_type: AssetType
    name: str
    path: Path
    loaded: bool = False
    surface: Optional[pygame.Surface] = None
    frames: List[pygame.Surface] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)


class AssetManager:
    """
    Manages game assets with automatic loading and caching.
    
    Features:
    - Automatic sprite sheet parsing
    - Animation frame management
    - On-demand asset loading
    - PixelLab integration for missing assets
    """
    
    def __init__(self, assets_dir: str = "game_assets"):
        self.assets_dir = Path(assets_dir)
        self.assets_dir.mkdir(exist_ok=True)
        
        # Asset registries
        self._assets: Dict[str, AssetInfo] = {}
        self._sprite_cache: Dict[str, pygame.Surface] = {}
        self._animation_cache: Dict[str, List[pygame.Surface]] = {}
        
        # Subdirectories
        self.characters_dir = self.assets_dir / "characters"
        self.tilesets_dir = self.assets_dir / "tilesets"
        self.items_dir = self.assets_dir / "items"
        self.ui_dir = self.assets_dir / "ui"
        
        for d in [self.characters_dir, self.tilesets_dir, self.items_dir, self.ui_dir]:
            d.mkdir(exist_ok=True)
        
        # Load manifest if exists
        self.manifest_path = self.assets_dir / "manifest.json"
        self._load_manifest()
    
    def _load_manifest(self) -> None:
        """Load asset manifest from disk."""
        if self.manifest_path.exists():
            try:
                data = json.loads(self.manifest_path.read_text())
                for asset_id, info in data.get("assets", {}).items():
                    self._assets[asset_id] = AssetInfo(
                        asset_id=asset_id,
                        asset_type=AssetType(info["type"]),
                        name=info["name"],
                        path=Path(info["path"]),
                        metadata=info.get("metadata", {})
                    )
            except Exception as e:
                print(f"Failed to load manifest: {e}")
    
    def _save_manifest(self) -> None:
        """Save asset manifest to disk."""
        data = {
            "assets": {
                asset_id: {
                    "type": info.asset_type.value,
                    "name": info.name,
                    "path": str(info.path),
                    "metadata": info.metadata
                }
                for asset_id, info in self._assets.items()
            }
        }
        self.manifest_path.write_text(json.dumps(data, indent=2))
    
    def register_asset(
        self,
        asset_id: str,
        asset_type: AssetType,
        name: str,
        path: Path,
        metadata: Optional[Dict] = None
    ) -> AssetInfo:
        """Register a new asset."""
        info = AssetInfo(
            asset_id=asset_id,
            asset_type=asset_type,
            name=name,
            path=path,
            metadata=metadata or {}
        )
        self._assets[asset_id] = info
        self._save_manifest()
        return info
    
    def get_asset(self, asset_id: str) -> Optional[AssetInfo]:
        """Get asset info by ID."""
        return self._assets.get(asset_id)
    
    def load_sprite(self, asset_id: str) -> Optional[pygame.Surface]:
        """
        Load a single sprite image.
        
        Returns cached version if already loaded.
        """
        if asset_id in self._sprite_cache:
            return self._sprite_cache[asset_id]
        
        asset = self._assets.get(asset_id)
        if not asset:
            return None
        
        if not asset.path.exists():
            return None
        
        try:
            surface = pygame.image.load(str(asset.path))
            if pygame.display.get_init():
                surface = surface.convert_alpha()
            
            self._sprite_cache[asset_id] = surface
            asset.loaded = True
            asset.surface = surface
            return surface
        except Exception as e:
            print(f"Failed to load sprite {asset_id}: {e}")
            return None
    
    def load_animation(
        self,
        asset_id: str,
        frame_width: int,
        frame_height: int,
        row: int = 0
    ) -> List[pygame.Surface]:
        """
        Load animation frames from a sprite sheet.
        
        Args:
            asset_id: Asset ID
            frame_width: Width of each frame
            frame_height: Height of each frame
            row: Row in sprite sheet (for multi-row sheets)
        
        Returns:
            List of frame surfaces
        """
        cache_key = f"{asset_id}_row{row}"
        if cache_key in self._animation_cache:
            return self._animation_cache[cache_key]
        
        # Load the sprite sheet
        sheet = self.load_sprite(asset_id)
        if not sheet:
            return []
        
        frames = []
        sheet_width = sheet.get_width()
        y = row * frame_height
        
        for x in range(0, sheet_width, frame_width):
            frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
            frame.blit(sheet, (0, 0), (x, y, frame_width, frame_height))
            frames.append(frame)
        
        self._animation_cache[cache_key] = frames
        return frames
    
    def load_tileset(
        self,
        asset_id: str,
        tile_width: int,
        tile_height: int
    ) -> Dict[int, pygame.Surface]:
        """
        Load a tileset and split into individual tiles.
        
        Returns:
            Dict mapping tile index to surface
        """
        sheet = self.load_sprite(asset_id)
        if not sheet:
            return {}
        
        tiles = {}
        sheet_width = sheet.get_width()
        sheet_height = sheet.get_height()
        cols = sheet_width // tile_width
        
        idx = 0
        for y in range(0, sheet_height, tile_height):
            for x in range(0, sheet_width, tile_width):
                tile = pygame.Surface((tile_width, tile_height), pygame.SRCALPHA)
                tile.blit(sheet, (0, 0), (x, y, tile_width, tile_height))
                tiles[idx] = tile
                idx += 1
        
        return tiles
    
    def create_placeholder(
        self,
        width: int,
        height: int,
        label: str = "",
        bg_color: Tuple[int, int, int] = (60, 60, 80)
    ) -> pygame.Surface:
        """Create a labeled placeholder surface."""
        surface = pygame.Surface((width, height))
        surface.fill(bg_color)
        
        # Border
        border_color = tuple(min(c + 40, 255) for c in bg_color)
        pygame.draw.rect(surface, border_color, (0, 0, width, height), 2)
        
        # Label
        if label:
            pygame.font.init()
            font = pygame.font.Font(None, max(12, min(width, height) // 4))
            text = font.render(label, True, (200, 200, 200))
            text_rect = text.get_rect(center=(width // 2, height // 2))
            surface.blit(text, text_rect)
        
        return surface
    
    def get_or_create_placeholder(
        self,
        asset_id: str,
        width: int,
        height: int,
        label: Optional[str] = None
    ) -> pygame.Surface:
        """
        Get an asset, or create a placeholder if not found.
        
        Useful during development when assets may not exist yet.
        """
        sprite = self.load_sprite(asset_id)
        if sprite:
            return sprite
        
        asset = self._assets.get(asset_id)
        name = asset.name if asset else asset_id
        return self.create_placeholder(width, height, label or name)
    
    # =========================================================================
    # CHARACTER HELPERS
    # =========================================================================
    
    def register_character(
        self,
        name: str,
        sprite_path: Path,
        directions: int = 8,
        frame_size: Tuple[int, int] = (48, 48)
    ) -> str:
        """
        Register a character with animations.
        
        Returns:
            Character asset ID
        """
        asset_id = f"char_{name.lower()}"
        self.register_asset(
            asset_id=asset_id,
            asset_type=AssetType.CHARACTER,
            name=name,
            path=sprite_path,
            metadata={
                "directions": directions,
                "frame_width": frame_size[0],
                "frame_height": frame_size[1]
            }
        )
        return asset_id
    
    def get_character_frame(
        self,
        asset_id: str,
        direction: str,
        animation: str,
        frame_index: int
    ) -> Optional[pygame.Surface]:
        """
        Get a specific character animation frame.
        
        Args:
            asset_id: Character asset ID
            direction: Direction name (south, west, etc.)
            animation: Animation name (idle, walk, etc.)
            frame_index: Frame number
        
        Returns:
            Frame surface or None
        """
        asset = self._assets.get(asset_id)
        if not asset:
            return None
        
        # Direction to row mapping (8-direction)
        direction_rows = {
            "south": 0, "south_west": 1, "west": 2, "north_west": 3,
            "north": 4, "north_east": 5, "east": 6, "south_east": 7
        }
        
        # For 4-direction
        if asset.metadata.get("directions", 8) == 4:
            direction_rows = {"south": 0, "west": 1, "north": 2, "east": 3}
        
        row = direction_rows.get(direction, 0)
        
        # Load animation frames
        frame_width = asset.metadata.get("frame_width", 48)
        frame_height = asset.metadata.get("frame_height", 48)
        
        # Animation offset (each animation on separate row block)
        animation_offset = {"idle": 0, "walk": 1, "attack": 2, "hurt": 3, "death": 4}
        anim_row = animation_offset.get(animation, 0) * asset.metadata.get("directions", 8)
        
        frames = self.load_animation(asset_id, frame_width, frame_height, row + anim_row)
        
        if frame_index < len(frames):
            return frames[frame_index]
        return frames[0] if frames else None
    
    # =========================================================================
    # TILESET HELPERS
    # =========================================================================
    
    def register_tileset(
        self,
        name: str,
        tileset_path: Path,
        tile_size: int = 32
    ) -> str:
        """
        Register a tileset.
        
        Returns:
            Tileset asset ID
        """
        asset_id = f"tileset_{name.lower()}"
        self.register_asset(
            asset_id=asset_id,
            asset_type=AssetType.TILESET,
            name=name,
            path=tileset_path,
            metadata={
                "tile_width": tile_size,
                "tile_height": tile_size
            }
        )
        return asset_id
    
    def get_tileset_tiles(self, asset_id: str) -> Dict[int, pygame.Surface]:
        """Get all tiles from a tileset."""
        asset = self._assets.get(asset_id)
        if not asset:
            return {}
        
        tile_width = asset.metadata.get("tile_width", 32)
        tile_height = asset.metadata.get("tile_height", 32)
        
        return self.load_tileset(asset_id, tile_width, tile_height)
    
    # =========================================================================
    # STATS
    # =========================================================================
    
    def get_stats(self) -> Dict[str, int]:
        """Get asset statistics."""
        return {
            "total_assets": len(self._assets),
            "loaded_sprites": len(self._sprite_cache),
            "loaded_animations": len(self._animation_cache),
            "characters": sum(1 for a in self._assets.values() if a.asset_type == AssetType.CHARACTER),
            "tilesets": sum(1 for a in self._assets.values() if a.asset_type == AssetType.TILESET),
            "items": sum(1 for a in self._assets.values() if a.asset_type == AssetType.ITEM),
        }
    
    def clear_cache(self) -> None:
        """Clear all caches."""
        self._sprite_cache.clear()
        self._animation_cache.clear()
        for asset in self._assets.values():
            asset.loaded = False
            asset.surface = None
            asset.frames.clear()


# Global instance
_asset_manager: Optional[AssetManager] = None


def get_asset_manager() -> AssetManager:
    """Get or create the global asset manager."""
    global _asset_manager
    if _asset_manager is None:
        _asset_manager = AssetManager()
    return _asset_manager

