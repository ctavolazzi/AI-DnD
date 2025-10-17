"""Entry point for running the session service with Uvicorn."""

from __future__ import annotations

import argparse

import uvicorn

from .api import app


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the AI-DnD session service")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8001)
    parser.add_argument("--reload", action="store_true")
    args = parser.parse_args()

    uvicorn.run(app, host=args.host, port=args.port, reload=args.reload)


if __name__ == "__main__":
    main()
