# PixelLab API Integration

This module provides a complete integration with the PixelLab API for pixel art generation, animation, and transformation.

## Overview

The `image_provider.py` module contains two main implementations:

1. **MockImageProvider** - Generates placeholder images for development (no API calls)
2. **APIImageProvider** - Calls the PixelLab API with graceful fallback to MockImageProvider

## Core Features

### Image Generation

#### Pixflux (Text-to-Image)
Generate pixel art images from text descriptions.

```python
provider = APIImageProvider(api_key="YOUR_API_KEY")
image = provider._generate_pixflux(
    description="cute dragon",
    width=128,
    height=128,
    detail="highly detailed",
    no_background=True
)
```

**Parameters:**
- `description` (str): Text description of the image
- `width` (int): Image width (32-400px)
- `height` (int): Image height (32-400px)
- `detail` (str, optional): "low detail", "medium detail", or "highly detailed"
- `direction` (str, optional): Cardinal direction (north, east, south, west, etc.)
- `isometric` (bool, optional): Generate in isometric view
- `no_background` (bool, optional): Transparent background

#### Bitforge (Style-Based Generation)
Generate images with custom art styles using reference images.

```python
provider._generate_bitforge(
    description="cute dragon",
    width=128,
    height=128,
    style_image=style_bytes,  # Reference image for styling
    detail="highly detailed"
)
```

**Parameters:**
- `description` (str): Text description
- `width` (int): Image width (max 200px)
- `height` (int): Image height (max 200px)
- `style_image` (bytes, optional): Reference image for style transfer
- `coverage_percentage` (int, optional): Canvas coverage (0-100%)

### Animation

#### Text-Guided Animation
Generate 4-frame animations from text descriptions and actions.

```python
provider._animate_with_text(
    description="human mage",
    action="walk",
    width=64,
    height=64,
    view="side",
    direction="south"
)
```

**Parameters:**
- `description` (str): Character description
- `action` (str): Animation action (walk, run, attack, cast, etc.)
- `width` (int): Image width (64px)
- `height` (int): Image height (64px)
- `view` (str, optional): "side", "front", or "back"
- `direction` (str, optional): Cardinal direction
- `n_frames` (int, optional): 2-20 frames (default 4)

#### Skeleton-Based Animation
Generate animations from skeleton poses and keypoints.

```python
provider._animate_with_skeleton(
    reference_image=character_bytes,
    width=64,
    height=64,
    skeleton_keypoints=keypoints,
    direction="south"
)
```

**Parameters:**
- `reference_image` (bytes): Character sprite image
- `width` (int): Image width (16-256px)
- `height` (int): Image height (16-256px)
- `skeleton_keypoints` (list, optional): Keypoint positions and labels
- `guidance_scale` (int, optional): Strength of skeleton influence (1-20)

### Transformation

#### Character Rotation
Rotate a sprite between different directions.

```python
provider._rotate_character(
    from_image=sprite_bytes,
    from_direction="south",
    to_direction="east",
    width=64,
    height=64
)
```

**Parameters:**
- `from_image` (bytes): Source sprite image
- `from_direction` (str): Current direction
- `to_direction` (str): Target direction
- `width` (int): Image width (16-128px)
- `height` (int): Image height (16-128px)
- `from_view` (str, optional): Camera view ("side", "low top-down", "high top-down")
- `to_view` (str, optional): Target camera view

#### Image Inpainting
Edit and modify existing pixel art images.

```python
provider._inpaint_image(
    description="add wings to the character",
    inpainting_image=original_sprite_bytes,
    mask_image=edit_mask_bytes,
    width=128,
    height=128
)
```

**Parameters:**
- `description` (str): What to modify
- `inpainting_image` (bytes): Original image
- `mask_image` (bytes): White areas indicate where to edit
- `width` (int): Image width (max 200px)
- `height` (int): Image height (max 200px)

### Utility

#### Skeleton Estimation
Extract skeleton keypoints from a character sprite.

```python
keypoints = provider._estimate_skeleton(character_image_bytes)
```

**Returns:**
A list of keypoint dictionaries with:
- `x`, `y`: Position coordinates
- `label`: Keypoint name (e.g., "head", "left_arm", "torso")
- `z_index`: Depth ordering

## Main API Methods

The public API provides high-level methods for common use cases:

```python
# Get scene backgrounds
scene_image = provider.get_scene_image("Dark Forest", 400, 300)

# Get character portraits
char_image = provider.get_character_portrait("Aragorn", "Ranger", 150, 200)

# Get item icons
item_image = provider.get_item_image("Sword of Truth", 64, 64)

# Get location maps
map_image = provider.get_map_image("Rivendell", 300, 300)
```

## Error Handling

All methods gracefully handle failures:

1. **API unavailable**: Returns `None`, triggering fallback
2. **Invalid parameters**: Caught and returns `None`
3. **Network errors**: Caught and returns `None`
4. **Missing API key**: Falls back to MockImageProvider automatically

### Example: Graceful Fallback

```python
provider = APIImageProvider(api_key=os.getenv("PIXELLAB_API_KEY"))

# If API is unavailable or returns None, MockImageProvider takes over
image = provider.get_scene_image("Dark Forest", 400, 300)
# Result: Either real AI-generated image or detailed placeholder

# Check if it's a real image or placeholder
if "API:" in surface_text:
    print("Using placeholder (API unavailable)")
else:
    print("Using real PixelLab API image")
```

## Configuration

Set your API key via environment variable:

```bash
export PIXELLAB_API_KEY="your_api_token_here"
```

Or pass it directly:

```python
provider = APIImageProvider(api_key="your_api_token_here")
```

## Caching

All generated images are cached by (type, name, width, height):

```python
# First call: API request
image1 = provider.get_character_portrait("Aragorn", "Ranger", 150, 200)

# Second call: Returns cached image instantly
image2 = provider.get_character_portrait("Aragorn", "Ranger", 150, 200)

# Clear cache if needed
provider.clear_cache()
```

## Testing

Tests verify:
- ✅ Image generation and caching
- ✅ Correct dimensions
- ✅ All API methods callable
- ✅ Graceful error handling
- ✅ MockImageProvider fallback

Run tests with:

```bash
python pygame_mvp/tests/test_image_provider.py
```

## API Reference

See the [PixelLab API Documentation](https://api.pixellab.ai/docs) for complete endpoint specifications.

### Endpoints Used

- `POST /v1/generate-image-pixflux` - Text-to-image generation
- `POST /v1/generate-image-bitforge` - Style-based generation
- `POST /v1/animate-with-text` - Text-guided animation
- `POST /v1/animate-with-skeleton` - Skeleton-based animation
- `POST /v1/rotate` - Character/object rotation
- `POST /v1/inpaint` - Image inpainting
- `POST /v1/estimate-skeleton` - Skeleton estimation
- `GET /v1/balance` - Account balance (for monitoring credits)

## Performance Notes

- Images are cached locally to avoid repeated API calls
- Bitforge has smaller max dimensions (200x200) vs Pixflux (400x400)
- Animation endpoints generate 4 frames by default
- Skeleton estimation requires transparent background images
- All methods timeout gracefully if API is slow/unavailable
