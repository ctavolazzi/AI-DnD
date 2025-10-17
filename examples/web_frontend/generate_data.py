"""Generate JSON snapshots for the static showcase front-end."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from examples.simple_demo.showcase_engine import ShowcaseSimulator  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--turns",
        type=int,
        default=4,
        help="Number of turns to simulate (default: 4)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=7,
        help="Seed used to initialize the deterministic showcase (default: 7)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parent / "data" / "demo_run.json",
        help="Destination JSON file for the generated dataset",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    simulator = ShowcaseSimulator(turns=args.turns, seed=args.seed)
    result = simulator.run().to_dict()

    output_path: Path = args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    relative = output_path.relative_to(Path(__file__).resolve().parent)
    print(f"Saved showcase dataset to {relative}")


if __name__ == "__main__":
    main()
