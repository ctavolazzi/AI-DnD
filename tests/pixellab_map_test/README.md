# PixelLab Map Generation Test Suite

Comprehensive testing framework for generating game maps and tilesets using PixelLab's AI-powered pixel art generation.

## Overview

This test suite demonstrates and validates the creation of complete game maps including:
- Top-down terrain tilesets
- Isometric tiles for strategy games
- 2D platformer tiles and levels
- Complete map composition
- Dungeon generation

## Quick Start

### 1. Get API Key
Visit https://www.pixellab.ai/vibe-coding to get your API key

### 2. Update Configuration
```python
# In test_map_generation.py
API_KEY = "your-actual-api-key-here"
```

### 3. Run Tests
```bash
cd tests/pixellab_map_test
python test_map_generation.py
```

## Test Suite Features

### Test Cases

#### 1. Basic Terrain Tiles
**Purpose:** Generate fundamental terrain types for top-down games

**Tiles Generated:**
- Grass terrain
- Dirt terrain
- Stone terrain
- Water terrain
- Sand terrain

**Output:** 5-tile horizontal tileset (160x32 pixels)

**Use Cases:** RPGs, strategy games, adventure games

---

#### 2. Isometric Tiles
**Purpose:** Generate isometric tiles for strategy/simulation games

**Tiles Generated:**
- Grass isometric tile
- Stone building isometric tile
- Tree isometric tile
- Water isometric tile

**Output:** 4-tile horizontal tileset (256x64 pixels)

**Use Cases:** City builders, strategy games, simulation games

---

#### 3. Platformer Tiles
**Purpose:** Generate tiles for 2D side-scrolling platformer games

**Tiles Generated:**
- Stone brick platform
- Grass platform
- Metal platform
- Wooden platform
- Ice platform

**Output:** 5-tile horizontal tileset (160x32 pixels)

**Use Cases:** Platformers, Metroidvania games, side-scrollers

---

#### 4. Complete Map Generation
**Purpose:** Demonstrate full map composition with multiple terrain types

**Map Features:**
- 8x8 tile grid (256x256 pixels)
- Multiple terrain types (grass, water, path, tree)
- Layered composition
- Game-ready output

**Use Cases:** Any game requiring pre-composed maps

---

#### 5. Dungeon Tiles
**Purpose:** Generate dungeon elements for roguelikes and RPGs

**Elements Generated:**
- Stone dungeon floor
- Stone dungeon wall
- Wooden door
- Torch on wall
- Treasure chest
- Dungeon stairs

**Output:** 3x2 tile grid (96x64 pixels)

**Use Cases:** Roguelikes, dungeon crawlers, RPGs

---

## Example Map Builder

The `example_map_builder.py` script demonstrates building complete, game-ready maps.

### Run Examples
```bash
python example_map_builder.py
```

### Examples Included

#### RPG Overworld Map
- **Size:** 12x12 tiles (384x384 pixels)
- **Features:** Mountains, forests, towns, castle, water, paths
- **Tiles:** 7 unique terrain types

#### Dungeon Floor
- **Size:** 10x10 tiles (320x320 pixels)
- **Features:** Walls, floors, doors, treasures, monsters, stairs
- **Tiles:** 6 unique dungeon elements

#### Platformer Level
- **Size:** 16x10 tiles (512x320 pixels)
- **Features:** Platforms, coins, enemies, checkpoint flag
- **Tiles:** 6 unique level elements

---

## Output Structure

```
pixellab_map_test/
├── map_outputs/              # Generated maps and tilesets
│   ├── basic_terrain_tiles_tileset.png
│   ├── isometric_tiles_tileset.png
│   ├── platformer_tiles_tileset.png
│   ├── complete_map_generation_8x8.png
│   ├── dungeon_tiles_tileset.png
│   ├── rpg_overworld/       # Example outputs
│   ├── dungeon/
│   └── platformer/
└── map_logs/                 # Test execution logs
    ├── map_test_YYYYMMDD_HHMMSS.log
    └── map_test_summary_YYYYMMDD_HHMMSS.json
```

---

## Understanding the Tests

### Test Framework

The `MapGenerationTester` class provides:

**Comprehensive Logging:**
- File logging (DEBUG level with full details)
- Console logging (INFO level for monitoring)
- Timestamp tracking
- Error stack traces

**Test Result Tracking:**
- Success/failure status
- Duration measurement
- Tiles generated count
- Map dimensions
- Output file paths
- Error details

**Test Summary:**
- Pass/fail statistics
- Total tiles generated
- Detailed results per test
- JSON export for analysis

### Extending the Tests

Add new test methods to `MapGenerationTester`:

```python
def test_my_custom_tiles(self) -> MapTestResult:
    """Test custom tile generation."""
    test_name = "my_custom_tiles"
    start_time = datetime.now()
    tiles_generated = 0

    try:
        # Your tile generation logic
        tile = self.generate_tile("my custom tile description", size=32)
        tiles_generated += 1

        # Save output
        output_path = OUTPUTS_DIR / f"{test_name}_output.png"
        tile.save(output_path, "PNG")

        # Create result
        duration = (datetime.now() - start_time).total_seconds()
        return MapTestResult(
            test_name=test_name,
            timestamp=start_time.isoformat(),
            success=True,
            duration_seconds=duration,
            tiles_generated=tiles_generated,
            output_path=str(output_path)
        )
    except Exception as e:
        # Error handling...
        pass
```

Then add to `run_all_tests()`:
```python
test_methods = [
    # ... existing tests
    self.test_my_custom_tiles,  # Add here
]
```

---

## Using Generated Maps in Games

### Unity
```csharp
// Import PNG as Sprite
// Set Sprite Mode: Multiple
// Slice by cell size (32x32)
// Use in Tilemap
```

### Godot
```gdscript
# Import PNG as Texture
# Create TileSet resource
# Set tile size (32x32)
# Use in TileMap node
```

### GameMaker Studio
```gml
// Import as Sprite
// Set frame size (32, 32)
// Create tileset from sprite
// Use in room editor
```

### Pygame
```python
# Load tileset
tileset = pygame.image.load('tileset.png')

# Extract individual tiles
tile_size = 32
for i in range(tile_count):
    x = i * tile_size
    tile = tileset.subsurface((x, 0, tile_size, tile_size))
```

---

## Tileset Types Explained

### Horizontal Tilesets
**Format:** All tiles in a single row
**Best for:** Small sets (5-10 tiles), sprite animation frames

**Example:**
```
[Grass][Dirt][Stone][Water][Sand]
```

### Grid Tilesets
**Format:** Tiles arranged in rows and columns
**Best for:** Large tile sets (20+ tiles), organized categories

**Example:**
```
[Floor][Wall][Door]
[Chest][Stairs][Torch]
```

### Wang Tilesets
**Format:** Tiles that seamlessly connect
**Best for:** Terrain transitions, organic layouts

**Note:** PixelLab can generate individual tiles that you arrange into Wang sets

---

## Performance Considerations

### API Usage

Each tile generation uses API credits:
- Simple tile: ~1 credit
- Complex tile: ~2-3 credits
- Average tileset (5 tiles): ~5-10 credits

### Optimization Tips

**Use Caching:**
```python
# Cache tiles for reuse
tile_cache = {}

def get_tile(description):
    if description not in tile_cache:
        tile_cache[description] = generate_tile(description)
    return tile_cache[description]
```

**Batch Generation:**
- Generate all unique tiles first
- Reuse cached tiles for map composition
- Avoid regenerating identical tiles

**Rate Limiting:**
- Add delays between requests if needed
- Monitor API quota
- Use local caching for development

---

## Troubleshooting

### Issue: Tests Fail with 403 Error
**Cause:** Invalid or missing API key

**Solution:**
1. Get valid key from https://www.pixellab.ai/vibe-coding
2. Update `API_KEY` in test file
3. Verify key is active

---

### Issue: Tiles Don't Look Consistent
**Cause:** Different generation parameters or seeds

**Solution:**
```python
# Use consistent parameters
tile = self.generate_tile(
    description,
    size=32,
    seed=42,  # Same seed = consistent style
    outline='thick',
    shading='smooth'
)
```

---

### Issue: Map Composition Looks Wrong
**Cause:** Tile layering or size mismatch

**Solution:**
```python
# Ensure all tiles are same size
assert all(t.size == (32, 32) for t in tiles)

# Paste with correct positioning
for y in range(rows):
    for x in range(cols):
        map_image.paste(tile, (x * 32, y * 32))
```

---

## Test Results Example

```
======================================================================
PIXELLAB MAP GENERATION TEST SUITE
======================================================================

✓ basic_terrain_tiles - 5 tiles generated in 12.34s
✓ isometric_tiles - 4 tiles generated in 10.56s
✓ platformer_tiles - 5 tiles generated in 11.89s
✓ complete_map_generation - 4 tiles, 8x8 map in 15.67s
✓ dungeon_tiles - 6 tiles generated in 13.45s

======================================================================
TEST SUMMARY
======================================================================
Total Tests: 5
Passed: 5
Failed: 0
Success Rate: 100.0%
Total Tiles Generated: 24

🎉 ALL MAP GENERATION TESTS PASSED!
```

---

## Advanced Usage

### Custom Map Layouts

```python
# Define your own map layout
layout = [
    ['G', 'G', 'P', 'W'],
    ['G', 'T', 'P', 'W'],
    ['P', 'P', 'P', 'W'],
    ['G', 'G', 'G', 'W']
]

# Define what each symbol means
tiles = {
    'G': "grass terrain",
    'P': "stone path",
    'W': "water",
    'T': "tree"
}

# Use MapBuilder to create the map
builder = MapBuilder(client, tile_size=32)
map_image = builder.create_map(layout, tiles)
```

### Procedural Generation

Combine PixelLab tiles with procedural algorithms:

```python
# Generate random dungeon layout
from random import choice

def generate_random_dungeon(width, height):
    layout = []
    for y in range(height):
        row = []
        for x in range(width):
            # Edges are walls
            if x == 0 or x == width-1 or y == 0 or y == height-1:
                row.append('#')
            # Random interior
            else:
                row.append(choice(['.', '.', '.', 'M']))  # Mostly floor
        layout.append(row)
    return layout
```

---

## Integration with AI-DnD

These map generation tests integrate seamlessly with the AI-DnD project:

**Use Cases:**
- Generate battle maps for combat encounters
- Create dungeon layouts for campaigns
- Build overworld maps for exploration
- Design platformer levels for mini-games

**Example Integration:**
```python
# In your AI-DnD game code
from tests.pixellab_map_test.example_map_builder import MapBuilder
from pixellab_integration import PixelLabClient

# Generate a dungeon for the current encounter
client = PixelLabClient(api_key=YOUR_KEY)
builder = MapBuilder(client)

# AI generates the layout
dungeon_layout = ai_dungeon_generator.create_layout()

# PixelLab generates the tiles
dungeon_map = builder.create_map(dungeon_layout, dungeon_tiles)

# Use in game
game.set_battle_map(dungeon_map)
```

---

## Resources

- **PixelLab Website:** https://www.pixellab.ai
- **Get API Key:** https://www.pixellab.ai/vibe-coding
- **Discord Support:** https://discord.gg/pBeyTBF8T7
- **Python SDK:** https://github.com/pixellab-code/pixellab-python
- **Main Integration:** ../../pixellab_integration/

---

## License

This test suite is part of the AI-DnD project.
See the main project LICENSE for details.

---

**Ready to generate game maps!** 🗺️✨
