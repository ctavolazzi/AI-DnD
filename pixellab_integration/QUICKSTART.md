# PixelLab Integration - Quick Start Guide

Get started with AI-powered pixel art generation in 5 minutes!

## Step 1: Get Your API Key

1. Visit https://www.pixellab.ai/vibe-coding
2. Sign up or log in
3. Copy your API token

## Step 2: Install Dependencies

```bash
# From the project root
pip install pixellab pillow
```

## Step 3: Update Your API Key

Edit any example file and replace:
```python
API_KEY = "your-api-key-here"
```

With your actual key:
```python
API_KEY = "sk-abc123..."  # Your real key
```

## Step 4: Run Your First Example

```bash
cd pixellab_integration
python examples/01_basic_character_generation.py
```

You should see:
```
PIXELLAB - BASIC CHARACTER GENERATION
======================================

API Credits: 1000

1. Generating wizard character...
   Generated: (64, 64)

2. Generating knight with custom parameters...
   Generated: (64, 64)

✓ All images saved to: outputs/basic_characters/
```

## Step 5: Check Your Generated Images

Open the `outputs/` folder to see your generated pixel art!

## What's Next?

Try the other examples:

```bash
# Character animation
python examples/02_character_animation.py

# Multi-directional characters
python examples/03_multi_directional.py

# Rotation and view changes
python examples/04_rotation_and_views.py

# Advanced features
python examples/05_advanced_features.py

# Complete game assets
python examples/06_game_ready_assets.py
```

## Quick Reference

### Generate a Character

```python
from pixellab_integration import PixelLabClient

client = PixelLabClient(api_key="your-key")

wizard = client.generate_character(
    description="fantasy wizard with blue robes",
    width=64,
    height=64,
    no_background=True
)

wizard.show()  # Display the image
```

### Create an Animation

```python
# Generate base character
base = client.generate_character("knight character")

# Animate it walking
walk_frames = client.animate_character_text(
    reference_image=base,
    description="knight character",
    action="walk",
    n_frames=4
)

# Create sprite sheet
sprite_sheet = client.create_sprite_sheet(
    walk_frames,
    columns=4,
    filename="knight_walk.png"
)
```

### 8-Directional Character

```python
from pixellab_integration import create_8_directional_character

directions_8 = create_8_directional_character(
    client,
    description="pixel art hero",
    width=64,
    height=64
)

# directions_8 is a dict: {'north': Image, 'east': Image, ...}
```

## Troubleshooting

**"Access denied" error?**
- Check your API key is correct
- Visit https://www.pixellab.ai to verify account status

**No images generated?**
- Check the `outputs/` folder
- Review console output for errors
- Ensure disk space available

**Need help?**
- Read the full README.md
- Join Discord: https://discord.gg/pBeyTBF8T7
- Check examples for working code

## Credits

Check your remaining credits:

```python
balance = client.get_balance()
print(f"Credits: {balance['credits']}")
```

## Ready to Build!

You're all set! Start generating pixel art for your game:

- Character sprites
- Animations
- Multi-directional assets
- Complete sprite sheets

Happy creating! 🎨
