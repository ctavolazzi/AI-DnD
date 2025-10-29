#!/usr/bin/env python3
"""
Comprehensive PixelLab Test Runner
Executes all PixelLab integration tests and generates structured results display
"""

import os
import sys
import json
import subprocess
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import traceback

# Add current directory to path for imports
sys.path.insert(0, '.')

# Configuration
API_KEY = os.getenv("PIXELLAB_API_KEY")
TEST_TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
RESULTS_DIR = Path(f"test_results_{TEST_TIMESTAMP}")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# Create subdirectories
IMAGES_DIR = RESULTS_DIR / "images"
ANIMATIONS_DIR = RESULTS_DIR / "animations"
LOGS_DIR = RESULTS_DIR / "logs"
REPORTS_DIR = RESULTS_DIR / "reports"

for dir_path in [IMAGES_DIR, ANIMATIONS_DIR, LOGS_DIR, REPORTS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)


@dataclass
class TestSuiteResult:
    """Results from a complete test suite."""
    suite_name: str
    timestamp: str
    total_tests: int
    passed_tests: int
    failed_tests: int
    success_rate: float
    duration_seconds: float
    generated_images: int
    generated_animations: int
    output_files: List[str]
    errors: List[str]
    test_results: List[Dict[str, Any]]


@dataclass
class ComprehensiveTestResult:
    """Overall test execution results."""
    timestamp: str
    total_suites: int
    total_tests: int
    total_passed: int
    total_failed: int
    overall_success_rate: float
    total_duration: float
    total_images_generated: int
    total_animations_generated: int
    suite_results: List[TestSuiteResult]
    api_key_status: str
    environment_status: Dict[str, Any]


class ComprehensiveTestRunner:
    """Runs all PixelLab tests and generates comprehensive results."""

    def __init__(self):
        self.setup_logging()
        self.results = []
        self.start_time = datetime.now()

    def setup_logging(self):
        """Setup comprehensive logging."""
        log_file = LOGS_DIR / f"comprehensive_test_{TEST_TIMESTAMP}.log"

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Comprehensive test runner initialized. Log: {log_file}")

    def check_environment(self) -> Dict[str, Any]:
        """Check environment and dependencies."""
        self.logger.info("Checking environment...")

        env_status = {
            "api_key_present": bool(API_KEY),
            "api_key_length": len(API_KEY) if API_KEY else 0,
            "python_version": sys.version,
            "working_directory": str(Path.cwd()),
            "results_directory": str(RESULTS_DIR)
        }

        # Check required packages
        try:
            import pixellab
            env_status["pixellab_available"] = True
            env_status["pixellab_version"] = getattr(pixellab, '__version__', 'unknown')
        except ImportError as e:
            env_status["pixellab_available"] = False
            env_status["pixellab_error"] = str(e)

        try:
            from PIL import Image
            env_status["pillow_available"] = True
        except ImportError as e:
            env_status["pillow_available"] = False
            env_status["pillow_error"] = str(e)

        self.logger.info(f"Environment check complete: {env_status}")
        return env_status

    def run_test_suite(self, suite_name: str, test_file: str, timeout: int = 300) -> TestSuiteResult:
        """Run a specific test suite and collect results."""
        self.logger.info(f"\n{'='*60}")
        self.logger.info(f"RUNNING TEST SUITE: {suite_name}")
        self.logger.info(f"{'='*60}")

        start_time = datetime.now()

        try:
            # Run the test file
            result = subprocess.run(
                [sys.executable, test_file],
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=Path.cwd()
            )

            duration = (datetime.now() - start_time).total_seconds()

            # Parse results from stdout/stderr
            stdout_lines = result.stdout.split('\n')
            stderr_lines = result.stderr.split('\n')

            # Count test results (look for PASS/FAIL patterns)
            passed_tests = len([line for line in stdout_lines if '✓' in line or 'PASS' in line])
            failed_tests = len([line for line in stdout_lines if '✗' in line or 'FAIL' in line])
            total_tests = passed_tests + failed_tests

            # If no explicit counts found, estimate from output
            if total_tests == 0:
                if result.returncode == 0:
                    passed_tests = 1
                    total_tests = 1
                else:
                    failed_tests = 1
                    total_tests = 1

            success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

            # Count generated files
            generated_images = len([line for line in stdout_lines if '.png' in line])
            generated_animations = len([line for line in stdout_lines if 'animation' in line.lower()])

            # Collect output files
            output_files = []
            for line in stdout_lines:
                if 'saved to:' in line or 'output:' in line:
                    # Extract file path
                    parts = line.split('saved to:') if 'saved to:' in line else line.split('output:')
                    if len(parts) > 1:
                        file_path = parts[1].strip()
                        output_files.append(file_path)

            # Collect errors
            errors = []
            if result.returncode != 0:
                errors.append(f"Test suite exited with code {result.returncode}")
            if stderr_lines and any(stderr_lines):
                errors.extend([line for line in stderr_lines if line.strip()])

            suite_result = TestSuiteResult(
                suite_name=suite_name,
                timestamp=start_time.isoformat(),
                total_tests=total_tests,
                passed_tests=passed_tests,
                failed_tests=failed_tests,
                success_rate=success_rate,
                duration_seconds=duration,
                generated_images=generated_images,
                generated_animations=generated_animations,
                output_files=output_files,
                errors=errors,
                test_results=[]
            )

            self.logger.info(f"✓ Suite '{suite_name}' completed")
            self.logger.info(f"  Tests: {passed_tests}/{total_tests} passed ({success_rate:.1f}%)")
            self.logger.info(f"  Duration: {duration:.2f}s")
            self.logger.info(f"  Images: {generated_images}, Animations: {generated_animations}")

            return suite_result

        except subprocess.TimeoutExpired:
            duration = (datetime.now() - start_time).total_seconds()
            self.logger.error(f"✗ Suite '{suite_name}' timed out after {timeout}s")

            return TestSuiteResult(
                suite_name=suite_name,
                timestamp=start_time.isoformat(),
                total_tests=0,
                passed_tests=0,
                failed_tests=1,
                success_rate=0.0,
                duration_seconds=duration,
                generated_images=0,
                generated_animations=0,
                output_files=[],
                errors=[f"Test suite timed out after {timeout} seconds"],
                test_results=[]
            )

        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            self.logger.error(f"✗ Suite '{suite_name}' failed: {e}")

            return TestSuiteResult(
                suite_name=suite_name,
                timestamp=start_time.isoformat(),
                total_tests=0,
                passed_tests=0,
                failed_tests=1,
                success_rate=0.0,
                duration_seconds=duration,
                generated_images=0,
                generated_animations=0,
                output_files=[],
                errors=[str(e)],
                test_results=[]
            )

    def run_all_tests(self) -> ComprehensiveTestResult:
        """Run all available test suites."""
        self.logger.info(f"\n{'#'*80}")
        self.logger.info("COMPREHENSIVE PIXELLAB TEST SUITE")
        self.logger.info(f"{'#'*80}")
        self.logger.info(f"Timestamp: {self.start_time.isoformat()}")
        self.logger.info(f"API Key: {'Present' if API_KEY else 'Missing'}")
        self.logger.info(f"Results Directory: {RESULTS_DIR}")

        # Check environment first
        env_status = self.check_environment()

        # Define test suites to run
        test_suites = [
            ("API Integration Tests", "tests/pixellab_api_test/test_pixellab_api.py"),
            ("Map Generation Tests", "tests/pixellab_map_test/test_map_generation.py"),
            ("Basic Character Generation", "pixellab_integration/examples/01_basic_character_generation.py"),
            ("Character Animation", "pixellab_integration/examples/02_character_animation.py"),
        ]

        # Add any standalone test files found
        standalone_tests = [
            "test_pixellab_api.py",
            "test_pixellab_final.py",
            "test_pixellab_animation_complete_final.py",
            "test_pixellab_mcp_features.py"
        ]

        for test_file in standalone_tests:
            if Path(test_file).exists():
                test_suites.append((f"Standalone Test: {test_file}", test_file))

        # Run each test suite
        suite_results = []
        for suite_name, test_file in test_suites:
            if Path(test_file).exists():
                suite_result = self.run_test_suite(suite_name, test_file)
                suite_results.append(suite_result)
            else:
                self.logger.warning(f"Test file not found: {test_file}")

        # Calculate overall results
        total_duration = (datetime.now() - self.start_time).total_seconds()
        total_tests = sum(sr.total_tests for sr in suite_results)
        total_passed = sum(sr.passed_tests for sr in suite_results)
        total_failed = sum(sr.failed_tests for sr in suite_results)
        total_images = sum(sr.generated_images for sr in suite_results)
        total_animations = sum(sr.generated_animations for sr in suite_results)

        overall_success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0

        comprehensive_result = ComprehensiveTestResult(
            timestamp=self.start_time.isoformat(),
            total_suites=len(suite_results),
            total_tests=total_tests,
            total_passed=total_passed,
            total_failed=total_failed,
            overall_success_rate=overall_success_rate,
            total_duration=total_duration,
            total_images_generated=total_images,
            total_animations_generated=total_animations,
            suite_results=suite_results,
            api_key_status="Present" if API_KEY else "Missing",
            environment_status=env_status
        )

        # Generate reports
        self.generate_reports(comprehensive_result)

        return comprehensive_result

    def generate_reports(self, result: ComprehensiveTestResult):
        """Generate comprehensive test reports."""
        self.logger.info(f"\n{'#'*60}")
        self.logger.info("GENERATING REPORTS")
        self.logger.info(f"{'#'*60}")

        # JSON Report
        json_file = REPORTS_DIR / f"comprehensive_test_results_{TEST_TIMESTAMP}.json"
        with open(json_file, 'w') as f:
            json.dump(asdict(result), f, indent=2)
        self.logger.info(f"✓ JSON report saved: {json_file}")

        # HTML Report
        html_file = REPORTS_DIR / f"test_results_{TEST_TIMESTAMP}.html"
        self.generate_html_report(result, html_file)
        self.logger.info(f"✓ HTML report saved: {html_file}")

        # Summary Report
        summary_file = REPORTS_DIR / f"test_summary_{TEST_TIMESTAMP}.txt"
        self.generate_summary_report(result, summary_file)
        self.logger.info(f"✓ Summary report saved: {summary_file}")

        # Copy generated images to results directory
        self.copy_generated_content()

    def generate_html_report(self, result: ComprehensiveTestResult, html_file: Path):
        """Generate comprehensive HTML test report."""
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PixelLab Comprehensive Test Results - {TEST_TIMESTAMP}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }}
        .header .timestamp {{
            opacity: 0.8;
            margin-top: 10px;
        }}
        .summary {{
            padding: 30px;
            background: #f8f9fa;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .stat-number {{
            font-size: 2em;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        .stat-label {{
            color: #666;
            font-size: 0.9em;
        }}
        .success {{ color: #27ae60; }}
        .warning {{ color: #f39c12; }}
        .error {{ color: #e74c3c; }}
        .suite-section {{
            padding: 30px;
        }}
        .suite-card {{
            background: white;
            border: 1px solid #ddd;
            border-radius: 8px;
            margin: 20px 0;
            overflow: hidden;
        }}
        .suite-header {{
            background: #f8f9fa;
            padding: 15px 20px;
            border-bottom: 1px solid #ddd;
            font-weight: bold;
        }}
        .suite-content {{
            padding: 20px;
        }}
        .suite-stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin: 15px 0;
        }}
        .suite-stat {{
            text-align: center;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 5px;
        }}
        .images-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        .image-card {{
            border: 1px solid #ddd;
            border-radius: 8px;
            overflow: hidden;
            background: white;
        }}
        .image-card img {{
            width: 100%;
            height: 150px;
            object-fit: cover;
        }}
        .image-info {{
            padding: 10px;
            font-size: 0.9em;
        }}
        .error-section {{
            background: #fdf2f2;
            border: 1px solid #fecaca;
            border-radius: 8px;
            padding: 15px;
            margin: 15px 0;
        }}
        .error-section h4 {{
            color: #dc2626;
            margin: 0 0 10px 0;
        }}
        .footer {{
            background: #2c3e50;
            color: white;
            padding: 20px;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎨 PixelLab Comprehensive Test Results</h1>
            <div class="timestamp">{result.timestamp}</div>
        </div>

        <div class="summary">
            <h2>📊 Test Summary</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number success">{result.total_passed}</div>
                    <div class="stat-label">Tests Passed</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number error">{result.total_failed}</div>
                    <div class="stat-label">Tests Failed</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{result.overall_success_rate:.1f}%</div>
                    <div class="stat-label">Success Rate</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{result.total_images_generated}</div>
                    <div class="stat-label">Images Generated</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{result.total_animations_generated}</div>
                    <div class="stat-label">Animations Generated</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{result.total_duration:.1f}s</div>
                    <div class="stat-label">Total Duration</div>
                </div>
            </div>

            <div class="stat-card">
                <h3>🔑 API Key Status</h3>
                <p><strong>{result.api_key_status}</strong></p>
                <p>Environment: {result.environment_status.get('api_key_length', 0)} characters</p>
            </div>
        </div>

        <div class="suite-section">
            <h2>🧪 Test Suite Results</h2>
"""

        # Add suite results
        for suite in result.suite_results:
            status_class = "success" if suite.failed_tests == 0 else "error"
            html_content += f"""
            <div class="suite-card">
                <div class="suite-header">
                    <span class="{status_class}">{'✓' if suite.failed_tests == 0 else '✗'}</span>
                    {suite.suite_name}
                </div>
                <div class="suite-content">
                    <div class="suite-stats">
                        <div class="suite-stat">
                            <div class="stat-number">{suite.passed_tests}/{suite.total_tests}</div>
                            <div class="stat-label">Tests</div>
                        </div>
                        <div class="suite-stat">
                            <div class="stat-number">{suite.success_rate:.1f}%</div>
                            <div class="stat-label">Success Rate</div>
                        </div>
                        <div class="suite-stat">
                            <div class="stat-number">{suite.duration_seconds:.1f}s</div>
                            <div class="stat-label">Duration</div>
                        </div>
                        <div class="suite-stat">
                            <div class="stat-number">{suite.generated_images}</div>
                            <div class="stat-label">Images</div>
                        </div>
                        <div class="suite-stat">
                            <div class="stat-number">{suite.generated_animations}</div>
                            <div class="stat-label">Animations</div>
                        </div>
                    </div>
"""

            # Add errors if any
            if suite.errors:
                html_content += f"""
                    <div class="error-section">
                        <h4>⚠️ Errors</h4>
                        <ul>
"""
                for error in suite.errors:
                    html_content += f"<li>{error}</li>"
                html_content += """
                        </ul>
                    </div>
"""

            # Add output files
            if suite.output_files:
                html_content += f"""
                    <h4>📁 Generated Files</h4>
                    <ul>
"""
                for file_path in suite.output_files:
                    html_content += f"<li>{file_path}</li>"
                html_content += """
                    </ul>
"""

            html_content += """
                </div>
            </div>
"""

        html_content += f"""
        </div>

        <div class="footer">
            <p>Generated by Comprehensive PixelLab Test Runner</p>
            <p>Results saved in: {RESULTS_DIR}</p>
        </div>
    </div>
</body>
</html>
"""

        with open(html_file, 'w') as f:
            f.write(html_content)

    def generate_summary_report(self, result: ComprehensiveTestResult, summary_file: Path):
        """Generate text summary report."""
        with open(summary_file, 'w') as f:
            f.write(f"PIXELLAB COMPREHENSIVE TEST RESULTS\n")
            f.write(f"{'='*50}\n")
            f.write(f"Timestamp: {result.timestamp}\n")
            f.write(f"Total Duration: {result.total_duration:.2f} seconds\n")
            f.write(f"API Key: {result.api_key_status}\n\n")

            f.write(f"OVERALL RESULTS:\n")
            f.write(f"  Total Suites: {result.total_suites}\n")
            f.write(f"  Total Tests: {result.total_tests}\n")
            f.write(f"  Passed: {result.total_passed}\n")
            f.write(f"  Failed: {result.total_failed}\n")
            f.write(f"  Success Rate: {result.overall_success_rate:.1f}%\n")
            f.write(f"  Images Generated: {result.total_images_generated}\n")
            f.write(f"  Animations Generated: {result.total_animations_generated}\n\n")

            f.write(f"SUITE DETAILS:\n")
            for suite in result.suite_results:
                f.write(f"  {suite.suite_name}:\n")
                f.write(f"    Tests: {suite.passed_tests}/{suite.total_tests} passed\n")
                f.write(f"    Duration: {suite.duration_seconds:.2f}s\n")
                f.write(f"    Images: {suite.generated_images}\n")
                f.write(f"    Animations: {suite.generated_animations}\n")
                if suite.errors:
                    f.write(f"    Errors: {len(suite.errors)}\n")
                f.write(f"\n")

    def copy_generated_content(self):
        """Copy generated images and animations to results directory."""
        self.logger.info("Copying generated content to results directory...")

        # Copy from various output directories
        source_dirs = [
            "pixellab_integration/outputs",
            "tests/pixellab_api_test/outputs",
            "tests/pixellab_map_test/map_outputs",
            "game_assets"
        ]

        copied_files = 0
        for source_dir in source_dirs:
            source_path = Path(source_dir)
            if source_path.exists():
                for file_path in source_path.rglob("*.png"):
                    try:
                        # Create relative path in results
                        rel_path = file_path.relative_to(source_path)
                        dest_path = IMAGES_DIR / rel_path
                        dest_path.parent.mkdir(parents=True, exist_ok=True)

                        # Copy file
                        import shutil
                        shutil.copy2(file_path, dest_path)
                        copied_files += 1
                    except Exception as e:
                        self.logger.warning(f"Failed to copy {file_path}: {e}")

        self.logger.info(f"✓ Copied {copied_files} files to results directory")


def main():
    """Main entry point."""
    print(f"\n{'='*80}")
    print("COMPREHENSIVE PIXELLAB TEST RUNNER")
    print(f"{'='*80}")
    print(f"Timestamp: {TEST_TIMESTAMP}")
    print(f"API Key: {'Present' if API_KEY else 'Missing'}")
    print(f"Results Directory: {RESULTS_DIR}")
    print(f"{'='*80}\n")

    if not API_KEY:
        print("⚠️  WARNING: PIXELLAB_API_KEY environment variable not set")
        print("   Some tests may fail without a valid API key")
        print("   Get your key at: https://www.pixellab.ai/vibe-coding")
        print()

    runner = ComprehensiveTestRunner()
    result = runner.run_all_tests()

    print(f"\n{'='*80}")
    print("TEST EXECUTION COMPLETE")
    print(f"{'='*80}")
    print(f"Total Suites: {result.total_suites}")
    print(f"Total Tests: {result.total_tests}")
    print(f"Passed: {result.total_passed}")
    print(f"Failed: {result.total_failed}")
    print(f"Success Rate: {result.overall_success_rate:.1f}%")
    print(f"Images Generated: {result.total_images_generated}")
    print(f"Animations Generated: {result.total_animations_generated}")
    print(f"Total Duration: {result.total_duration:.2f}s")
    print(f"\nResults saved in: {RESULTS_DIR}")
    print(f"HTML Report: {RESULTS_DIR}/reports/test_results_{TEST_TIMESTAMP}.html")
    print(f"{'='*80}\n")

    if result.total_failed == 0:
        print("🎉 ALL TESTS PASSED!")
    else:
        print(f"⚠️  {result.total_failed} TEST(S) FAILED")

    return result


if __name__ == "__main__":
    main()
