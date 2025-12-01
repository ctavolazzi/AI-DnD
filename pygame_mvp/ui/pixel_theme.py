"""
Pixel Art Theme - Inspired by Nano Banana Games mockups

A warm, parchment-style pixel art theme with decorative borders.
"""

from typing import Dict, Tuple

# =============================================================================
# PIXEL ART COLOR PALETTE
# =============================================================================

# Parchment/Paper tones
PARCHMENT_LIGHT = (244, 228, 178)  # Main background
PARCHMENT_MEDIUM = (228, 200, 142)  # Secondary areas
PARCHMENT_DARK = (180, 150, 100)   # Shadows/borders

# Wood/Frame tones (from the border)
WOOD_LIGHT = (139, 90, 43)
WOOD_MEDIUM = (101, 67, 33)
WOOD_DARK = (60, 40, 20)

# Item slot brown
SLOT_BG = (165, 130, 95)
SLOT_BORDER = (120, 90, 60)
SLOT_HIGHLIGHT = (200, 170, 130)

# Stat bar colors
HP_RED = (200, 60, 60)
HP_RED_DARK = (140, 40, 40)
MP_BLUE = (70, 130, 200)
MP_BLUE_DARK = (40, 80, 140)

# Text colors
TEXT_DARK = (60, 40, 20)
TEXT_MEDIUM = (100, 70, 40)
TEXT_LIGHT = (200, 180, 140)
TEXT_GOLD = (255, 200, 50)
TEXT_WHITE = (255, 250, 240)

# Decorative green (vine border)
VINE_GREEN = (60, 120, 60)
VINE_GREEN_LIGHT = (80, 150, 80)
VINE_GREEN_DARK = (40, 80, 40)

# Accent colors
GOLD_HIGHLIGHT = (255, 215, 0)
GOLD_DARK = (180, 140, 20)
BANANA_YELLOW = (255, 230, 100)


# =============================================================================
# PIXEL THEME CLASS
# =============================================================================

class PixelTheme:
    """Pixel art theme with warm parchment colors."""
    
    def __init__(self):
        self.name = "pixel"
        
        # Main backgrounds
        self.background = WOOD_DARK
        self.panel_bg = PARCHMENT_LIGHT
        self.panel_bg_dark = PARCHMENT_MEDIUM
        self.panel_border = WOOD_MEDIUM
        self.panel_header = WOOD_LIGHT
        
        # Text
        self.text_primary = TEXT_DARK
        self.text_secondary = TEXT_MEDIUM
        self.text_highlight = TEXT_GOLD
        self.text_light = TEXT_LIGHT
        
        # Buttons/Interactive
        self.button_bg = SLOT_BG
        self.button_hover = SLOT_HIGHLIGHT
        self.button_pressed = SLOT_BORDER
        self.button_border = WOOD_MEDIUM
        
        # Stat bars
        self.hp_bar = HP_RED
        self.hp_bar_bg = HP_RED_DARK
        self.mana_bar = MP_BLUE
        self.mana_bar_bg = MP_BLUE_DARK
        
        # Item slots
        self.slot_bg = SLOT_BG
        self.slot_border = SLOT_BORDER
        self.slot_highlight = GOLD_HIGHLIGHT
        
        # Decorative
        self.vine_border = VINE_GREEN
        self.gold_accent = GOLD_HIGHLIGHT
        
        # Title screen
        self.title_text = TEXT_GOLD
        self.title_shadow = WOOD_DARK
        self.menu_text = TEXT_WHITE
        self.menu_text_selected = TEXT_GOLD


# Global pixel theme instance
_pixel_theme = PixelTheme()


def get_pixel_theme() -> PixelTheme:
    """Get the pixel art theme."""
    return _pixel_theme

