# PixelLab API Test Suite

Comprehensive testing framework for PixelLab API integration with detailed logging, error handling, and diagnostics.

## Quick Start

```bash
# Run the test suite
python tests/pixellab_api_test/test_pixellab_api.py
```

## Overview

This test suite provides a robust framework for testing PixelLab's AI-powered pixel art generation API. It includes:

- **Comprehensive Logging:** Multi-level logging to file and console
- **Error Handling:** Graceful handling of network, API, and filesystem errors
- **Detailed Diagnostics:** Stack traces, request/response tracking, timing data
- **Image Management:** Automated image saving and metadata tracking
- **Test Results:** JSON-formatted results for easy analysis

## Directory Structure

```
pixellab_api_test/
├── test_pixellab_api.py          # Main test script
├── outputs/                      # Generated pixel art images
├── logs/                         # Test execution logs
├── README.md                     # This file
└── DIAGNOSTIC_REPORT.md          # Latest diagnostic report
```

## Configuration

Update the API key in `test_pixellab_api.py`:

```python
API_KEY = "your-api-key-here"
```

Get your API key at [pixellab.ai](https://www.pixellab.ai/)

## Test Cases

### Current Tests

1. **simple_character_generation**
   - Generates a 64x64 pixel character
   - Tests basic API functionality
   - Validates image save workflow

2. **larger_image_generation**
   - Generates a 128x128 pixel character
   - Tests larger image handling
   - Validates scaling capabilities

### Adding New Tests

Create a new test method in the `PixelLabTester` class:

```python
def test_my_new_test(self) -> TestResult:
    """Test description."""
    test_name = "my_new_test"
    start_time = datetime.now()

    params = {
        "description": "your prompt here",
        "image_size": {"width": 64, "height": 64}
    }

    try:
        response = self.client.generate_image_pixflux(**params)
        pil_image = response.image.pil_image()

        # Save image logic...

        return TestResult(
            test_name=test_name,
            timestamp=start_time.isoformat(),
            success=True,
            duration_seconds=(datetime.now() - start_time).total_seconds(),
            # ... other fields
        )
    except Exception as e:
        # Error handling...
        pass
```

Then add it to `run_all_tests()`:

```python
test_methods = [
    self.test_simple_character,
    self.test_larger_image,
    self.test_my_new_test,  # Add here
]
```

## Output Files

### Log Files

Located in `logs/`:
- `pixellab_test_YYYYMMDD_HHMMSS.log` - Detailed execution log
- `test_summary_YYYYMMDD_HHMMSS.json` - JSON test results

### Generated Images

Located in `outputs/`:
- `{test_name}_YYYYMMDD_HHMMSS.png` - Generated pixel art

## Logging Levels

The test suite uses structured logging:

- **DEBUG:** Detailed internal operations, stack traces
- **INFO:** Test progress, API calls, image saves (default console level)
- **WARNING:** Non-fatal issues, partial failures
- **ERROR:** Test failures, API errors

View DEBUG logs in the log file, INFO+ in console.

## Test Results Format

### Console Output

```
============================================================
TEST: simple_character_generation
============================================================
Request parameters: {...}
Sending API request...
✓ API request successful
✓ Image converted - Size: (64, 64)
Saving image to: /path/to/image.png
✓ Image saved successfully
✓ TEST PASSED - Duration: 2.34s
```

### JSON Summary

```json
{
  "timestamp": "2025-10-28T18:19:27.594287",
  "total_tests": 2,
  "passed": 1,
  "failed": 1,
  "success_rate": 50.0,
  "results": [
    {
      "test_name": "simple_character_generation",
      "success": true,
      "duration_seconds": 2.34,
      "image_path": "/path/to/image.png",
      "image_size": [64, 64],
      "error_message": null
    }
  ]
}
```

## Error Handling

The test suite handles:

1. **Network Errors**
   - Connection timeouts
   - DNS failures
   - Proxy issues

2. **API Errors**
   - Authentication failures (401, 403)
   - Rate limiting (429)
   - Server errors (5xx)
   - Invalid parameters (400)

3. **Filesystem Errors**
   - Permission denied
   - Disk space
   - Invalid paths

4. **Image Processing Errors**
   - Invalid image format
   - Corrupt data
   - Conversion failures

All errors are logged with full stack traces and structured metadata.

## Troubleshooting

### HTTP 403 Forbidden

**Symptom:** All tests fail with "403 Client Error: Forbidden"

**Causes:**
1. Invalid or expired API key
2. API key not activated
3. Insufficient permissions
4. Network/proxy restrictions

**Solutions:**
1. Verify API key at [pixellab.ai](https://www.pixellab.ai/)
2. Generate a new API key
3. Check account status and tier
4. Review proxy/network settings

See `DIAGNOSTIC_REPORT.md` for detailed analysis.

### No Images Generated

**Symptom:** Tests pass but no images in `outputs/`

**Causes:**
1. Filesystem permissions
2. Disk space issues
3. Image save logic not executing

**Solutions:**
1. Check directory permissions
2. Verify disk space
3. Review logs for save operation

### Rate Limiting

**Symptom:** Tests fail after several successful runs

**Causes:**
1. API rate limits exceeded
2. Free tier restrictions

**Solutions:**
1. Add delays between tests
2. Upgrade account tier
3. Reduce test frequency

## Dependencies

Installed automatically via `pip install pixellab`:

- `pixellab` (1.0.5) - Official PixelLab Python SDK
- `pillow` (12.0.0) - Image processing
- `pydantic` (2.12.3) - Data validation
- `requests` (2.32.5) - HTTP client

## Resources

- **PixelLab Website:** https://www.pixellab.ai/
- **API Documentation:** https://api.pixellab.ai/v1/docs
- **Discord Support:** https://discord.gg/pBeyTBF8T7
- **GitHub SDK:** https://github.com/pixellab-code/pixellab-python
- **MCP Integration:** https://github.com/pixellab-code/pixellab-mcp

## License

This test suite is part of the AI-DnD project.
See the main project LICENSE for details.
