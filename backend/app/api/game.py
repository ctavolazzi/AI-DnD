"""Game session CRUD API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

from ..database import get_db
from ..models import GameSession, Character as DBCharacter, Location as DBLocation, Event as DBEvent
from ..services.game_state_manager import (
    GameStateManager,
    get_session,
    create_session,
    delete_session,
    get_all_active_sessions
)
from ..services.game_service import game_service

router = APIRouter(prefix="/api/v1/game", tags=["game"])


# Pydantic schemas for request/response
class CreateGameRequest(BaseModel):
    name: str = Field(default="New Adventure", description="Game session name")
    difficulty: str = Field(default="medium", description="Difficulty level")
    ai_model: str = Field(default="mistral", description="AI model to use")


class GameSessionResponse(BaseModel):
    id: str
    name: str
    created_at: str
    updated_at: Optional[str]
    last_played_at: Optional[str]
    turn_count: int
    status: str
    current_location_id: Optional[str]
    difficulty: str
    ai_model: str


class CharacterUpdateRequest(BaseModel):
    hp: Optional[int] = None
    mana: Optional[int] = None
    current_location_id: Optional[str] = None
    status_effects: Optional[List[str]] = None
    inventory: Optional[Dict[str, Any]] = None


class TurnAdvanceRequest(BaseModel):
    events: List[Dict[str, Any]] = Field(default=[], description="Events that occurred this turn")


# ========== Game Session Management ==========

@router.post("/sessions", response_model=GameSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_game_session(
    request: CreateGameRequest,
    db: Session = Depends(get_db)
):
    """
    Create a new game session.

    This initializes:
    - Database record for persistence
    - In-memory state manager for fast access
    - Default game state
    """
    # Generate unique session ID
    session_id = f"game_{uuid.uuid4().hex[:16]}"

    # Create database record
    db_session = GameSession(
        id=session_id,
        name=request.name,
        difficulty=request.difficulty,
        ai_model=request.ai_model,
        turn_count=0,
        status="active",
        quest_progress={}
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)

    # Create in-memory state manager
    state_manager = create_session(session_id)

    return GameSessionResponse(
        id=db_session.id,
        name=db_session.name,
        created_at=db_session.created_at.isoformat(),
        updated_at=db_session.updated_at.isoformat() if db_session.updated_at else None,
        last_played_at=db_session.last_played_at.isoformat() if db_session.last_played_at else None,
        turn_count=db_session.turn_count,
        status=db_session.status,
        current_location_id=db_session.current_location_id,
        difficulty=db_session.difficulty,
        ai_model=db_session.ai_model
    )


@router.get("/sessions", response_model=List[GameSessionResponse])
async def list_game_sessions(
    limit: int = 20,
    offset: int = 0,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    List all game sessions with pagination.

    Filter by status (active, completed, failed, paused).
    """
    query = db.query(GameSession).filter(GameSession.deleted_at == None)

    if status:
        query = query.filter(GameSession.status == status)

    sessions = query.order_by(desc(GameSession.last_played_at)).offset(offset).limit(limit).all()

    return [
        GameSessionResponse(
            id=s.id,
            name=s.name,
            created_at=s.created_at.isoformat(),
            updated_at=s.updated_at.isoformat() if s.updated_at else None,
            last_played_at=s.last_played_at.isoformat() if s.last_played_at else None,
            turn_count=s.turn_count,
            status=s.status,
            current_location_id=s.current_location_id,
            difficulty=s.difficulty,
            ai_model=s.ai_model
        )
        for s in sessions
    ]


@router.get("/sessions/{session_id}", response_model=GameSessionResponse)
async def get_game_session(
    session_id: str,
    db: Session = Depends(get_db)
):
    """Get a specific game session"""
    db_session = db.query(GameSession).filter(
        GameSession.id == session_id,
        GameSession.deleted_at == None
    ).first()

    if not db_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Game session {session_id} not found"
        )

    return GameSessionResponse(
        id=db_session.id,
        name=db_session.name,
        created_at=db_session.created_at.isoformat(),
        updated_at=db_session.updated_at.isoformat() if db_session.updated_at else None,
        last_played_at=db_session.last_played_at.isoformat() if db_session.last_played_at else None,
        turn_count=db_session.turn_count,
        status=db_session.status,
        current_location_id=db_session.current_location_id,
        difficulty=db_session.difficulty,
        ai_model=db_session.ai_model
    )


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_game_session(
    session_id: str,
    hard_delete: bool = False,
    db: Session = Depends(get_db)
):
    """
    Delete a game session.

    By default does soft delete. Set hard_delete=true to permanently remove.
    """
    db_session = db.query(GameSession).filter(GameSession.id == session_id).first()

    if not db_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Game session {session_id} not found"
        )

    if hard_delete:
        # Permanently delete (cascade will handle related records)
        db.delete(db_session)
    else:
        # Soft delete
        db_session.deleted_at = datetime.now()

    db.commit()

    # Remove from memory
    delete_session(session_id)
    game_service.clear_cache(session_id)


# ========== Game State Management ==========

@router.get("/sessions/{session_id}/state")
async def get_game_state(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    Get complete game state (fast, from memory if available).

    Returns the full in-memory state including characters, locations, and recent events.
    """
    # Check session exists in DB
    db_session = db.query(GameSession).filter(
        GameSession.id == session_id,
        GameSession.deleted_at == None
    ).first()

    if not db_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Game session {session_id} not found"
        )

    # Get from memory if available
    state_manager = get_session(session_id)

    if state_manager:
        return {
            "session_id": session_id,
            "source": "memory",
            "state": state_manager.get_state(),
            "summary": state_manager.get_summary()
        }

    # Otherwise load from database snapshot
    if db_session.state_snapshot:
        return {
            "session_id": session_id,
            "source": "database",
            "state": db_session.state_snapshot,
            "summary": {
                "turn": db_session.turn_count,
                "status": db_session.status,
                "last_played": db_session.last_played_at.isoformat() if db_session.last_played_at else None
            }
        }

    # No state available yet
    return {
        "session_id": session_id,
        "source": "empty",
        "state": {},
        "summary": {}
    }


@router.post("/sessions/{session_id}/save")
async def save_game_state(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    Save current game state to database.

    Takes the in-memory state and persists it to the database.
    Includes integrity checksum for verification.
    """
    # Get in-memory state
    state_manager = get_session(session_id)

    if not state_manager:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No active session {session_id} in memory. Load it first."
        )

    # Create snapshot with checksum
    snapshot_data = state_manager.snapshot()

    # Update database record
    db_session = db.query(GameSession).filter(GameSession.id == session_id).first()

    if not db_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Game session {session_id} not found in database"
        )

    db_session.state_snapshot = snapshot_data["snapshot"]
    db_session.turn_count = state_manager.get_turn()
    db_session.status = state_manager.get_status()
    db_session.current_location_id = state_manager.state.get("current_location_id")
    db_session.last_played_at = datetime.now()
    db_session.updated_at = datetime.now()

    db.commit()

    return {
        "session_id": session_id,
        "saved_at": snapshot_data["timestamp"],
        "checksum": snapshot_data["checksum"],
        "turn": db_session.turn_count,
        "status": "success"
    }


@router.post("/sessions/{session_id}/load")
async def load_game_state(
    session_id: str,
    verify_integrity: bool = True,
    db: Session = Depends(get_db)
):
    """
    Load game state from database into memory.

    Creates or updates the in-memory state manager with persisted data.
    Optionally verifies integrity using checksum.
    """
    db_session = db.query(GameSession).filter(
        GameSession.id == session_id,
        GameSession.deleted_at == None
    ).first()

    if not db_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Game session {session_id} not found"
        )

    if not db_session.state_snapshot:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No saved state available for session {session_id}"
        )

    # Get or create state manager
    state_manager = get_session(session_id)
    if not state_manager:
        state_manager = create_session(session_id)

    # Load state
    state_json = state_manager.to_json()
    state_manager.from_json(str(db_session.state_snapshot))

    # Update last played
    db_session.last_played_at = datetime.now()
    db.commit()

    return {
        "session_id": session_id,
        "loaded_at": datetime.now().isoformat(),
        "turn": state_manager.get_turn(),
        "status": state_manager.get_status(),
        "summary": state_manager.get_summary()
    }


# ========== Turn Management ==========

@router.post("/sessions/{session_id}/turns/next")
async def advance_turn(
    session_id: str,
    request: TurnAdvanceRequest,
    auto_save: bool = True,
    db: Session = Depends(get_db)
):
    """
    Advance to the next turn.

    Updates turn counter, logs events, optionally auto-saves.
    """
    state_manager = get_session(session_id)

    if not state_manager:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No active session {session_id}. Load it first."
        )

    # Advance turn
    new_turn = state_manager.next_turn()

    # Log events to memory
    for event_data in request.events:
        event_data["turn_number"] = new_turn
        state_manager.add_event(event_data)

        # Also persist event to database
        db_event = DBEvent(
            session_id=session_id,
            event_type=event_data.get("type", "unknown"),
            turn_number=new_turn,
            summary=event_data.get("summary", ""),
            description=event_data.get("description"),
            location_id=event_data.get("location_id"),
            character_ids=event_data.get("character_ids", []),
            data=event_data
        )
        db.add(db_event)

    db.commit()

    # Auto-save if requested
    if auto_save:
        db_session = db.query(GameSession).filter(GameSession.id == session_id).first()
        if db_session:
            snapshot_data = state_manager.snapshot()
            db_session.state_snapshot = snapshot_data["snapshot"]
            db_session.turn_count = new_turn
            db_session.last_played_at = datetime.now()
            db.commit()

    return {
        "session_id": session_id,
        "turn": new_turn,
        "events_logged": len(request.events),
        "auto_saved": auto_save
    }


# ========== Character Management ==========

@router.get("/sessions/{session_id}/characters")
async def get_characters(
    session_id: str,
    alive_only: bool = False
):
    """Get all characters in the session"""
    state_manager = get_session(session_id)

    if not state_manager:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No active session {session_id}"
        )

    if alive_only:
        return {"characters": state_manager.get_alive_characters()}

    return {"characters": state_manager.get_all_characters()}


@router.put("/sessions/{session_id}/characters/{char_id}")
async def update_character(
    session_id: str,
    char_id: str,
    updates: CharacterUpdateRequest
):
    """Update character state"""
    state_manager = get_session(session_id)

    if not state_manager:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No active session {session_id}"
        )

    character = state_manager.get_character(char_id)
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character {char_id} not found"
        )

    # Apply updates
    update_dict = updates.dict(exclude_unset=True)
    state_manager.update_character(char_id, update_dict)

    return {
        "char_id": char_id,
        "updated_fields": list(update_dict.keys()),
        "character": state_manager.get_character(char_id)
    }


# ========== Narrative History ==========

@router.get("/sessions/{session_id}/events")
async def get_events(
    session_id: str,
    turn: Optional[int] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Get event history for a session.

    Retrieves from database for complete history.
    """
    query = db.query(DBEvent).filter(DBEvent.session_id == session_id)

    if turn is not None:
        query = query.filter(DBEvent.turn_number == turn)

    events = query.order_by(desc(DBEvent.created_at)).limit(limit).all()

    return {
        "session_id": session_id,
        "event_count": len(events),
        "events": [event.to_dict() for event in events]
    }


# ========== Utility Endpoints ==========

@router.get("/active-sessions")
async def get_active_sessions():
    """Get list of currently active (in-memory) sessions"""
    sessions = get_all_active_sessions()
    return {
        "active_count": len(sessions),
        "sessions": sessions
    }


@router.get("/sessions/{session_id}/summary")
async def get_session_summary(session_id: str):
    """Get quick summary of session state"""
    state_manager = get_session(session_id)

    if not state_manager:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No active session {session_id}"
        )

    return state_manager.get_summary()
