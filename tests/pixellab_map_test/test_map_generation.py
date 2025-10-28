#!/usr/bin/env python3
"""
PixelLab Map Generation Test Suite
Comprehensive testing of map and tileset generation for game development
"""

import logging
import sys
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import traceback

import pixellab
from PIL import Image, ImageDraw


# Configuration
API_KEY = "your-api-key-here"  # Replace with your actual key
TEST_DIR = Path(__file__).parent
OUTPUTS_DIR = TEST_DIR / "map_outputs"
LOGS_DIR = TEST_DIR / "map_logs"

# Create directories
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class MapTestResult:
    """Data structure to track map generation test results."""
    test_name: str
    timestamp: str
    success: bool
    duration_seconds: float
    tiles_generated: int
    map_size: Optional[Tuple[int, int]] = None
    tile_size: Optional[Tuple[int, int]] = None
    error_message: Optional[str] = None
    error_type: Optional[str] = None
    error_traceback: Optional[str] = None
    output_path: Optional[str] = None


class MapGenerationTester:
    """Comprehensive map and tileset generation testing framework."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = None
        self.test_results = []
        self.setup_logging()

    def setup_logging(self):
        """Configure comprehensive logging to file and console."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = LOGS_DIR / f"map_test_{timestamp}.log"

        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(console_formatter)

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

        self.logger.info(f"Map generation testing initialized. Log file: {log_file}")

    def initialize_client(self) -> bool:
        """Initialize PixelLab API client."""
        self.logger.info("Initializing PixelLab API client...")

        try:
            self.client = pixellab.Client(secret=self.api_key)
            self.logger.info("✓ Client initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"✗ Client initialization failed: {e}")
            self.logger.debug(f"Traceback: {traceback.format_exc()}")
            return False

    def generate_tile(self, description: str, size: int = 32, **kwargs) -> Image.Image:
        """Generate a single tile."""
        response = self.client.generate_image_pixflux(
            description=description,
            image_size={"width": size, "height": size},
            no_background=True,
            **kwargs
        )
        return response.image.pil_image()

    def test_basic_terrain_tiles(self) -> MapTestResult:
        """Test basic terrain tile generation."""
        test_name = "basic_terrain_tiles"
        self.logger.info(f"\n{'='*60}")
        self.logger.info(f"TEST: {test_name}")
        self.logger.info(f"{'='*60}")

        start_time = datetime.now()
        tiles_generated = 0

        try:
            terrain_types = [
                "grass tile pixel art top-down",
                "dirt tile pixel art top-down",
                "stone tile pixel art top-down",
                "water tile pixel art top-down",
                "sand tile pixel art top-down"
            ]

            tiles = []
            for terrain in terrain_types:
                self.logger.info(f"Generating: {terrain}")
                tile = self.generate_tile(terrain, size=32)
                tiles.append(tile)
                tiles_generated += 1
                self.logger.info(f"✓ Generated {terrain}")

            # Create tileset
            tileset_width = 5 * 32  # 5 tiles wide
            tileset_height = 32
            tileset = Image.new('RGBA', (tileset_width, tileset_height), (0, 0, 0, 0))

            for i, tile in enumerate(tiles):
                tileset.paste(tile, (i * 32, 0))

            output_path = OUTPUTS_DIR / f"{test_name}_tileset.png"
            tileset.save(output_path, "PNG")
            self.logger.info(f"✓ Tileset saved to: {output_path}")

            duration = (datetime.now() - start_time).total_seconds()

            result = MapTestResult(
                test_name=test_name,
                timestamp=start_time.isoformat(),
                success=True,
                duration_seconds=duration,
                tiles_generated=tiles_generated,
                tile_size=(32, 32),
                output_path=str(output_path)
            )

            self.logger.info(f"✓ TEST PASSED - Duration: {duration:.2f}s, Tiles: {tiles_generated}")
            return result

        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            error_trace = traceback.format_exc()

            self.logger.error(f"✗ TEST FAILED: {e}")
            self.logger.debug(f"Traceback:\n{error_trace}")

            result = MapTestResult(
                test_name=test_name,
                timestamp=start_time.isoformat(),
                success=False,
                duration_seconds=duration,
                tiles_generated=tiles_generated,
                error_message=str(e),
                error_type=type(e).__name__,
                error_traceback=error_trace
            )

            return result

    def test_isometric_tiles(self) -> MapTestResult:
        """Test isometric tile generation."""
        test_name = "isometric_tiles"
        self.logger.info(f"\n{'='*60}")
        self.logger.info(f"TEST: {test_name}")
        self.logger.info(f"{'='*60}")

        start_time = datetime.now()
        tiles_generated = 0

        try:
            tile_types = [
                "grass isometric tile",
                "stone building isometric tile",
                "tree isometric tile",
                "water isometric tile"
            ]

            tiles = []
            for tile_desc in tile_types:
                self.logger.info(f"Generating: {tile_desc}")
                tile = self.generate_tile(
                    tile_desc,
                    size=64,
                    isometric=True
                )
                tiles.append(tile)
                tiles_generated += 1
                self.logger.info(f"✓ Generated {tile_desc}")

            # Create tileset
            tileset = Image.new('RGBA', (64 * 4, 64), (0, 0, 0, 0))
            for i, tile in enumerate(tiles):
                tileset.paste(tile, (i * 64, 0))

            output_path = OUTPUTS_DIR / f"{test_name}_tileset.png"
            tileset.save(output_path, "PNG")

            duration = (datetime.now() - start_time).total_seconds()

            result = MapTestResult(
                test_name=test_name,
                timestamp=start_time.isoformat(),
                success=True,
                duration_seconds=duration,
                tiles_generated=tiles_generated,
                tile_size=(64, 64),
                output_path=str(output_path)
            )

            self.logger.info(f"✓ TEST PASSED - Duration: {duration:.2f}s, Tiles: {tiles_generated}")
            return result

        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            error_trace = traceback.format_exc()

            self.logger.error(f"✗ TEST FAILED: {e}")
            self.logger.debug(f"Traceback:\n{error_trace}")

            result = MapTestResult(
                test_name=test_name,
                timestamp=start_time.isoformat(),
                success=False,
                duration_seconds=duration,
                tiles_generated=tiles_generated,
                error_message=str(e),
                error_type=type(e).__name__,
                error_traceback=error_trace
            )

            return result

    def test_platformer_tiles(self) -> MapTestResult:
        """Test 2D platformer tile generation."""
        test_name = "platformer_tiles"
        self.logger.info(f"\n{'='*60}")
        self.logger.info(f"TEST: {test_name}")
        self.logger.info(f"{'='*60}")

        start_time = datetime.now()
        tiles_generated = 0

        try:
            platform_tiles = [
                "stone brick platform tile side view",
                "grass platform tile side view",
                "metal platform tile side view",
                "wooden platform tile side view",
                "ice platform tile side view"
            ]

            tiles = []
            for tile_desc in platform_tiles:
                self.logger.info(f"Generating: {tile_desc}")
                tile = self.generate_tile(
                    tile_desc,
                    size=32,
                    view='side'
                )
                tiles.append(tile)
                tiles_generated += 1
                self.logger.info(f"✓ Generated {tile_desc}")

            # Create horizontal tileset
            tileset = Image.new('RGBA', (32 * len(tiles), 32), (0, 0, 0, 0))
            for i, tile in enumerate(tiles):
                tileset.paste(tile, (i * 32, 0))

            output_path = OUTPUTS_DIR / f"{test_name}_tileset.png"
            tileset.save(output_path, "PNG")

            duration = (datetime.now() - start_time).total_seconds()

            result = MapTestResult(
                test_name=test_name,
                timestamp=start_time.isoformat(),
                success=True,
                duration_seconds=duration,
                tiles_generated=tiles_generated,
                tile_size=(32, 32),
                output_path=str(output_path)
            )

            self.logger.info(f"✓ TEST PASSED - Duration: {duration:.2f}s, Tiles: {tiles_generated}")
            return result

        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            error_trace = traceback.format_exc()

            self.logger.error(f"✗ TEST FAILED: {e}")
            self.logger.debug(f"Traceback:\n{error_trace}")

            result = MapTestResult(
                test_name=test_name,
                timestamp=start_time.isoformat(),
                success=False,
                duration_seconds=duration,
                tiles_generated=tiles_generated,
                error_message=str(e),
                error_type=type(e).__name__,
                error_traceback=error_trace
            )

            return result

    def test_complete_map_generation(self) -> MapTestResult:
        """Test generating a complete small map."""
        test_name = "complete_map_generation"
        self.logger.info(f"\n{'='*60}")
        self.logger.info(f"TEST: {test_name}")
        self.logger.info(f"{'='*60}")

        start_time = datetime.now()
        tiles_generated = 0

        try:
            # Generate different terrain types
            self.logger.info("Generating terrain tiles...")

            terrains = {
                'grass': self.generate_tile("grass terrain pixel art top-down", size=32),
                'water': self.generate_tile("water terrain pixel art top-down", size=32),
                'path': self.generate_tile("stone path pixel art top-down", size=32),
                'tree': self.generate_tile("tree pixel art top-down", size=32, no_background=True)
            }
            tiles_generated = len(terrains)

            self.logger.info(f"✓ Generated {tiles_generated} terrain types")

            # Create a simple 8x8 map
            map_width, map_height = 8, 8
            tile_size = 32

            map_image = Image.new(
                'RGBA',
                (map_width * tile_size, map_height * tile_size),
                (0, 0, 0, 0)
            )

            # Simple map layout (grass with water and path)
            map_layout = [
                ['grass', 'grass', 'grass', 'path', 'grass', 'grass', 'grass', 'grass'],
                ['grass', 'tree', 'grass', 'path', 'grass', 'tree', 'grass', 'grass'],
                ['grass', 'grass', 'grass', 'path', 'grass', 'grass', 'grass', 'water'],
                ['path', 'path', 'path', 'path', 'path', 'path', 'path', 'water'],
                ['grass', 'grass', 'grass', 'grass', 'grass', 'grass', 'grass', 'water'],
                ['grass', 'tree', 'grass', 'grass', 'tree', 'grass', 'grass', 'water'],
                ['grass', 'grass', 'grass', 'grass', 'grass', 'grass', 'grass', 'water'],
                ['grass', 'grass', 'grass', 'grass', 'grass', 'grass', 'water', 'water']
            ]

            self.logger.info("Composing map...")
            for y, row in enumerate(map_layout):
                for x, terrain_type in enumerate(row):
                    tile = terrains[terrain_type]
                    map_image.paste(tile, (x * tile_size, y * tile_size))

            output_path = OUTPUTS_DIR / f"{test_name}_8x8.png"
            map_image.save(output_path, "PNG")
            self.logger.info(f"✓ Map saved to: {output_path}")

            duration = (datetime.now() - start_time).total_seconds()

            result = MapTestResult(
                test_name=test_name,
                timestamp=start_time.isoformat(),
                success=True,
                duration_seconds=duration,
                tiles_generated=tiles_generated,
                map_size=(map_width, map_height),
                tile_size=(tile_size, tile_size),
                output_path=str(output_path)
            )

            self.logger.info(f"✓ TEST PASSED - Duration: {duration:.2f}s")
            self.logger.info(f"  Map size: {map_width}x{map_height} tiles")
            return result

        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            error_trace = traceback.format_exc()

            self.logger.error(f"✗ TEST FAILED: {e}")
            self.logger.debug(f"Traceback:\n{error_trace}")

            result = MapTestResult(
                test_name=test_name,
                timestamp=start_time.isoformat(),
                success=False,
                duration_seconds=duration,
                tiles_generated=tiles_generated,
                error_message=str(e),
                error_type=type(e).__name__,
                error_traceback=error_trace
            )

            return result

    def test_dungeon_tiles(self) -> MapTestResult:
        """Test dungeon tile generation."""
        test_name = "dungeon_tiles"
        self.logger.info(f"\n{'='*60}")
        self.logger.info(f"TEST: {test_name}")
        self.logger.info(f"{'='*60}")

        start_time = datetime.now()
        tiles_generated = 0

        try:
            dungeon_elements = [
                "stone dungeon floor tile top-down",
                "stone dungeon wall tile top-down",
                "wooden door tile top-down",
                "torch on wall tile top-down",
                "treasure chest tile top-down",
                "dungeon stairs down tile top-down"
            ]

            tiles = []
            for element in dungeon_elements:
                self.logger.info(f"Generating: {element}")
                tile = self.generate_tile(element, size=32)
                tiles.append(tile)
                tiles_generated += 1

            # Create tileset grid (3x2)
            tileset = Image.new('RGBA', (32 * 3, 32 * 2), (0, 0, 0, 0))
            for i, tile in enumerate(tiles):
                x = (i % 3) * 32
                y = (i // 3) * 32
                tileset.paste(tile, (x, y))

            output_path = OUTPUTS_DIR / f"{test_name}_tileset.png"
            tileset.save(output_path, "PNG")

            duration = (datetime.now() - start_time).total_seconds()

            result = MapTestResult(
                test_name=test_name,
                timestamp=start_time.isoformat(),
                success=True,
                duration_seconds=duration,
                tiles_generated=tiles_generated,
                tile_size=(32, 32),
                output_path=str(output_path)
            )

            self.logger.info(f"✓ TEST PASSED - Duration: {duration:.2f}s, Tiles: {tiles_generated}")
            return result

        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            error_trace = traceback.format_exc()

            self.logger.error(f"✗ TEST FAILED: {e}")
            self.logger.debug(f"Traceback:\n{error_trace}")

            result = MapTestResult(
                test_name=test_name,
                timestamp=start_time.isoformat(),
                success=False,
                duration_seconds=duration,
                tiles_generated=tiles_generated,
                error_message=str(e),
                error_type=type(e).__name__,
                error_traceback=error_trace
            )

            return result

    def run_all_tests(self):
        """Execute all map generation tests."""
        self.logger.info(f"\n{'#'*60}")
        self.logger.info("PIXELLAB MAP GENERATION TEST SUITE")
        self.logger.info(f"{'#'*60}\n")
        self.logger.info(f"Timestamp: {datetime.now().isoformat()}")
        self.logger.info(f"Output Directory: {OUTPUTS_DIR}")
        self.logger.info(f"Logs Directory: {LOGS_DIR}")

        if not self.initialize_client():
            self.logger.error("Cannot proceed without initialized client. Aborting tests.")
            return

        # Run tests
        test_methods = [
            self.test_basic_terrain_tiles,
            self.test_isometric_tiles,
            self.test_platformer_tiles,
            self.test_complete_map_generation,
            self.test_dungeon_tiles
        ]

        for test_method in test_methods:
            result = test_method()
            self.test_results.append(result)

        self.generate_summary()

    def generate_summary(self):
        """Generate and save test summary."""
        self.logger.info(f"\n{'#'*60}")
        self.logger.info("TEST SUMMARY")
        self.logger.info(f"{'#'*60}\n")

        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r.success)
        failed_tests = total_tests - passed_tests
        total_tiles = sum(r.tiles_generated for r in self.test_results)

        self.logger.info(f"Total Tests: {total_tests}")
        self.logger.info(f"Passed: {passed_tests}")
        self.logger.info(f"Failed: {failed_tests}")
        self.logger.info(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
        self.logger.info(f"Total Tiles Generated: {total_tiles}")

        self.logger.info(f"\nDetailed Results:")
        for i, result in enumerate(self.test_results, 1):
            status = "✓ PASS" if result.success else "✗ FAIL"
            self.logger.info(f"\n{i}. {result.test_name}")
            self.logger.info(f"   Status: {status}")
            self.logger.info(f"   Duration: {result.duration_seconds:.2f}s")
            self.logger.info(f"   Tiles: {result.tiles_generated}")

            if result.success:
                self.logger.info(f"   Output: {result.output_path}")
                if result.map_size:
                    self.logger.info(f"   Map Size: {result.map_size[0]}x{result.map_size[1]}")
            else:
                self.logger.info(f"   Error: {result.error_type}: {result.error_message}")

        # Save summary to JSON
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        summary_file = LOGS_DIR / f"map_test_summary_{timestamp}.json"

        summary_data = {
            "timestamp": datetime.now().isoformat(),
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "success_rate": passed_tests/total_tests*100 if total_tests > 0 else 0,
            "total_tiles_generated": total_tiles,
            "results": [asdict(r) for r in self.test_results]
        }

        with open(summary_file, 'w') as f:
            json.dump(summary_data, f, indent=2)

        self.logger.info(f"\nTest summary saved to: {summary_file}")

        if failed_tests == 0:
            self.logger.info("\n🎉 ALL MAP GENERATION TESTS PASSED!")
        else:
            self.logger.warning(f"\n⚠️  {failed_tests} TEST(S) FAILED")


def main():
    """Main entry point."""
    print("\n" + "="*60)
    print("PIXELLAB MAP GENERATION TEST SUITE")
    print("="*60)
    print("\nThis test suite generates various types of game maps and tilesets:")
    print("  • Basic terrain tiles (grass, water, stone, etc.)")
    print("  • Isometric tiles for strategy games")
    print("  • Platformer tiles for side-scrolling games")
    print("  • Complete map generation (8x8 tile map)")
    print("  • Dungeon tiles for roguelikes/RPGs")
    print("\nNOTE: Requires a valid PixelLab API key!")
    print("Get your key at: https://www.pixellab.ai/vibe-coding")
    print("="*60 + "\n")

    if API_KEY == "your-api-key-here":
        print("⚠️  ERROR: Please update API_KEY in this file with your actual PixelLab API key")
        print("   Get your key at: https://www.pixellab.ai/vibe-coding")
        sys.exit(1)

    tester = MapGenerationTester(api_key=API_KEY)
    tester.run_all_tests()


if __name__ == "__main__":
    main()
