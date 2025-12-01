"""
Pixel Art HUD Components

HP/MP bars and minimap inspired by Nano Banana Games dungeon mockup.
"""

import pygame
from typing import Optional, List, Tuple

try:
    from pygame_mvp.config import SCREEN_WIDTH, SCREEN_HEIGHT, PADDING
    from pygame_mvp.ui.pixel_theme import (
        get_pixel_theme, HP_RED, HP_RED_DARK, MP_BLUE, MP_BLUE_DARK,
        TEXT_WHITE, BANANA_YELLOW, SLOT_BG, SLOT_BORDER
    )
except ImportError:
    from config import SCREEN_WIDTH, SCREEN_HEIGHT, PADDING
    from ui.pixel_theme import (
        get_pixel_theme, HP_RED, HP_RED_DARK, MP_BLUE, MP_BLUE_DARK,
        TEXT_WHITE, BANANA_YELLOW, SLOT_BG, SLOT_BORDER
    )


class PixelStatBar:
    """
    Pixel art stat bar (HP or MP).
    
    Features:
    - Segmented bar appearance
    - Icon label
    - Animated damage/healing effects
    """
    
    def __init__(
        self, 
        x: int, 
        y: int, 
        width: int = 180, 
        height: int = 24,
        bar_type: str = "HP"
    ):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.bar_type = bar_type
        
        # Colors based on type
        if bar_type == "HP":
            self.fill_color = HP_RED
            self.bg_color = HP_RED_DARK
            self.icon_color = (255, 100, 100)
        else:  # MP
            self.fill_color = MP_BLUE
            self.bg_color = MP_BLUE_DARK
            self.icon_color = (100, 150, 255)
        
        # Values
        self.current = 100
        self.maximum = 100
        self.displayed = 100  # For smooth animation
        
        # Animation
        self.animation_speed = 2
        self.flash_frames = 0
        
        # Font
        pygame.font.init()
        self.font = pygame.font.Font(None, 18)
    
    def set_values(self, current: int, maximum: int) -> None:
        """Set current and maximum values."""
        old_current = self.current
        self.current = max(0, min(current, maximum))
        self.maximum = maximum
        
        # Trigger flash on damage
        if self.current < old_current:
            self.flash_frames = 10
    
    def update(self) -> None:
        """Update animation."""
        # Smooth bar movement
        target = (self.current / self.maximum * 100) if self.maximum > 0 else 0
        if self.displayed > target:
            self.displayed = max(target, self.displayed - self.animation_speed)
        elif self.displayed < target:
            self.displayed = min(target, self.displayed + self.animation_speed)
        
        # Flash countdown
        if self.flash_frames > 0:
            self.flash_frames -= 1
    
    def render(self, surface: pygame.Surface) -> None:
        """Render the stat bar."""
        # Label icon (heart or droplet)
        icon_rect = pygame.Rect(self.x, self.y, 20, self.height)
        
        if self.bar_type == "HP":
            # Heart icon
            pygame.draw.polygon(surface, self.icon_color, [
                (self.x + 10, self.y + 6),
                (self.x + 4, self.y + 12),
                (self.x + 10, self.y + 20),
                (self.x + 16, self.y + 12),
            ])
        else:
            # Water droplet icon
            pygame.draw.polygon(surface, self.icon_color, [
                (self.x + 10, self.y + 4),
                (self.x + 4, self.y + 14),
                (self.x + 10, self.y + 20),
                (self.x + 16, self.y + 14),
            ])
        
        # Label text
        label = self.font.render(self.bar_type, True, TEXT_WHITE)
        surface.blit(label, (self.x + 22, self.y + 4))
        
        # Bar background
        bar_x = self.x + 45
        bar_width = self.width - 45
        bar_rect = pygame.Rect(bar_x, self.y + 2, bar_width, self.height - 4)
        
        pygame.draw.rect(surface, self.bg_color, bar_rect, border_radius=3)
        pygame.draw.rect(surface, (40, 30, 25), bar_rect, 2, border_radius=3)
        
        # Bar fill
        fill_width = int((self.displayed / 100) * (bar_width - 4))
        if fill_width > 0:
            fill_rect = pygame.Rect(bar_x + 2, self.y + 4, fill_width, self.height - 8)
            
            # Flash effect
            color = self.fill_color
            if self.flash_frames > 0 and self.flash_frames % 4 < 2:
                color = (255, 255, 255)
            
            pygame.draw.rect(surface, color, fill_rect, border_radius=2)
            
            # Highlight
            highlight_rect = pygame.Rect(bar_x + 2, self.y + 4, fill_width, 3)
            highlight_color = tuple(min(c + 40, 255) for c in color)
            pygame.draw.rect(surface, highlight_color, highlight_rect, border_radius=2)


class PixelMinimap:
    """
    Pixel art minimap in corner.
    
    Features:
    - Circular frame
    - Banana marker for player position
    - Simple terrain representation
    """
    
    def __init__(self, x: int, y: int, radius: int = 60):
        self.x = x
        self.y = y
        self.radius = radius
        
        # Map data
        self.map_width = 20
        self.map_height = 15
        self.tiles: List[List[int]] = []  # 0=floor, 1=wall
        self.player_pos = (10, 7)  # Grid position
        self.pois: List[Tuple[int, int, str]] = []  # (x, y, type)
        
        # Colors
        self.frame_color = (80, 60, 40)
        self.bg_color = (50, 50, 45)
        self.floor_color = (80, 75, 65)
        self.wall_color = (40, 35, 30)
        self.player_color = BANANA_YELLOW
        self.poi_color = (200, 180, 100)
        
        # Pre-render frame
        self._create_frame()
    
    def _create_frame(self) -> None:
        """Create the circular frame."""
        size = self.radius * 2 + 10
        self.frame_surface = pygame.Surface((size, size), pygame.SRCALPHA)
        
        center = size // 2
        
        # Outer ring
        pygame.draw.circle(self.frame_surface, self.frame_color, (center, center), self.radius + 4)
        
        # Inner ring
        pygame.draw.circle(self.frame_surface, (60, 45, 30), (center, center), self.radius + 2)
        
        # Map background
        pygame.draw.circle(self.frame_surface, self.bg_color, (center, center), self.radius)
    
    def set_map(self, tiles: List[List[int]], width: int, height: int) -> None:
        """Set the map tile data."""
        self.tiles = tiles
        self.map_width = width
        self.map_height = height
    
    def set_player_pos(self, x: int, y: int) -> None:
        """Set player position on map."""
        self.player_pos = (x, y)
    
    def add_poi(self, x: int, y: int, poi_type: str) -> None:
        """Add a point of interest marker."""
        self.pois.append((x, y, poi_type))
    
    def clear_pois(self) -> None:
        """Clear all POI markers."""
        self.pois = []
    
    def render(self, surface: pygame.Surface) -> None:
        """Render the minimap."""
        # Draw frame
        surface.blit(self.frame_surface, (self.x - 5, self.y - 5))
        
        center_x = self.x + self.radius
        center_y = self.y + self.radius
        
        # Create clip mask for circular map
        map_surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        
        # Draw tiles relative to player (centered view)
        px, py = self.player_pos
        scale = 4  # Pixels per tile
        view_range = self.radius // scale
        
        for dy in range(-view_range, view_range + 1):
            for dx in range(-view_range, view_range + 1):
                tx = px + dx
                ty = py + dy
                
                # Screen position
                sx = self.radius + dx * scale
                sy = self.radius + dy * scale
                
                # Check if in circle
                dist = (dx * scale) ** 2 + (dy * scale) ** 2
                if dist > (self.radius - 2) ** 2:
                    continue
                
                # Get tile color
                if 0 <= tx < self.map_width and 0 <= ty < self.map_height and self.tiles:
                    if ty < len(self.tiles) and tx < len(self.tiles[ty]):
                        tile = self.tiles[ty][tx]
                        color = self.wall_color if tile == 1 else self.floor_color
                    else:
                        color = self.wall_color
                else:
                    color = self.wall_color
                
                pygame.draw.rect(map_surface, color, (sx, sy, scale, scale))
        
        # Draw POIs
        for poi_x, poi_y, poi_type in self.pois:
            dx = poi_x - px
            dy = poi_y - py
            dist = (dx * scale) ** 2 + (dy * scale) ** 2
            if dist < (self.radius - 2) ** 2:
                sx = self.radius + dx * scale
                sy = self.radius + dy * scale
                pygame.draw.circle(map_surface, self.poi_color, (sx + scale // 2, sy + scale // 2), 3)
        
        # Draw player (banana!)
        self._draw_banana_marker(map_surface, self.radius, self.radius, 10)
        
        # Blit map surface
        surface.blit(map_surface, (self.x, self.y))
        
        # Draw direction indicator (north arrow)
        arrow_points = [
            (center_x, self.y + 8),
            (center_x - 5, self.y + 16),
            (center_x + 5, self.y + 16),
        ]
        pygame.draw.polygon(surface, (200, 180, 140), arrow_points)
    
    def _draw_banana_marker(self, surface: pygame.Surface, x: int, y: int, size: int) -> None:
        """Draw banana marker for player."""
        points = [
            (x - size // 2, y),
            (x - size // 4, y - size // 2),
            (x + size // 4, y - size // 2),
            (x + size // 2, y),
            (x + size // 4, y + size // 2),
            (x - size // 4, y + size // 2),
        ]
        pygame.draw.polygon(surface, self.player_color, points)
        pygame.draw.polygon(surface, (200, 180, 80), points, 1)


class PixelGameHUD:
    """
    Complete game HUD combining stat bars and minimap.
    
    Layout:
    - Top-left: HP and MP bars
    - Top-right: Minimap
    """
    
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.margin = 15
        
        # HP Bar
        self.hp_bar = PixelStatBar(
            self.margin, self.margin,
            width=180, height=24,
            bar_type="HP"
        )
        
        # MP Bar
        self.mp_bar = PixelStatBar(
            self.margin, self.margin + 30,
            width=180, height=24,
            bar_type="MP"
        )
        
        # Minimap
        minimap_radius = 55
        self.minimap = PixelMinimap(
            SCREEN_WIDTH - minimap_radius * 2 - self.margin - 10,
            self.margin,
            radius=minimap_radius
        )
    
    def set_hp(self, current: int, maximum: int) -> None:
        """Set HP values."""
        self.hp_bar.set_values(current, maximum)
    
    def set_mp(self, current: int, maximum: int) -> None:
        """Set MP values."""
        self.mp_bar.set_values(current, maximum)
    
    def set_player_pos(self, x: int, y: int) -> None:
        """Set player position on minimap."""
        self.minimap.set_player_pos(x, y)
    
    def set_map_tiles(self, tiles: List[List[int]], width: int, height: int) -> None:
        """Set minimap tile data."""
        self.minimap.set_map(tiles, width, height)
    
    def update(self) -> None:
        """Update all HUD elements."""
        self.hp_bar.update()
        self.mp_bar.update()
    
    def render(self) -> None:
        """Render all HUD elements."""
        self.hp_bar.render(self.screen)
        self.mp_bar.render(self.screen)
        self.minimap.render(self.screen)

