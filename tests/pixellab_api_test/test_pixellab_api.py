#!/usr/bin/env python3
"""
PixelLab API Test Suite
Comprehensive testing of PixelLab API integration with detailed logging and error handling.
"""

import logging
import os
import sys
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
import traceback

import pixellab
from PIL import Image


# Configuration
API_KEY = os.getenv("PIXELLAB_API_KEY")
if not API_KEY:
    raise ValueError(
        "PIXELLAB_API_KEY environment variable not set.\n"
        "Get your API key from https://www.pixellab.ai/vibe-coding\n"
        "Then set it: export PIXELLAB_API_KEY=your-api-key"
    )
TEST_DIR = Path(__file__).parent
OUTPUTS_DIR = TEST_DIR / "outputs"
LOGS_DIR = TEST_DIR / "logs"


@dataclass
class TestResult:
    """Data structure to track test execution results."""
    test_name: str
    timestamp: str
    success: bool
    duration_seconds: float
    error_message: Optional[str] = None
    error_type: Optional[str] = None
    error_traceback: Optional[str] = None
    request_params: Optional[Dict[str, Any]] = None
    response_data: Optional[Dict[str, Any]] = None
    image_path: Optional[str] = None
    image_size: Optional[tuple] = None
    image_format: Optional[str] = None


class PixelLabTester:
    """Comprehensive PixelLab API testing framework."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = None
        self.test_results = []
        self.setup_logging()

    def setup_logging(self):
        """Configure comprehensive logging to file and console."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = LOGS_DIR / f"pixellab_test_{timestamp}.log"

        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )

        # File handler (detailed)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)

        # Console handler (less verbose)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(console_formatter)

        # Configure root logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

        self.logger.info(f"Logging initialized. Log file: {log_file}")

    def initialize_client(self) -> bool:
        """Initialize PixelLab API client with error handling."""
        self.logger.info("Initializing PixelLab API client...")

        try:
            self.client = pixellab.Client(secret=self.api_key)
            self.logger.info("✓ Client initialized successfully")
            return True

        except Exception as e:
            self.logger.error(f"✗ Client initialization failed: {e}")
            self.logger.debug(f"Traceback: {traceback.format_exc()}")
            return False

    def test_simple_character(self) -> TestResult:
        """Test simple character generation."""
        test_name = "simple_character_generation"
        self.logger.info(f"\n{'='*60}")
        self.logger.info(f"TEST: {test_name}")
        self.logger.info(f"{'='*60}")

        start_time = datetime.now()

        # Request parameters
        params = {
            "description": "fantasy wizard with blue robes",
            "image_size": {"width": 64, "height": 64}
        }

        self.logger.info(f"Request parameters: {json.dumps(params, indent=2)}")

        try:
            # Make API request
            self.logger.info("Sending API request...")
            response = self.client.generate_image_pixflux(**params)

            self.logger.info("✓ API request successful")
            self.logger.debug(f"Response type: {type(response)}")

            # Convert to PIL Image
            self.logger.info("Converting response to PIL Image...")
            pil_image = response.image.pil_image()
            self.logger.info(f"✓ Image converted - Size: {pil_image.size}, Format: {pil_image.format}, Mode: {pil_image.mode}")

            # Save image
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            image_filename = f"{test_name}_{timestamp}.png"
            image_path = OUTPUTS_DIR / image_filename

            self.logger.info(f"Saving image to: {image_path}")
            pil_image.save(image_path, "PNG")
            self.logger.info(f"✓ Image saved successfully")

            # Calculate duration
            duration = (datetime.now() - start_time).total_seconds()

            # Create result
            result = TestResult(
                test_name=test_name,
                timestamp=start_time.isoformat(),
                success=True,
                duration_seconds=duration,
                request_params=params,
                response_data={"response_type": str(type(response))},
                image_path=str(image_path),
                image_size=pil_image.size,
                image_format=pil_image.format
            )

            self.logger.info(f"✓ TEST PASSED - Duration: {duration:.2f}s")
            return result

        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            error_trace = traceback.format_exc()

            self.logger.error(f"✗ TEST FAILED: {e}")
            self.logger.error(f"Error type: {type(e).__name__}")
            self.logger.debug(f"Traceback:\n{error_trace}")

            result = TestResult(
                test_name=test_name,
                timestamp=start_time.isoformat(),
                success=False,
                duration_seconds=duration,
                error_message=str(e),
                error_type=type(e).__name__,
                error_traceback=error_trace,
                request_params=params
            )

            return result

    def test_larger_image(self) -> TestResult:
        """Test generating a larger image."""
        test_name = "larger_image_generation"
        self.logger.info(f"\n{'='*60}")
        self.logger.info(f"TEST: {test_name}")
        self.logger.info(f"{'='*60}")

        start_time = datetime.now()

        params = {
            "description": "medieval knight with sword and shield",
            "image_size": {"width": 128, "height": 128}
        }

        self.logger.info(f"Request parameters: {json.dumps(params, indent=2)}")

        try:
            self.logger.info("Sending API request...")
            response = self.client.generate_image_pixflux(**params)

            self.logger.info("✓ API request successful")

            pil_image = response.image.pil_image()
            self.logger.info(f"✓ Image converted - Size: {pil_image.size}, Format: {pil_image.format}, Mode: {pil_image.mode}")

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            image_filename = f"{test_name}_{timestamp}.png"
            image_path = OUTPUTS_DIR / image_filename

            self.logger.info(f"Saving image to: {image_path}")
            pil_image.save(image_path, "PNG")
            self.logger.info(f"✓ Image saved successfully")

            duration = (datetime.now() - start_time).total_seconds()

            result = TestResult(
                test_name=test_name,
                timestamp=start_time.isoformat(),
                success=True,
                duration_seconds=duration,
                request_params=params,
                response_data={"response_type": str(type(response))},
                image_path=str(image_path),
                image_size=pil_image.size,
                image_format=pil_image.format
            )

            self.logger.info(f"✓ TEST PASSED - Duration: {duration:.2f}s")
            return result

        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            error_trace = traceback.format_exc()

            self.logger.error(f"✗ TEST FAILED: {e}")
            self.logger.error(f"Error type: {type(e).__name__}")
            self.logger.debug(f"Traceback:\n{error_trace}")

            result = TestResult(
                test_name=test_name,
                timestamp=start_time.isoformat(),
                success=False,
                duration_seconds=duration,
                error_message=str(e),
                error_type=type(e).__name__,
                error_traceback=error_trace,
                request_params=params
            )

            return result

    def run_all_tests(self):
        """Execute all test cases."""
        self.logger.info(f"\n{'#'*60}")
        self.logger.info("PIXELLAB API TEST SUITE")
        self.logger.info(f"{'#'*60}\n")
        self.logger.info(f"Timestamp: {datetime.now().isoformat()}")
        self.logger.info(f"API Key: {self.api_key[:10]}...{self.api_key[-10:]}")
        self.logger.info(f"Output Directory: {OUTPUTS_DIR}")
        self.logger.info(f"Logs Directory: {LOGS_DIR}")

        # Initialize client
        if not self.initialize_client():
            self.logger.error("Cannot proceed without initialized client. Aborting tests.")
            return

        # Run tests
        test_methods = [
            self.test_simple_character,
            self.test_larger_image,
        ]

        for test_method in test_methods:
            result = test_method()
            self.test_results.append(result)

        # Generate summary
        self.generate_summary()

    def generate_summary(self):
        """Generate and save test summary."""
        self.logger.info(f"\n{'#'*60}")
        self.logger.info("TEST SUMMARY")
        self.logger.info(f"{'#'*60}\n")

        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r.success)
        failed_tests = total_tests - passed_tests

        self.logger.info(f"Total Tests: {total_tests}")
        self.logger.info(f"Passed: {passed_tests}")
        self.logger.info(f"Failed: {failed_tests}")
        self.logger.info(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")

        # Detailed results
        self.logger.info(f"\nDetailed Results:")
        for i, result in enumerate(self.test_results, 1):
            status = "✓ PASS" if result.success else "✗ FAIL"
            self.logger.info(f"\n{i}. {result.test_name}")
            self.logger.info(f"   Status: {status}")
            self.logger.info(f"   Duration: {result.duration_seconds:.2f}s")

            if result.success:
                self.logger.info(f"   Image: {result.image_path}")
                self.logger.info(f"   Size: {result.image_size}")
            else:
                self.logger.info(f"   Error: {result.error_type}: {result.error_message}")

        # Save summary to JSON
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        summary_file = LOGS_DIR / f"test_summary_{timestamp}.json"

        summary_data = {
            "timestamp": datetime.now().isoformat(),
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "success_rate": passed_tests/total_tests*100 if total_tests > 0 else 0,
            "results": [asdict(r) for r in self.test_results]
        }

        with open(summary_file, 'w') as f:
            json.dump(summary_data, f, indent=2)

        self.logger.info(f"\nTest summary saved to: {summary_file}")

        # Final status
        if failed_tests == 0:
            self.logger.info("\n🎉 ALL TESTS PASSED!")
        else:
            self.logger.warning(f"\n⚠️  {failed_tests} TEST(S) FAILED")


def main():
    """Main entry point."""
    tester = PixelLabTester(api_key=API_KEY)
    tester.run_all_tests()


if __name__ == "__main__":
    main()
