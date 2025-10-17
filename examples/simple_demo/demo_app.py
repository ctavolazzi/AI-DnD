"""Interactive showcase for the AI-DnD engine.

This demo project is intentionally lightweight so it can run without
connecting to Ollama or external LLMs. It replaces the default narrative
engine with deterministic, prewritten responses and renders a compact HUD
with Rich so you can watch a handful of automated turns play out.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

# Ensure the repository root is importable when the demo is launched
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from examples.simple_demo.showcase_engine import (  # noqa: E402  (import after path fix)
    CharacterSnapshot,
    ShowcaseResult,
    ShowcaseSimulator,
    TurnFrame,
)


class Showcase:
    """Runs a trimmed-down combat loop and renders it with Rich."""

    def __init__(self, turns: int = 4, delay: float = 0.8, seed: int | None = 7) -> None:
        self.turn_limit = turns
        self.delay = delay
        self.console = Console()
        self.event_history: list[str] = []
        self.turn = 0
        self.quest_hook = ""
        self._current_players: list[CharacterSnapshot] = []
        self._current_enemies: list[CharacterSnapshot] = []
        self._current_frame_is_final = False
        self._current_result: ShowcaseResult | None = None
        self._frames: list[TurnFrame] = []

        self.simulator = ShowcaseSimulator(turns=turns, seed=seed)

    def _character_table(self, characters: list[CharacterSnapshot], title: str) -> Table:
        table = Table(title=title, expand=True, show_edge=False)
        table.add_column("Name", style="bright_cyan")
        table.add_column("Class", style="bright_white")
        table.add_column("HP", style="bright_yellow", justify="right")
        table.add_column("Status", style="bright_white")

        for char in characters:
            status = "Defeated"
            status_style = "bold red"
            if char.alive:
                status = "Ready"
                status_style = "bold green"
            table.add_row(
                char.name,
                char.char_class,
                f"{char.hp}/{char.max_hp}",
                Text(status, style=status_style),
            )

        return table

    def _log_panel(self) -> Panel:
        log_text = Text()
        if not self.event_history:
            log_text.append("Logs will appear here once the adventure begins.\n", style="grey62")
        else:
            for line in self.event_history[-12:]:
                log_text.append(f"• {line}\n", style="white")

        if self._current_frame_is_final:
            title = "Conclusion"
        elif self.turn:
            title = f"Turn {self.turn} / {self.turn_limit}"
        else:
            title = "Setup"
        return Panel(log_text, title=title, border_style="bright_blue")

    def _build_layout(self) -> Layout:
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=5),
            Layout(name="status", ratio=2),
            Layout(name="log", ratio=3),
        )
        layout["status"].split_row(
            Layout(name="players"),
            Layout(name="enemies"),
        )
        return layout

    def _render(self, layout: Layout) -> None:
        header_text = Text("AI-DnD Sample Showcase", style="bold bright_white")
        header_text.append("\n" + self.quest_hook, style="bright_cyan")
        layout["header"].update(Panel(header_text, border_style="bright_magenta"))
        layout["players"].update(Panel(self._character_table(self._current_players, "Adventurers"), border_style="green"))
        layout["enemies"].update(Panel(self._character_table(self._current_enemies, "Adversaries"), border_style="red"))
        layout["log"].update(self._log_panel())

    def run(self) -> None:
        layout = self._build_layout()
        self._current_result = self.simulator.run()
        self.quest_hook = self._current_result.quest_hook
        self._frames = list(self._current_result.frames)

        with Live(layout, refresh_per_second=6, screen=False) as live:
            for index, frame in enumerate(self._frames):
                self.turn = frame.turn
                self.event_history = list(frame.cumulative_events)
                self._current_players = list(frame.players)
                self._current_enemies = list(frame.enemies)
                self._current_frame_is_final = frame.is_final
                self._render(layout)
                live.update(layout)
                if index < len(self._frames) - 1:
                    time.sleep(self.delay)

        conclusion_text = self._current_result.conclusion if self._current_result else ""
        if conclusion_text:
            self.console.print(f"\n{conclusion_text}", style="bright_green")
        self.console.print("Demo complete! Thanks for watching the sample encounter.", style="bright_green")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the AI-DnD showcase demo.")
    parser.add_argument("--turns", type=int, default=4, help="Number of turns to simulate (default: 4)")
    parser.add_argument("--delay", type=float, default=0.8, help="Delay between turns in seconds (default: 0.8)")
    parser.add_argument("--seed", type=int, default=7, help="Random seed for reproducible stats (default: 7)")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    showcase = Showcase(turns=args.turns, delay=args.delay, seed=args.seed)
    showcase.run()


if __name__ == "__main__":
    main()
