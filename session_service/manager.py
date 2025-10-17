"""In-memory session manager powering the MVP service."""

from __future__ import annotations

import threading
import uuid
from dataclasses import dataclass
from typing import Dict, Iterable, List

from examples.simple_demo.showcase_engine import ShowcaseResult, ShowcaseSimulator

from .schemas import SessionPayload, TurnFrameModel


@dataclass
class LiveSession:
    """Represents a playable session constructed from deterministic frames."""

    session_id: str
    result: ShowcaseResult
    cursor: int = 0

    def advance(self, steps: int = 1) -> SessionPayload:
        """Advance the internal pointer and return the updated payload."""

        if self.cursor < len(self.result.frames) - 1:
            self.cursor = min(self.cursor + steps, len(self.result.frames) - 1)
        return self.payload

    @property
    def payload(self) -> SessionPayload:
        frames = list(self._visible_frames)
        is_complete = bool(frames and frames[-1].is_final)
        conclusion = self.result.conclusion if is_complete else None
        return SessionPayload(
            session_id=self.session_id,
            quest_hook=self.result.quest_hook,
            frames=frames,
            conclusion=conclusion,
            is_complete=is_complete,
            turn_index=self.cursor,
        )

    @property
    def _visible_frames(self) -> Iterable[TurnFrameModel]:
        for frame in self.result.frames[: self.cursor + 1]:
            yield TurnFrameModel(
                turn=frame.turn,
                players=[
                    {
                        "name": character.name,
                        "char_class": character.char_class,
                        "hp": character.hp,
                        "max_hp": character.max_hp,
                        "alive": character.alive,
                    }
                    for character in frame.players
                ],
                enemies=[
                    {
                        "name": character.name,
                        "char_class": character.char_class,
                        "hp": character.hp,
                        "max_hp": character.max_hp,
                        "alive": character.alive,
                    }
                    for character in frame.enemies
                ],
                new_events=list(frame.new_events),
                cumulative_events=list(frame.cumulative_events),
                is_final=frame.is_final,
            )


class SessionManager:
    """Thread-safe registry for active sessions."""

    def __init__(self) -> None:
        self._sessions: Dict[str, LiveSession] = {}
        self._lock = threading.RLock()

    def create_session(self, *, turns: int = 6, seed: int | None = 11) -> SessionPayload:
        """Create a deterministic session based on the showcase simulator."""

        simulator = ShowcaseSimulator(turns=turns, seed=seed)
        result = simulator.run()
        session_id = uuid.uuid4().hex
        live_session = LiveSession(session_id=session_id, result=result)

        with self._lock:
            self._sessions[session_id] = live_session

        return live_session.payload

    def get_session(self, session_id: str) -> SessionPayload:
        with self._lock:
            session = self._sessions.get(session_id)
        if not session:
            raise KeyError(session_id)
        return session.payload

    def advance_session(self, session_id: str, *, steps: int = 1) -> SessionPayload:
        with self._lock:
            session = self._sessions.get(session_id)
            if not session:
                raise KeyError(session_id)
            payload = session.advance(steps=steps)
        return payload

    def active_session_ids(self) -> List[str]:
        with self._lock:
            return list(self._sessions.keys())
