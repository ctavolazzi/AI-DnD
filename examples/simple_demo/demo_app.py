"""Interactive showcase for the AI-DnD engine.

This demo project is intentionally lightweight so it can run without
connecting to Ollama or external LLMs. It replaces the default narrative
engine with deterministic, prewritten responses and renders a compact HUD
with Rich so you can watch a handful of automated turns play out.
"""
from __future__ import annotations

import argparse
import logging
import random
import sys
import time
from itertools import cycle
from pathlib import Path
from typing import Iterable, List

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

from dnd_game import DnDGame  # noqa: E402  (import after path fix)
from log_aggregator import LogAggregator  # noqa: E402
from narrative_engine import NarrativeEngine  # noqa: E402


class DemoNarrativeEngine(NarrativeEngine):
    """Narrative engine that serves curated sample text instead of calling Ollama."""

    def __init__(self) -> None:
        super().__init__(model="demo")
        self._scene_lines = cycle(
            [
                "{characters} regroup inside {location}, lantern light brushing dusty maps.",
                "Footfalls echo through {location} as {characters} ready their next move.",
                "A hushed wind slips across {location} while {characters} exchange quick glances.",
            ]
        )
        self._combat_lines = cycle(
            [
                "{attacker} {action} {defender}, steel ringing {damage_phrase}.",
                "With practiced ease, {attacker} {action} {defender} {damage_phrase}.",
                "{attacker} sweeps toward {defender} and {damage_phrase}.",
            ]
        )
        self._dialogue_lines = cycle(
            [
                "{player} {action} while the party observes, {context}.",
                "Calmly, {player} {action}; the others nod at the {context}.",
                "{player} briefly {action}, a steady reminder of the {context}.",
            ]
        )
        self._quest_lines = cycle(
            [
                "Rescue miners trapped beneath Emberpeak and seal the shattered rune.",
                "Escort a relic caravan safely through the whispering fen.",
                "Hunt the moonlit beast prowling the outskirts of Wayfarer Hollow.",
            ]
        )
        self._encounter_lines = cycle(
            [
                "A scarred scout requests aid tracking goblins near the ridge.",
                "A caravan master pleads for protection from lurking bandits.",
                "An injured druid warns of restless spirits in the marsh.",
            ]
        )
        self._conclusion_lines = cycle(
            [
                "Battered yet grinning, the heroes secure the night's campfire tale.",
                "Relieved villagers shower the party with praise and warm bread.",
                "The heroes toast quietly, knowing darker roads still await.",
            ]
        )

    def describe_scene(self, location: str, characters: Iterable[str]) -> str:  # type: ignore[override]
        names = ", ".join(characters) or "nobody"
        return next(self._scene_lines).format(location=location, characters=names)

    def describe_combat(
        self,
        attacker: str,
        defender: str,
        action: str,
        damage: int | None = None,
    ) -> str:  # type: ignore[override]
        damage_phrase = f"for {damage} damage" if damage else "with a burst of momentum"
        return next(self._combat_lines).format(
            attacker=attacker,
            defender=defender,
            action=action,
            damage_phrase=damage_phrase,
        )

    def handle_player_action(self, player_name: str, action: str, context: str) -> str:  # type: ignore[override]
        return next(self._dialogue_lines).format(
            player=player_name,
            action=action,
            context=context.lower(),
        )

    def generate_quest(self, difficulty: str = "medium", theme: str | None = None) -> str:  # type: ignore[override]
        quest = next(self._quest_lines)
        if theme:
            return f"{quest} (theme: {theme})"
        return quest

    def generate_random_encounter(self, party_level: int, environment: str) -> str:  # type: ignore[override]
        return next(self._encounter_lines)

    def summarize_combat(self, combat_log: Iterable[str]) -> str:  # type: ignore[override]
        return "The skirmish resolves quickly and cleanly."

    def generate_conclusion(self) -> str:  # type: ignore[override]
        return next(self._conclusion_lines)


class Showcase:
    """Runs a trimmed-down combat loop and renders it with Rich."""

    def __init__(self, turns: int = 4, delay: float = 0.8, seed: int | None = 7) -> None:
        self.turn_limit = turns
        self.delay = delay
        self.console = Console()
        self.event_history: List[str] = []
        self.turn = 0

        if seed is not None:
            random.seed(seed)

        self.aggregator = LogAggregator()
        self.aggregator.setLevel(logging.INFO)
        self.aggregator.setFormatter(logging.Formatter("%(message)s"))
        self._configure_loggers()

        self.game = DnDGame(auto_create_characters=True, model="demo")
        self.game.narrative_engine = DemoNarrativeEngine()

        self.quest_hook = self.game.narrative_engine.generate_quest(theme="showcase expedition")
        logging.getLogger("dnd_game").info("Quest Hook:")
        logging.getLogger("dnd_game").info(self.quest_hook)
        self._capture_events()

        introductions = self.game.generate_character_introductions()
        if introductions:
            self._capture_events()

    def _configure_loggers(self) -> None:
        root_logger = logging.getLogger()
        root_logger.handlers.clear()
        root_logger.setLevel(logging.INFO)
        root_logger.addHandler(self.aggregator)

        for name in ("dnd_game", "narrative_engine"):
            logger = logging.getLogger(name)
            logger.handlers.clear()
            logger.setLevel(logging.INFO)
            logger.addHandler(self.aggregator)
            logger.propagate = False

    def _capture_events(self) -> List[str]:
        raw = self.aggregator.get_logs()
        if not raw:
            return []
        lines = [line.strip() for line in raw.splitlines() if line.strip()]
        self.event_history.extend(lines)
        self.event_history = self.event_history[-18:]
        self.aggregator.clear()
        return lines

    def _character_table(self, characters, title: str) -> Table:
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

        title = f"Turn {self.turn} / {self.turn_limit}" if self.turn else "Setup"
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
        layout["players"].update(Panel(self._character_table(self.game.players, "Adventurers"), border_style="green"))
        layout["enemies"].update(Panel(self._character_table(self.game.enemies, "Adversaries"), border_style="red"))
        layout["log"].update(self._log_panel())

    def _run_turn(self, layout: Layout, live: Live) -> None:
        encounter = None
        if self.turn == 1 or self.turn % 2 == 1:
            encounter = self.game.narrative_engine.generate_random_encounter(
                party_level=1,
                environment=self.game.current_location,
            )
            logging.getLogger("dnd_game").info(f"Encounter: {encounter}")
            self._capture_events()

        self.game.play_turn()
        self._capture_events()

        if encounter:
            summary = self.game.narrative_engine.summarize_combat(self.event_history[-5:])
            logging.getLogger("dnd_game").info(summary)
            self._capture_events()

        self._render(layout)
        live.update(layout)

    def run(self) -> None:
        layout = self._build_layout()
        self._render(layout)

        with Live(layout, refresh_per_second=6, screen=False) as live:
            live.update(layout)
            time.sleep(self.delay)

            for self.turn in range(1, self.turn_limit + 1):
                self._run_turn(layout, live)
                time.sleep(self.delay)
                if self.game.is_game_over():
                    break

            conclusion = self.game.narrative_engine.generate_conclusion()
            logging.getLogger("dnd_game").info(conclusion)
            self._capture_events()
            self._render(layout)
            live.update(layout)
            time.sleep(self.delay)

        self.console.print("\nDemo complete! Thanks for watching the sample encounter.", style="bright_green")


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
