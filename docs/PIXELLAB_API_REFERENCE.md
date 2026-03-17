# PixelLab API Complete Reference

Complete parameter reference for all PixelLab API endpoints.

**API Base URL:** `https://api.pixellab.ai/v1`

**Authentication:** Bearer token in `Authorization` header

```bash
Authorization: Bearer YOUR_API_KEY
```

---

## Table of Contents

- [Generate Image (PixFlux)](#generate-image-pixflux)
- [Generate Image (BitForge)](#generate-image-bitforge)
- [Animate with Text](#animate-with-text)
- [Animate with Skeleton](#animate-with-skeleton)
- [Estimate Skeleton](#estimate-skeleton)
- [Rotate Character/Object](#rotate-characterobject)
- [Inpaint Image](#inpaint-image)
- [Get Balance](#get-balance)
- [Common Parameters](#common-parameters)

---

## Generate Image (PixFlux)

**Endpoint:** `POST /generate-image-pixflux`

**Description:** Creates pixel art from text descriptions. Best for general-purpose generation.

**Image Size Limits:**
- Minimum: 32x32 pixels
- Maximum: 400x400 pixels (area)

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `description` | string | ✅ | - | Text description of image to generate |
| `image_size` | object | ✅ | - | `{width: int, height: int}` |
| `no_background` | boolean | ❌ | false | Generate with transparent background (blank background over 200x200 area) |
| `detail` | enum | ❌ | - | Detail level: `"low detail"`, `"medium detail"`, `"highly detailed"` |
| `outline` | enum | ❌ | - | Outline style (see [Outline Styles](#outline-styles)) |
| `direction` | enum | ❌ | - | Subject direction (see [Directions](#directions)) |
| `isometric` | boolean | ❌ | false | Generate in isometric view (weakly guiding) |
| `seed` | integer | ❌ | - | Seed for reproducible generation |
| `negative_description` | string | ❌ | "" | **(Deprecated)** What to avoid |
| `init_image` | Base64Image | ❌ | - | Initial image to guide generation |
| `init_image_strength` | integer | ❌ | 300 | Strength of initial image influence (1-999) |
| `color_image` | Base64Image | ❌ | - | Color palette reference image |

### Example Request

```python
import pixellab

client = pixellab.Client(secret="YOUR_API_KEY")

response = client.generate_image_pixflux(
    description="cute dragon",
    image_size=dict(width=128, height=128),
    no_background=True,
    detail="highly detailed",
    outline="single color black outline",
    direction="south-east"
)

image = response.image.pil_image()
```

### Response

```json
{
  "usage": {
    "type": "usd",
    "usd": 1
  },
  "image": {
    "type": "base64",
    "base64": "<base64_encoded_image>"
  }
}
```

---

## Generate Image (BitForge)

**Endpoint:** `POST /generate-image-bitforge`

**Description:** Generates pixel art with style reference images. Best for style-consistent generation.

**Image Size Limits:**
- Maximum: 200x200 pixels (area)

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `description` | string | ✅ | - | Text description |
| `image_size` | object | ✅ | - | `{width: int, height: int}` |
| `style_image` | Base64Image | ❌ | - | Reference image for style matching |
| `style_strength` | integer | ❌ | 20 | How strongly to apply style (1-100) |
| `style_guidance_scale` | float | ❌ | 3 | Style guidance strength (0-20) |
| `text_guidance_scale` | float | ❌ | 3 | Text guidance strength (0-20) |
| `no_background` | boolean | ❌ | false | Transparent background |
| `detail` | enum | ❌ | - | Detail level |
| `outline` | enum | ❌ | - | Outline style |
| `direction` | enum | ❌ | - | Subject direction |
| `isometric` | boolean | ❌ | false | Isometric view |
| `coverage_percentage` | integer | ❌ | - | Percentage of canvas to cover (0-100) |
| `inpainting_image` | Base64Image | ❌ | - | Image to inpaint |
| `mask_image` | Base64Image | ❌ | - | Inpainting mask (white = repaint) |
| `init_image` | Base64Image | ❌ | - | Initial image |
| `init_image_strength` | integer | ❌ | 300 | Init image strength (1-999) |
| `color_image` | Base64Image | ❌ | - | Color palette reference |
| `negative_description` | string | ❌ | "" | What to avoid |
| `seed` | integer | ❌ | - | Random seed |

### Example Request

```python
response = client.generate_image_bitforge(
    description="wizard with purple robes",
    image_size=dict(width=64, height=64),
    style_image=reference_image,
    style_strength=20,
    style_guidance_scale=3,
    detail="highly detailed"
)
```

---

## Animate with Text

**Endpoint:** `POST /animate-with-text`

**Description:** Creates animation from text description.

**Image Size:** Currently only 64x64

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `description` | string | ✅ | - | Character description |
| `action` | string | ✅ | - | Animation action ("walk", "run", "attack", etc.) |
| `reference_image` | Base64Image | ✅ | - | Character to animate |
| `image_size` | object | ✅ | - | `{width: 64, height: 64}` |
| `view` | enum | ✅ | - | Camera view: `"side"`, `"front"`, `"3/4"` |
| `direction` | enum | ✅ | - | Subject direction (see [Directions](#directions)) |
| `n_frames` | integer | ❌ | 4 | Number of frames (2-20, generates 4 at a time) |
| `image_guidance_scale` | float | ❌ | 1.4 | Reference image guidance (1-20) |
| `init_images` | array | ❌ | - | Initial frames to start from |
| `inpainting_images` | array | ❌ | [null...] | Existing frames to guide generation |
| `mask_images` | array | ❌ | [null...] | Inpainting masks |
| `init_image_strength` | integer | ❌ | 300 | Init strength (1-999) |
| `color_image` | Base64Image | ❌ | - | Color palette |
| `seed` | integer | ❌ | - | Random seed |

### Example Request

```python
response = client.animate_with_text(
    description="human mage",
    action="walk",
    reference_image=mage_image,
    image_size=dict(width=64, height=64),
    view="side",
    direction="south",
    n_frames=4
)

frames = [img.pil_image() for img in response.images]
```

---

## Animate with Skeleton

**Endpoint:** `POST /animate-with-skeleton`

**Description:** Creates animation using skeleton keypoints for precise pose control.

**Supported Sizes:** 16x16, 32x32, 64x64, 128x128, 256x256

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `reference_image` | Base64Image | ✅ | - | Character reference |
| `image_size` | object | ✅ | - | `{width: int, height: int}` |
| `skeleton_keypoints` | array | ✅ | - | List of skeleton frames with poses |
| `view` | enum | ✅ | - | Camera view |
| `direction` | enum | ✅ | - | Subject direction |
| `guidance_scale` | float | ❌ | 4 | How closely to follow skeleton (1-20) |
| `inpainting_images` | array | ❌ | [null...] | Connected skeleton images |
| `mask_images` | array | ❌ | [null...] | Inpainting masks |
| `init_images` | array | ❌ | - | Initial frames |
| `init_image_strength` | integer | ❌ | 300 | Init strength |
| `color_image` | Base64Image | ❌ | - | Color palette |
| `isometric` | boolean | ❌ | false | Isometric view |
| `oblique_projection` | boolean | ❌ | false | Oblique projection |
| `seed` | integer | ❌ | - | Random seed |

### Example Request

```python
# First estimate skeleton
skeleton_result = client.estimate_skeleton(image=character_image)

# Then animate with modified keypoints
response = client.animate_with_skeleton(
    reference_image=character_image,
    image_size=dict(width=64, height=64),
    skeleton_keypoints=modified_keypoints,
    view="side",
    direction="south",
    guidance_scale=4
)
```

---

## Estimate Skeleton

**Endpoint:** `POST /estimate-skeleton`

**Description:** Extracts skeleton structure from character image.

**Supported Sizes:** 16x16, 32x32, 64x64, 128x128, 256x256

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `image` | Base64Image | ✅ | Character on transparent background |

### Example Request

```python
response = client.estimate_skeleton(
    image=character_image
)

keypoints = response.keypoints
```

### Response

```json
{
  "usage": {"type": "usd", "usd": 1},
  "keypoints": [
    {
      "x": 32,
      "y": 20,
      "label": "head",
      "z_index": 5
    },
    // ... more keypoints
  ]
}
```

---

## Rotate Character/Object

**Endpoint:** `POST /rotate`

**Description:** Rotate characters or objects to different views/directions.

**Supported Sizes:** 16x16, 32x32, 64x64, 128x128

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `from_image` | Base64Image | ✅ | - | Image to rotate |
| `image_size` | object | ✅ | - | `{width: int, height: int}` |
| `from_view` | enum | ❌ | "side" | Starting view (see [Camera Views](#camera-views)) |
| `to_view` | enum | ❌ | - | Target view |
| `from_direction` | enum | ❌ | "south" | Starting direction |
| `to_direction` | enum | ❌ | - | Target direction |
| `direction_change` | integer | ❌ | - | Rotation in degrees (-180 to 180) |
| `description` | string | ❌ | - | Object description (helps with rotation) |
| `image_guidance_scale` | float | ❌ | 3 | Reference image guidance (1-20) |
| `init_image` | Base64Image | ❌ | - | Initial image |
| `init_image_strength` | integer | ❌ | 300 | Init strength |
| `mask_image` | Base64Image | ❌ | - | Mask for selective rotation |
| `color_image` | Base64Image | ❌ | - | Color palette |
| `isometric` | boolean | ❌ | false | Isometric view |
| `oblique_projection` | boolean | ❌ | false | Oblique projection |
| `seed` | integer | ❌ | - | Random seed |

### Example Request

```python
response = client.rotate(
    from_image=character_image,
    image_size=dict(width=64, height=64),
    from_direction="south",
    to_direction="east",
    image_guidance_scale=7.5
)
```

---

## Inpaint Image

**Endpoint:** `POST /inpaint`

**Description:** Modify specific regions of an image.

**Image Size Limit:** Maximum 200x200 (area)

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `description` | string | ✅ | - | What to paint in masked region |
| `inpainting_image` | Base64Image | ✅ | - | Original image |
| `mask_image` | Base64Image | ✅ | - | Mask (white = repaint, black = keep) |
| `image_size` | object | ✅ | - | `{width: int, height: int}` |
| `no_background` | boolean | ❌ | false | Transparent background |
| `detail` | enum | ❌ | - | Detail level |
| `outline` | enum | ❌ | - | Outline style |
| `direction` | enum | ❌ | - | Subject direction |
| `isometric` | boolean | ❌ | false | Isometric view |
| `init_image` | Base64Image | ❌ | - | Initial image |
| `init_image_strength` | integer | ❌ | 300 | Init strength |
| `color_image` | Base64Image | ❌ | - | Color palette |
| `negative_description` | string | ❌ | "" | What to avoid |
| `extra_guidance_scale` | float | ❌ | 3 | **(Deprecated)** |
| `seed` | integer | ❌ | - | Random seed |

### Example Request

```python
response = client.inpaint(
    description="glowing magic sword",
    inpainting_image=character_image,
    mask_image=weapon_mask,
    image_size=dict(width=64, height=64),
    detail="highly detailed"
)
```

---

## Get Balance

**Endpoint:** `GET /balance`

**Description:** Check current API credit balance.

### Example Request

```python
balance = client.get_balance()
print(f"Balance: ${balance.usd} USD")
```

### Response

```json
{
  "type": "usd",
  "usd": 10.50
}
```

---

## Common Parameters

### Directions

8-directional compass values:

- `"north"` - N
- `"north-east"` - NE
- `"east"` - E
- `"south-east"` - SE
- `"south"` - S
- `"south-west"` - SW
- `"west"` - W
- `"north-west"` - NW

### Camera Views

- `"side"` - Side view (most common for 2D games)
- `"front"` - Front-facing view
- `"back"` - Back-facing view
- `"3/4"` - Three-quarter view
- `"low top-down"` - Low angle top-down
- `"high top-down"` - High angle top-down

### Outline Styles

- `"single color black outline"` - Classic black pixel art outline
- `"single color outline"` - Colored outline
- `"selective outline"` - Outline only where needed
- `"lineless"` - No outline (painterly style)

### Detail Levels

- `"low detail"` - Simple, minimalist
- `"medium detail"` - Balanced detail
- `"highly detailed"` - Maximum detail

### Shading Styles

- `"flat shading"` - No shading
- `"basic shading"` - Simple cel shading
- `"medium shading"` - Standard shading
- `"detailed shading"` - Complex shading
- `"highly detailed shading"` - Maximum shading complexity

### Base64Image Format

Images must be provided in this format:

```json
{
  "type": "base64",
  "base64": "<base64_encoded_png_or_jpg>"
}
```

In Python with PIL:

```python
import base64
from io import BytesIO

# Encode image to base64
buffer = BytesIO()
image.save(buffer, format="PNG")
base64_str = base64.b64encode(buffer.getvalue()).decode()

base64_image = {
    "type": "base64",
    "base64": base64_str
}
```

---

## Error Responses

### 401 - Invalid API Token

```json
{
  "error": "Invalid API token"
}
```

### 402 - Insufficient Credits

```json
{
  "error": "Insufficient credits"
}
```

### 422 - Validation Error

```json
{
  "detail": [
    {
      "loc": ["body", "description"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### 429 - Too Many Requests

```json
{
  "error": "Too many requests"
}
```

### 529 - Rate Limit Exceeded

```json
{
  "error": "Rate limit exceeded"
}
```

---

## Rate Limits

- Standard rate limits apply per API key
- Contact PixelLab support for enterprise rate limits
- Use the `/balance` endpoint to monitor credit usage

---

## Best Practices

1. **Image Size Selection**
   - Use 64x64 for standard game sprites
   - Use 128x128 for detailed characters
   - Keep under limits for each endpoint

2. **Seed Usage**
   - Save seeds for reproducible generation
   - Use same seed with slight prompt variations for consistency

3. **Style Consistency**
   - Use BitForge with style images for consistent art styles
   - Save reference images for each character type

4. **Animation Workflow**
   - Generate base character first
   - Rotate to all needed directions
   - Animate each direction separately
   - Use skeleton animation for precise control

5. **Credit Management**
   - Check balance before large batch operations
   - Cache and reuse generated assets
   - Use lower resolutions for testing

---

## Support

- Website: https://www.pixellab.ai
- Documentation: https://api.pixellab.ai/docs
- GitHub: https://github.com/pixellab-ai

---

**Last Updated:** 2025-12-01
