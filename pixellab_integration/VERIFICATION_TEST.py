#!/usr/bin/env python3
"""
COMPREHENSIVE VERIFICATION TEST
Tests all code without requiring a valid API key
"""

import sys
import traceback
from pathlib import Path

# Test results tracking
tests_passed = 0
tests_failed = 0
issues_found = []

def test(name, func):
    """Run a test and track results"""
    global tests_passed, tests_failed, issues_found
    try:
        func()
        print(f"✓ {name}")
        tests_passed += 1
        return True
    except Exception as e:
        print(f"✗ {name}")
        print(f"  Error: {e}")
        tests_failed += 1
        issues_found.append(f"{name}: {e}")
        return False

print("=" * 70)
print("PIXELLAB INTEGRATION - COMPREHENSIVE VERIFICATION")
print("=" * 70)
print()

# Test 1: Import main client
def test_import_client():
    import pixellab_client
    assert hasattr(pixellab_client, 'PixelLabClient')

test("Import pixellab_client module", test_import_client)

# Test 2: Import PixelLab SDK
def test_import_sdk():
    import pixellab
    assert hasattr(pixellab, 'Client')

test("Import pixellab SDK", test_import_sdk)

# Test 3: Import all SDK components we use
def test_import_sdk_components():
    from pixellab.models import ImageSize
    from pixellab.types import Outline, Shading, Detail, CameraView, Direction
    from pixellab.animate_with_skeleton import SkeletonFrame

test("Import all SDK components", test_import_sdk_components)

# Test 4: Instantiate client (no API calls)
def test_instantiate_client():
    from pixellab_client import PixelLabClient
    client = PixelLabClient(api_key="test-key", auto_save=False)
    assert client is not None
    assert client.client is not None

test("Instantiate PixelLabClient", test_instantiate_client)

# Test 5: Check all client methods exist
def test_client_methods():
    from pixellab_client import PixelLabClient
    client = PixelLabClient(api_key="test", auto_save=False)

    methods = [
        'get_balance',
        'generate_character',
        'generate_with_style',
        'animate_character_text',
        'animate_character_skeleton',
        'rotate_character',
        'inpaint_image',
        'estimate_skeleton',
        'create_sprite_sheet',
        'batch_generate_directions',
        '_save_image'
    ]

    for method in methods:
        assert hasattr(client, method), f"Missing method: {method}"
        assert callable(getattr(client, method)), f"Not callable: {method}"

test("All client methods exist", test_client_methods)

# Test 6: Check helper functions
def test_helper_functions():
    import pixellab_client
    assert hasattr(pixellab_client, 'create_walking_animation')
    assert hasattr(pixellab_client, 'create_8_directional_character')

test("Helper functions exist", test_helper_functions)

# Test 7: Verify SDK method signatures match our usage
def test_sdk_signatures():
    import pixellab
    import inspect

    sdk_client = pixellab.Client(secret="test")

    # Check each method we wrap
    assert hasattr(sdk_client, 'generate_image_pixflux')
    assert hasattr(sdk_client, 'generate_image_bitforge')
    assert hasattr(sdk_client, 'animate_with_text')
    assert hasattr(sdk_client, 'animate_with_skeleton')
    assert hasattr(sdk_client, 'rotate')
    assert hasattr(sdk_client, 'inpaint')
    assert hasattr(sdk_client, 'estimate_skeleton')
    assert hasattr(sdk_client, 'get_balance')

    # Verify key parameters exist
    sig = inspect.signature(sdk_client.generate_image_pixflux)
    params = list(sig.parameters.keys())
    assert 'description' in params
    assert 'image_size' in params

test("SDK method signatures match", test_sdk_signatures)

# Test 8: Example scripts syntax
def test_example_syntax():
    import py_compile
    examples_dir = Path('examples')

    if not examples_dir.exists():
        raise FileNotFoundError("examples/ directory not found")

    for example in examples_dir.glob('*.py'):
        py_compile.compile(str(example), doraise=True)

test("All example scripts compile", test_example_syntax)

# Test 9: Package structure
def test_package_structure():
    files = [
        '__init__.py',
        'pixellab_client.py',
        'requirements.txt',
        'README.md',
        'QUICKSTART.md',
        'examples/01_basic_character_generation.py',
        'examples/02_character_animation.py',
        'examples/03_multi_directional.py',
        'examples/04_rotation_and_views.py',
        'examples/05_advanced_features.py',
        'examples/06_game_ready_assets.py'
    ]

    for file in files:
        path = Path(file)
        assert path.exists(), f"Missing file: {file}"

test("Package structure complete", test_package_structure)

# Test 10: Can create sprite sheet from dummy images
def test_sprite_sheet_creation():
    from pixellab_client import PixelLabClient
    from PIL import Image

    client = PixelLabClient(api_key="test", auto_save=False)

    # Create dummy images
    frames = [Image.new('RGBA', (64, 64), (255, 0, 0, 255)) for _ in range(4)]

    # Create sprite sheet
    sheet = client.create_sprite_sheet(frames, columns=2, filename="test.png")
    assert sheet.size == (128, 128)  # 2 columns x 2 rows of 64x64

test("Sprite sheet creation works", test_sprite_sheet_creation)

print()
print("=" * 70)
print("VERIFICATION SUMMARY")
print("=" * 70)
print(f"Tests Passed: {tests_passed}")
print(f"Tests Failed: {tests_failed}")
print(f"Success Rate: {tests_passed/(tests_passed+tests_failed)*100:.1f}%")
print()

if issues_found:
    print("ISSUES FOUND:")
    for issue in issues_found:
        print(f"  - {issue}")
    print()

if tests_failed == 0:
    print("✓ ALL TESTS PASSED!")
    print()
    print("WHAT THIS MEANS:")
    print("- All code compiles without syntax errors")
    print("- All imports work correctly")
    print("- Client instantiates properly")
    print("- All methods exist and are callable")
    print("- SDK method signatures match our usage")
    print("- Package structure is complete")
    print()
    print("WHAT STILL NEEDS TESTING:")
    print("- Actual API calls (requires valid API key)")
    print("- Image generation (requires valid API key)")
    print("- Animation creation (requires valid API key)")
    print("- Error handling with real API responses")
    print()
    print("TO TEST WITH REAL API:")
    print("1. Get API key from https://www.pixellab.ai")
    print("2. Update API_KEY in example scripts")
    print("3. Run: python examples/01_basic_character_generation.py")
    sys.exit(0)
else:
    print("⚠ SOME TESTS FAILED")
    print("Please review the issues above.")
    sys.exit(1)
