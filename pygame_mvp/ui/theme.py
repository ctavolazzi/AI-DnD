"""
Theme System

Manages color themes and visual styling.
"""

from typing import Dict, Tuple, Optional

# Use absolute imports for standalone execution
try:
    from pygame_mvp.config import THEME_CLASSIC, THEME_DARK
except ImportError:
    from config import THEME_CLASSIC, THEME_DARK


class Theme:
    """
    Theme manager for consistent styling.

    Provides easy access to theme colors and can switch between themes.
    """

    def __init__(self, theme_dict: Dict[str, Tuple[int, int, int]]):
        self._colors = theme_dict
        self.name = theme_dict.get("name", "custom")

    def __getattr__(self, name: str) -> Tuple[int, int, int]:
        """Access colors as attributes."""
        if name.startswith("_"):
            return super().__getattribute__(name)
        if name in self._colors:
            return self._colors[name]
        raise AttributeError(f"Theme has no color '{name}'")

    def get(self, name: str, default: Tuple[int, int, int] = (128, 128, 128)) -> Tuple[int, int, int]:
        """Get a color with a default fallback."""
        return self._colors.get(name, default)

    def lighten(self, color_name: str, amount: int = 20) -> Tuple[int, int, int]:
        """Get a lightened version of a color."""
        color = self.get(color_name)
        return tuple(min(c + amount, 255) for c in color)

    def darken(self, color_name: str, amount: int = 20) -> Tuple[int, int, int]:
        """Get a darkened version of a color."""
        color = self.get(color_name)
        return tuple(max(c - amount, 0) for c in color)

    def with_alpha(self, color_name: str, alpha: int) -> Tuple[int, int, int, int]:
        """Get a color with alpha channel."""
        color = self.get(color_name)
        return (*color, alpha)


# Pre-built themes
THEMES = {
    "classic": Theme(THEME_CLASSIC),
    "dark": Theme(THEME_DARK)
}

# Current active theme
_current_theme: Theme = THEMES["classic"]


def get_theme() -> Theme:
    """Get the current active theme."""
    return _current_theme


def set_theme(name: str) -> Theme:
    """Set and return a theme by name."""
    global _current_theme
    if name in THEMES:
        _current_theme = THEMES[name]
    return _current_theme

