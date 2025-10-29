# PixelLab API Test Suite

Comprehensive testing infrastructure for PixelLab API endpoints with automated comparison and regression detection.

## 🎯 Purpose

This test suite provides:
- **Automated API Testing**: Run all PixelLab endpoints with known inputs
- **Baseline Comparison**: Compare outputs against known-good baselines
- **Image Comparison**: Visual diff for pixel art changes
- **Regression Detection**: Catch unexpected API behavior changes
- **Expandable Framework**: Easy to add new test cases

## 📁 Directory Structure

```
pixellab_tests/
├── README.md              # This file
├── test_cases/            # Test case definitions (JSON)
│   ├── character_generation.json
│   ├── character_rotation.json
│   ├── character_animation.json
│   └── ...
├── baselines/             # Known-good outputs (images + metadata)
│   ├── character_generation/
│   ├── character_rotation/
│   └── ...
├── results/               # Test run results
│   └── YYYY-MM-DD_HH-MM-SS/
│       ├── summary.json
│       ├── report.html
│       ├── outputs/       # Generated images
│       └── diffs/         # Visual diffs
└── docs/                  # Documentation
    ├── API_ENDPOINTS.md   # PixelLab API reference
    └── WRITING_TESTS.md   # How to write test cases
```

## 🚀 Quick Start

### 1. Run All Tests
```bash
python3 scripts/pixellab_actions.py --test-all
```

### 2. Run Specific Endpoint Tests
```bash
python3 scripts/pixellab_actions.py --test character_generation
python3 scripts/pixellab_actions.py --test character_rotation
```

### 3. Update Baselines (After Confirming Output is Correct)
```bash
python3 scripts/pixellab_actions.py --update-baseline character_generation
```

### 4. View Test Report
```bash
# Open the latest HTML report
open pixellab_tests/results/latest/report.html
```

## 📝 Test Case Format

Test cases are defined in JSON files in the `test_cases/` directory.

**Example: `test_cases/character_generation.json`**
```json
{
  "endpoint": "character_generation",
  "description": "Test character generation with various prompts",
  "test_cases": [
    {
      "id": "knight_basic",
      "name": "Basic Knight",
      "inputs": {
        "prompt": "heroic knight with sword",
        "width": 64,
        "height": 64
      },
      "expected": {
        "status": "success",
        "image_size": [64, 64],
        "min_duration": 5.0,
        "max_duration": 30.0
      },
      "baseline": "baselines/character_generation/knight_basic.png"
    },
    {
      "id": "mage_complex",
      "name": "Complex Mage",
      "inputs": {
        "prompt": "powerful mage with glowing staff, purple robes, lightning",
        "width": 128,
        "height": 128
      },
      "expected": {
        "status": "success",
        "image_size": [128, 128]
      }
    }
  ]
}
```

## 🔍 What Gets Tested

For each test case, the suite validates:

### ✅ API Response
- HTTP status code (200 OK expected)
- Response structure (contains required fields)
- Error handling (proper error messages if applicable)

### ✅ Timing
- API call duration within expected range
- No timeouts or hangs

### ✅ Image Output
- Image format (valid PNG/base64)
- Image dimensions match request
- Image file size reasonable
- Image is not blank/corrupted

### ✅ Baseline Comparison (if baseline exists)
- Visual similarity score (SSIM - Structural Similarity Index)
- Pixel difference percentage
- Histogram comparison
- Side-by-side diff visualization

### ✅ Metadata
- All expected metadata fields present
- Values within expected ranges
- Consistent with inputs

## 📊 Test Results

After each test run, you get:

1. **Console Summary**
   ```
   ================================================================================
   PIXELLAB TEST SUITE RESULTS
   ================================================================================

   Test Run: 2025-10-29 04:30:15

   Character Generation: ✅ 5/5 passed
   Character Rotation:   ✅ 4/4 passed
   Character Animation:  ⚠️  2/3 passed (1 warning)

   Total: 11/12 tests passed (91.7%)
   Duration: 2m 34s
   ```

2. **JSON Summary** (`results/YYYY-MM-DD_HH-MM-SS/summary.json`)
   - Detailed results for each test
   - Timing data
   - Comparison metrics
   - Links to outputs and diffs

3. **HTML Report** (`results/YYYY-MM-DD_HH-MM-SS/report.html`)
   - Visual test report
   - Side-by-side image comparisons
   - Diff heatmaps
   - Sortable/filterable results

## 🎨 Image Comparison Metrics

The suite uses multiple metrics to compare images:

### SSIM (Structural Similarity Index)
- Range: 0.0 (completely different) to 1.0 (identical)
- **> 0.95**: Excellent match (expected for deterministic generation)
- **0.85-0.95**: Good match (minor differences)
- **0.70-0.85**: Moderate differences (investigate)
- **< 0.70**: Significant differences (likely regression)

### Pixel Difference
- Percentage of pixels that differ
- **< 1%**: Excellent match
- **1-5%**: Minor differences
- **> 5%**: Investigate differences

### Histogram Correlation
- Color distribution similarity
- **> 0.95**: Excellent match
- **0.85-0.95**: Good match
- **< 0.85**: Different color palette

## 🔧 Adding New Tests

### 1. Create Test Case File
Create `pixellab_tests/test_cases/your_endpoint.json`:

```json
{
  "endpoint": "your_endpoint",
  "description": "Test your endpoint functionality",
  "test_cases": [
    {
      "id": "test_001",
      "name": "Descriptive Test Name",
      "inputs": {
        "param1": "value1",
        "param2": 123
      },
      "expected": {
        "status": "success"
      }
    }
  ]
}
```

### 2. Add Endpoint to Test Runner
Update `scripts/pixellab_actions.py` with your endpoint handler.

### 3. Run Test and Create Baseline
```bash
# Run test
python3 scripts/pixellab_actions.py --test your_endpoint

# If output looks good, save as baseline
python3 scripts/pixellab_actions.py --update-baseline your_endpoint
```

### 4. Test is Now Automated!
Future runs will compare against your baseline.

## 📚 PixelLab API Endpoints

See `docs/API_ENDPOINTS.md` for complete PixelLab API reference.

### Currently Tested Endpoints
- ✅ `/generate-character` - Character generation (Pixflux)
- ✅ `/rotate-character` - Character rotation
- 🔜 `/animate-character` - Character animation
- 🔜 `/inpaint-character` - Character inpainting
- 🔜 `/estimate-skeleton` - Skeleton detection

## 🐛 Troubleshooting

### Test Fails: "Baseline not found"
**Solution:** Run `--update-baseline` to create initial baseline
```bash
python3 scripts/pixellab_actions.py --update-baseline <endpoint>
```

### Test Fails: "SSIM score too low"
**Possible causes:**
1. API output changed (regression or improvement)
2. Baseline was created with different settings
3. Non-deterministic generation (use fixed seed)

**Solution:**
1. Check the diff image in results folder
2. If new output is correct, update baseline
3. If output is wrong, investigate API changes

### Test Times Out
**Possible causes:**
1. PixelLab API is slow/overloaded
2. Network issues
3. Server not running

**Solution:**
1. Check server status: `curl http://127.0.0.1:8787/health`
2. Increase timeout in test case
3. Check PixelLab API status

## 📈 Best Practices

### ✅ DO:
- Use descriptive test names and IDs
- Add comments explaining what each test validates
- Use fixed seeds for deterministic tests
- Update baselines after confirming changes are correct
- Run full test suite before major changes

### ❌ DON'T:
- Commit large baseline images without LFS
- Update baselines without verifying output
- Skip baseline comparisons for visual endpoints
- Use overly tight timing constraints
- Test with random/unpredictable inputs

## 🔐 CI/CD Integration

Add to your GitHub Actions workflow:

```yaml
- name: Run PixelLab Tests
  run: |
    python3 scripts/pixellab_actions.py --test-all

- name: Upload Test Results
  uses: actions/upload-artifact@v3
  with:
    name: pixellab-test-results
    path: pixellab_tests/results/latest/
```

## 📝 License

Same as project root (see LICENSE file).

## 🤝 Contributing

1. Add test cases for new endpoints
2. Update documentation
3. Ensure all tests pass before PR
4. Include test results in PR description

---

**Last Updated:** 2025-10-29
**Version:** 1.0.0

