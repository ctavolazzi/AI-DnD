# PixelLab Integration Guide

Complete guide to using PixelLab AI-powered pixel art generation in AI-DnD.

## Table of Contents
- [Quick Start](#quick-start)
- [MCP Server Setup](#mcp-server-setup)
- [Python API Usage](#python-api-usage)
- [Game Asset Generator](#game-asset-generator)
- [Dashboard Usage](#dashboard-usage)
- [API Reference](#api-reference)

---

## Quick Start

### Prerequisites

1. **Get API Key**: Sign up at [https://www.pixellab.ai](https://www.pixellab.ai) and obtain your API key
2. **Set Environment Variable**: Add to `.env` file:
   ```bash
   PIXELLAB_API_KEY=your-api-key-here
   ```

3. **Install Dependencies**:
   ```bash
   pip install pixellab pillow python-dotenv
   ```

---

## MCP Server Setup

Configure Claude Code to use PixelLab's Model Context Protocol server for natural language asset generation.

### Installation

```bash
claude mcp add pixellab https://api.pixellab.ai/mcp -t http -H "Authorization: Bearer YOUR_API_KEY"
```

Replace `YOUR_API_KEY` with your actual PixelLab API key.

### Configuration File

The `.mcp.json` configuration:

```json
{
  "mcpServers": {
    "pixellab": {
      "type": "http",
      "url": "https://api.pixellab.ai/mcp",
      "headers": {
        "Authorization": "Bearer ${PIXELLAB_API_KEY}"
      }
    }
  }
}
```

### Usage with Claude Code

Once configured, you can use natural language to generate assets:

```
User: "Create a pixel art wizard character facing 8 directions"
Claude: [Uses PixelLab MCP to generate the sprites]

User: "Generate a walking animation for this character"
Claude: [Creates 4-frame walking animation]

User: "Rotate this sprite to face north"
Claude: [Rotates the character sprite]
```

---

## Python API Usage

### Basic Character Generation

```python
from pixellab_integration.pixellab_client import PixelLabClient

# Initialize client
client = PixelLabClient(api_key="your-api-key")

# Generate a character
character = client.generate_character(
    description="heroic knight in shining armor",
    width=64,
    height=64,
    no_background=True
)

# Save the image
character.save("knight.png")
```

### 8-Directional Sprites

```python
# Generate all 8 directions at once
sprites = client.batch_generate_directions(
    description="elven archer",
    directions=['north', 'northeast', 'east', 'southeast',
                'south', 'southwest', 'west', 'northwest'],
    width=64,
    height=64
)

# Access individual directions
north_sprite = sprites['north']
east_sprite = sprites['east']
```

### Character Animation

```python
# Generate base character
base_char = client.generate_character(
    description="goblin warrior",
    width=64,
    height=64
)

# Create walking animation
walk_frames = client.animate_character_text(
    reference_image=base_char,
    description="goblin warrior",
    action="walk",
    n_frames=4,
    direction="east",
    view="side"
)

# Create sprite sheet from frames
sprite_sheet = client.create_sprite_sheet(
    frames=walk_frames,
    columns=4
)
```

### Character Rotation

```python
# Rotate character to different direction
rotated = client.rotate_character(
    image=base_char,
    from_direction="south",
    to_direction="north",
    width=64,
    height=64
)
```

### Image Inpainting

```python
from PIL import Image

# Modify specific regions of a sprite
modified = client.inpaint_image(
    description="glowing magic sword",
    inpainting_image=character_image,
    mask_image=mask,  # White pixels = areas to repaint
    width=64,
    height=64
)
```

---

## Game Asset Generator

Automated tool for generating complete character sprite sets.

### Basic Usage

```bash
# Generate a player character
python utils/game_asset_generator.py \
    --character "elven ranger with bow" \
    --animations walk,idle,attack \
    --size 64

# Generate an NPC
python utils/game_asset_generator.py \
    --npc "friendly merchant" \
    --animations idle \
    --size 64
```

### Batch Generation

Create a JSON file defining multiple characters:

```json
[
  {
    "name": "hero_warrior",
    "description": "heroic knight in shining armor",
    "size": 64,
    "animations": ["walk", "idle", "attack"]
  },
  {
    "name": "goblin_enemy",
    "description": "small green goblin",
    "size": 48,
    "animations": ["walk", "attack"]
  }
]
```

Run batch generation:

```bash
python utils/game_asset_generator.py --batch characters.json
```

### Output Structure

```
assets/generated/
├── elven_ranger/
│   ├── north.png
│   ├── northeast.png
│   ├── east.png
│   ├── southeast.png
│   ├── south.png
│   ├── southwest.png
│   ├── west.png
│   ├── northwest.png
│   ├── spritesheet_8dir.png
│   ├── animations/
│   │   ├── walk/
│   │   │   ├── frame_00.png
│   │   │   ├── frame_01.png
│   │   │   ├── frame_02.png
│   │   │   ├── frame_03.png
│   │   │   └── spritesheet.png
│   │   └── idle/
│   │       └── ...
│   └── metadata.json
```

---

## Dashboard Usage

Interactive web-based dashboard for parallel asset generation.

### Start Dashboard

```bash
# Terminal 1: Start HTTP server
cd dashboards && python3 -m http.server 8080

# Terminal 2: Start Actions server
python3 scripts/pixellab_actions.py --serve

# Open browser
# http://localhost:8080/pixellab_dashboard.html
```

### Features

- **Parallel Job Queue**: Run up to 3 generations simultaneously
- **Character Rotation**: Rotate completed characters to all 8 directions
- **Real-time Monitoring**: Live status updates and logging
- **Job History**: Persistent storage with automatic backups

---

## API Reference

### PixelLabClient Methods

#### `generate_character(description, width, height, **kwargs)`
Generate a pixel art character.

**Parameters:**
- `description` (str): Character description
- `width` (int): Image width in pixels
- `height` (int): Image height in pixels
- `no_background` (bool): Remove background (transparent)
- `outline` (str): Outline style ('single color black outline', 'lineless', etc.)
- `shading` (str): Shading style ('flat', 'basic', 'medium', 'detailed')
- `detail` (str): Detail level ('low', 'medium', 'highly detailed')
- `view` (str): Camera view ('side', 'front', 'back', '3/4')
- `direction` (str): Direction facing ('north', 'south', 'east', 'west', etc.)
- `isometric` (bool): Use isometric projection
- `seed` (int): Random seed for reproducibility

**Returns:** PIL.Image.Image

#### `animate_character_text(reference_image, description, action, n_frames, **kwargs)`
Create character animation from text description.

**Parameters:**
- `reference_image` (Image): Character to animate
- `description` (str): Character description
- `action` (str): Animation action ('walk', 'run', 'idle', 'attack', etc.)
- `n_frames` (int): Number of animation frames
- `view` (str): Camera view
- `direction` (str): Direction facing

**Returns:** List[PIL.Image.Image]

#### `rotate_character(image, to_direction, from_direction, **kwargs)`
Rotate character sprite to different direction.

**Parameters:**
- `image` (Image): Character image to rotate
- `to_direction` (str): Target direction
- `from_direction` (str): Current direction (optional)
- `width` (int): Output width
- `height` (int): Output height

**Returns:** PIL.Image.Image

#### `batch_generate_directions(description, directions, **kwargs)`
Generate character facing multiple directions.

**Parameters:**
- `description` (str): Character description
- `directions` (List[str]): List of directions to generate
- `width` (int): Image width
- `height` (int): Image height

**Returns:** Dict[str, PIL.Image.Image]

#### `create_sprite_sheet(frames, columns, filename)`
Combine animation frames into sprite sheet.

**Parameters:**
- `frames` (List[Image]): Animation frames
- `columns` (int): Number of columns in sheet
- `filename` (str): Output filename

**Returns:** PIL.Image.Image

#### `get_balance()`
Check API credit balance.

**Returns:** Dict with balance information

---

## Examples

### Complete Workflow Example

```python
#!/usr/bin/env python3
"""Generate a complete game character with all assets."""

import os
from pathlib import Path
from pixellab_integration.pixellab_client import PixelLabClient

# Initialize
api_key = os.getenv("PIXELLAB_API_KEY")
client = PixelLabClient(api_key=api_key, auto_save=False)
output_dir = Path("assets/my_character")
output_dir.mkdir(parents=True, exist_ok=True)

# Step 1: Generate 8-directional sprites
print("Generating 8-directional sprites...")
directions = client.batch_generate_directions(
    description="cyberpunk hacker with neon hair",
    directions=['north', 'northeast', 'east', 'southeast',
                'south', 'southwest', 'west', 'northwest'],
    width=64,
    height=64,
    no_background=True
)

# Save individual directions
for direction, sprite in directions.items():
    sprite.save(output_dir / f"{direction}.png")

# Step 2: Create walking animation
print("Creating walking animation...")
walk_frames = client.animate_character_text(
    reference_image=directions['south'],
    description="cyberpunk hacker with neon hair",
    action="walk",
    n_frames=4,
    direction="south"
)

# Save animation frames
anim_dir = output_dir / "animations" / "walk"
anim_dir.mkdir(parents=True, exist_ok=True)
for i, frame in enumerate(walk_frames):
    frame.save(anim_dir / f"frame_{i:02d}.png")

# Step 3: Create sprite sheets
print("Creating sprite sheets...")
walk_sheet = client.create_sprite_sheet(walk_frames, columns=4)
walk_sheet.save(output_dir / "walk_animation.png")

# Step 4: Check remaining credits
balance = client.get_balance()
print(f"Remaining balance: ${balance['usd']}")

print(f"✅ Assets saved to {output_dir}")
```

---

## Troubleshooting

### API Key Not Found
```bash
# Set in .env file
echo "PIXELLAB_API_KEY=your-key-here" >> .env

# Or export directly
export PIXELLAB_API_KEY=your-key-here
```

### Import Errors
```bash
# Install required packages
pip install pixellab pillow python-dotenv
```

### Rate Limiting
PixelLab API has rate limits. Use the dashboard's parallel queue to manage multiple generations efficiently.

### Balance Check
```python
client = PixelLabClient(api_key="your-key")
balance = client.get_balance()
print(f"Remaining: ${balance['usd']}")
```

---

## Additional Resources

- **PixelLab API Docs**: https://api.pixellab.ai/docs
- **Dashboard Guide**: `dashboards/README.md`
- **Test Suite**: `pixellab_tests/README.md`
- **Client Source**: `pixellab_integration/pixellab_client.py`

---

## Credits

PixelLab integration developed for AI-DnD autonomous campaign simulator.
API provided by PixelLab AI (https://www.pixellab.ai)
