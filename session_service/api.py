"""FastAPI application exposing the MVP session endpoints."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .manager import SessionManager
from .schemas import AdvanceRequest, CreateSessionRequest, SessionPayload

app = FastAPI(title="AI-DnD Session Service", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

manager = SessionManager()


@app.post("/sessions", response_model=SessionPayload)
def create_session(request: CreateSessionRequest) -> SessionPayload:
    if request.mode != "demo":
        raise HTTPException(status_code=400, detail="Only demo mode is available in the MVP")
    return manager.create_session(turns=request.turns, seed=request.seed)


@app.get("/sessions/{session_id}", response_model=SessionPayload)
def get_session(session_id: str) -> SessionPayload:
    try:
        return manager.get_session(session_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Session not found") from exc


@app.post("/sessions/{session_id}/advance", response_model=SessionPayload)
def advance_session(session_id: str, request: AdvanceRequest | None = None) -> SessionPayload:
    steps = request.steps if request else 1
    try:
        return manager.advance_session(session_id, steps=steps)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Session not found") from exc


@app.get("/sessions", response_model=list[str])
def list_sessions() -> list[str]:
    return manager.active_session_ids()


__all__ = ["app"]
