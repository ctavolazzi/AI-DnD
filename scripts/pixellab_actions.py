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
from typing import Any, Dict

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


def generate_character_action(prompt: str, width: int = 64, height: int = 64) -> ActionResult:
    _require_api_key()

    if width <= 0 or height <= 0:
        raise ValueError("Width and height must be positive integers")

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    run_dir = OUTPUT_ROOT / timestamp
    run_dir.mkdir(parents=True, exist_ok=True)

    client = PixelLabClient(api_key=PIXELLAB_API_KEY, auto_save=False)

    started = time.perf_counter()
    image = client.generate_character(
        description=prompt,
        width=width,
        height=height,
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
    )


# ----------------------------------------------------------------------------
# HTTP server implementation
# ----------------------------------------------------------------------------

class PixellabRequestHandler(BaseHTTPRequestHandler):
    server_version = "PixellabActions/1.0"

    def _set_headers(self, status: HTTPStatus = HTTPStatus.OK, content_type: str = "application/json") -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_OPTIONS(self) -> None:  # noqa: N802
        self.send_response(HTTPStatus.NO_CONTENT)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self) -> None:  # noqa: N802
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length) if content_length else b"{}"
            payload = json.loads(body or b"{}")

            if self.path == "/generate-character":
                result = self._handle_generate_character(payload)
                self._set_headers(HTTPStatus.OK)
                self.wfile.write(result.to_json().encode("utf-8"))
            else:
                self._set_headers(HTTPStatus.NOT_FOUND)
                self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode("utf-8"))
        except Exception as exc:  # pragma: no cover - runtime guard
            self._set_headers(HTTPStatus.INTERNAL_SERVER_ERROR)
            error_payload = ActionResult(
                status="fail",
                prompt=payload.get("prompt", ""),
                width=payload.get("width", 0),
                height=payload.get("height", 0),
                duration=0.0,
                timestamp=datetime.utcnow().isoformat(),
                error_message=str(exc),
            )
            self.wfile.write(error_payload.to_json().encode("utf-8"))

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A003 - suppress default logging
        return

    def _handle_generate_character(self, payload: Dict[str, Any]) -> ActionResult:
        prompt = payload.get("prompt", "").strip()
        width = int(payload.get("width", 64) or 64)
        height = int(payload.get("height", 64) or 64)

        if not prompt:
            raise ValueError("Prompt is required")

        return generate_character_action(prompt=prompt, width=width, height=height)


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
        result = generate_character_action(args.prompt, args.width, args.height)
        print(result.to_json())
        return

    # Default behaviour when no command is supplied.
    print("Nothing to do. Use --serve or a subcommand. Run with -h for help.")


if __name__ == "__main__":
    main()
