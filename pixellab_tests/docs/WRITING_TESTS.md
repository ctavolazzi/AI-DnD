# Writing Test Cases

Guide for creating comprehensive test cases for PixelLab API endpoints.

## 📋 Test Case Structure

All test cases are defined in JSON files in the `test_cases/` directory.

### Basic Template

```json
{
  "endpoint": "endpoint_name",
  "description": "What this test suite validates",
  "test_cases": [
    {
      "id": "unique_test_id",
      "name": "Human-readable test name",
      "inputs": {
        // API parameters
      },
      "expected": {
        // Validation criteria
      },
      "baseline": "path/to/baseline/image.png"
    }
  ]
}
```

## 🎯 Test Case Components

### 1. Test Suite Metadata

```json
{
  "endpoint": "character_generation",
  "description": "Test character generation with various prompts and settings"
}
```

- **`endpoint`**: Name of the API endpoint being tested
- **`description`**: Overview of what this test suite covers

### 2. Individual Test Case

Each test case has 4 main sections:

#### a) Identification
```json
{
  "id": "knight_basic",
  "name": "Basic Knight - 64x64"
}
```

- **`id`**: Unique identifier (snake_case, no spaces)
- **`name`**: Human-readable description

#### b) Inputs
```json
{
  "inputs": {
    "prompt": "heroic knight with sword",
    "width": 64,
    "height": 64,
    "seed": 12345
  }
}
```

Parameters to send to the API endpoint.

**Best Practices:**
- ✅ Use fixed `seed` for deterministic results
- ✅ Test edge cases (min/max dimensions)
- ✅ Test different parameter combinations
- ✅ Include negative test cases (invalid inputs)

#### c) Expected Results
```json
{
  "expected": {
    "status": "success",
    "image_size": [64, 64],
    "min_duration": 5.0,
    "max_duration": 30.0,
    "has_transparency": false
  }
}
```

Criteria for test to pass.

**Common Expectations:**

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | Expected status: "success" or "error" |
| `image_size` | array | Expected `[width, height]` |
| `min_duration` | float | Minimum acceptable duration (seconds) |
| `max_duration` | float | Maximum acceptable duration (seconds) |
| `has_transparency` | boolean | Should image have alpha channel? |
| `min_file_size` | integer | Minimum file size (bytes) |
| `max_file_size` | integer | Maximum file size (bytes) |
| `error_message` | string | Expected error message (for negative tests) |

#### d) Baseline
```json
{
  "baseline": "baselines/character_generation/knight_basic.png"
}
```

Path to known-good output for comparison.

**Baseline Workflow:**
1. Run test without baseline (will fail)
2. Manually verify output is correct
3. Update baseline with correct output
4. Future runs compare against this baseline

## 📝 Test Case Examples

### Example 1: Simple Generation Test

```json
{
  "id": "simple_warrior",
  "name": "Simple Warrior",
  "inputs": {
    "prompt": "warrior with sword",
    "width": 64,
    "height": 64,
    "seed": 12345
  },
  "expected": {
    "status": "success",
    "image_size": [64, 64]
  },
  "baseline": "baselines/character_generation/simple_warrior.png"
}
```

### Example 2: Detailed Test with Multiple Validations

```json
{
  "id": "detailed_mage",
  "name": "Highly Detailed Mage",
  "inputs": {
    "prompt": "powerful mage with glowing staff, purple robes",
    "width": 128,
    "height": 128,
    "detail": "highly detailed",
    "shading": "detailed shading",
    "seed": 67890
  },
  "expected": {
    "status": "success",
    "image_size": [128, 128],
    "min_duration": 10.0,
    "max_duration": 45.0,
    "min_file_size": 2000,
    "max_file_size": 50000
  },
  "baseline": "baselines/character_generation/detailed_mage.png"
}
```

### Example 3: Negative Test (Expected Error)

```json
{
  "id": "invalid_dimensions",
  "name": "Invalid Image Dimensions",
  "inputs": {
    "prompt": "knight",
    "width": 999,
    "height": 999
  },
  "expected": {
    "status": "error",
    "error_message": "Invalid dimensions"
  }
}
```

### Example 4: Edge Case Test

```json
{
  "id": "minimum_size",
  "name": "Minimum Image Size (32x32)",
  "inputs": {
    "prompt": "tiny sprite",
    "width": 32,
    "height": 32,
    "seed": 11111
  },
  "expected": {
    "status": "success",
    "image_size": [32, 32],
    "max_duration": 15.0
  },
  "baseline": "baselines/character_generation/minimum_size.png"
}
```

### Example 5: Rotation Test

```json
{
  "id": "knight_8dir",
  "name": "Knight - All 8 Directions",
  "inputs": {
    "base_character": {
      "prompt": "knight with sword",
      "width": 64,
      "height": 64,
      "seed": 12345
    },
    "rotations": [
      {"to_direction": "north"},
      {"to_direction": "north-east"},
      {"to_direction": "east"},
      {"to_direction": "south-east"},
      {"to_direction": "south"},
      {"to_direction": "south-west"},
      {"to_direction": "west"},
      {"to_direction": "north-west"}
    ]
  },
  "expected": {
    "status": "success",
    "image_size": [64, 64],
    "sprite_sheet": true
  },
  "baseline": "baselines/character_rotation/knight_8dir/"
}
```

## 🎨 Image Comparison Thresholds

When creating baselines, understand the comparison metrics:

### SSIM (Structural Similarity Index)

```json
{
  "expected": {
    "min_ssim": 0.95,  // 0.0 to 1.0
    "max_pixel_diff": 0.01  // 1% of pixels
  }
}
```

**Recommended Thresholds:**

| Use Case | min_ssim | max_pixel_diff |
|----------|----------|----------------|
| Deterministic (fixed seed) | 0.99 | 0.001 (0.1%) |
| Mostly deterministic | 0.95 | 0.01 (1%) |
| Some randomness | 0.85 | 0.05 (5%) |
| Visual similarity only | 0.70 | 0.10 (10%) |

## 🔧 Advanced Test Patterns

### Pattern 1: Parametric Testing

Test multiple variations of the same concept:

```json
{
  "test_cases": [
    {
      "id": "knight_size_32",
      "inputs": {"prompt": "knight", "width": 32, "height": 32, "seed": 123}
    },
    {
      "id": "knight_size_64",
      "inputs": {"prompt": "knight", "width": 64, "height": 64, "seed": 123}
    },
    {
      "id": "knight_size_128",
      "inputs": {"prompt": "knight", "width": 128, "height": 128, "seed": 123}
    }
  ]
}
```

### Pattern 2: Style Variations

Test different visual styles:

```json
{
  "test_cases": [
    {
      "id": "warrior_flat",
      "inputs": {"prompt": "warrior", "shading": "flat shading", "seed": 123}
    },
    {
      "id": "warrior_basic",
      "inputs": {"prompt": "warrior", "shading": "basic shading", "seed": 123}
    },
    {
      "id": "warrior_detailed",
      "inputs": {"prompt": "warrior", "shading": "detailed shading", "seed": 123}
    }
  ]
}
```

### Pattern 3: Negative Prompt Testing

Test that negative prompts work:

```json
{
  "id": "simple_vs_complex",
  "inputs": {
    "prompt": "warrior",
    "negative_description": "complex, detailed, ornate",
    "seed": 123
  },
  "expected": {
    "status": "success",
    "max_file_size": 5000  // Should be simpler/smaller
  }
}
```

### Pattern 4: Multi-Step Tests

Tests that require multiple API calls:

```json
{
  "id": "generate_and_rotate",
  "steps": [
    {
      "endpoint": "character_generation",
      "inputs": {"prompt": "knight", "seed": 123},
      "save_output_as": "base_character"
    },
    {
      "endpoint": "character_rotation",
      "inputs": {
        "image_data_url": "{{base_character}}",
        "to_direction": "east"
      }
    }
  ]
}
```

## ✅ Test Quality Checklist

Before committing test cases, ensure:

### Coverage
- [ ] Tests cover happy path (normal usage)
- [ ] Tests cover edge cases (min/max values)
- [ ] Tests cover error cases (invalid inputs)
- [ ] Tests cover different parameter combinations

### Determinism
- [ ] Uses fixed seeds where possible
- [ ] Comparison thresholds are appropriate
- [ ] No dependency on external randomness

### Documentation
- [ ] Test ID is unique and descriptive
- [ ] Test name explains what's being tested
- [ ] Description explains the test suite's purpose
- [ ] Baseline path is correct

### Baselines
- [ ] Baseline images are committed (or .gitignored if too large)
- [ ] Baselines are verified correct manually
- [ ] Baseline paths follow naming convention

### Performance
- [ ] Duration expectations are realistic
- [ ] File size expectations are appropriate
- [ ] Tests don't take unnecessarily long

## 🚀 Running Your Tests

After creating test cases:

### 1. Run Test Suite
```bash
python3 scripts/pixellab_actions.py --test character_generation
```

### 2. Review Results
```bash
# View HTML report
open pixellab_tests/results/latest/report.html

# View JSON summary
cat pixellab_tests/results/latest/summary.json | jq
```

### 3. Update Baselines (if needed)
```bash
python3 scripts/pixellab_actions.py --update-baseline character_generation
```

## 📚 Further Reading

- [API_ENDPOINTS.md](API_ENDPOINTS.md) - Complete API reference
- [../README.md](../README.md) - Test suite overview
- PixelLab API Docs: https://api.pixellab.ai/v2/llms.txt

---

**Last Updated:** 2025-10-29

