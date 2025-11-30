"""
UI Components

Reusable UI components for the game interface.
"""

import pygame
from typing import Optional, Callable, List, Tuple, Dict, Any
from abc import ABC, abstractmethod

# Use absolute imports for standalone execution
try:
    from pygame_mvp.config import (
        CURRENT_THEME,
        PADDING,
        PANEL_BORDER_WIDTH,
        PANEL_CORNER_RADIUS,
        FONT_SIZE_SMALL,
        FONT_SIZE_NORMAL,
        FONT_SIZE_LARGE,
        FONT_SIZE_HEADER,
        BUTTON_HEIGHT,
        BUTTON_MIN_WIDTH,
        BUTTON_PADDING,
        STAT_BAR_HEIGHT,
        STAT_BAR_CORNER_RADIUS,
        INVENTORY_SLOT_SIZE,
        INVENTORY_SLOT_SPACING,
        INVENTORY_SLOTS_PER_ROW
    )
    from pygame_mvp.ui.theme import get_theme
except ImportError:
    from config import (
        CURRENT_THEME,
        PADDING,
        PANEL_BORDER_WIDTH,
        PANEL_CORNER_RADIUS,
        FONT_SIZE_SMALL,
        FONT_SIZE_NORMAL,
        FONT_SIZE_LARGE,
        FONT_SIZE_HEADER,
        BUTTON_HEIGHT,
        BUTTON_MIN_WIDTH,
        BUTTON_PADDING,
        STAT_BAR_HEIGHT,
        STAT_BAR_CORNER_RADIUS,
        INVENTORY_SLOT_SIZE,
        INVENTORY_SLOT_SPACING,
        INVENTORY_SLOTS_PER_ROW
    )
    from ui.theme import get_theme


class UIComponent(ABC):
    """
    Base class for all UI components.

    Provides common functionality for positioning, visibility, and event handling.
    """

    def __init__(self, x: int, y: int, width: int, height: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.visible = True
        self.enabled = True
        self._rect = pygame.Rect(x, y, width, height)

        # Fonts (initialized on first render)
        self._fonts_initialized = False
        self._font_small: Optional[pygame.font.Font] = None
        self._font_normal: Optional[pygame.font.Font] = None
        self._font_large: Optional[pygame.font.Font] = None
        self._font_header: Optional[pygame.font.Font] = None

    def _init_fonts(self) -> None:
        """Initialize fonts on first use."""
        if self._fonts_initialized:
            return
        pygame.font.init()
        self._font_small = pygame.font.Font(None, FONT_SIZE_SMALL + 4)
        self._font_normal = pygame.font.Font(None, FONT_SIZE_NORMAL + 4)
        self._font_large = pygame.font.Font(None, FONT_SIZE_LARGE + 4)
        self._font_header = pygame.font.Font(None, FONT_SIZE_HEADER + 4)
        self._fonts_initialized = True

    @property
    def rect(self) -> pygame.Rect:
        """Get the component's bounding rectangle."""
        return self._rect

    def set_position(self, x: int, y: int) -> None:
        """Update component position."""
        self.x = x
        self.y = y
        self._rect.x = x
        self._rect.y = y

    def contains_point(self, x: int, y: int) -> bool:
        """Check if point is within component bounds."""
        return self._rect.collidepoint(x, y)

    @abstractmethod
    def render(self, surface: pygame.Surface) -> None:
        """Render the component to a surface."""
        pass

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle a pygame event.

        Returns:
            True if the event was consumed, False otherwise.
        """
        return False


class Panel(UIComponent):
    """
    Container panel with title and border.

    Can contain other UI components as children.
    """

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        title: str = "",
        show_border: bool = True
    ):
        super().__init__(x, y, width, height)
        self.title = title
        self.show_border = show_border
        self.children: List[UIComponent] = []

        # Calculate content area
        self.header_height = 24 if title else 0
        self.content_x = x + PADDING
        self.content_y = y + self.header_height + PADDING
        self.content_width = width - PADDING * 2
        self.content_height = height - self.header_height - PADDING * 2

    def add_child(self, child: UIComponent) -> None:
        """Add a child component."""
        self.children.append(child)

    def render(self, surface: pygame.Surface) -> None:
        """Render the panel and its children."""
        if not self.visible:
            return

        self._init_fonts()
        theme = get_theme()

        # Draw background
        pygame.draw.rect(
            surface,
            theme.panel_bg,
            self._rect,
            border_radius=PANEL_CORNER_RADIUS
        )

        # Draw border
        if self.show_border:
            pygame.draw.rect(
                surface,
                theme.panel_border,
                self._rect,
                PANEL_BORDER_WIDTH,
                border_radius=PANEL_CORNER_RADIUS
            )

        # Draw header
        if self.title:
            header_rect = pygame.Rect(
                self.x + PANEL_BORDER_WIDTH,
                self.y + PANEL_BORDER_WIDTH,
                self.width - PANEL_BORDER_WIDTH * 2,
                self.header_height
            )
            pygame.draw.rect(
                surface,
                theme.panel_header,
                header_rect,
                border_top_left_radius=PANEL_CORNER_RADIUS - 1,
                border_top_right_radius=PANEL_CORNER_RADIUS - 1
            )

            # Draw title text
            title_text = self._font_normal.render(self.title, True, theme.text_primary)
            title_rect = title_text.get_rect(
                centery=header_rect.centery,
                left=header_rect.left + PADDING
            )
            surface.blit(title_text, title_rect)

        # Render children
        for child in self.children:
            child.render(surface)

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Pass events to children."""
        for child in reversed(self.children):  # Top children first
            if child.handle_event(event):
                return True
        return False


class Button(UIComponent):
    """
    Clickable button with hover and pressed states.
    """

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        text: str,
        callback: Optional[Callable] = None
    ):
        super().__init__(x, y, max(width, BUTTON_MIN_WIDTH), height)
        self.text = text
        self.callback = callback
        self.hovered = False
        self.pressed = False

    def render(self, surface: pygame.Surface) -> None:
        """Render the button."""
        if not self.visible:
            return

        self._init_fonts()
        theme = get_theme()

        # Determine background color based on state
        if not self.enabled:
            bg_color = theme.darken("button_bg", 20)
        elif self.pressed:
            bg_color = theme.button_pressed
        elif self.hovered:
            bg_color = theme.button_hover
        else:
            bg_color = theme.button_bg

        # Draw background
        pygame.draw.rect(
            surface,
            bg_color,
            self._rect,
            border_radius=4
        )

        # Draw border
        pygame.draw.rect(
            surface,
            theme.button_border,
            self._rect,
            2,
            border_radius=4
        )

        # Draw text
        text_color = theme.text_primary if self.enabled else theme.text_secondary
        text_surface = self._font_normal.render(self.text, True, text_color)
        text_rect = text_surface.get_rect(center=self._rect.center)
        surface.blit(text_surface, text_rect)

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle mouse events."""
        if not self.visible or not self.enabled:
            return False

        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.contains_point(*event.pos)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.contains_point(*event.pos):
                self.pressed = True
                return True

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.pressed:
                self.pressed = False
                if self.contains_point(*event.pos) and self.callback:
                    self.callback()
                return True

        return False


class TextBox(UIComponent):
    """
    Scrollable text display area.
    """

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        lines: Optional[List[str]] = None
    ):
        super().__init__(x, y, width, height)
        self.lines = lines or []
        self.scroll_offset = 0
        self.line_height = FONT_SIZE_NORMAL + 6
        self.max_visible_lines = (height - PADDING * 2) // self.line_height

    def add_line(self, text: str) -> None:
        """Add a line of text."""
        self.lines.append(text)
        # Auto-scroll to bottom
        self._scroll_to_bottom()

    def set_lines(self, lines: List[str]) -> None:
        """Set all lines."""
        self.lines = lines
        self._scroll_to_bottom()

    def clear(self) -> None:
        """Clear all text."""
        self.lines = []
        self.scroll_offset = 0

    def _scroll_to_bottom(self) -> None:
        """Scroll to show the most recent lines."""
        total_lines = len(self.lines)
        if total_lines > self.max_visible_lines:
            self.scroll_offset = total_lines - self.max_visible_lines

    def render(self, surface: pygame.Surface) -> None:
        """Render the text box."""
        if not self.visible:
            return

        self._init_fonts()
        theme = get_theme()

        # Draw background
        pygame.draw.rect(
            surface,
            theme.darken("panel_bg", 10),
            self._rect,
            border_radius=3
        )

        # Create clip rect for text
        clip_rect = pygame.Rect(
            self.x + PADDING,
            self.y + PADDING,
            self.width - PADDING * 2,
            self.height - PADDING * 2
        )

        # Render visible lines
        y_pos = self.y + PADDING
        start_idx = self.scroll_offset
        end_idx = min(start_idx + self.max_visible_lines, len(self.lines))

        for i in range(start_idx, end_idx):
            line = self.lines[i]
            text_surface = self._font_small.render(line, True, theme.text_secondary)

            # Clip text to box width
            if text_surface.get_width() > clip_rect.width:
                text_surface = text_surface.subsurface(
                    (0, 0, clip_rect.width, text_surface.get_height())
                )

            surface.blit(text_surface, (clip_rect.x, y_pos))
            y_pos += self.line_height

        # Draw scroll indicators if needed
        if self.scroll_offset > 0:
            # Up arrow indicator
            pygame.draw.polygon(
                surface,
                theme.text_secondary,
                [(self.x + self.width - 15, self.y + 10),
                 (self.x + self.width - 10, self.y + 5),
                 (self.x + self.width - 5, self.y + 10)]
            )

        if end_idx < len(self.lines):
            # Down arrow indicator
            pygame.draw.polygon(
                surface,
                theme.text_secondary,
                [(self.x + self.width - 15, self.y + self.height - 10),
                 (self.x + self.width - 10, self.y + self.height - 5),
                 (self.x + self.width - 5, self.y + self.height - 10)]
            )

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle scroll events."""
        if not self.visible:
            return False

        if event.type == pygame.MOUSEWHEEL:
            if self.contains_point(*pygame.mouse.get_pos()):
                self.scroll_offset = max(
                    0,
                    min(
                        self.scroll_offset - event.y,
                        max(0, len(self.lines) - self.max_visible_lines)
                    )
                )
                return True

        return False


class ImageFrame(UIComponent):
    """
    Display area for images (placeholder or real).
    """

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        image: Optional[pygame.Surface] = None,
        label: str = ""
    ):
        super().__init__(x, y, width, height)
        self.image = image
        self.label = label

    def set_image(self, image: pygame.Surface) -> None:
        """Set the displayed image."""
        self.image = image

    def render(self, surface: pygame.Surface) -> None:
        """Render the image frame."""
        if not self.visible:
            return

        self._init_fonts()
        theme = get_theme()

        # Draw border
        pygame.draw.rect(
            surface,
            theme.panel_border,
            self._rect,
            1,
            border_radius=2
        )

        # Draw image or placeholder
        if self.image:
            # Scale image to fit if needed
            img_rect = self.image.get_rect()
            scale_x = (self.width - 4) / img_rect.width
            scale_y = (self.height - 4) / img_rect.height
            scale = min(scale_x, scale_y, 1.0)  # Don't upscale

            if scale < 1.0:
                new_size = (int(img_rect.width * scale), int(img_rect.height * scale))
                scaled = pygame.transform.smoothscale(self.image, new_size)
            else:
                scaled = self.image

            # Center the image
            img_x = self.x + (self.width - scaled.get_width()) // 2
            img_y = self.y + (self.height - scaled.get_height()) // 2
            surface.blit(scaled, (img_x, img_y))
        else:
            # Draw placeholder background
            inner_rect = pygame.Rect(
                self.x + 2, self.y + 2,
                self.width - 4, self.height - 4
            )
            pygame.draw.rect(
                surface,
                theme.placeholder_scene,
                inner_rect
            )

            # Draw label if provided
            if self.label:
                label_text = self._font_small.render(self.label, True, theme.text_secondary)
                label_rect = label_text.get_rect(center=self._rect.center)
                surface.blit(label_text, label_rect)


class StatBar(UIComponent):
    """
    Progress bar for HP, Mana, XP, etc.
    """

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int = STAT_BAR_HEIGHT,
        value: float = 1.0,
        bar_color: str = "hp_bar",
        bg_color: str = "hp_bar_bg",
        show_text: bool = True,
        label: str = ""
    ):
        super().__init__(x, y, width, height)
        self.value = value  # 0.0 to 1.0
        self.bar_color = bar_color
        self.bg_color = bg_color
        self.show_text = show_text
        self.label = label
        self.current = 0
        self.maximum = 100

    def set_value(self, current: int, maximum: int) -> None:
        """Set the bar value."""
        self.current = current
        self.maximum = maximum
        self.value = current / maximum if maximum > 0 else 0

    def render(self, surface: pygame.Surface) -> None:
        """Render the stat bar."""
        if not self.visible:
            return

        self._init_fonts()
        theme = get_theme()

        # Draw background
        pygame.draw.rect(
            surface,
            theme.get(self.bg_color),
            self._rect,
            border_radius=STAT_BAR_CORNER_RADIUS
        )

        # Draw filled portion
        fill_width = int((self.width - 2) * max(0, min(1, self.value)))
        if fill_width > 0:
            fill_rect = pygame.Rect(
                self.x + 1,
                self.y + 1,
                fill_width,
                self.height - 2
            )
            pygame.draw.rect(
                surface,
                theme.get(self.bar_color),
                fill_rect,
                border_radius=max(0, STAT_BAR_CORNER_RADIUS - 1)
            )

        # Draw border
        pygame.draw.rect(
            surface,
            theme.panel_border,
            self._rect,
            1,
            border_radius=STAT_BAR_CORNER_RADIUS
        )

        # Draw text
        if self.show_text:
            if self.label:
                text = f"{self.label}: {self.current}/{self.maximum}"
            else:
                text = f"{self.current}/{self.maximum}"
            text_surface = self._font_small.render(text, True, theme.text_primary)
            text_rect = text_surface.get_rect(center=self._rect.center)
            surface.blit(text_surface, text_rect)


class InventorySlot(UIComponent):
    """
    Single inventory slot that can hold an item.
    """

    def __init__(
        self,
        x: int,
        y: int,
        size: int = INVENTORY_SLOT_SIZE,
        item_image: Optional[pygame.Surface] = None,
        quantity: int = 0,
        on_click: Optional[Callable] = None
    ):
        super().__init__(x, y, size, size)
        self.item_image = item_image
        self.quantity = quantity
        self.on_click = on_click
        self.selected = False
        self.hovered = False

    def set_item(self, image: Optional[pygame.Surface], quantity: int = 1) -> None:
        """Set the item in this slot."""
        self.item_image = image
        self.quantity = quantity

    def clear(self) -> None:
        """Clear the slot."""
        self.item_image = None
        self.quantity = 0

    def render(self, surface: pygame.Surface) -> None:
        """Render the inventory slot."""
        if not self.visible:
            return

        self._init_fonts()
        theme = get_theme()

        # Determine background color
        if self.selected:
            bg_color = theme.lighten("panel_bg", 30)
        elif self.hovered:
            bg_color = theme.lighten("panel_bg", 15)
        else:
            bg_color = theme.darken("panel_bg", 5)

        # Draw background
        pygame.draw.rect(
            surface,
            bg_color,
            self._rect,
            border_radius=3
        )

        # Draw border
        border_color = theme.text_highlight if self.selected else theme.panel_border
        pygame.draw.rect(
            surface,
            border_color,
            self._rect,
            1,
            border_radius=3
        )

        # Draw item image
        if self.item_image:
            # Scale to fit
            img_size = self.width - 8
            scaled = pygame.transform.smoothscale(self.item_image, (img_size, img_size))
            img_x = self.x + 4
            img_y = self.y + 4
            surface.blit(scaled, (img_x, img_y))

            # Draw quantity
            if self.quantity > 1:
                qty_text = self._font_small.render(str(self.quantity), True, theme.text_primary)
                qty_rect = qty_text.get_rect(
                    right=self.x + self.width - 2,
                    bottom=self.y + self.height - 2
                )
                # Draw shadow
                shadow_text = self._font_small.render(str(self.quantity), True, (0, 0, 0))
                surface.blit(shadow_text, (qty_rect.x + 1, qty_rect.y + 1))
                surface.blit(qty_text, qty_rect)

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle mouse events."""
        if not self.visible:
            return False

        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.contains_point(*event.pos)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.contains_point(*event.pos):
                if self.on_click:
                    self.on_click()
                return True

        return False


class InventoryGrid(UIComponent):
    """
    Grid of inventory slots.
    """

    def __init__(
        self,
        x: int,
        y: int,
        slots_per_row: int = INVENTORY_SLOTS_PER_ROW,
        num_slots: int = 20,
        slot_size: int = INVENTORY_SLOT_SIZE,
        spacing: int = INVENTORY_SLOT_SPACING
    ):
        self.slots_per_row = slots_per_row
        self.num_slots = num_slots
        self.slot_size = slot_size
        self.spacing = spacing

        # Calculate dimensions
        num_rows = (num_slots + slots_per_row - 1) // slots_per_row
        width = slots_per_row * (slot_size + spacing) - spacing
        height = num_rows * (slot_size + spacing) - spacing

        super().__init__(x, y, width, height)

        # Create slots
        self.slots: List[InventorySlot] = []
        for i in range(num_slots):
            row = i // slots_per_row
            col = i % slots_per_row
            slot_x = x + col * (slot_size + spacing)
            slot_y = y + row * (slot_size + spacing)
            slot = InventorySlot(slot_x, slot_y, slot_size)
            self.slots.append(slot)

        self.selected_index: Optional[int] = None

    def set_slot(self, index: int, image: Optional[pygame.Surface], quantity: int = 1) -> None:
        """Set item in a specific slot."""
        if 0 <= index < len(self.slots):
            self.slots[index].set_item(image, quantity)

    def clear_slot(self, index: int) -> None:
        """Clear a specific slot."""
        if 0 <= index < len(self.slots):
            self.slots[index].clear()

    def clear_all(self) -> None:
        """Clear all slots."""
        for slot in self.slots:
            slot.clear()

    def render(self, surface: pygame.Surface) -> None:
        """Render all inventory slots."""
        if not self.visible:
            return

        for i, slot in enumerate(self.slots):
            slot.selected = (i == self.selected_index)
            slot.render(surface)

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle events for all slots."""
        for i, slot in enumerate(self.slots):
            if slot.handle_event(event):
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.selected_index = i
                return True
        return False

