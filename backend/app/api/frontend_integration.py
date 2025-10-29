"""Frontend Integration API - Simplified endpoints for web frontend"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

from ..database import get_db
from ..models import GameSession, Character as DBCharacter, Location as DBLocation, Event as DBEvent
from ..services.game_state_manager import get_session, create_session

router = APIRouter(prefix="/api/v1/frontend", tags=["frontend"])


# ========== Simplified Schemas for Frontend ==========

class GameSessionSummary(BaseModel):
    id: str
    name: str
    status: str
    turn_count: int
    current_location: Optional[str] = None
    character_count: int = 0
    last_played: Optional[str] = None


class CharacterSummary(BaseModel):
    id: str
    name: str
    char_class: str
    hp: int
    max_hp: int
    alive: bool
    team: Optional[str] = None


class LocationSummary(BaseModel):
    id: str
    name: str
    description: str
    location_type: str
    visited: bool = False


class GameStateSummary(BaseModel):
    session: GameSessionSummary
    characters: List[CharacterSummary]
    current_location: Optional[LocationSummary] = None
    recent_events: List[Dict[str, Any]] = []


# ========== Frontend-Optimized Endpoints ==========

@router.get("/sessions", response_model=List[GameSessionSummary])
async def list_sessions_summary(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get a simplified list of all game sessions for frontend display"""
    sessions = db.query(GameSession).filter(
        GameSession.deleted_at == None
    ).order_by(GameSession.last_played_at.desc()).limit(limit).all()

    summaries = []
    for session in sessions:
        # Count characters
        char_count = db.query(DBCharacter).filter(
            DBCharacter.session_id == session.id,
            DBCharacter.deleted_at == None
        ).count()

        summaries.append(GameSessionSummary(
            id=session.id,
            name=session.name,
            status=session.status,
            turn_count=session.turn_count,
            current_location=session.current_location_id,
            character_count=char_count,
            last_played=session.last_played_at.isoformat() if session.last_played_at else None
        ))

    return summaries


@router.get("/sessions/{session_id}/state", response_model=GameStateSummary)
async def get_game_state_summary(
    session_id: str,
    db: Session = Depends(get_db)
):
    """Get complete game state in a frontend-friendly format"""
    # Get session
    db_session = db.query(GameSession).filter(
        GameSession.id == session_id,
        GameSession.deleted_at == None
    ).first()

    if not db_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Game session {session_id} not found"
        )

    # Get characters
    characters = db.query(DBCharacter).filter(
        DBCharacter.session_id == session_id,
        DBCharacter.deleted_at == None
    ).all()

    character_summaries = [
        CharacterSummary(
            id=char.id,
            name=char.name,
            char_class=char.char_class,
            hp=char.hp,
            max_hp=char.max_hp,
            alive=char.data.get("alive", True) if char.data else True,
            team=char.team
        )
        for char in characters
    ]

    # Get current location
    current_location = None
    if db_session.current_location_id:
        loc = db.query(DBLocation).filter(
            DBLocation.id == db_session.current_location_id,
            DBLocation.session_id == session_id,
            DBLocation.deleted_at == None
        ).first()

        if loc:
            current_location = LocationSummary(
                id=loc.id,
                name=loc.name,
                description=loc.description,
                location_type=loc.location_type,
                visited=loc.data.get("visited_count", 0) > 0 if loc.data else False
            )

    # Get recent events
    recent_events = db.query(DBEvent).filter(
        DBEvent.session_id == session_id
    ).order_by(DBEvent.created_at.desc()).limit(10).all()

    event_summaries = [
        {
            "id": event.id,
            "type": event.event_type,
            "description": event.description,
            "turn": event.turn_number,
            "timestamp": event.created_at.isoformat()
        }
        for event in recent_events
    ]

    return GameStateSummary(
        session=GameSessionSummary(
            id=db_session.id,
            name=db_session.name,
            status=db_session.status,
            turn_count=db_session.turn_count,
            current_location=db_session.current_location_id,
            character_count=len(character_summaries),
            last_played=db_session.last_played_at.isoformat() if db_session.last_played_at else None
        ),
        characters=character_summaries,
        current_location=current_location,
        recent_events=event_summaries
    )


@router.post("/sessions/{session_id}/quick-action")
async def perform_quick_action(
    session_id: str,
    action: str,
    target_id: Optional[str] = None,
    data: Optional[Dict[str, Any]] = None,
    db: Session = Depends(get_db)
):
    """Perform common game actions with simplified parameters"""
    # Verify session exists
    db_session = db.query(GameSession).filter(
        GameSession.id == session_id,
        GameSession.deleted_at == None
    ).first()

    if not db_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Game session {session_id} not found"
        )

    # Get or create state manager
    state_manager = get_session(session_id)
    if not state_manager:
        state_manager = create_session(session_id)

    result = {"action": action, "success": False, "message": ""}

    if action == "create_character":
        # Quick character creation
        char_data = data or {}
        char_id = f"char_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        character = {
            "id": char_id,
            "name": char_data.get("name", "Adventurer"),
            "char_class": char_data.get("class", "Fighter"),
            "hp": char_data.get("hp", 30),
            "max_hp": char_data.get("max_hp", 30),
            "attack": char_data.get("attack", 10),
            "defense": char_data.get("defense", 5),
            "alive": True,
            "team": char_data.get("team", "player")
        }

        state_manager.add_character(character)

        # Persist to database
        db_char = DBCharacter(
            id=char_id,
            session_id=session_id,
            name=character["name"],
            char_class=character["char_class"],
            hp=character["hp"],
            max_hp=character["max_hp"],
            attack=character["attack"],
            defense=character["defense"],
            team=character["team"],
            data=character
        )
        db.add(db_char)
        db.commit()

        result.update({
            "success": True,
            "message": f"Created character {character['name']}",
            "character_id": char_id
        })

    elif action == "attack":
        # Quick attack action
        if not target_id:
            result["message"] = "Target ID required for attack"
            return result

        attacker = state_manager.get_character(data.get("attacker_id")) if data else None
        target = state_manager.get_character(target_id)

        if not attacker or not target:
            result["message"] = "Attacker or target not found"
            return result

        # Simple attack calculation
        damage = max(1, attacker["attack"] - target["defense"])
        target["hp"] = max(0, target["hp"] - damage)

        if target["hp"] <= 0:
            target["alive"] = False
            message = f"{attacker['name']} defeats {target['name']}!"
        else:
            message = f"{attacker['name']} attacks {target['name']} for {damage} damage!"

        state_manager.update_character(target_id, target)

        # Log event
        event = DBEvent(
            session_id=session_id,
            event_type="combat",
            turn_number=db_session.turn_count,
            summary=message,
            description=message,
            character_ids=[attacker["id"], target_id],
            data={"action": "attack", "damage": damage}
        )
        db.add(event)
        db.commit()

        result.update({
            "success": True,
            "message": message,
            "damage": damage
        })

    elif action == "move":
        # Quick location change
        if not target_id:
            result["message"] = "Location ID required for move"
            return result

        # Verify location exists
        location = db.query(DBLocation).filter(
            DBLocation.id == target_id,
            DBLocation.session_id == session_id,
            DBLocation.deleted_at == None
        ).first()

        if not location:
            result["message"] = "Location not found"
            return result

        # Update session current location
        db_session.current_location_id = target_id
        db_session.updated_at = datetime.now()

        # Update location visited count
        if not location.data:
            location.data = {}
        location.data["visited_count"] = location.data.get("visited_count", 0) + 1
        location.updated_at = datetime.now()

        db.commit()

        result.update({
            "success": True,
            "message": f"Moved to {location.name}",
            "location_id": target_id
        })

    else:
        result["message"] = f"Unknown action: {action}"

    return result


@router.get("/sessions/{session_id}/dashboard")
async def get_dashboard_data(session_id: str, db: Session = Depends(get_db)):
    """Get dashboard data for the frontend"""
    # Get session
    db_session = db.query(GameSession).filter(
        GameSession.id == session_id,
        GameSession.deleted_at == None
    ).first()

    if not db_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Game session {session_id} not found"
        )

    # Get statistics
    char_count = db.query(DBCharacter).filter(
        DBCharacter.session_id == session_id,
        DBCharacter.deleted_at == None
    ).count()

    loc_count = db.query(DBLocation).filter(
        DBLocation.session_id == session_id,
        DBLocation.deleted_at == None
    ).count()

    event_count = db.query(DBEvent).filter(
        DBEvent.session_id == session_id
    ).count()

    # Get recent activity
    recent_events = db.query(DBEvent).filter(
        DBEvent.session_id == session_id
    ).order_by(DBEvent.created_at.desc()).limit(5).all()

    recent_activity = [
        {
            "type": event.event_type,
            "description": event.description,
            "timestamp": event.created_at.isoformat(),
            "turn": event.turn_number
        }
        for event in recent_events
    ]

    return {
        "session_id": session_id,
        "session_name": db_session.name,
        "statistics": {
            "characters": char_count,
            "locations": loc_count,
            "events": event_count,
            "turns": db_session.turn_count
        },
        "recent_activity": recent_activity,
        "status": db_session.status,
        "last_played": db_session.last_played_at.isoformat() if db_session.last_played_at else None
    }
