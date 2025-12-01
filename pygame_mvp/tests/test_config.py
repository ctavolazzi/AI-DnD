#!/usr/bin/env python3
"""
Test 1: Configuration Module

Tests that all configuration constants are properly defined and valid.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, GAME_TITLE,
    THEME_CLASSIC, THEME_DARK, CURRENT_THEME,
    MARGIN, PADDING, PANEL_BORDER_WIDTH,
    LEFT_SIDEBAR_WIDTH, RIGHT_SIDEBAR_WIDTH, CENTER_WIDTH
)


def test_screen_settings():
    """Test screen configuration values."""
    print("Testing screen settings...")

    assert SCREEN_WIDTH > 0, "Screen width must be positive"
    assert SCREEN_HEIGHT > 0, "Screen height must be positive"
    assert SCREEN_WIDTH >= 800, "Screen width should be at least 800"
    assert SCREEN_HEIGHT >= 600, "Screen height should be at least 600"
    assert FPS > 0, "FPS must be positive"
    assert FPS <= 144, "FPS should be reasonable (<=144)"
    assert isinstance(GAME_TITLE, str), "Game title must be a string"
    assert len(GAME_TITLE) > 0, "Game title must not be empty"

    print(f"   Screen: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")
    print(f"   FPS: {FPS}")
    print(f"   Title: {GAME_TITLE}")
    print("✅ Screen settings valid")
    return True


def test_theme_structure():
    """Test that themes have all required color keys."""
    print("\nTesting theme structure...")

    required_keys = [
        "name", "background", "panel_bg", "panel_border", "panel_header",
        "text_primary", "text_secondary", "text_highlight",
        "button_bg", "button_hover", "button_pressed", "button_border",
        "hp_bar", "hp_bar_bg", "mana_bar", "mana_bar_bg",
        "success", "warning", "error",
        "placeholder_scene", "placeholder_character", "placeholder_item"
    ]

    # Test classic theme
    for key in required_keys:
        assert key in THEME_CLASSIC, f"THEME_CLASSIC missing key: {key}"

    # Test dark theme
    for key in required_keys:
        assert key in THEME_DARK, f"THEME_DARK missing key: {key}"

    # Test current theme
    for key in required_keys:
        assert key in CURRENT_THEME, f"CURRENT_THEME missing key: {key}"

    print(f"   Classic theme: {len(THEME_CLASSIC)} keys")
    print(f"   Dark theme: {len(THEME_DARK)} keys")
    print(f"   Current theme: {CURRENT_THEME['name']}")
    print("✅ Theme structure valid")
    return True


def test_color_values():
    """Test that all colors are valid RGB tuples."""
    print("\nTesting color values...")

    def is_valid_color(color):
        """Check if color is valid RGB tuple."""
        if not isinstance(color, tuple):
            return False
        if len(color) != 3:
            return False
        return all(isinstance(c, int) and 0 <= c <= 255 for c in color)

    # Test all colors in current theme
    color_count = 0
    for key, value in CURRENT_THEME.items():
        if key != "name":  # Skip name string
            assert is_valid_color(value), f"Invalid color for {key}: {value}"
            color_count += 1

    print(f"   Validated {color_count} colors")
    print("✅ All colors are valid RGB tuples")
    return True


def test_layout_constants():
    """Test layout constants are sensible."""
    print("\nTesting layout constants...")

    assert MARGIN >= 0, "Margin must be non-negative"
    assert PADDING >= 0, "Padding must be non-negative"
    assert PANEL_BORDER_WIDTH >= 0, "Border width must be non-negative"

    # Test sidebar widths
    assert LEFT_SIDEBAR_WIDTH > 0, "Left sidebar width must be positive"
    assert RIGHT_SIDEBAR_WIDTH > 0, "Right sidebar width must be positive"
    assert CENTER_WIDTH > 0, "Center width must be positive"

    # Test that layout fits on screen
    total_width = LEFT_SIDEBAR_WIDTH + RIGHT_SIDEBAR_WIDTH + CENTER_WIDTH + (MARGIN * 4)
    assert total_width <= SCREEN_WIDTH, f"Layout too wide: {total_width} > {SCREEN_WIDTH}"

    print(f"   Left sidebar: {LEFT_SIDEBAR_WIDTH}px")
    print(f"   Center area: {CENTER_WIDTH}px")
    print(f"   Right sidebar: {RIGHT_SIDEBAR_WIDTH}px")
    print(f"   Total layout width: {total_width}px / {SCREEN_WIDTH}px")
    print("✅ Layout constants valid")
    return True


def test_layout_proportions():
    """Test that layout proportions are reasonable."""
    print("\nTesting layout proportions...")

    # Sidebars shouldn't take up more than 70% of screen
    sidebar_total = LEFT_SIDEBAR_WIDTH + RIGHT_SIDEBAR_WIDTH
    sidebar_percent = (sidebar_total / SCREEN_WIDTH) * 100

    assert sidebar_percent < 70, f"Sidebars too wide: {sidebar_percent:.1f}%"

    # Center should be at least 30% of screen
    center_percent = (CENTER_WIDTH / SCREEN_WIDTH) * 100
    assert center_percent >= 30, f"Center too narrow: {center_percent:.1f}%"

    print(f"   Sidebars: {sidebar_percent:.1f}% of screen")
    print(f"   Center: {center_percent:.1f}% of screen")
    print("✅ Layout proportions reasonable")
    return True


def main():
    """Run all config tests."""
    print("🧪 Test 1: Configuration Module")
    print("=" * 60)

    tests = [
        test_screen_settings,
        test_theme_structure,
        test_color_values,
        test_layout_constants,
        test_layout_proportions,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            if test():
                passed += 1
        except AssertionError as e:
            print(f"❌ Test failed: {e}")
        except Exception as e:
            print(f"❌ Test error: {e}")

    print("\n" + "=" * 60)
    print(f"Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All configuration tests passed!")
        return 0
    else:
        print("❌ Some configuration tests failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
