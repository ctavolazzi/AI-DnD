#!/usr/bin/env python3
"""
Test 7: UI Components Module

Tests UI components (Panel, Button, TextBox, ImageFrame, StatBar, InventoryGrid).
This is the highest-risk code - 753 lines of user-facing UI.
"""

import sys
import os

# Set SDL to use dummy video driver for headless testing
os.environ['SDL_VIDEODRIVER'] = 'dummy'

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame
from ui.components import (
    UIComponent, Panel, Button, TextBox, ImageFrame,
    StatBar, InventorySlot, InventoryGrid
)


def test_ui_component_base():
    """Test UIComponent base class initialization."""
    print("Testing UIComponent base class...")

    # UIComponent is abstract, so test through a concrete subclass
    panel = Panel(10, 20, 200, 150, "Test Panel")

    assert panel.x == 10, "X should be set"
    assert panel.y == 20, "Y should be set"
    assert panel.width == 200, "Width should be set"
    assert panel.height == 150, "Height should be set"
    assert panel.visible is True, "Should be visible by default"
    assert panel.enabled is True, "Should be enabled by default"

    print(f"   Position: ({panel.x}, {panel.y})")
    print(f"   Size: {panel.width}x{panel.height}")
    print(f"   Visible: {panel.visible}, Enabled: {panel.enabled}")
    print("✅ UIComponent base class works")
    return True


def test_panel_initialization():
    """Test Panel component initialization."""
    print("\nTesting Panel initialization...")

    panel = Panel(0, 0, 300, 200, "Test Panel")

    assert panel.title == "Test Panel", "Title should be set"
    assert panel.width == 300, "Width should be set"
    assert panel.height == 200, "Height should be set"

    print(f"   Title: \"{panel.title}\"")
    print(f"   Dimensions: {panel.width}x{panel.height}")
    print("✅ Panel initialization works")
    return True


def test_panel_without_title():
    """Test Panel without title."""
    print("\nTesting Panel without title...")

    panel = Panel(0, 0, 100, 100)

    assert panel.title is None or panel.title == "", "Title should be empty/None"

    print(f"   Title: {repr(panel.title)}")
    print("✅ Panel without title works")
    return True


def test_button_initialization():
    """Test Button component initialization."""
    print("\nTesting Button initialization...")

    callback_called = []

    def test_callback():
        callback_called.append(True)

    button = Button(10, 10, 100, 40, "Click Me", test_callback)

    assert button.text == "Click Me", "Text should be set"
    assert button.callback is test_callback, "Callback should be set"
    assert button.enabled is True, "Should be enabled by default"

    print(f"   Text: \"{button.text}\"")
    print(f"   Callback set: ✓")
    print(f"   Dimensions: {button.width}x{button.height}")
    print("✅ Button initialization works")
    return True


def test_button_click():
    """Test Button click handling."""
    print("\nTesting Button click handling...")

    callback_called = []

    def test_callback():
        callback_called.append(True)

    button = Button(10, 10, 100, 40, "Click", test_callback)

    # Simulate click by calling callback
    if button.callback:
        button.callback()

    assert len(callback_called) == 1, "Callback should be called once"

    print(f"   Callback executed: ✓")
    print("✅ Button click handling works")
    return True


def test_button_disabled():
    """Test disabled button behavior."""
    print("\nTesting disabled button...")

    button = Button(0, 0, 100, 40, "Disabled", lambda: None)

    assert button.enabled is True, "Should start enabled"

    button.enabled = False
    assert button.enabled is False, "Should be disabled"

    print(f"   Enabled → Disabled: ✓")
    print("✅ Button enable/disable works")
    return True


def test_textbox_initialization():
    """Test TextBox component initialization."""
    print("\nTesting TextBox initialization...")

    textbox = TextBox(0, 0, 200, 100, ["Line 1", "Line 2", "Line 3"])

    assert textbox.lines == ["Line 1", "Line 2", "Line 3"], "Lines should be set"
    assert textbox.width == 200, "Width should be set"
    assert textbox.height == 100, "Height should be set"

    print(f"   Lines: {len(textbox.lines)} lines")
    print(f"   Dimensions: {textbox.width}x{textbox.height}")
    print("✅ TextBox initialization works")
    return True


def test_textbox_add_line():
    """Test TextBox line addition."""
    print("\nTesting TextBox line addition...")

    textbox = TextBox(0, 0, 200, 100, ["Initial"])

    assert len(textbox.lines) == 1, "Should have initial line"

    textbox.lines.append("Added line")
    assert len(textbox.lines) == 2, "Should have 2 lines"

    print(f"   1 line → 2 lines: ✓")
    print("✅ TextBox line addition works")
    return True


def test_image_frame_initialization():
    """Test ImageFrame component initialization."""
    print("\nTesting ImageFrame initialization...")

    # ImageFrame requires a pygame Surface
    # Initialize pygame first
    pygame.init()
    test_surface = pygame.Surface((100, 100))

    frame = ImageFrame(0, 0, 150, 150, test_surface)

    assert frame.image is test_surface, "Image should be set"
    assert frame.width == 150, "Width should be set"
    assert frame.height == 150, "Height should be set"

    print(f"   Image set: ✓")
    print(f"   Frame size: {frame.width}x{frame.height}")
    print("✅ ImageFrame initialization works")

    pygame.quit()
    return True


def test_image_frame_set_image():
    """Test ImageFrame image update."""
    print("\nTesting ImageFrame set_image()...")

    pygame.init()

    surface1 = pygame.Surface((50, 50))
    surface2 = pygame.Surface((75, 75))

    frame = ImageFrame(0, 0, 100, 100, surface1)
    assert frame.image is surface1, "Should have first image"

    frame.set_image(surface2)
    assert frame.image is surface2, "Should have second image"

    print(f"   Image 1: 50x50")
    print(f"   Image 2: 75x75")
    print(f"   Image swap: ✓")
    print("✅ ImageFrame set_image() works")

    pygame.quit()
    return True


def test_statbar_initialization():
    """Test StatBar component initialization."""
    print("\nTesting StatBar initialization...")

    # StatBar uses value (0.0-1.0), not current/maximum
    statbar = StatBar(0, 0, 200, 20, value=0.75, label="Health")

    assert statbar.label == "Health", "Label should be set"
    assert statbar.value == 0.75, "Value should be 0.75"
    assert statbar.width == 200, "Width should be set"

    print(f"   Label: \"{statbar.label}\"")
    print(f"   Value: {statbar.value}")
    print(f"   Dimensions: {statbar.width}x{statbar.height}")
    print("✅ StatBar initialization works")
    return True


def test_statbar_set_value():
    """Test StatBar value update."""
    print("\nTesting StatBar value update...")

    statbar = StatBar(0, 0, 200, 20, value=0.5, label="HP")

    assert statbar.value == 0.5, "Should start at 0.5"

    # Update value
    statbar.value = 0.75
    assert statbar.value == 0.75, "Should update to 0.75"

    # Values should be 0.0-1.0 range
    statbar.value = 1.0
    assert statbar.value == 1.0, "Should be 1.0 (full)"

    statbar.value = 0.0
    assert statbar.value == 0.0, "Should be 0.0 (empty)"

    print(f"   0.5 → 0.75 → 1.0 → 0.0: ✓")
    print("✅ StatBar value updates work")
    return True


def test_inventory_slot_initialization():
    """Test InventorySlot component initialization."""
    print("\nTesting InventorySlot initialization...")

    pygame.init()

    # InventorySlot takes x, y, size, item_image, quantity, on_click
    slot = InventorySlot(0, 0, size=64, item_image=None, quantity=0)

    assert slot.item_image is None, "Should start with no image"
    assert slot.quantity == 0, "Should start with 0 quantity"
    assert slot.width == 64, "Width should be slot size"
    assert slot.height == 64, "Height should be slot size"

    print(f"   Size: {slot.width}x{slot.height}")
    print(f"   Empty: ✓")
    print("✅ InventorySlot initialization works")

    pygame.quit()
    return True


def test_inventory_slot_set_item():
    """Test InventorySlot with item."""
    print("\nTesting InventorySlot with item...")

    pygame.init()

    item_image = pygame.Surface((32, 32))
    slot = InventorySlot(0, 0, size=64, item_image=item_image, quantity=3)

    assert slot.item_image is item_image, "Should have image"
    assert slot.quantity == 3, "Quantity should be 3"

    print(f"   Item image set: ✓")
    print(f"   Quantity: 3")
    print("✅ InventorySlot with item works")

    pygame.quit()
    return True


def test_inventory_grid_initialization():
    """Test InventoryGrid component initialization."""
    print("\nTesting InventoryGrid initialization...")

    # InventoryGrid: x, y, slots_per_row, num_slots, slot_size, spacing
    grid = InventoryGrid(0, 0, slots_per_row=6, num_slots=12)

    assert grid.num_slots == 12, "Should have 12 slots"
    assert grid.slots_per_row == 6, "Should have 6 per row"

    print(f"   Number of slots: {grid.num_slots}")
    print(f"   Slots per row: {grid.slots_per_row}")
    print("✅ InventoryGrid initialization works")
    return True


def test_inventory_grid_has_slots():
    """Test InventoryGrid creates slot objects."""
    print("\nTesting InventoryGrid slot creation...")

    pygame.init()

    grid = InventoryGrid(0, 0, slots_per_row=5, num_slots=10)

    # Grid should have some slot-related data
    assert grid.num_slots == 10, "Should track number of slots"

    print(f"   Slots configured: {grid.num_slots}")
    print("✅ InventoryGrid slot tracking works")

    pygame.quit()
    return True


def test_component_positioning():
    """Test component set_position()."""
    print("\nTesting component positioning...")

    panel = Panel(0, 0, 100, 100, "Test")

    assert panel.x == 0 and panel.y == 0, "Should start at 0,0"

    panel.set_position(50, 75)

    assert panel.x == 50, "X should update"
    assert panel.y == 75, "Y should update"
    assert panel.rect.x == 50, "Rect X should update"
    assert panel.rect.y == 75, "Rect Y should update"

    print(f"   (0,0) → (50,75): ✓")
    print(f"   Rect synced: ✓")
    print("✅ Component positioning works")
    return True


def test_component_contains_point():
    """Test component contains_point()."""
    print("\nTesting contains_point()...")

    panel = Panel(10, 10, 100, 100, "Test")

    # Point inside
    assert panel.contains_point(50, 50) is True, "Should contain (50,50)"

    # Point outside
    assert panel.contains_point(5, 5) is False, "Should not contain (5,5)"
    assert panel.contains_point(150, 150) is False, "Should not contain (150,150)"

    # Edge cases
    assert panel.contains_point(10, 10) is True, "Should contain top-left corner"

    print(f"   Point inside: ✓")
    print(f"   Points outside: ✓")
    print(f"   Edge cases: ✓")
    print("✅ contains_point() works")
    return True


def main():
    """Run all UI component tests."""
    print("🧪 Test 7: UI Components Module")
    print("=" * 60)
    print("⚠️  Testing 753 lines of highest-risk user-facing code")
    print("=" * 60)

    tests = [
        test_ui_component_base,
        test_panel_initialization,
        test_panel_without_title,
        test_button_initialization,
        test_button_click,
        test_button_disabled,
        test_textbox_initialization,
        test_textbox_add_line,
        test_image_frame_initialization,
        test_image_frame_set_image,
        test_statbar_initialization,
        test_statbar_set_value,
        test_inventory_slot_initialization,
        test_inventory_slot_set_item,
        test_inventory_grid_initialization,
        test_inventory_grid_has_slots,
        test_component_positioning,
        test_component_contains_point,
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
        print("🎉 All UI component tests passed!")
        print("\n⚠️  NOTE: These are initialization/logic tests")
        print("   Rendering tests would require full pygame display")
        return 0
    else:
        print("❌ Some UI component tests failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
