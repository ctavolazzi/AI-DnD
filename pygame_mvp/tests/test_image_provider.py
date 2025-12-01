#!/usr/bin/env python3
"""
Test 3: Image Provider Module

Tests the MockImageProvider (placeholder) and APIImageProvider (stub).
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock pygame if not available
try:
    import pygame
except ImportError:
    print("⚠️  Pygame not installed - creating mock")
    import sys
    from unittest.mock import MagicMock
    sys.modules['pygame'] = MagicMock()

from services.image_provider import MockImageProvider, APIImageProvider


def test_mock_provider_initialization():
    """Test MockImageProvider initialization."""
    print("Testing MockImageProvider initialization...")

    provider = MockImageProvider()

    assert hasattr(provider, '_cache'), "Provider should have cache"
    assert hasattr(provider, '_font_small'), "Provider should have small font"
    assert hasattr(provider, '_font_normal'), "Provider should have normal font"

    print(f"   Cache initialized: ✓")
    print(f"   Small font initialized: ✓")
    print(f"   Normal font initialized: ✓")
    print("✅ MockImageProvider initializes correctly")
    return True


def test_mock_provider_scene_image():
    """Test MockImageProvider scene image generation."""
    print("\nTesting MockImageProvider scene images...")

    provider = MockImageProvider()

    # Test scene image with correct API signature
    scene_img = provider.get_scene_image("Dark Forest", 400, 300)

    assert scene_img is not None, "Scene image should not be None"
    assert scene_img.get_width() == 400, "Scene image should have correct width"
    assert scene_img.get_height() == 300, "Scene image should have correct height"

    # Test caching - same parameters should return cached image
    scene_img_2 = provider.get_scene_image("Dark Forest", 400, 300)
    assert scene_img is scene_img_2, "Should return cached image for same parameters"

    # Test different parameters return different image
    scene_img_3 = provider.get_scene_image("Bright Meadow", 400, 300)
    assert scene_img is not scene_img_3, "Different scene name should return different image"

    print(f"   Scene image generation: ✓")
    print(f"   Image dimensions: ✓")
    print(f"   Image caching: ✓")
    print("✅ Scene image generation works")
    return True


def test_mock_provider_character_image():
    """Test MockImageProvider character image generation."""
    print("\nTesting MockImageProvider character images...")

    provider = MockImageProvider()

    # Test character portrait with correct API signature
    char_img = provider.get_character_portrait("Brave Warrior", "Fighter", 150, 200)

    assert char_img is not None, "Character image should not be None"
    assert char_img.get_width() == 150, "Character image should have correct width"
    assert char_img.get_height() == 200, "Character image should have correct height"

    # Test caching
    char_img_2 = provider.get_character_portrait("Brave Warrior", "Fighter", 150, 200)
    assert char_img is char_img_2, "Should return cached image for same parameters"

    print(f"   Character portrait generation: ✓")
    print(f"   Image dimensions: ✓")
    print(f"   Image caching: ✓")
    print("✅ Character portrait generation works")
    return True


def test_mock_provider_item_image():
    """Test MockImageProvider item image generation."""
    print("\nTesting MockImageProvider item images...")

    provider = MockImageProvider()

    # Test item image with correct API signature
    item_img = provider.get_item_image("Sword of Truth", 64, 64)

    assert item_img is not None, "Item image should not be None"
    assert item_img.get_width() == 64, "Item image should have correct width"
    assert item_img.get_height() == 64, "Item image should have correct height"

    # Test caching
    item_img_2 = provider.get_item_image("Sword of Truth", 64, 64)
    assert item_img is item_img_2, "Should return cached image for same parameters"

    print(f"   Item image generation: ✓")
    print(f"   Image dimensions: ✓")
    print(f"   Image caching: ✓")
    print("✅ Item image generation works")
    return True


def test_mock_provider_map_image():
    """Test MockImageProvider map image generation."""
    print("\nTesting MockImageProvider map images...")

    provider = MockImageProvider()

    # Test map image
    map_img = provider.get_map_image("Dragon's Lair", 300, 300)

    assert map_img is not None, "Map image should not be None"
    assert map_img.get_width() == 300, "Map image should have correct width"
    assert map_img.get_height() == 300, "Map image should have correct height"

    print(f"   Map image generation: ✓")
    print(f"   Image dimensions: ✓")
    print("✅ Map image generation works")
    return True


def test_mock_provider_cache_clearing():
    """Test cache clearing functionality."""
    print("\nTesting cache clearing...")

    provider = MockImageProvider()

    # Generate some images
    provider.get_scene_image("Scene 1", 400, 300)
    provider.get_character_portrait("Hero", "Fighter", 150, 200)
    provider.get_item_image("Sword", 64, 64)

    # Cache should have entries now
    assert len(provider._cache) == 3, "Should have 3 cached images"

    # Clear cache
    provider.clear_cache()

    assert len(provider._cache) == 0, "Cache should be empty after clearing"

    print(f"   Images cached: 3")
    print(f"   Cache cleared: ✓")
    print(f"   Final cache size: {len(provider._cache)}")
    print("✅ Cache clearing works")
    return True


def test_api_provider_initialization():
    """Test APIImageProvider initialization."""
    print("\nTesting APIImageProvider initialization...")

    provider = APIImageProvider(api_url="http://localhost:8000/api/v1")

    assert provider.api_url == "http://localhost:8000/api/v1"
    assert hasattr(provider, '_cache'), "Provider should have cache"
    assert hasattr(provider, '_fallback'), "Provider should have fallback"

    print(f"   API URL: {provider.api_url}")
    print(f"   Cache initialized: ✓")
    print(f"   Fallback provider: ✓")
    print("✅ APIImageProvider initializes correctly")
    return True


def test_api_provider_placeholder_fallback():
    """Test that APIImageProvider returns placeholders when API unavailable."""
    print("\nTesting APIImageProvider placeholder fallback...")

    provider = APIImageProvider(api_url="http://localhost:8000/api/v1")

    # Since we don't have a real API, this should fall back to placeholders
    scene_img = provider.get_scene_image("Test scene", 400, 300)

    assert scene_img is not None, "Should return placeholder image"
    assert scene_img.get_width() == 400, "Should have correct width"
    assert scene_img.get_height() == 300, "Should have correct height"

    print(f"   Scene image (placeholder): ✓")
    print(f"   Fallback working: ✓")
    print(f"   Dimensions correct: ✓")
    print("✅ APIImageProvider fallback works")
    return True


def main():
    """Run all image provider tests."""
    print("🧪 Test 3: Image Provider Module")
    print("=" * 60)

    tests = [
        test_mock_provider_initialization,
        test_mock_provider_scene_image,
        test_mock_provider_character_image,
        test_mock_provider_item_image,
        test_mock_provider_map_image,
        test_mock_provider_cache_clearing,
        test_api_provider_initialization,
        test_api_provider_placeholder_fallback,
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
        print("🎉 All image provider tests passed!")
        return 0
    else:
        print("❌ Some image provider tests failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
