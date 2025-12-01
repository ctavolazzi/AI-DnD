"""
Pixel Art Inventory Screen

Inspired by Nano Banana Games inventory mockup.
Features:
- Category tabs (Weapons, Armor, Potions, Key Items, Misc)
- 5x6 item grid with pixel art icons
- Character portrait with 6 stats (STR, DEX, CON, INT, WIS, CHA)
- Item description panel with decorative vine border
"""

import pygame
from typing import Optional, List, Callable, Dict, Any
from enum import Enum
from dataclasses import dataclass

try:
    from pygame_mvp.config import SCREEN_WIDTH, SCREEN_HEIGHT, PADDING
    from pygame_mvp.ui.pixel_theme import (
        get_pixel_theme, PARCHMENT_LIGHT, PARCHMENT_MEDIUM, 
        SLOT_BG, SLOT_BORDER, SLOT_HIGHLIGHT, VINE_GREEN,
        TEXT_DARK, GOLD_HIGHLIGHT, BANANA_YELLOW
    )
    from pygame_mvp.game.systems import Item, ItemType, Stats, Player
except ImportError:
    from config import SCREEN_WIDTH, SCREEN_HEIGHT, PADDING
    from ui.pixel_theme import (
        get_pixel_theme, PARCHMENT_LIGHT, PARCHMENT_MEDIUM, 
        SLOT_BG, SLOT_BORDER, SLOT_HIGHLIGHT, VINE_GREEN,
        TEXT_DARK, GOLD_HIGHLIGHT, BANANA_YELLOW
    )
    from game.systems import Item, ItemType, Stats, Player


class ItemCategory(Enum):
    WEAPONS = "WEAPONS"
    ARMOR = "ARMOR"
    POTIONS = "POTIONS"
    KEY_ITEMS = "KEY ITEMS"
    MISC = "MISC"


@dataclass
class InventorySlot:
    """Represents a single inventory slot."""
    item: Optional[Item] = None
    quantity: int = 1
    selected: bool = False


class PixelInventoryScreen:
    """
    Full-screen inventory interface in pixel art style.
    
    Layout:
    - Left: Category tabs (vertical)
    - Center: Item grid (5 columns x 6 rows)
    - Right: Character portrait + stats
    - Bottom-Right: Item description panel
    """
    
    GRID_COLS = 5
    GRID_ROWS = 6
    SLOT_SIZE = 52
    SLOT_SPACING = 4
    
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.theme = get_pixel_theme()
        self.visible = False
        
        # Fonts
        pygame.font.init()
        self.category_font = pygame.font.Font(None, 24)
        self.stat_font = pygame.font.Font(None, 22)
        self.desc_font = pygame.font.Font(None, 20)
        self.title_font = pygame.font.Font(None, 28)
        
        # State
        self.current_category = ItemCategory.WEAPONS
        self.selected_slot = 0
        self.hovered_slot = -1
        self.selected_item: Optional[Item] = None
        
        # Item slots (5x6 = 30 slots)
        self.slots: List[InventorySlot] = [InventorySlot() for _ in range(self.GRID_COLS * self.GRID_ROWS)]
        
        # Player reference (set externally)
        self.player: Optional[Player] = None
        
        # Calculate layout
        self._calculate_layout()
        
        # Pre-render static elements
        self._create_background()
        self._create_category_tabs()
        
        # Callbacks
        self.on_item_select: Optional[Callable[[Item], None]] = None
        self.on_item_use: Optional[Callable[[Item], None]] = None
        self.on_close: Optional[Callable] = None
    
    def _calculate_layout(self) -> None:
        """Calculate positions for all UI elements."""
        # Background frame inset
        self.frame_margin = 40
        self.content_x = self.frame_margin + 20
        self.content_y = self.frame_margin + 20
        
        # Category tabs (left side)
        self.tab_x = self.content_x
        self.tab_y = self.content_y + 40
        self.tab_width = 120
        self.tab_height = 40
        self.tab_spacing = 8
        
        # Item grid (center)
        self.grid_x = self.tab_x + self.tab_width + 30
        self.grid_y = self.content_y + 20
        self.grid_width = self.GRID_COLS * (self.SLOT_SIZE + self.SLOT_SPACING)
        self.grid_height = self.GRID_ROWS * (self.SLOT_SIZE + self.SLOT_SPACING)
        
        # Character panel (right side)
        self.char_x = self.grid_x + self.grid_width + 30
        self.char_y = self.content_y + 20
        self.char_width = 200
        self.portrait_size = 96
        
        # Stats area
        self.stats_y = self.char_y + self.portrait_size + 20
        
        # Description panel (bottom right)
        self.desc_x = self.char_x - 40
        self.desc_y = SCREEN_HEIGHT - self.frame_margin - 160
        self.desc_width = 280
        self.desc_height = 120
    
    def _create_background(self) -> None:
        """Create the parchment background with frame."""
        self.background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.background.fill(PARCHMENT_LIGHT)
        
        # Draw decorative frame border
        frame_color = (139, 90, 43)
        frame_dark = (80, 50, 25)
        
        # Outer frame
        pygame.draw.rect(self.background, frame_dark, 
                        (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT), 
                        self.frame_margin)
        
        # Inner frame edge
        pygame.draw.rect(self.background, frame_color,
                        (self.frame_margin - 5, self.frame_margin - 5,
                         SCREEN_WIDTH - self.frame_margin * 2 + 10,
                         SCREEN_HEIGHT - self.frame_margin * 2 + 10), 5)
        
        # Add banana decorations to frame
        for x in range(60, SCREEN_WIDTH - 60, 100):
            self._draw_banana(self.background, x, 10, 30)
            self._draw_banana(self.background, x + 40, SCREEN_HEIGHT - 35, 28)
        
        for y in range(80, SCREEN_HEIGHT - 80, 100):
            self._draw_banana(self.background, 8, y, 26)
            self._draw_banana(self.background, SCREEN_WIDTH - 35, y + 30, 26)
    
    def _draw_banana(self, surface: pygame.Surface, x: int, y: int, size: int) -> None:
        """Draw a simple banana icon."""
        banana_color = BANANA_YELLOW
        
        points = [
            (x, y + size // 3),
            (x + size // 4, y),
            (x + size * 3 // 4, y),
            (x + size, y + size // 3),
            (x + size * 3 // 4, y + size * 2 // 3),
            (x + size // 4, y + size * 2 // 3),
        ]
        pygame.draw.polygon(surface, banana_color, points)
        
        # Stem
        pygame.draw.rect(surface, (100, 80, 40), (x + size // 2 - 2, y - 3, 5, 6))
    
    def _create_category_tabs(self) -> None:
        """Pre-render category tab surfaces."""
        self.tab_surfaces = {}
        
        for category in ItemCategory:
            # Normal state
            normal = pygame.Surface((self.tab_width, self.tab_height), pygame.SRCALPHA)
            pygame.draw.rect(normal, PARCHMENT_MEDIUM, (0, 0, self.tab_width, self.tab_height), border_radius=4)
            pygame.draw.rect(normal, SLOT_BORDER, (0, 0, self.tab_width, self.tab_height), 2, border_radius=4)
            text = self.category_font.render(category.value, True, TEXT_DARK)
            text_x = (self.tab_width - text.get_width()) // 2
            text_y = (self.tab_height - text.get_height()) // 2
            normal.blit(text, (text_x, text_y))
            
            # Selected state
            selected = pygame.Surface((self.tab_width, self.tab_height), pygame.SRCALPHA)
            pygame.draw.rect(selected, SLOT_HIGHLIGHT, (0, 0, self.tab_width, self.tab_height), border_radius=4)
            pygame.draw.rect(selected, GOLD_HIGHLIGHT, (0, 0, self.tab_width, self.tab_height), 2, border_radius=4)
            selected.blit(text, (text_x, text_y))
            
            # Banana icon for potions
            if category == ItemCategory.POTIONS:
                self._draw_banana(normal, 5, self.tab_height // 2 - 10, 20)
                self._draw_banana(selected, 5, self.tab_height // 2 - 10, 20)
            
            self.tab_surfaces[category] = {
                'normal': normal,
                'selected': selected
            }
    
    def set_player(self, player: Player) -> None:
        """Set the player reference for stats display."""
        self.player = player
        self._sync_inventory_from_player()
    
    def _sync_inventory_from_player(self) -> None:
        """Sync slots from player inventory."""
        if not self.player:
            return
        
        # Clear slots
        for slot in self.slots:
            slot.item = None
            slot.quantity = 1
        
        # Fill slots from player inventory
        for i, item in enumerate(self.player.inventory[:len(self.slots)]):
            self.slots[i].item = item
    
    def show(self) -> None:
        """Show the inventory screen."""
        self.visible = True
        self._sync_inventory_from_player()
    
    def hide(self) -> None:
        """Hide the inventory screen."""
        self.visible = False
    
    def toggle(self) -> None:
        """Toggle visibility."""
        if self.visible:
            self.hide()
        else:
            self.show()
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle input events."""
        if not self.visible:
            return False
        
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_i):
                self.hide()
                if self.on_close:
                    self.on_close()
                return True
            
            # Grid navigation
            if event.key == pygame.K_UP:
                if self.selected_slot >= self.GRID_COLS:
                    self.selected_slot -= self.GRID_COLS
                return True
            elif event.key == pygame.K_DOWN:
                if self.selected_slot < len(self.slots) - self.GRID_COLS:
                    self.selected_slot += self.GRID_COLS
                return True
            elif event.key == pygame.K_LEFT:
                if self.selected_slot % self.GRID_COLS > 0:
                    self.selected_slot -= 1
                return True
            elif event.key == pygame.K_RIGHT:
                if self.selected_slot % self.GRID_COLS < self.GRID_COLS - 1:
                    self.selected_slot += 1
                return True
            
            # Category switching with Tab
            elif event.key == pygame.K_TAB:
                categories = list(ItemCategory)
                current_idx = categories.index(self.current_category)
                self.current_category = categories[(current_idx + 1) % len(categories)]
                return True
            
            # Use item with Enter
            elif event.key == pygame.K_RETURN:
                slot = self.slots[self.selected_slot]
                if slot.item and self.on_item_use:
                    self.on_item_use(slot.item)
                return True
        
        elif event.type == pygame.MOUSEMOTION:
            self._update_hover(event.pos)
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                return self._handle_click(event.pos)
        
        return False
    
    def _update_hover(self, pos: tuple) -> None:
        """Update hovered slot based on mouse position."""
        self.hovered_slot = -1
        
        for i in range(len(self.slots)):
            slot_rect = self._get_slot_rect(i)
            if slot_rect.collidepoint(pos):
                self.hovered_slot = i
                break
    
    def _handle_click(self, pos: tuple) -> bool:
        """Handle mouse click."""
        # Check category tabs
        for i, category in enumerate(ItemCategory):
            tab_rect = pygame.Rect(
                self.tab_x,
                self.tab_y + i * (self.tab_height + self.tab_spacing),
                self.tab_width,
                self.tab_height
            )
            if tab_rect.collidepoint(pos):
                self.current_category = category
                return True
        
        # Check item slots
        for i in range(len(self.slots)):
            slot_rect = self._get_slot_rect(i)
            if slot_rect.collidepoint(pos):
                self.selected_slot = i
                slot = self.slots[i]
                if slot.item and self.on_item_select:
                    self.on_item_select(slot.item)
                return True
        
        return False
    
    def _get_slot_rect(self, index: int) -> pygame.Rect:
        """Get the rectangle for a slot by index."""
        col = index % self.GRID_COLS
        row = index // self.GRID_COLS
        
        x = self.grid_x + col * (self.SLOT_SIZE + self.SLOT_SPACING)
        y = self.grid_y + row * (self.SLOT_SIZE + self.SLOT_SPACING)
        
        return pygame.Rect(x, y, self.SLOT_SIZE, self.SLOT_SIZE)
    
    def render(self) -> None:
        """Render the inventory screen."""
        if not self.visible:
            return
        
        # Draw background
        self.screen.blit(self.background, (0, 0))
        
        # Draw category tabs
        self._render_category_tabs()
        
        # Draw item grid
        self._render_item_grid()
        
        # Draw character panel
        self._render_character_panel()
        
        # Draw description panel
        self._render_description_panel()
    
    def _render_category_tabs(self) -> None:
        """Render the category tabs."""
        for i, category in enumerate(ItemCategory):
            y = self.tab_y + i * (self.tab_height + self.tab_spacing)
            
            if category == self.current_category:
                surface = self.tab_surfaces[category]['selected']
            else:
                surface = self.tab_surfaces[category]['normal']
            
            self.screen.blit(surface, (self.tab_x, y))
    
    def _render_item_grid(self) -> None:
        """Render the item grid."""
        for i, slot in enumerate(self.slots):
            rect = self._get_slot_rect(i)
            is_selected = (i == self.selected_slot)
            is_hovered = (i == self.hovered_slot)
            
            # Slot background
            bg_color = SLOT_HIGHLIGHT if is_selected or is_hovered else SLOT_BG
            pygame.draw.rect(self.screen, bg_color, rect, border_radius=4)
            
            # Slot border
            border_color = GOLD_HIGHLIGHT if is_selected else SLOT_BORDER
            border_width = 3 if is_selected else 2
            pygame.draw.rect(self.screen, border_color, rect, border_width, border_radius=4)
            
            # Item icon (if present)
            if slot.item:
                self._render_item_icon(rect, slot.item)
                
                # Quantity badge
                if slot.quantity > 1:
                    qty_text = self.desc_font.render(str(slot.quantity), True, (255, 255, 255))
                    qty_bg = pygame.Rect(rect.right - 16, rect.bottom - 14, 14, 12)
                    pygame.draw.rect(self.screen, (60, 40, 20), qty_bg, border_radius=2)
                    self.screen.blit(qty_text, (qty_bg.x + 2, qty_bg.y))
    
    def _render_item_icon(self, rect: pygame.Rect, item: Item) -> None:
        """Render an item icon in a slot."""
        # Simple colored placeholder based on item type
        icon_margin = 6
        icon_rect = pygame.Rect(
            rect.x + icon_margin,
            rect.y + icon_margin,
            rect.width - icon_margin * 2,
            rect.height - icon_margin * 2
        )
        
        # Color by item type
        if item.item_type == ItemType.WEAPON:
            color = (180, 180, 200)  # Silver
            # Simple sword shape
            pygame.draw.rect(self.screen, color, 
                           (icon_rect.centerx - 3, icon_rect.top, 6, icon_rect.height - 8))
            pygame.draw.rect(self.screen, (139, 90, 43),
                           (icon_rect.centerx - 10, icon_rect.bottom - 12, 20, 6))
        elif item.item_type == ItemType.ARMOR:
            color = (139, 90, 43)  # Brown leather
            pygame.draw.rect(self.screen, color, icon_rect, border_radius=4)
            # Simple tunic shape
            pygame.draw.rect(self.screen, (100, 65, 30),
                           (icon_rect.centerx - 8, icon_rect.top + 5, 16, 20), border_radius=2)
        elif item.item_type == ItemType.POTION:
            # Red potion bottle
            pygame.draw.circle(self.screen, (200, 60, 60), 
                             (icon_rect.centerx, icon_rect.centery + 5), 12)
            pygame.draw.rect(self.screen, (150, 50, 50),
                           (icon_rect.centerx - 4, icon_rect.top + 3, 8, 12))
            pygame.draw.rect(self.screen, (200, 200, 200),
                           (icon_rect.centerx - 5, icon_rect.top, 10, 6))
        else:
            # Generic item
            pygame.draw.rect(self.screen, (160, 140, 100), icon_rect, border_radius=4)
    
    def _render_character_panel(self) -> None:
        """Render the character portrait and stats."""
        # Portrait frame
        portrait_rect = pygame.Rect(self.char_x, self.char_y, self.portrait_size, self.portrait_size)
        pygame.draw.rect(self.screen, PARCHMENT_MEDIUM, portrait_rect)
        pygame.draw.rect(self.screen, GOLD_HIGHLIGHT, portrait_rect, 3)
        
        # Simple character placeholder
        self._render_character_placeholder(portrait_rect)
        
        # Stats
        if self.player:
            stats = self.player.total_stats
            stat_list = [
                (f"STR: {stats.strength}", "banana"),
                (f"INT: {stats.intelligence}", "banana"),
                (f"DEX: {stats.dexterity}", "banana"),
                (f"WIS: 10", "banana"),  # Not in current Stats class
                (f"CON: {stats.constitution}", "banana"),
                (f"CHA: 10", "banana"),  # Not in current Stats class
            ]
            
            # Two columns of stats
            col1_x = self.char_x
            col2_x = self.char_x + 90
            start_y = self.stats_y
            
            for i, (text, icon) in enumerate(stat_list):
                x = col1_x if i % 2 == 0 else col2_x
                y = start_y + (i // 2) * 28
                
                # Draw small banana icon
                self._draw_banana(self.screen, x, y + 2, 16)
                
                # Draw stat text
                stat_surface = self.stat_font.render(text, True, TEXT_DARK)
                self.screen.blit(stat_surface, (x + 20, y))
    
    def _render_character_placeholder(self, rect: pygame.Rect) -> None:
        """Render a placeholder character portrait."""
        # Simple pixel art face
        center_x = rect.centerx
        center_y = rect.centery
        
        # Hair (brown)
        pygame.draw.ellipse(self.screen, (100, 70, 40), 
                          (center_x - 25, center_y - 35, 50, 35))
        
        # Face (skin tone)
        pygame.draw.ellipse(self.screen, (230, 190, 150),
                          (center_x - 20, center_y - 20, 40, 45))
        
        # Eyes
        pygame.draw.circle(self.screen, (60, 40, 30), (center_x - 8, center_y - 5), 4)
        pygame.draw.circle(self.screen, (60, 40, 30), (center_x + 8, center_y - 5), 4)
        
        # Smile
        pygame.draw.arc(self.screen, (60, 40, 30),
                       (center_x - 8, center_y + 5, 16, 10), 3.14, 0, 2)
        
        # Shirt/body hint
        pygame.draw.rect(self.screen, (70, 140, 170),
                        (center_x - 18, rect.bottom - 25, 36, 25))
    
    def _render_description_panel(self) -> None:
        """Render the item description panel with vine border."""
        rect = pygame.Rect(self.desc_x, self.desc_y, self.desc_width, self.desc_height)
        
        # Parchment background
        pygame.draw.rect(self.screen, PARCHMENT_LIGHT, rect, border_radius=8)
        
        # Vine border
        self._draw_vine_border(rect)
        
        # Get selected item
        slot = self.slots[self.selected_slot] if self.selected_slot < len(self.slots) else None
        item = slot.item if slot else None
        
        if item:
            # Item name
            name_text = self.title_font.render(item.name.upper() + ":", True, TEXT_DARK)
            self.screen.blit(name_text, (rect.x + 15, rect.y + 15))
            
            # Description
            desc = item.description or f"A {item.item_type.value.lower()}."
            lines = self._wrap_text(desc, self.desc_width - 30)
            
            y = rect.y + 45
            for line in lines[:3]:  # Max 3 lines
                line_surface = self.desc_font.render(line, True, TEXT_DARK)
                self.screen.blit(line_surface, (rect.x + 15, y))
                y += 22
        else:
            # Empty slot message
            hint_text = self.desc_font.render("Select an item to view details.", True, TEXT_DARK)
            self.screen.blit(hint_text, (rect.x + 15, rect.y + 50))
    
    def _draw_vine_border(self, rect: pygame.Rect) -> None:
        """Draw a decorative vine border around a rectangle."""
        vine_color = VINE_GREEN
        
        # Draw vine along each edge
        pygame.draw.rect(self.screen, vine_color, rect, 4, border_radius=8)
        
        # Add leaf decorations at corners
        leaf_offsets = [
            (rect.left + 10, rect.top + 5),
            (rect.right - 25, rect.top + 5),
            (rect.left + 10, rect.bottom - 20),
            (rect.right - 25, rect.bottom - 20),
        ]
        
        for lx, ly in leaf_offsets:
            # Simple leaf shape
            points = [(lx, ly + 7), (lx + 7, ly), (lx + 15, ly + 7), (lx + 7, ly + 14)]
            pygame.draw.polygon(self.screen, vine_color, points)
        
        # Add banana decorations
        self._draw_banana(self.screen, rect.left + 40, rect.top - 5, 22)
        self._draw_banana(self.screen, rect.right - 60, rect.bottom - 18, 22)
    
    def _wrap_text(self, text: str, max_width: int) -> List[str]:
        """Wrap text to fit within a width."""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            test_surface = self.desc_font.render(test_line, True, TEXT_DARK)
            
            if test_surface.get_width() <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines

