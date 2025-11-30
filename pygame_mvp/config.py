"""
Configuration constants for Pygame MVP

All game settings, dimensions, colors, and layout constants in one place.
"""

# =============================================================================
# SCREEN SETTINGS
# =============================================================================

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
GAME_TITLE = "AI D&D Adventure"

# =============================================================================
# COLOR THEMES
# =============================================================================

# D&D Classic Theme (Brown/Gold)
THEME_CLASSIC = {
    "name": "classic",
    "background": (30, 20, 15),
    "panel_bg": (45, 35, 30),
    "panel_border": (139, 90, 43),
    "panel_header": (101, 67, 33),
    "text_primary": (255, 245, 220),
    "text_secondary": (200, 180, 150),
    "text_highlight": (255, 215, 0),
    "button_bg": (70, 50, 35),
    "button_hover": (90, 65, 45),
    "button_pressed": (50, 35, 25),
    "button_border": (139, 90, 43),
    "hp_bar": (180, 40, 40),
    "hp_bar_bg": (60, 20, 20),
    "mana_bar": (40, 80, 180),
    "mana_bar_bg": (20, 30, 60),
    "success": (60, 180, 60),
    "warning": (220, 180, 40),
    "error": (200, 50, 50),
    # Placeholder image colors
    "placeholder_scene": (40, 60, 100),
    "placeholder_character": (40, 100, 60),
    "placeholder_item": (100, 80, 40),
}

# Dark Fantasy Theme
THEME_DARK = {
    "name": "dark",
    "background": (15, 15, 20),
    "panel_bg": (25, 25, 35),
    "panel_border": (80, 70, 100),
    "panel_header": (50, 45, 70),
    "text_primary": (220, 220, 240),
    "text_secondary": (150, 150, 170),
    "text_highlight": (180, 150, 255),
    "button_bg": (40, 40, 55),
    "button_hover": (55, 55, 75),
    "button_pressed": (30, 30, 40),
    "button_border": (100, 90, 130),
    "hp_bar": (160, 50, 50),
    "hp_bar_bg": (50, 20, 20),
    "mana_bar": (80, 60, 180),
    "mana_bar_bg": (30, 25, 60),
    "success": (50, 200, 100),
    "warning": (220, 160, 50),
    "error": (220, 60, 60),
    "placeholder_scene": (30, 40, 80),
    "placeholder_character": (30, 80, 50),
    "placeholder_item": (80, 60, 30),
}

# Current active theme
CURRENT_THEME = THEME_CLASSIC

# =============================================================================
# LAYOUT CONSTANTS
# =============================================================================

# Margins and padding
MARGIN = 10
PADDING = 8
PANEL_BORDER_WIDTH = 2
PANEL_CORNER_RADIUS = 5

# Left sidebar (Navigation, Map)
LEFT_SIDEBAR_WIDTH = 250
LEFT_SIDEBAR_X = MARGIN
LEFT_SIDEBAR_Y = MARGIN

# Right sidebar (Character Stats, Inventory)
RIGHT_SIDEBAR_WIDTH = 280
RIGHT_SIDEBAR_X = SCREEN_WIDTH - RIGHT_SIDEBAR_WIDTH - MARGIN
RIGHT_SIDEBAR_Y = MARGIN

# Center area (Scene Viewer, Adventure Log)
CENTER_X = LEFT_SIDEBAR_WIDTH + MARGIN * 2
CENTER_WIDTH = SCREEN_WIDTH - LEFT_SIDEBAR_WIDTH - RIGHT_SIDEBAR_WIDTH - MARGIN * 4
CENTER_Y = MARGIN

# Bottom bar (Action Buttons)
BOTTOM_BAR_HEIGHT = 60
BOTTOM_BAR_Y = SCREEN_HEIGHT - BOTTOM_BAR_HEIGHT - MARGIN

# Scene Viewer (main image area)
SCENE_VIEWER_WIDTH = CENTER_WIDTH
SCENE_VIEWER_HEIGHT = 320
SCENE_VIEWER_X = CENTER_X
SCENE_VIEWER_Y = CENTER_Y

# Adventure Log (text area below scene)
ADVENTURE_LOG_X = CENTER_X
ADVENTURE_LOG_Y = SCENE_VIEWER_Y + SCENE_VIEWER_HEIGHT + MARGIN
ADVENTURE_LOG_WIDTH = CENTER_WIDTH
ADVENTURE_LOG_HEIGHT = SCREEN_HEIGHT - SCENE_VIEWER_HEIGHT - BOTTOM_BAR_HEIGHT - MARGIN * 5

# Map panel (left sidebar top)
MAP_PANEL_WIDTH = LEFT_SIDEBAR_WIDTH - MARGIN
MAP_PANEL_HEIGHT = 180
MAP_PANEL_X = LEFT_SIDEBAR_X
MAP_PANEL_Y = LEFT_SIDEBAR_Y

# Navigation panel (left sidebar bottom)
NAV_PANEL_WIDTH = LEFT_SIDEBAR_WIDTH - MARGIN
NAV_PANEL_HEIGHT = SCREEN_HEIGHT - MAP_PANEL_HEIGHT - BOTTOM_BAR_HEIGHT - MARGIN * 4
NAV_PANEL_X = LEFT_SIDEBAR_X
NAV_PANEL_Y = MAP_PANEL_Y + MAP_PANEL_HEIGHT + MARGIN

# Character panel (right sidebar top)
CHARACTER_PANEL_WIDTH = RIGHT_SIDEBAR_WIDTH - MARGIN
CHARACTER_PANEL_HEIGHT = 280
CHARACTER_PANEL_X = RIGHT_SIDEBAR_X
CHARACTER_PANEL_Y = RIGHT_SIDEBAR_Y

# Inventory panel (right sidebar middle)
INVENTORY_PANEL_WIDTH = RIGHT_SIDEBAR_WIDTH - MARGIN
INVENTORY_PANEL_HEIGHT = 200
INVENTORY_PANEL_X = RIGHT_SIDEBAR_X
INVENTORY_PANEL_Y = CHARACTER_PANEL_Y + CHARACTER_PANEL_HEIGHT + MARGIN

# Quest panel (right sidebar bottom)
QUEST_PANEL_WIDTH = RIGHT_SIDEBAR_WIDTH - MARGIN
QUEST_PANEL_HEIGHT = SCREEN_HEIGHT - CHARACTER_PANEL_HEIGHT - INVENTORY_PANEL_HEIGHT - BOTTOM_BAR_HEIGHT - MARGIN * 5
QUEST_PANEL_X = RIGHT_SIDEBAR_X
QUEST_PANEL_Y = INVENTORY_PANEL_Y + INVENTORY_PANEL_HEIGHT + MARGIN

# =============================================================================
# IMAGE PLACEHOLDER DIMENSIONS
# =============================================================================

# Scene images (main view)
SCENE_IMAGE_WIDTH = SCENE_VIEWER_WIDTH - PADDING * 2
SCENE_IMAGE_HEIGHT = SCENE_VIEWER_HEIGHT - 30  # Account for title bar

# Character portraits
PORTRAIT_WIDTH = 80
PORTRAIT_HEIGHT = 100

# Item icons
ITEM_ICON_SIZE = 40

# Map thumbnail
MAP_THUMB_WIDTH = MAP_PANEL_WIDTH - PADDING * 2
MAP_THUMB_HEIGHT = MAP_PANEL_HEIGHT - 30

# =============================================================================
# FONT SETTINGS
# =============================================================================

FONT_FAMILY = None  # Use pygame default (will try system fonts)
FONT_SIZE_SMALL = 12
FONT_SIZE_NORMAL = 14
FONT_SIZE_LARGE = 18
FONT_SIZE_TITLE = 24
FONT_SIZE_HEADER = 20

# =============================================================================
# BUTTON SETTINGS
# =============================================================================

BUTTON_HEIGHT = 36
BUTTON_MIN_WIDTH = 100
BUTTON_PADDING = 12

# Action button dimensions (bottom bar)
ACTION_BUTTON_WIDTH = 140
ACTION_BUTTON_HEIGHT = 44
ACTION_BUTTON_SPACING = 15

# =============================================================================
# INVENTORY SETTINGS
# =============================================================================

INVENTORY_SLOTS_PER_ROW = 5
INVENTORY_SLOT_SIZE = 44
INVENTORY_SLOT_SPACING = 4

# =============================================================================
# STAT BAR SETTINGS
# =============================================================================

STAT_BAR_WIDTH = 150
STAT_BAR_HEIGHT = 16
STAT_BAR_CORNER_RADIUS = 3

# =============================================================================
# API SETTINGS (for future real image provider)
# =============================================================================

API_BASE_URL = "http://localhost:8000/api/v1"
API_TIMEOUT = 30
IMAGE_CACHE_SIZE = 50

# =============================================================================
# DEBUG SETTINGS
# =============================================================================

DEBUG_MODE = False
SHOW_FPS = True
SHOW_GRID = False

