"""Narrative and World Management API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

from ..database import get_db
from ..models import GameSession, Location as DBLocation, Event as DBEvent
from ..services.game_state_manager import get_session, create_session

router = APIRouter(prefix="/api/v1/narrative", tags=["narrative"])


# ========== Pydantic Schemas ==========

class LocationCreateRequest(BaseModel):
    name: str = Field(..., description="Location name")
    description: str = Field(..., description="Location description")
    location_type: str = Field(default="general", description="Type of location")
    connections: List[str] = Field(default=[], description="Connected location IDs")
    npcs: List[Dict[str, Any]] = Field(default=[], description="NPCs in this location")
    items: List[Dict[str, Any]] = Field(default=[], description="Items in this location")
    events: List[Dict[str, Any]] = Field(default=[], description="Possible events")


class LocationResponse(BaseModel):
    id: str
    name: str
    description: str
    location_type: str
    connections: List[str]
    npcs: List[Dict[str, Any]]
    items: List[Dict[str, Any]]
    events: List[Dict[str, Any]]
    created_at: str
    visited_count: int = 0


class NarrativeEventRequest(BaseModel):
    event_type: str = Field(..., description="Type of narrative event")
    description: str = Field(..., description="Event description")
    location_id: Optional[str] = None
    character_ids: List[str] = Field(default=[], description="Characters involved")
    data: Dict[str, Any] = Field(default={}, description="Additional event data")


class NarrativeEventResponse(BaseModel):
    id: str
    event_type: str
    description: str
    location_id: Optional[str]
    character_ids: List[str]
    data: Dict[str, Any]
    turn_number: int
    created_at: str


class WorldStateResponse(BaseModel):
    session_id: str
    current_location_id: Optional[str]
    locations: List[LocationResponse]
    recent_events: List[NarrativeEventResponse]
    world_events: List[Dict[str, Any]]


# ========== Location Management ==========

@router.post("/sessions/{session_id}/locations", response_model=LocationResponse)
async def create_location(
    session_id: str,
    request: LocationCreateRequest,
    db: Session = Depends(get_db)
):
    """Create a new location in the game world"""
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

    location_id = f"loc_{uuid.uuid4().hex[:12]}"
    location_data = {
        "id": location_id,
        "name": request.name,
        "description": request.description,
        "location_type": request.location_type,
        "connections": request.connections,
        "npcs": request.npcs,
        "items": request.items,
        "events": request.events,
        "created_at": datetime.now().isoformat(),
        "visited_count": 0
    }

    # Persist to database
    db_location = DBLocation(
        id=location_id,
        session_id=session_id,
        name=request.name,
        description=request.description,
        location_type=request.location_type,
        data=location_data
    )
    db.add(db_location)
    db.commit()

    return LocationResponse(**location_data)


@router.get("/sessions/{session_id}/locations", response_model=List[LocationResponse])
async def get_locations(
    session_id: str,
    location_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all locations in the session"""
    query = db.query(DBLocation).filter(
        DBLocation.session_id == session_id,
        DBLocation.deleted_at == None
    )

    if location_type:
        query = query.filter(DBLocation.location_type == location_type)

    locations = query.all()

    return [
        LocationResponse(
            id=loc.id,
            name=loc.name,
            description=loc.description,
            location_type=loc.location_type,
            connections=loc.data.get("connections", []) if loc.data else [],
            npcs=loc.data.get("npcs", []) if loc.data else [],
            items=loc.data.get("items", []) if loc.data else [],
            events=loc.data.get("events", []) if loc.data else [],
            created_at=loc.created_at.isoformat(),
            visited_count=loc.data.get("visited_count", 0) if loc.data else 0
        )
        for loc in locations
    ]


@router.get("/sessions/{session_id}/locations/{location_id}", response_model=LocationResponse)
async def get_location(
    session_id: str,
    location_id: str,
    db: Session = Depends(get_db)
):
    """Get a specific location"""
    location = db.query(DBLocation).filter(
        DBLocation.id == location_id,
        DBLocation.session_id == session_id,
        DBLocation.deleted_at == None
    ).first()

    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Location {location_id} not found"
        )

    return LocationResponse(
        id=location.id,
        name=location.name,
        description=location.description,
        location_type=location.location_type,
        connections=location.data.get("connections", []) if location.data else [],
        npcs=location.data.get("npcs", []) if location.data else [],
        items=location.data.get("items", []) if location.data else [],
        events=location.data.get("events", []) if location.data else [],
        created_at=location.created_at.isoformat(),
        visited_count=location.data.get("visited_count", 0) if location.data else 0
    )


@router.post("/sessions/{session_id}/locations/{location_id}/visit")
async def visit_location(
    session_id: str,
    location_id: str,
    db: Session = Depends(get_db)
):
    """Mark a location as visited and update session current location"""
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

    # Get location
    location = db.query(DBLocation).filter(
        DBLocation.id == location_id,
        DBLocation.session_id == session_id,
        DBLocation.deleted_at == None
    ).first()

    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Location {location_id} not found"
        )

    # Update location visited count
    if not location.data:
        location.data = {}

    location.data["visited_count"] = location.data.get("visited_count", 0) + 1
    location.updated_at = datetime.now()

    # Update session current location
    db_session.current_location_id = location_id
    db_session.updated_at = datetime.now()

    db.commit()

    return {
        "location_id": location_id,
        "visited_count": location.data["visited_count"],
        "current_location": True
    }


# ========== Narrative Events ==========

@router.post("/sessions/{session_id}/events", response_model=NarrativeEventResponse)
async def create_narrative_event(
    session_id: str,
    request: NarrativeEventRequest,
    db: Session = Depends(get_db)
):
    """Create a narrative event"""
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

    event_id = f"event_{uuid.uuid4().hex[:12]}"
    event_data = {
        "id": event_id,
        "event_type": request.event_type,
        "description": request.description,
        "location_id": request.location_id,
        "character_ids": request.character_ids,
        "data": request.data,
        "turn_number": db_session.turn_count,
        "created_at": datetime.now().isoformat()
    }

    # Persist to database
    db_event = DBEvent(
        id=event_id,
        session_id=session_id,
        event_type=request.event_type,
        turn_number=db_session.turn_count,
        summary=request.description[:100],  # Truncate for summary
        description=request.description,
        location_id=request.location_id,
        character_ids=request.character_ids,
        data=event_data
    )
    db.add(db_event)
    db.commit()

    return NarrativeEventResponse(**event_data)


@router.get("/sessions/{session_id}/events", response_model=List[NarrativeEventResponse])
async def get_narrative_events(
    session_id: str,
    event_type: Optional[str] = None,
    location_id: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get narrative events for the session"""
    query = db.query(DBEvent).filter(DBEvent.session_id == session_id)

    if event_type:
        query = query.filter(DBEvent.event_type == event_type)

    if location_id:
        query = query.filter(DBEvent.location_id == location_id)

    events = query.order_by(DBEvent.created_at.desc()).limit(limit).all()

    return [
        NarrativeEventResponse(
            id=event.id,
            event_type=event.event_type,
            description=event.description,
            location_id=event.location_id,
            character_ids=event.character_ids,
            data=event.data,
            turn_number=event.turn_number,
            created_at=event.created_at.isoformat()
        )
        for event in events
    ]


# ========== World State ==========

@router.get("/sessions/{session_id}/world-state", response_model=WorldStateResponse)
async def get_world_state(
    session_id: str,
    db: Session = Depends(get_db)
):
    """Get complete world state including locations and recent events"""
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

    # Get all locations
    locations = db.query(DBLocation).filter(
        DBLocation.session_id == session_id,
        DBLocation.deleted_at == None
    ).all()

    location_responses = [
        LocationResponse(
            id=loc.id,
            name=loc.name,
            description=loc.description,
            location_type=loc.location_type,
            connections=loc.data.get("connections", []) if loc.data else [],
            npcs=loc.data.get("npcs", []) if loc.data else [],
            items=loc.data.get("items", []) if loc.data else [],
            events=loc.data.get("events", []) if loc.data else [],
            created_at=loc.created_at.isoformat(),
            visited_count=loc.data.get("visited_count", 0) if loc.data else 0
        )
        for loc in locations
    ]

    # Get recent events
    recent_events = db.query(DBEvent).filter(
        DBEvent.session_id == session_id
    ).order_by(DBEvent.created_at.desc()).limit(20).all()

    event_responses = [
        NarrativeEventResponse(
            id=event.id,
            event_type=event.event_type,
            description=event.description,
            location_id=event.location_id,
            character_ids=event.character_ids,
            data=event.data,
            turn_number=event.turn_number,
            created_at=event.created_at.isoformat()
        )
        for event in recent_events
    ]

    return WorldStateResponse(
        session_id=session_id,
        current_location_id=db_session.current_location_id,
        locations=location_responses,
        recent_events=event_responses,
        world_events=[]  # Placeholder for future world events
    )


# ========== AI Narrative Generation ==========

@router.post("/sessions/{session_id}/generate-narrative")
async def generate_narrative(
    session_id: str,
    prompt: str,
    context: Optional[Dict[str, Any]] = None
):
    """Generate narrative content using AI (placeholder for future integration)"""
    # This would integrate with the existing narrative engine
    # For now, return a placeholder response

    return {
        "session_id": session_id,
        "prompt": prompt,
        "generated_text": f"Generated narrative for: {prompt}",
        "context": context or {},
        "status": "placeholder"
    }
