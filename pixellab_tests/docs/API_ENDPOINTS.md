# PixelLab API Endpoints Reference

Complete reference for all PixelLab API endpoints used in this project.

**Base URL:** `https://api.pixellab.ai/v2`

**Documentation:** https://api.pixellab.ai/v2/llms.txt

---

## 🎨 Character Generation (Pixflux)

Generate pixel art characters from text descriptions.

### Endpoint
```
POST /generate-character
```

### Request Body
```json
{
  "prompt": "heroic knight with sword",
  "width": 64,
  "height": 64,
  "seed": null,
  "detail": "medium detail",
  "outline": "single color black outline",
  "shading": "basic shading",
  "no_background": false,
  "text_guidance_scale": 8.0,
  "negative_description": "blurry, distorted"
}
```

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `prompt` | string | ✅ Yes | - | Description of character to generate |
| `width` | integer | No | 64 | Image width (32, 64, 128, 256) |
| `height` | integer | No | 64 | Image height (32, 64, 128, 256) |
| `seed` | integer | No | null | Random seed (null for random) |
| `detail` | string | No | "medium detail" | "low detail", "medium detail", "highly detailed" |
| `outline` | string | No | "single color black outline" | See outline options below |
| `shading` | string | No | "basic shading" | See shading options below |
| `no_background` | boolean | No | false | Transparent background for sprites |
| `text_guidance_scale` | float | No | 8.0 | How closely to follow prompt (1.0-20.0) |
| `negative_description` | string | No | "" | What to avoid in generation |

**Outline Options:**
- `"single color black outline"`
- `"single color outline"`
- `"selective outline"`
- `"lineless"`

**Shading Options:**
- `"flat shading"`
- `"basic shading"`
- `"medium shading"`
- `"detailed shading"`
- `"highly detailed shading"`

### Response
```json
{
  "status": "success",
  "prompt": "heroic knight with sword",
  "width": 64,
  "height": 64,
  "duration": 12.45,
  "image_data_url": "data:image/png;base64,iVBORw0KG...",
  "saved_path": "dashboards/generated/character_001.png"
}
```

### Example Test Cases

**Basic Character:**
```json
{
  "prompt": "heroic knight",
  "width": 64,
  "height": 64
}
```

**High Detail Character:**
```json
{
  "prompt": "wizard with glowing staff, purple robes, intricate patterns",
  "width": 128,
  "height": 128,
  "detail": "highly detailed",
  "shading": "detailed shading"
}
```

**Sprite (No Background):**
```json
{
  "prompt": "dragon breathing fire",
  "width": 64,
  "height": 64,
  "no_background": true
}
```

---

## 🔄 Character Rotation

Rotate a character to face different directions.

### Endpoint
```
POST /rotate-character
```

### Request Body
```json
{
  "image_data_url": "data:image/png;base64,iVBORw0KG...",
  "to_direction": "east",
  "from_direction": "south",
  "width": 64,
  "height": 64
}
```

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `image_data_url` | string | ✅ Yes | - | Base64 encoded PNG image |
| `to_direction` | string | ✅ Yes | - | Target direction to face |
| `from_direction` | string | No | null | Current direction (helps accuracy) |
| `width` | integer | No | 64 | Output width |
| `height` | integer | No | 64 | Output height |

**Direction Options:**
- `"north"`
- `"north-east"`
- `"east"`
- `"south-east"`
- `"south"`
- `"south-west"`
- `"west"`
- `"north-west"`

### Response
```json
{
  "status": "success",
  "to_direction": "east",
  "from_direction": "south",
  "width": 64,
  "height": 64,
  "duration": 8.23,
  "image_data_url": "data:image/png;base64,iVBORw0KG...",
  "saved_path": "dashboards/generated/rotation_001.png"
}
```

### Example Test Cases

**8-Direction Sprite Sheet:**
```json
{
  "image_data_url": "...",
  "to_direction": "north",
  "from_direction": "south"
}
```

**Unknown Source Direction:**
```json
{
  "image_data_url": "...",
  "to_direction": "east"
}
```

---

## 🎬 Character Animation (Text-Based)

Create animated pixel art sequences from text descriptions.

### Endpoint
```
POST /animate-character-text
```

### Request Body
```json
{
  "description": "knight in armor",
  "action": "walking",
  "reference_image_path": "path/to/character.png",
  "n_frames": 4,
  "direction": "east",
  "view": "side",
  "width": 64,
  "height": 64,
  "text_guidance_scale": 7.5,
  "image_guidance_scale": 1.5,
  "init_image_strength": 300,
  "seed": 0
}
```

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `description` | string | ✅ Yes | - | Character description |
| `action` | string | ✅ Yes | - | Action to animate (walking, attacking, etc.) |
| `reference_image_path` | string | ✅ Yes | - | Path to reference character image |
| `n_frames` | integer | No | 4 | Number of frames (1-20) |
| `direction` | string | No | "east" | Facing direction |
| `view` | string | No | "side" | Camera view: "side", "low top-down", "high top-down" |
| `width` | integer | No | 64 | Output width |
| `height` | integer | No | 64 | Output height |
| `text_guidance_scale` | float | No | 7.5 | Text prompt adherence (1.0-20.0) |
| `image_guidance_scale` | float | No | 1.5 | Reference image adherence (1.0-20.0) |
| `init_image_strength` | integer | No | 300 | Init image strength (1-999) |
| `seed` | integer | No | 0 | Random seed (0 for random) |

### Response
```json
{
  "status": "success",
  "description": "knight in armor",
  "action": "walking",
  "n_frames": 4,
  "duration": 45.67,
  "frames": [
    "data:image/png;base64,iVBORw0KG...",
    "data:image/png;base64,iVBORw0KG...",
    "data:image/png;base64,iVBORw0KG...",
    "data:image/png;base64,iVBORw0KG..."
  ],
  "saved_paths": [
    "dashboards/generated/anim_001_frame_0.png",
    "dashboards/generated/anim_001_frame_1.png",
    "dashboards/generated/anim_001_frame_2.png",
    "dashboards/generated/anim_001_frame_3.png"
  ]
}
```

---

## 🎨 Character Inpainting

Edit specific regions of pixel art using a mask.

### Endpoint
```
POST /inpaint-character
```

### Request Body
```json
{
  "image_path": "path/to/character.png",
  "mask_path": "path/to/mask.png",
  "description": "red wizard hat",
  "width": 64,
  "height": 64
}
```

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `image_path` | string | ✅ Yes | - | Path to original image |
| `mask_path` | string | ✅ Yes | - | Path to mask (white=edit, black=keep) |
| `description` | string | ✅ Yes | - | What to paint in masked area |
| `width` | integer | No | 64 | Output width |
| `height` | integer | No | 64 | Output height |

### Response
```json
{
  "status": "success",
  "description": "red wizard hat",
  "width": 64,
  "height": 64,
  "duration": 10.23,
  "image_data_url": "data:image/png;base64,iVBORw0KG...",
  "saved_path": "dashboards/generated/inpaint_001.png"
}
```

---

## 🦴 Skeleton Estimation

Detect skeleton/pose keypoints in character images.

### Endpoint
```
POST /estimate-skeleton
```

### Request Body
```json
{
  "image_path": "path/to/character.png"
}
```

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `image_path` | string | ✅ Yes | - | Path to character image |

### Response
```json
{
  "status": "success",
  "keypoints": [
    {"label": "NOSE", "x": 32, "y": 20, "z_index": 0},
    {"label": "NECK", "x": 32, "y": 28, "z_index": 0},
    {"label": "RIGHT SHOULDER", "x": 28, "y": 30, "z_index": 0},
    ...
  ],
  "duration": 2.45
}
```

**Keypoint Labels:**
- `NOSE`, `NECK`
- `RIGHT SHOULDER`, `RIGHT ELBOW`, `RIGHT ARM`
- `LEFT SHOULDER`, `LEFT ELBOW`, `LEFT ARM`
- `RIGHT HIP`, `RIGHT KNEE`, `RIGHT LEG`
- `LEFT HIP`, `LEFT KNEE`, `LEFT LEG`
- `RIGHT EYE`, `LEFT EYE`
- `RIGHT EAR`, `LEFT EAR`

---

## 🦴 Skeleton-Based Animation

Create animations using skeleton keyframes.

### Endpoint
```
POST /animate-character-skeleton
```

### Request Body
```json
{
  "skeleton_frames": [
    {
      "keypoints": [
        {"label": "NOSE", "x": 32, "y": 20, "z_index": 0},
        ...
      ]
    }
  ],
  "reference_image_path": "path/to/character.png",
  "direction": "east",
  "view": "side",
  "width": 64,
  "height": 64,
  "pose_guidance_scale": 3.0,
  "reference_guidance_scale": 1.1,
  "init_image_strength": 300,
  "seed": 0
}
```

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `skeleton_frames` | array | ✅ Yes | - | Array of skeleton frames |
| `reference_image_path` | string | No | null | Reference character image |
| `direction` | string | No | "east" | Facing direction |
| `view` | string | No | "side" | Camera view |
| `width` | integer | No | 64 | Output width |
| `height` | integer | No | 64 | Output height |
| `pose_guidance_scale` | float | No | 3.0 | Pose adherence (1.0-20.0) |
| `reference_guidance_scale` | float | No | 1.1 | Reference adherence (1.0-20.0) |
| `init_image_strength` | integer | No | 300 | Init strength (0-1000) |
| `isometric` | boolean | No | false | Use isometric projection |
| `oblique_projection` | boolean | No | false | Use oblique projection |
| `seed` | integer | No | 0 | Random seed |

### Response
```json
{
  "status": "success",
  "n_frames": 3,
  "duration": 52.34,
  "frames": [...],
  "saved_paths": [...]
}
```

---

## ❤️ Health Check

Check server and API status.

### Endpoint
```
GET /health
```

### Response
```json
{
  "status": "ok",
  "server": "online",
  "pixellab_api": "detected",
  "timestamp": "2025-10-29T04:30:15Z"
}
```

---

## ⚠️ Error Responses

All endpoints return errors in this format:

```json
{
  "status": "error",
  "error": "Error message here",
  "details": "Additional error details"
}
```

**Common HTTP Status Codes:**
- `200 OK` - Success
- `400 Bad Request` - Invalid parameters
- `500 Internal Server Error` - Server/API error
- `503 Service Unavailable` - PixelLab API unavailable

---

## 📊 Rate Limits

PixelLab API has rate limits:
- Check with `mcp_pixellab_get_balance` for current credits
- Generation endpoints use more credits than utility endpoints
- Implement exponential backoff for retries

---

**Last Updated:** 2025-10-29
**API Version:** v2

