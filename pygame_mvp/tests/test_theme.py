#!/usr/bin/env python3
"""
Test 6: Theme System Module

Tests the theme management system for UI styling.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.theme import Theme, THEMES, get_theme, set_theme
from config import THEME_CLASSIC, THEME_DARK


def test_theme_initialization():
    """Test Theme initialization with dict."""
    print("Testing Theme initialization...")

    theme = Theme(THEME_CLASSIC)

    assert theme.name == "classic", "Should extract name from dict"
    assert theme._colors == THEME_CLASSIC, "Should store colors"

    print(f"   Theme name: {theme.name}")
    print(f"   Colors stored: {len(theme._colors)} colors")
    print("✅ Theme initialization works")
    return True


def test_theme_attribute_access():
    """Test accessing colors as attributes."""
    print("\nTesting theme attribute access...")

    theme = Theme(THEME_CLASSIC)

    # Test accessing colors as attributes
    bg_color = theme.background
    assert isinstance(bg_color, tuple), "Should return tuple"
    assert len(bg_color) == 3, "Should be RGB tuple"
    assert all(isinstance(c, int) for c in bg_color), "All values should be int"

    panel_color = theme.panel_bg
    assert isinstance(panel_color, tuple), "Panel color should be tuple"

    print(f"   Background color: {bg_color}")
    print(f"   Panel color: {panel_color}")
    print("✅ Attribute access works")
    return True


def test_theme_attribute_error():
    """Test accessing non-existent color raises AttributeError."""
    print("\nTesting non-existent color...")

    theme = Theme(THEME_CLASSIC)

    try:
        _ = theme.nonexistent_color
        print("❌ Should have raised AttributeError")
        return False
    except AttributeError as e:
        assert "nonexistent_color" in str(e), "Error should mention color name"
        print(f"   AttributeError raised correctly: ✓")
        print("✅ Non-existent color handling works")
        return True


def test_theme_get_with_default():
    """Test get() method with default fallback."""
    print("\nTesting get() with default...")

    theme = Theme(THEME_CLASSIC)

    # Test existing color
    bg = theme.get("background")
    assert bg == THEME_CLASSIC["background"], "Should return actual color"

    # Test non-existent color with default
    fake = theme.get("fake_color", (100, 100, 100))
    assert fake == (100, 100, 100), "Should return default"

    # Test non-existent without explicit default
    fake2 = theme.get("another_fake")
    assert fake2 == (128, 128, 128), "Should return default gray"

    print(f"   Existing color: {bg}")
    print(f"   Default fallback: {fake}")
    print("✅ get() with default works")
    return True


def test_theme_lighten():
    """Test lightening colors."""
    print("\nTesting color lightening...")

    theme = Theme(THEME_CLASSIC)

    original = theme.background
    lightened = theme.lighten("background", 20)

    assert isinstance(lightened, tuple), "Should return tuple"
    assert len(lightened) == 3, "Should be RGB"

    # Each component should be lighter (or maxed at 255)
    for i in range(3):
        assert lightened[i] >= original[i], f"Component {i} should be lighter or same"
        assert lightened[i] <= 255, f"Component {i} should not exceed 255"

    print(f"   Original: {original}")
    print(f"   Lightened: {lightened}")
    print("✅ Color lightening works")
    return True


def test_theme_darken():
    """Test darkening colors."""
    print("\nTesting color darkening...")

    theme = Theme(THEME_CLASSIC)

    original = theme.background
    darkened = theme.darken("background", 10)

    assert isinstance(darkened, tuple), "Should return tuple"
    assert len(darkened) == 3, "Should be RGB"

    # Each component should be darker (or bottomed at 0)
    for i in range(3):
        assert darkened[i] <= original[i], f"Component {i} should be darker or same"
        assert darkened[i] >= 0, f"Component {i} should not go below 0"

    print(f"   Original: {original}")
    print(f"   Darkened: {darkened}")
    print("✅ Color darkening works")
    return True


def test_theme_with_alpha():
    """Test adding alpha channel to colors."""
    print("\nTesting alpha channel...")

    theme = Theme(THEME_CLASSIC)

    color = theme.background
    with_alpha = theme.with_alpha("background", 128)

    assert isinstance(with_alpha, tuple), "Should return tuple"
    assert len(with_alpha) == 4, "Should be RGBA"
    assert with_alpha[:3] == color, "RGB should match original"
    assert with_alpha[3] == 128, "Alpha should be 128"

    print(f"   RGB: {color}")
    print(f"   RGBA: {with_alpha}")
    print("✅ Alpha channel works")
    return True


def test_prebuilt_themes():
    """Test pre-built themes are available."""
    print("\nTesting pre-built themes...")

    assert "classic" in THEMES, "Classic theme should exist"
    assert "dark" in THEMES, "Dark theme should exist"

    classic = THEMES["classic"]
    dark = THEMES["dark"]

    assert isinstance(classic, Theme), "Classic should be Theme instance"
    assert isinstance(dark, Theme), "Dark should be Theme instance"
    assert classic.name == "classic", "Classic should have correct name"
    assert dark.name == "dark", "Dark should have correct name"

    print(f"   Classic theme: ✓")
    print(f"   Dark theme: ✓")
    print("✅ Pre-built themes available")
    return True


def test_get_current_theme():
    """Test get_theme() function."""
    print("\nTesting get_theme()...")

    theme = get_theme()

    assert isinstance(theme, Theme), "Should return Theme instance"
    assert theme.name in ["classic", "dark"], "Should be a known theme"

    print(f"   Current theme: {theme.name}")
    print("✅ get_theme() works")
    return True


def test_set_theme():
    """Test set_theme() function."""
    print("\nTesting set_theme()...")

    # Get current theme
    original = get_theme()
    original_name = original.name

    # Switch to different theme
    new_name = "dark" if original_name == "classic" else "classic"
    set_theme(new_name)

    current = get_theme()
    assert current.name == new_name, "Theme should have changed"

    # Switch back
    set_theme(original_name)
    restored = get_theme()
    assert restored.name == original_name, "Theme should be restored"

    print(f"   Original: {original_name}")
    print(f"   Switched to: {new_name}")
    print(f"   Restored: {original_name}")
    print("✅ set_theme() works")
    return True


def test_theme_edge_cases():
    """Test edge cases for color manipulation."""
    print("\nTesting edge cases...")

    theme = Theme({"name": "test", "white": (255, 255, 255), "black": (0, 0, 0)})

    # Lighten white (should max at 255)
    lightened_white = theme.lighten("white", 50)
    assert lightened_white == (255, 255, 255), "White can't get lighter"

    # Darken black (should stay at 0)
    darkened_black = theme.darken("black", 50)
    assert darkened_black == (0, 0, 0), "Black can't get darker"

    print(f"   Lighten white: {lightened_white} ✓")
    print(f"   Darken black: {darkened_black} ✓")
    print("✅ Edge cases handled correctly")
    return True


def main():
    """Run all theme tests."""
    print("🧪 Test 6: Theme System Module")
    print("=" * 60)

    tests = [
        test_theme_initialization,
        test_theme_attribute_access,
        test_theme_attribute_error,
        test_theme_get_with_default,
        test_theme_lighten,
        test_theme_darken,
        test_theme_with_alpha,
        test_prebuilt_themes,
        test_get_current_theme,
        test_set_theme,
        test_theme_edge_cases,
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
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 60)
    print(f"Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All theme system tests passed!")
        return 0
    else:
        print("❌ Some theme system tests failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
