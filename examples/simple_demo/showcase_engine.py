"""Shared simulation utilities for showcase demos.

This module extracts the deterministic narrative engine and helper classes
needed to generate lightweight previews of the AI-DnD combat loop. It powers
both the Rich-based terminal showcase and the optional web front-end so the
gameplay logic lives in one place.
"""

from __future__ import annotations

import logging
import random
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, List, Sequence

# Ensure the repository root is importable when this module is executed as a
# script via examples.
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from dnd_game import DnDGame  # noqa: E402  (import after path fix)
from log_aggregator import LogAggregator  # noqa: E402
from narrative_engine import NarrativeEngine  # noqa: E402


@dataclass(frozen=True)
class CharacterSnapshot:
    """Serializable view of a combatant's state."""

    name: str
    char_class: str
    hp: int
    max_hp: int
    alive: bool

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class TurnFrame:
    """Represents a single moment in the showcase timeline."""

    turn: int
    players: Sequence[CharacterSnapshot]
    enemies: Sequence[CharacterSnapshot]
    new_events: Sequence[str]
    cumulative_events: Sequence[str]
    is_final: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "turn": self.turn,
            "players": [character.to_dict() for character in self.players],
            "enemies": [character.to_dict() for character in self.enemies],
            "new_events": list(self.new_events),
            "cumulative_events": list(self.cumulative_events),
            "is_final": self.is_final,
        }


@dataclass(frozen=True)
class ShowcaseResult:
    """Container for the deterministic simulation output."""

    quest_hook: str
    frames: Sequence[TurnFrame]
    conclusion: str

    def to_dict(self) -> dict[str, object]:
        return {
            "quest_hook": self.quest_hook,
            "frames": [frame.to_dict() for frame in self.frames],
            "conclusion": self.conclusion,
        }


class DemoNarrativeEngine(NarrativeEngine):
    """Narrative engine that serves curated sample text instead of calling Ollama."""

    def __init__(self) -> None:
        super().__init__(model="demo")
        self._scene_lines = _cycling_text(
            "{characters} regroup inside {location}, lantern light brushing dusty maps.",
            "Footfalls echo through {location} as {characters} ready their next move.",
            "A hushed wind slips across {location} while {characters} exchange quick glances.",
        )
        self._combat_lines = _cycling_text(
            "{attacker} {action} {defender}, steel ringing {damage_phrase}.",
            "With practiced ease, {attacker} {action} {defender} {damage_phrase}.",
            "{attacker} sweeps toward {defender} and {damage_phrase}.",
        )
        self._dialogue_lines = _cycling_text(
            "{player} {action} while the party observes, {context}.",
            "Calmly, {player} {action}; the others nod at the {context}.",
            "{player} briefly {action}, a steady reminder of the {context}.",
        )
        self._quest_lines = _cycling_text(
            "Rescue miners trapped beneath Emberpeak and seal the shattered rune.",
            "Escort a relic caravan safely through the whispering fen.",
            "Hunt the moonlit beast prowling the outskirts of Wayfarer Hollow.",
        )
        self._encounter_lines = _cycling_text(
            "A scarred scout requests aid tracking goblins near the ridge.",
            "A caravan master pleads for protection from lurking bandits.",
            "An injured druid warns of restless spirits in the marsh.",
        )
        self._conclusion_lines = _cycling_text(
            "Battered yet grinning, the heroes secure the night's campfire tale.",
            "Relieved villagers shower the party with praise and warm bread.",
            "The heroes toast quietly, knowing darker roads still await.",
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


class ShowcaseSimulator:
    """Runs deterministic turns and captures the resulting state timeline."""

    def __init__(self, turns: int = 4, seed: int | None = 7) -> None:
        self.turn_limit = turns
        self.event_history: List[str] = []

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

    def run(self) -> ShowcaseResult:
        frames: List[TurnFrame] = []

        initial_events = self._capture_events()
        introductions = self.game.generate_character_introductions()
        if introductions:
            initial_events.extend(self._capture_events())
        frames.append(self._snapshot(turn=0, new_events=initial_events))

        for turn in range(1, self.turn_limit + 1):
            new_events: List[str] = []
            encounter = None

            if turn == 1 or turn % 2 == 1:
                encounter = self.game.narrative_engine.generate_random_encounter(
                    party_level=1,
                    environment=self.game.current_location,
                )
                logging.getLogger("dnd_game").info(f"Encounter: {encounter}")
                new_events.extend(self._capture_events())

            self.game.play_turn()
            new_events.extend(self._capture_events())

            if encounter:
                summary = self.game.narrative_engine.summarize_combat(new_events[-5:])
                logging.getLogger("dnd_game").info(summary)
                new_events.extend(self._capture_events())

            frames.append(self._snapshot(turn=turn, new_events=new_events))

            if self.game.is_game_over():
                break

        conclusion = self.game.narrative_engine.generate_conclusion()
        logging.getLogger("dnd_game").info(conclusion)
        conclusion_events = self._capture_events()
        frames.append(self._snapshot(turn=frames[-1].turn, new_events=conclusion_events, is_final=True))

        return ShowcaseResult(quest_hook=self.quest_hook, frames=frames, conclusion=conclusion)

    def _snapshot(
        self,
        turn: int,
        *,
        new_events: Sequence[str],
        is_final: bool = False,
    ) -> TurnFrame:
        return TurnFrame(
            turn=turn,
            players=self._snapshot_characters(self.game.players),
            enemies=self._snapshot_characters(self.game.enemies),
            new_events=list(new_events),
            cumulative_events=list(self.event_history),
            is_final=is_final,
        )

    def _snapshot_characters(self, characters: Sequence[object]) -> List[CharacterSnapshot]:
        snapshots: List[CharacterSnapshot] = []
        for character in characters:
            snapshots.append(
                CharacterSnapshot(
                    name=getattr(character, "name", "Unknown"),
                    char_class=getattr(character, "char_class", "Adventurer"),
                    hp=max(0, int(getattr(character, "hp", 0))),
                    max_hp=max(0, int(getattr(character, "max_hp", 0))),
                    alive=bool(getattr(character, "alive", False)),
                )
            )
        return snapshots

    def _capture_events(self) -> List[str]:
        raw = self.aggregator.get_logs()
        if not raw:
            return []
        lines = [line.strip() for line in raw.splitlines() if line.strip()]
        self.event_history.extend(lines)
        self.event_history = self.event_history[-50:]
        self.aggregator.clear()
        return lines

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


def _cycling_text(*lines: str):
    """Return a generator cycling through deterministic narrative lines."""

    if not lines:
        raise ValueError("At least one line is required for cycling text")
    while True:
        for line in lines:
            yield line

