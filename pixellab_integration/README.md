# PixelLab Integration for AI-DnD

**Complete AI-powered pixel art generation for game development**

This integration provides a fully-featured Python client for PixelLab's API, enabling you to generate characters, animations, tilesets, and complete game assets directly within the AI-DnD project.

## 🚀 Quick Start

### 1. Get Your API Key

Visit [PixelLab](https://www.pixellab.ai/vibe-coding) to:
- Sign up for an account
- Get your API token
- Check your credit balance

### 2. Install Dependencies

```bash
pip install pixellab pillow
```

### 3. Run Your First Example

```python
from pixellab_integration.pixellab_client import PixelLabClient

# Initialize client
client = PixelLabClient(api_key="your-api-key-here")

# Generate a character
wizard = client.generate_character(
    description="fantasy wizard with blue robes",
    width=64,
    height=64
)

wizard.show()  # View the generated character
```

## 📚 Features

### ✨ Character Generation
- **PixFlux Engine:** Generate characters from text descriptions
- **BitForge Engine:** Style transfer using reference images
- Customizable outline, shading, and detail levels
- Multiple camera views (side, front, back, 3/4)
- 8-directional character creation
- Isometric projection support
- Transparent backgrounds

### 🎬 Animation
- **Text-based animation:** Describe the action ("walk", "run", "attack")
- **Skeleton-based animation:** Use keypoint data for precise control
- Multiple animation frames (4, 6, 8+ frames)
- All directions supported
- Sprite sheet generation
- Skeleton extraction from existing characters

### 🔄 Image Manipulation
- **Rotation:** Change character direction or camera view
- **Inpainting:** Modify specific regions of existing art
- **View changes:** Convert between side/front/back views
- **Variations:** Generate multiple versions with seeds

### 🎮 Game-Ready Assets
- Complete character asset sets
- Multi-directional sprite sheets
- Animation sequences
- Master sprite sheet compilation
- Ready for Unity, Godot, GameMaker, etc.

## 📖 Examples

We've included 6 comprehensive examples demonstrating all features:

### Example 1: Basic Character Generation
```bash
python examples/01_basic_character_generation.py
```
- Simple character creation
- Custom parameters (outline, shading, detail)
- Isometric characters
- Reproducible generation with seeds
- Negative prompts

### Example 2: Character Animation
```bash
python examples/02_character_animation.py
```
- Walking, running, attacking, idle animations
- Sprite sheet creation
- Multiple action sequences
- Complete animation sets

### Example 3: Multi-Directional Characters
```bash
python examples/03_multi_directional.py
```
- 4-directional (N, S, E, W)
- 8-directional (all cardinal + ordinal)
- Directional walking animations
- Top-down game assets

### Example 4: Rotation and Views
```bash
python examples/04_rotation_and_views.py
```
- Direction rotation
- Camera view changes
- 360° rotation sequences
- View comparison sheets

### Example 5: Advanced Features
```bash
python examples/05_advanced_features.py
```
- Style transfer with BitForge
- Inpainting demonstrations
- Skeleton extraction
- Character variations
- High-detail generation

### Example 6: Game-Ready Assets
```bash
python examples/06_game_ready_assets.py
```
- Complete character asset creation
- Hero, enemy, and NPC sets
- All animations included
- Master sprite sheets
- Production-ready workflow

## 🎯 API Reference

### PixelLabClient

```python
client = PixelLabClient(
    api_key="your-key",
    auto_save=True,
    save_dir="outputs"
)
```

#### Core Methods

**`generate_character(description, width, height, **kwargs)`**
Generate a pixel art character.

Parameters:
- `description` (str): Character description
- `width` (int): Image width
- `height` (int): Image height
- `outline` (str): 'thin' | 'thick' | None
- `shading` (str): 'flat' | 'smooth' | None
- `detail` (str): 'low' | 'medium' | 'high' | None
- `view` (str): 'side' | 'front' | 'back' | '3/4'
- `direction` (str): 'north' | 'south' | 'east' | 'west' | etc.
- `isometric` (bool): Use isometric projection
- `no_background` (bool): Transparent background
- `seed` (int): Random seed for reproducibility

**`generate_with_style(description, style_image, width, height, **kwargs)`**
Generate using a reference style image.

**`animate_character_text(reference_image, description, action, **kwargs)`**
Create animation from text description.

Parameters:
- `reference_image`: Character to animate
- `description`: Character description
- `action`: Animation action ("walk", "run", "attack", etc.)
- `n_frames`: Number of frames
- `view`: Camera view
- `direction`: Facing direction

**`animate_character_skeleton(skeleton_keypoints, **kwargs)`**
Create animation from skeleton data.

**`rotate_character(image, from_view, to_view, **kwargs)`**
Rotate character to different view/direction.

**`inpaint_image(description, inpainting_image, mask_image, **kwargs)`**
Modify specific regions of an image.

**`estimate_skeleton(character_image)`**
Extract skeleton keypoints from a character.

**`get_balance()`**
Check current API credit balance.

#### Helper Methods

**`create_sprite_sheet(frames, columns, filename)`**
Combine frames into a sprite sheet.

**`batch_generate_directions(description, directions, **kwargs)`**
Generate character facing multiple directions.

### Convenience Functions

**`create_walking_animation(client, description, **kwargs)`**
Quick helper for walking animations.

**`create_8_directional_character(client, description, **kwargs)`**
Generate all 8 directional views.

## 💡 Usage Tips

### Best Practices

1. **Be Specific:** Detailed descriptions yield better results
   ```python
   # Good
   "fantasy wizard with blue robes, tall hat, and wooden staff"

   # Better
   "elderly fantasy wizard wearing flowing blue robes with star patterns,
    tall pointed hat, holding gnarled wooden staff with crystal orb"
   ```

2. **Use Seeds for Consistency:** When creating related assets
   ```python
   hero = client.generate_character("hero knight", seed=42)
   hero_run = client.generate_character("hero knight running", seed=42)
   ```

3. **Start Simple:** Test with basic generation before complex workflows
   ```python
   # Test first
   test = client.generate_character("simple knight", width=32, height=32)

   # Then scale up
   final = client.generate_character("ornate knight", width=128, height=128)
   ```

4. **Use Negative Prompts:** Exclude unwanted features
   ```python
   character = client.generate_character(
       description="warrior character",
       negative_description="no helmet, no cape, no modern weapons"
   )
   ```

5. **Batch Operations:** Generate multiple assets efficiently
   ```python
   directions = client.batch_generate_directions(
       description="goblin enemy",
       directions=['north', 'south', 'east', 'west']
   )
   ```

### Parameter Guide

**Outline:**
- `'thin'` - Subtle outlines, modern pixel art style
- `'thick'` - Bold outlines, classic retro style
- `None` - No outlines, painterly style

**Shading:**
- `'flat'` - No shading, solid colors
- `'smooth'` - Gradient shading, 3D appearance
- `None` - Automatic shading

**Detail:**
- `'low'` - Simple, clean sprites
- `'medium'` - Balanced detail
- `'high'` - Complex, ornate designs

**Text Guidance Scale (1-20):**
- Low (1-5): More creative, loose interpretation
- Medium (6-10): Balanced
- High (11-20): Very literal, strict adherence

## 🔧 Integration with AI-DnD

### Using Generated Assets

```python
# Generate character for your DnD campaign
wizard_character = client.generate_character(
    description="wise old wizard NPC with grey beard and purple robes",
    width=64,
    height=64,
    no_background=True
)

# Save to game assets
wizard_character.save("assets/characters/wizard_npc.png")

# Generate complete animation set
directions_8 = create_8_directional_character(
    client,
    description="player character knight",
    width=64,
    height=64
)

# Create sprite sheet for game engine
frames = list(directions_8.values())
sprite_sheet = client.create_sprite_sheet(
    frames,
    columns=4,
    filename="player_knight.png"
)
```

### MCP Integration

The `.mcp.json` file is already configured for Claude Code integration:

```json
{
  "mcpServers": {
    "pixellab": {
      "type": "http",
      "url": "https://api.pixellab.ai/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_API_KEY"
      }
    }
  }
}
```

Use natural language in Claude Code:
```
"Generate a pixel art wizard character with 8 directions for my game"
```

## 📊 Output Structure

```
pixellab_integration/
├── outputs/              # All generated images
│   ├── basic_characters/
│   ├── animations/
│   ├── directional/
│   ├── rotations/
│   ├── advanced/
│   └── game_assets/
├── examples/             # Example scripts
├── pixellab_client.py    # Main client library
└── README.md             # This file
```

## 🎮 Game Engine Integration

### Unity

```csharp
// Import sprite sheets as Texture2D
// Slice into individual sprites
// Use Sprite Animator or Animation window
```

### Godot

```gdscript
# Import PNG sprite sheets
# Use AnimatedSprite or AnimationPlayer
# Set up sprite frames from sheet
```

### GameMaker Studio

```gml
// Import sprite sheet
// Set frame size and count
// Use in sprite_index
```

### Pygame

```python
# Load sprite sheet
sprite_sheet = pygame.image.load('character.png')

# Extract individual frames
frames = []
for i in range(8):
    frame = sprite_sheet.subsurface((i*64, 0, 64, 64))
    frames.append(frame)
```

## 🐛 Troubleshooting

### HTTP 403 Forbidden

**Problem:** API returns "Access denied"

**Solutions:**
1. Verify API key is correct and active
2. Check key hasn't expired
3. Ensure sufficient credits
4. Visit https://www.pixellab.ai to check account status

### Images Not Saving

**Problem:** No output files generated

**Solutions:**
1. Check `auto_save=True` in client initialization
2. Verify `save_dir` has write permissions
3. Check disk space
4. Review logs for save errors

### Low Quality Results

**Problem:** Generated images don't match expectations

**Solutions:**
1. Use more detailed descriptions
2. Adjust `text_guidance_scale` (try 8-12)
3. Set appropriate `detail` level
4. Use negative prompts to exclude unwanted elements
5. Try different seeds for variations

## 📝 API Credits

PixelLab uses a credit-based system. Check your balance:

```python
balance = client.get_balance()
print(f"Credits: {balance['credits']}")
```

Visit [PixelLab](https://www.pixellab.ai) to:
- View current balance
- Purchase additional credits
- Check pricing tiers

## 🔗 Resources

- **PixelLab Website:** https://www.pixellab.ai
- **MCP Setup Guide:** https://www.pixellab.ai/vibe-coding
- **Discord Community:** https://discord.gg/pBeyTBF8T7
- **Python SDK:** https://github.com/pixellab-code/pixellab-python
- **MCP Server:** https://github.com/pixellab-code/pixellab-mcp

## 📄 License

This integration is part of the AI-DnD project.
PixelLab API usage subject to PixelLab's Terms of Service.

---

**Built with ❤️ for the AI-DnD project**
**Powered by PixelLab AI**
