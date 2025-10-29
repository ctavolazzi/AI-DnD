#!/usr/bin/env python3
"""
PixelLab Actions Server & CLI Utilities

This script exposes a simple interface for triggering PixelLab workflows from the
PixelLab Command Center dashboard. It supports two usage modes:

1. CLI: Run a single action and print the JSON response to stdout.
   Example:
       python3 scripts/pixellab_actions.py generate-character \
           --prompt "mystic archer" --width 64 --height 64

2. Server: Start a lightweight HTTP server that the dashboard can talk to.
   Example:
       python3 scripts/pixellab_actions.py --serve
   Then open dashboards/pixellab_dashboard.html and click the run button.
"""

from __future__ import annotations

import argparse
import base64
import io
import json
import os
import sys
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any, Dict, Optional

try:
    from PIL import Image
except ImportError as exc:  # pragma: no cover
    raise SystemExit("Pillow is required. Install with `pip install Pillow`") from exc

try:
    from dotenv import load_dotenv
except ImportError as exc:  # pragma: no cover
    raise SystemExit("python-dotenv is required. Install with `pip install python-dotenv`." ) from exc

# ----------------------------------------------------------------------------
# Path setup & environment loading
# ----------------------------------------------------------------------------
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

ENV_PATH = ROOT_DIR / ".env"
if ENV_PATH.exists():
    load_dotenv(ENV_PATH)
else:
    load_dotenv()  # fallback to default lookup

PIXELLAB_API_KEY = os.getenv("PIXELLAB_API_KEY")

from pixellab_integration.pixellab_client import PixelLabClient  # noqa: E402

OUTPUT_ROOT = ROOT_DIR / "dashboards" / "generated"
OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)

JOB_HISTORY_FILE = ROOT_DIR / "dashboards" / "job_history.json"

SERVER_STARTED = time.time()


@dataclass
class ActionResult:
    status: str
    prompt: str
    width: int
    height: int
    duration: float
    timestamp: str
    image_path: str | None = None
    image_data_url: str | None = None
    seed: Optional[str] = None
    error_message: str | None = None

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False)


# ----------------------------------------------------------------------------
# Core action implementations
# ----------------------------------------------------------------------------

def _require_api_key() -> None:
    if not PIXELLAB_API_KEY:
        raise RuntimeError(
            "PIXELLAB_API_KEY is not set. Update your .env file or export the variable."
        )


def _slugify(text: str) -> str:
    return "".join(ch if ch.isalnum() or ch in ("-", "_") else "_" for ch in text.lower()).strip("_")


def _get_client(auto_save: bool = False) -> PixelLabClient:
    _require_api_key()
    return PixelLabClient(api_key=PIXELLAB_API_KEY, auto_save=auto_save)


def _balance_payload() -> Dict[str, Any]:
    if not PIXELLAB_API_KEY:
        return {"status": "missing"}

    try:
        client = _get_client(auto_save=False)
        balance = client.get_balance()
        return {
            "status": "ok",
            "usd": balance.get("usd"),
            "type": balance.get("type"),
        }
    except Exception as exc:  # pragma: no cover
        return {"status": "error", "message": str(exc)}


def load_job_history() -> Dict[str, Any]:
    """Load job history from JSON file."""
    try:
        if not JOB_HISTORY_FILE.exists():
            return {
                "status": "ok",
                "jobs": [],
                "lastJobId": 1,
                "message": "No history file found"
            }

        with open(JOB_HISTORY_FILE, "r") as f:
            data = json.load(f)

        return {
            "status": "ok",
            "jobs": data.get("jobs", []),
            "lastJobId": data.get("lastJobId", 1),
            "savedAt": data.get("savedAt"),
            "message": f"Loaded {len(data.get('jobs', []))} jobs"
        }
    except Exception as exc:
        return {
            "status": "error",
            "message": str(exc),
            "jobs": [],
            "lastJobId": 1
        }


def save_job_history(jobs: list, last_job_id: int) -> Dict[str, Any]:
    """Save job history to JSON file."""
    try:
        data = {
            "jobs": jobs,
            "lastJobId": last_job_id,
            "savedAt": datetime.utcnow().isoformat(),
            "version": "1.0"
        }

        # Create backup if file exists
        if JOB_HISTORY_FILE.exists():
            backup_path = JOB_HISTORY_FILE.with_suffix(".json.backup")
            import shutil
            shutil.copy2(JOB_HISTORY_FILE, backup_path)

        # Write new data
        with open(JOB_HISTORY_FILE, "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return {
            "status": "ok",
            "message": f"Saved {len(jobs)} jobs",
            "savedAt": data["savedAt"],
            "fileSize": JOB_HISTORY_FILE.stat().st_size
        }
    except Exception as exc:
        return {
            "status": "error",
            "message": str(exc)
        }


def generate_character_action(
    prompt: str,
    width: int = 64,
    height: int = 64,
    seed: Optional[str] = None,
) -> ActionResult:
    _require_api_key()

    if width <= 0 or height <= 0:
        raise ValueError("Width and height must be positive integers")

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    run_dir = OUTPUT_ROOT / timestamp
    run_dir.mkdir(parents=True, exist_ok=True)

    client = _get_client(auto_save=False)

    started = time.perf_counter()
    image = client.generate_character(
        description=prompt,
        width=width,
        height=height,
        seed=seed if seed else None,
        no_background=True,
    )
    duration = time.perf_counter() - started

    filename = f"pixflux_{_slugify(prompt)[:40]}_{timestamp}.png"
    file_path = run_dir / filename
    image.save(file_path, "PNG")

    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    data_url = "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode("utf-8")

    return ActionResult(
        status="success",
        prompt=prompt,
        width=width,
        height=height,
        duration=duration,
        timestamp=datetime.utcnow().isoformat(),
        image_path=str(file_path.relative_to(ROOT_DIR)),
        image_data_url=data_url,
        seed=seed,
    )


def rotate_character_action(
    image_data_url: str,
    to_direction: str,
    from_direction: Optional[str] = None,
    width: int = 64,
    height: int = 64,
) -> ActionResult:
    _require_api_key()

    if width <= 0 or height <= 0:
        raise ValueError("Width and height must be positive integers")

    # Decode base64 image
    if image_data_url.startswith("data:image"):
        image_data_url = image_data_url.split(",")[1]

    image_bytes = base64.b64decode(image_data_url)
    source_image = Image.open(io.BytesIO(image_bytes))

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    run_dir = OUTPUT_ROOT / timestamp
    run_dir.mkdir(parents=True, exist_ok=True)

    client = _get_client(auto_save=False)

    started = time.perf_counter()
    rotated_image = client.rotate_character(
        image=source_image,
        from_direction=from_direction,
        to_direction=to_direction,
        width=width,
        height=height,
    )
    duration = time.perf_counter() - started

    from_dir = from_direction or "unknown"
    filename = f"rotate_{from_dir}_to_{to_direction}_{timestamp}.png"
    file_path = run_dir / filename
    rotated_image.save(file_path, "PNG")

    buffer = io.BytesIO()
    rotated_image.save(buffer, format="PNG")
    data_url = "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode("utf-8")

    prompt_text = f"Rotate {from_dir} → {to_direction}"
    return ActionResult(
        status="success",
        prompt=prompt_text,
        width=width,
        height=height,
        duration=duration,
        timestamp=datetime.utcnow().isoformat(),
        image_path=str(file_path.relative_to(ROOT_DIR)),
        image_data_url=data_url,
        seed=None,
    )


# ----------------------------------------------------------------------------
# Test suite infrastructure
# ----------------------------------------------------------------------------

TEST_CASES_DIR = ROOT_DIR / "pixellab_tests" / "test_cases"
TEST_RESULTS_DIR = ROOT_DIR / "pixellab_tests" / "results"
TEST_BASELINES_DIR = ROOT_DIR / "pixellab_tests" / "baselines"


def load_test_cases(endpoint: str) -> Dict[str, Any]:
    """Load test cases for a specific endpoint."""
    test_file = TEST_CASES_DIR / f"{endpoint}.json"

    if not test_file.exists():
        raise FileNotFoundError(f"Test case file not found: {test_file}")

    with open(test_file, 'r') as f:
        return json.load(f)


def run_test_case(test_case: Dict[str, Any], endpoint: str) -> Dict[str, Any]:
    """Execute a single test case and return results."""
    test_id = test_case.get("id", "unknown")
    test_name = test_case.get("name", "Unnamed Test")
    inputs = test_case.get("inputs", {})
    expected = test_case.get("expected", {})

    result = {
        "test_id": test_id,
        "test_name": test_name,
        "status": "unknown",
        "passed": False,
        "errors": [],
        "warnings": [],
        "actual": {},
        "expected": expected,
        "duration": 0.0
    }

    try:
        started = time.perf_counter()

        # Execute based on endpoint
        if endpoint == "character_generation":
            action_result = generate_character_action(
                prompt=inputs.get("prompt", ""),
                width=inputs.get("width", 64),
                height=inputs.get("height", 64),
                seed=inputs.get("seed")
            )
        elif endpoint == "character_rotation":
            # For rotation, we need to generate the base character first
            base_inputs = inputs.get("base_character", {})
            base_result = generate_character_action(
                prompt=base_inputs.get("prompt", ""),
                width=base_inputs.get("width", 64),
                height=base_inputs.get("height", 64),
                seed=base_inputs.get("seed")
            )

            # Now rotate it
            rotations = inputs.get("rotations", [])
            if rotations:
                rotation = rotations[0]  # Test first rotation
                action_result = rotate_character_action(
                    image_data_url=base_result.image_data_url,
                    to_direction=rotation.get("to_direction"),
                    from_direction=rotation.get("from_direction"),
                    width=base_inputs.get("width", 64),
                    height=base_inputs.get("height", 64)
                )
            else:
                raise ValueError("No rotations specified in test case")
        else:
            raise ValueError(f"Unsupported endpoint for testing: {endpoint}")

        duration = time.perf_counter() - started

        # Populate actual results
        result["actual"] = {
            "status": action_result.status,
            "duration": duration,
            "image_size": [action_result.width, action_result.height]
        }

        # Validate against expected results
        validation_errors = []

        # Check status
        if expected.get("status") and action_result.status != expected["status"]:
            validation_errors.append(
                f"Status mismatch: expected '{expected['status']}', got '{action_result.status}'"
            )

        # Check duration
        min_duration = expected.get("min_duration")
        max_duration = expected.get("max_duration")
        if min_duration is not None and duration < min_duration:
            validation_errors.append(
                f"Duration too fast: {duration:.2f}s < {min_duration}s"
            )
        if max_duration is not None and duration > max_duration:
            validation_errors.append(
                f"Duration too slow: {duration:.2f}s > {max_duration}s"
            )

        # Check image size
        if expected.get("image_size"):
            exp_size = expected["image_size"]
            if [action_result.width, action_result.height] != exp_size:
                validation_errors.append(
                    f"Image size mismatch: expected {exp_size}, got [{action_result.width}, {action_result.height}]"
                )

        # Determine test result
        if validation_errors:
            result["status"] = "failed"
            result["passed"] = False
            result["errors"] = validation_errors
        else:
            result["status"] = "passed"
            result["passed"] = True

        result["duration"] = duration

    except Exception as e:
        result["status"] = "error"
        result["passed"] = False
        result["errors"] = [str(e)]
        result["duration"] = time.perf_counter() - started

    return result


def run_test_suite(endpoint: str) -> Dict[str, Any]:
    """Run all test cases for an endpoint and return summary."""
    try:
        test_data = load_test_cases(endpoint)
        test_cases = test_data.get("test_cases", [])

        results = {
            "endpoint": endpoint,
            "description": test_data.get("description", ""),
            "timestamp": datetime.utcnow().isoformat(),
            "total_tests": len(test_cases),
            "passed": 0,
            "failed": 0,
            "errors": 0,
            "test_results": []
        }

        for test_case in test_cases:
            test_result = run_test_case(test_case, endpoint)
            results["test_results"].append(test_result)

            if test_result["status"] == "passed":
                results["passed"] += 1
            elif test_result["status"] == "failed":
                results["failed"] += 1
            elif test_result["status"] == "error":
                results["errors"] += 1

        # Save results
        result_dir = TEST_RESULTS_DIR / datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
        result_dir.mkdir(parents=True, exist_ok=True)

        result_file = result_dir / f"{endpoint}_results.json"
        with open(result_file, 'w') as f:
            json.dump(results, f, indent=2)

        results["result_file"] = str(result_file.relative_to(ROOT_DIR))

        return results

    except FileNotFoundError as e:
        return {
            "endpoint": endpoint,
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "endpoint": endpoint,
            "status": "error",
            "error": f"Unexpected error: {str(e)}",
            "timestamp": datetime.utcnow().isoformat()
        }


# ----------------------------------------------------------------------------
# HTTP server implementation
# ----------------------------------------------------------------------------

class PixellabRequestHandler(BaseHTTPRequestHandler):
    server_version = "PixellabActions/1.1"

    def _set_headers(self, status: HTTPStatus = HTTPStatus.OK, content_type: str = "application/json") -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def _write_json(self, payload: Dict[str, Any], status: HTTPStatus = HTTPStatus.OK) -> None:
        self._set_headers(status)
        self.wfile.write(json.dumps(payload).encode("utf-8"))

    def do_OPTIONS(self) -> None:  # noqa: N802
        self.send_response(HTTPStatus.NO_CONTENT)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self) -> None:  # noqa: N802
        try:
            if self.path == "/health":
                payload = {
                    "status": "ok",
                    "server_time": datetime.utcnow().isoformat(),
                    "uptime_seconds": time.time() - SERVER_STARTED,
                    "api_key_detected": bool(PIXELLAB_API_KEY),
                    "balance": _balance_payload(),
                }
                self._write_json(payload)
                return

            if self.path == "/balance":
                self._write_json(_balance_payload())
                return

            if self.path == "/load-jobs":
                self._write_json(load_job_history())
                return

            if self.path.startswith("/test/"):
                # Extract endpoint name from path like /test/character_generation
                endpoint = self.path[6:]  # Remove "/test/" prefix
                if endpoint:
                    result = run_test_suite(endpoint)
                    self._write_json(result)
                else:
                    self._write_json({"error": "Endpoint name required"}, HTTPStatus.BAD_REQUEST)
                return

            if self.path == "/test-cases":
                # List available test case files
                test_files = []
                if TEST_CASES_DIR.exists():
                    for file in TEST_CASES_DIR.glob("*.json"):
                        test_files.append({
                            "endpoint": file.stem,
                            "file": str(file.relative_to(ROOT_DIR))
                        })
                self._write_json({"test_cases": test_files})
                return

            self._write_json({"error": "Endpoint not found"}, HTTPStatus.NOT_FOUND)
        except Exception as exc:  # pragma: no cover
            self._write_json({"error": str(exc)}, HTTPStatus.INTERNAL_SERVER_ERROR)

    def do_POST(self) -> None:  # noqa: N802
        payload: Dict[str, Any] = {}
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length) if content_length else b"{}"
            payload = json.loads(body or b"{}")

            if self.path == "/generate-character":
                result = self._handle_generate_character(payload)
                self._write_json(asdict(result))
            elif self.path == "/rotate-character":
                result = self._handle_rotate_character(payload)
                self._write_json(asdict(result))
            elif self.path == "/save-jobs":
                jobs = payload.get("jobs", [])
                last_job_id = payload.get("lastJobId", 1)
                result = save_job_history(jobs, last_job_id)
                self._write_json(result)
            else:
                self._write_json({"error": "Endpoint not found"}, HTTPStatus.NOT_FOUND)
        except Exception as exc:  # pragma: no cover - runtime guard
            error_payload = ActionResult(
                status="fail",
                prompt=payload.get("prompt", ""),
                width=payload.get("width", 0),
                height=payload.get("height", 0),
                duration=0.0,
                timestamp=datetime.utcnow().isoformat(),
                seed=payload.get("seed"),
                error_message=str(exc),
            )
            self._write_json(asdict(error_payload), HTTPStatus.INTERNAL_SERVER_ERROR)

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A003 - suppress default logging
        return

    def _handle_generate_character(self, payload: Dict[str, Any]) -> ActionResult:
        prompt = payload.get("prompt", "").strip()
        width = int(payload.get("width", 64) or 64)
        height = int(payload.get("height", 64) or 64)
        seed = payload.get("seed") or None

        if not prompt:
            raise ValueError("Prompt is required")

        return generate_character_action(prompt=prompt, width=width, height=height, seed=seed)

    def _handle_rotate_character(self, payload: Dict[str, Any]) -> ActionResult:
        image_data_url = payload.get("image_data_url", "").strip()
        to_direction = payload.get("to_direction", "").strip()
        from_direction = payload.get("from_direction", "").strip() or None
        width = int(payload.get("width", 64) or 64)
        height = int(payload.get("height", 64) or 64)

        if not image_data_url:
            raise ValueError("Image data URL is required")
        if not to_direction:
            raise ValueError("Target direction is required")

        return rotate_character_action(
            image_data_url=image_data_url,
            to_direction=to_direction,
            from_direction=from_direction,
            width=width,
            height=height,
        )


def run_server(host: str = "127.0.0.1", port: int = 8787) -> None:
    server = HTTPServer((host, port), PixellabRequestHandler)
    print(f"📡 PixelLab actions server listening on http://{host}:{port}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:  # pragma: no cover - manual shutdown
        print("Shutting down PixelLab actions server...")
    finally:
        server.server_close()


# ----------------------------------------------------------------------------
# CLI interface
# ----------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="PixelLab actions runner")
    subparsers = parser.add_subparsers(dest="command")

    gen_parser = subparsers.add_parser("generate-character", help="Generate a character via PixFlux")
    gen_parser.add_argument("--prompt", required=True, help="Description of the character")
    gen_parser.add_argument("--width", type=int, default=64, help="Image width in pixels")
    gen_parser.add_argument("--height", type=int, default=64, help="Image height in pixels")
    gen_parser.add_argument("--seed", help="Optional seed for reproducibility")

    subparsers.add_parser("balance", help="Display current PixelLab balance")
    subparsers.add_parser("health", help="Show server health diagnostics")

    parser.add_argument("--serve", action="store_true", help="Start the actions HTTP server")
    parser.add_argument("--host", default="127.0.0.1", help="Host for HTTP server")
    parser.add_argument("--port", type=int, default=8787, help="Port for HTTP server")

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.serve:
        run_server(host=args.host, port=args.port)
        return

    if args.command == "generate-character":
        result = generate_character_action(args.prompt, args.width, args.height, args.seed)
        print(result.to_json())
        return

    if args.command == "balance":
        print(json.dumps(_balance_payload(), ensure_ascii=False))
        return

    if args.command == "health":
        payload = {
            "status": "ok",
            "server_time": datetime.utcnow().isoformat(),
            "uptime_seconds": 0,
            "api_key_detected": bool(PIXELLAB_API_KEY),
            "balance": _balance_payload(),
        }
        print(json.dumps(payload, ensure_ascii=False))
        return

    # Default behaviour when no command is supplied.
    print("Nothing to do. Use --serve or a subcommand. Run with -h for help.")


if __name__ == "__main__":
    main()
