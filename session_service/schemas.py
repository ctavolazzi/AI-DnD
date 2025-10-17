"""Pydantic models shared by the session service endpoints."""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class CharacterModel(BaseModel):
    """Represents the battle state for a single combatant."""

    name: str
    char_class: str
    hp: int
    max_hp: int
    alive: bool


class TurnFrameModel(BaseModel):
    """Single point-in-time snapshot for the client timeline."""

    turn: int
    players: List[CharacterModel]
    enemies: List[CharacterModel]
    new_events: List[str] = Field(default_factory=list)
    cumulative_events: List[str] = Field(default_factory=list)
    is_final: bool = False


class SessionPayload(BaseModel):
    """Envelope returned to the front end when requesting session state."""

    session_id: str
    quest_hook: str
    frames: List[TurnFrameModel]
    conclusion: Optional[str] = None
    is_complete: bool = False
    turn_index: int = 0


class CreateSessionRequest(BaseModel):
    """Parameters accepted when starting a new session."""

    mode: str = Field(default="demo", description="Session type to create")
    turns: int = Field(default=6, ge=1, le=20)
    seed: Optional[int] = Field(default=11, description="Deterministic seed for demo mode")


class AdvanceRequest(BaseModel):
    """Optional payload for the advance endpoint."""

    steps: int = Field(default=1, ge=1, le=5)
