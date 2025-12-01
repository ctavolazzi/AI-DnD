# PixelLab Integration Guide

Complete guide to using PixelLab AI-powered pixel art generation in AI-DnD.

## Quick Navigation

- 📚 [Complete API Reference](PIXELLAB_API_REFERENCE.md) - All endpoints and parameters
- 💻 [Python Examples](../examples/pixellab_api_examples.py) - Feature showcase
- 🎮 [Game Asset Pipeline](../pipelines/complete_game_asset_pipeline.py) - Production workflow

---

## Table of Contents

- [Overview](#overview)
- [Setup](#setup)
  - [MCP Server](#mcp-server-setup)
  - [Python Client](#python-client-setup)
- [Quick Start](#quick-start)
- [Examples](#examples)
- [Production Pipeline](#production-pipeline)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## Overview

PixelLab provides AI-powered pixel art generation with multiple models and features:

**Available Models:**
- **PixFlux** - General-purpose generation from text (up to 400x400)
- **BitForge** - Style-consistent generation with reference images (up to 200x200)

**Capabilities:**
- 🎨 Image Generation from text descriptions
- 🎬 Text-based Animation (walk, attack, run, etc.)
- 🦴 Skeleton-based Animation (precise pose control)
- 🔄 Character/Object Rotation (8 directions)
- ✏️ Image Inpainting (modify specific regions)
- 📐 Skeleton Estimation (extract character structure)

---

## Setup

### MCP Server Setup

The Model Context Protocol (MCP) allows Claude Code to use PixelLab directly through natural language.

#### 1. Get API Key

Sign up at [https://www.pixellab.ai](https://www.pixellab.ai) and obtain your API key.

#### 2. Add MCP Server to Claude Code

```bash
claude mcp add pixellab https://api.pixellab.ai/mcp \
  -t http \
  -H "Authorization: Bearer YOUR_API_KEY"
```

Replace `YOUR_API_KEY` with your actual PixelLab API key.

#### 3. Verify Installation

The MCP server will be listed in `.mcp.json`:

```json
{
  "servers": {
    "pixellab": {
      "url": "https://api.pixellab.ai/mcp",
      "type": "http",
      "headers": {
        "Authorization": "Bearer YOUR_API_KEY"
      }
    }
  }
}
```

#### 4. Use in Claude Code

You can now ask Claude Code to generate assets:

```
"Create a pixel art wizard character with 8 directions"
"Generate a walking animation for my knight character"
"Rotate this goblin sprite to face north"
```

---

### Python Client Setup

For programmatic access and batch operations:

#### 1. Install Client

```bash
pip install pixellab pillow python-dotenv
```

#### 2. Configure Environment

Add to `.env`:

```env
PIXELLAB_API_KEY=your_api_key_here
```

#### 3. Import and Use

```python
from pixellab_integration.pixellab_client import PixelLabClient

# Initialize client
client = PixelLabClient(
    api_key="YOUR_API_KEY",
    auto_save=True,
    save_dir="outputs"
)

# Generate a character
dragon = client.generate_character(
    description="cute dragon",
    width=128,
    height=128,
    no_background=True
)

# Check balance
balance = client.get_balance()
print(f"Credits: ${balance['usd']}")
```

---

## Quick Start

### Example 1: Generate Single Character

```python
import os
from pixellab_integration.pixellab_client import PixelLabClient

client = PixelLabClient(os.getenv("PIXELLAB_API_KEY"))

# Generate character
warrior = client.generate_character(
    description="heroic knight in shining armor with sword",
    width=64,
    height=64,
    direction="south",
    no_background=True,
    detail="highly detailed"
)

# warrior.png saved to outputs/
```

### Example 2: Create Walking Animation

```python
# Generate base character
mage = client.generate_character(
    description="wizard in blue robes with staff",
    width=64,
    height=64,
    no_background=True
)

# Create walking animation
walk_frames = client.animate_character_text(
    reference_image=mage,
    description="wizard",
    action="walk",
    width=64,
    height=64,
    n_frames=4,
    direction="south"
)

# Create sprite sheet
sprite_sheet = client.create_sprite_sheet(
    frames=walk_frames,
    columns=4,
    filename="mage_walk.png"
)
```

### Example 3: Generate 8-Directional Character

```python
# Generate all 8 directions
directions = client.batch_generate_directions(
    description="elf ranger with bow",
    directions=['north', 'north-east', 'east', 'south-east',
                'south', 'south-west', 'west', 'north-west'],
    width=64,
    height=64,
    no_background=True
)

# Create directional sprite sheet
direction_sheet = client.create_sprite_sheet(
    frames=list(directions.values()),
    columns=4,
    filename="elf_directions.png"
)
```

---

## Examples

### Run Complete Examples Suite

```bash
# Run all examples
python examples/pixellab_api_examples.py --example all

# Run specific example
python examples/pixellab_api_examples.py --example generation
python examples/pixellab_api_examples.py --example animation
python examples/pixellab_api_examples.py --example rotation

# Custom output directory
python examples/pixellab_api_examples.py \
  --example complete \
  --output my_assets
```

### Available Examples

1. **Basic Generation** - Simple image generation with PixFlux
2. **Style Generation** - BitForge with style references
3. **Text Animation** - Create animations from text descriptions
4. **Skeleton Animation** - Precise pose-based animation
5. **Rotation** - Rotate characters to different directions
6. **Inpainting** - Modify specific image regions
7. **Complete Character** - Full character asset pack
8. **Balance Check** - Check API credits

See [`examples/pixellab_api_examples.py`](../examples/pixellab_api_examples.py) for full code.

---

## Production Pipeline

The **Complete Game Asset Pipeline** automates creation of production-ready game assets.

### Features

- ✅ 8-directional character sprites
- ✅ Multiple animation sets per character
- ✅ Organized directory structure
- ✅ Sprite sheet generation
- ✅ JSON metadata for game integration
- ✅ Batch processing support

### Usage

#### Single Character

```bash
python pipelines/complete_game_asset_pipeline.py \
  --project "my-rpg" \
  --character "warrior" \
  --description "heroic knight with sword and shield" \
  --animations walk,attack,idle \
  --size 64
```

#### Batch from JSON

Create `characters.json`:

```json
[
  {
    "name": "hero_warrior",
    "description": "heroic knight in shining armor",
    "animations": ["walk", "attack", "idle"],
    "category": "characters",
    "size": 64
  },
  {
    "name": "goblin_enemy",
    "description": "small green goblin with crude weapons",
    "animations": ["walk", "attack"],
    "category": "enemies",
    "size": 48
  }
]
```

Run batch:

```bash
python pipelines/complete_game_asset_pipeline.py \
  --project "my-rpg" \
  --batch characters.json
```

#### Demo Mode

```bash
python pipelines/complete_game_asset_pipeline.py \
  --project "demo" \
  --demo
```

### Output Structure

```
game_assets/my-rpg/
├── characters/
│   └── hero_warrior/
│       ├── hero_warrior_base.png
│       ├── hero_warrior_directions.png
│       ├── hero_warrior_walk_sheet.png
│       ├── hero_warrior_attack_sheet.png
│       ├── hero_warrior_metadata.json
│       ├── directions/
│       │   ├── hero_warrior_north.png
│       │   ├── hero_warrior_east.png
│       │   └── ...
│       └── animations/
│           ├── walk/
│           │   ├── north/
│           │   ├── east/
│           │   └── ...
│           └── attack/
│               └── ...
├── npcs/
├── enemies/
└── party_manifest.json
```

### Metadata Format

```json
{
  "name": "hero_warrior",
  "description": "heroic knight in shining armor",
  "size": 64,
  "directions": 8,
  "animations": ["walk", "attack", "idle"],
  "created": "2025-12-01T10:30:00",
  "sprite_info": {
    "frame_size": [64, 64],
    "directions": ["north", "north-east", ...],
    "animations": {
      "walk": {"frames": 4, "directions": 4},
      "attack": {"frames": 4, "directions": 4}
    }
  }
}
```

---

## Best Practices

### 1. Cost Management

```python
# Check balance before large operations
balance = client.get_balance()
if balance['usd'] < 5.0:
    print("Low balance! Top up before continuing.")

# Use smaller sizes for testing
test_image = client.generate_character(
    description="test character",
    width=32,  # Smaller = cheaper
    height=32
)
```

### 2. Consistency

```python
# Use seeds for reproducibility
base = client.generate_character(
    description="my hero",
    seed=12345
)

# Use same seed for variations
variation = client.generate_character(
    description="my hero with different pose",
    seed=12345  # Same seed = consistent style
)

# Use style references (BitForge)
styled = client.generate_with_style(
    description="new character",
    style_image=base,  # Match existing style
    style_strength=0.8
)
```

### 3. Animation Workflow

```python
# 1. Generate base character
char = client.generate_character(description="warrior", ...)

# 2. Create all directions
directions = client.batch_generate_directions(
    description="warrior",
    directions=['north', 'east', 'south', 'west']
)

# 3. Animate each direction
for direction, image in directions.items():
    frames = client.animate_character_text(
        reference_image=image,
        description="warrior",
        action="walk",
        direction=direction
    )
    # Save frames...
```

### 4. Caching

```python
import json
from pathlib import Path

# Save generated assets with metadata
def save_with_metadata(image, description, params):
    filename = f"{description.replace(' ', '_')}.png"
    image.save(f"cache/{filename}")

    metadata = {
        "description": description,
        "params": params,
        "filename": filename
    }
    with open(f"cache/{filename}.json", 'w') as f:
        json.dump(metadata, f)

# Reuse cached assets
def load_from_cache(description):
    filename = f"{description.replace(' ', '_')}.png"
    cache_file = Path(f"cache/{filename}")
    if cache_file.exists():
        return Image.open(cache_file)
    return None
```

### 5. Error Handling

```python
import time

def generate_with_retry(func, max_retries=3, **kwargs):
    """Retry failed generations with exponential backoff."""
    for attempt in range(max_retries):
        try:
            return func(**kwargs)
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            wait_time = 2 ** attempt
            print(f"Error: {e}. Retrying in {wait_time}s...")
            time.sleep(wait_time)

# Usage
character = generate_with_retry(
    client.generate_character,
    description="my character",
    width=64,
    height=64
)
```

---

## Troubleshooting

### Issue: "401 Invalid API token"

**Solution:** Check your API key

```python
# Verify API key is set
import os
api_key = os.getenv("PIXELLAB_API_KEY")
if not api_key:
    print("API key not found in environment!")
```

### Issue: "402 Insufficient credits"

**Solution:** Check balance and top up

```python
balance = client.get_balance()
print(f"Current balance: ${balance['usd']}")
# Top up at https://www.pixellab.ai
```

### Issue: "422 Validation error"

**Solution:** Check parameter ranges

- Image size within limits (PixFlux: 32x32 to 400x400, BitForge: max 200x200)
- Valid enum values (see [API Reference](PIXELLAB_API_REFERENCE.md))
- Required fields provided

### Issue: "429 Too many requests"

**Solution:** Implement rate limiting

```python
import time

def rate_limited_generate(descriptions, delay=2):
    """Generate with delay between requests."""
    results = []
    for desc in descriptions:
        result = client.generate_character(description=desc)
        results.append(result)
        time.sleep(delay)  # Wait between requests
    return results
```

### Issue: Images not saving

**Solution:** Check save directory

```python
# Ensure directory exists and is writable
save_dir = Path("outputs")
save_dir.mkdir(parents=True, exist_ok=True)

# Check permissions
if not os.access(save_dir, os.W_OK):
    print(f"No write permission for {save_dir}")
```

### Issue: Out of memory

**Solution:** Generate in batches

```python
def batch_generate(descriptions, batch_size=10):
    """Generate in smaller batches to avoid memory issues."""
    results = []
    for i in range(0, len(descriptions), batch_size):
        batch = descriptions[i:i+batch_size]
        batch_results = [
            client.generate_character(description=desc)
            for desc in batch
        ]
        results.extend(batch_results)
        # Clean up
        import gc
        gc.collect()
    return results
```

---

## Additional Resources

- 📖 [Complete API Reference](PIXELLAB_API_REFERENCE.md)
- 💻 [Example Scripts](../examples/pixellab_api_examples.py)
- 🎮 [Production Pipeline](../pipelines/complete_game_asset_pipeline.py)
- 🌐 [PixelLab Website](https://www.pixellab.ai)
- 📚 [Official API Docs](https://api.pixellab.ai/docs)

---

## Support

For issues with:
- **AI-DnD Integration:** Open an issue on this repository
- **PixelLab API:** Contact PixelLab support at https://www.pixellab.ai
- **MCP Server:** Check `.mcp.json` configuration

---

**Last Updated:** 2025-12-01
