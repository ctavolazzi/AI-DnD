"""Game Logic API endpoints - Core D&D game mechanics"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
import uuid
import sys
from pathlib import Path

# Add project root to path for dnd_game import
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from dnd_game import Character as GameCharacter

from ..database import get_db
from ..models import GameSession, Character as DBCharacter, Location as DBLocation, Event as DBEvent
from ..services.game_state_manager import get_session, create_session
from ..services.game_service import GameService

router = APIRouter(prefix="/api/v1/game-logic", tags=["game-logic"])


# ========== Pydantic Schemas ==========

class CharacterCreateRequest(BaseModel):
    name: str = Field(..., description="Character name")
    char_class: str = Field(..., description="Character class")
    hp: Optional[int] = None
    max_hp: Optional[int] = None
    attack: Optional[int] = None
    defense: Optional[int] = None
    team: Optional[str] = None


class CharacterResponse(BaseModel):
    """Character response model - matches dnd_game.Character.to_dict() format"""
    id: Optional[str] = None  # Added from character_data
    name: str
    char_class: str
    hp: int
    max_hp: int
    attack: int
    defense: int
    mana: int
    max_mana: int
    alive: bool
    status_effects: List[str]
    ability_scores: Dict[str, int]
    team: Optional[str] = None
    inventory: Optional[Dict[str, Any]] = None
    spells: Optional[List[str]] = None
    proficiency_bonus: Optional[int] = None
    skill_proficiencies: Optional[List[str]] = None
    abilities: Optional[List[str]] = None
    current_location_id: Optional[str] = None


class CombatActionRequest(BaseModel):
    action_type: str = Field(..., description="Type of action (attack, spell, item, etc.)")
    target_id: Optional[str] = None
    spell_name: Optional[str] = None
    item_name: Optional[str] = None
    description: Optional[str] = None


class CombatResult(BaseModel):
    action: str
    attacker: str
    target: Optional[str] = None
    damage: Optional[int] = None
    healing: Optional[int] = None
    status_effect: Optional[str] = None
    description: str
    success: bool
    loot_collected: Optional[Dict[str, Any]] = None


class QuestCreateRequest(BaseModel):
    title: str = Field(..., description="Quest title")
    description: str = Field(..., description="Quest description")
    objectives: List[Dict[str, Any]] = Field(default=[], description="Quest objectives")
    reward_type: str = Field(default="experience", description="Type of reward")
    reward_value: int = Field(default=100, description="Reward value")


class QuestResponse(BaseModel):
    id: str
    title: str
    description: str
    status: str
    objectives: List[Dict[str, Any]]
    reward_type: str
    reward_value: int
    created_at: str
    completed_at: Optional[str] = None


# ========== Character Management ==========

@router.post("/sessions/{session_id}/characters", response_model=CharacterResponse)
async def create_character(
    session_id: str,
    request: CharacterCreateRequest,
    db: Session = Depends(get_db)
):
    """Create a new character in the game session"""
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

    # Create character using dnd_game.Character (game logic)
    char_id = f"char_{uuid.uuid4().hex[:12]}"

    # Create game character instance
    game_character = GameCharacter(
        name=request.name,
        char_class=request.char_class,
        hp=request.hp,
        max_hp=request.max_hp,
        attack=request.attack,
        defense=request.defense,
        character_id=char_id
    )

    # Set team if provided
    if request.team:
        game_character.team = request.team

    # Convert to dict for state manager (using to_dict)
    character_data = game_character.to_dict()
    character_data["id"] = char_id
    character_data["current_location_id"] = db_session.current_location_id

    # Add to state manager
    state_manager.add_character(char_id, character_data)

    # Convert to database format using to_db_dict
    db_char_dict = game_character.to_db_dict(char_id, session_id)
    db_char_dict["current_location_id"] = db_session.current_location_id

    # Create SQLAlchemy model
    db_character = DBCharacter(**db_char_dict)
    db.add(db_character)
    db.commit()
    db.refresh(db_character)

    # Invalidate cache so new character is picked up by game service
    GameService.get_instance().invalidate_cache(session_id)

    # Return response using game character dict
    return CharacterResponse(**character_data)


@router.get("/sessions/{session_id}/characters", response_model=List[CharacterResponse])
async def get_characters(
    session_id: str,
    team: Optional[str] = None,
    alive_only: bool = False
):
    """Get all characters in the session, optionally filtered by team or alive status"""
    state_manager = get_session(session_id)

    if not state_manager:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No active session {session_id}"
        )

    characters = state_manager.get_all_characters()

    if team:
        characters = [c for c in characters if c.get("team") == team]

    if alive_only:
        characters = [c for c in characters if c.get("alive", True)]

    return [CharacterResponse(**char) for char in characters]


@router.get("/sessions/{session_id}/characters/{char_id}", response_model=CharacterResponse)
async def get_character(
    session_id: str,
    char_id: str
):
    """Get a specific character"""
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

    return CharacterResponse(**character)


# ========== Combat System ==========

@router.post("/sessions/{session_id}/combat/action", response_model=CombatResult)
async def perform_combat_action(
    session_id: str,
    char_id: str,
    request: CombatActionRequest,
    db: Session = Depends(get_db)
):
    """Perform a combat action (attack, spell, item use, etc.)"""
    db_session = db.query(GameSession).filter(
        GameSession.id == session_id,
        GameSession.deleted_at == None
    ).first()

    if not db_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Game session {session_id} not found"
        )

    db_character = db.query(DBCharacter).filter(
        DBCharacter.id == char_id,
        DBCharacter.session_id == session_id,
        DBCharacter.deleted_at == None
    ).first()

    if not db_character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character {char_id} not found"
        )

    try:
        # Define the action to execute in the thread pool
        def combat_action(game):
            # Find the actor character object in the loaded game instance
            # We need to find by ID or name. dnd_game.Character has .id field now.
            actor = next((c for c in game.players + game.enemies if c.id == char_id), None)
            # Fallback to name match if ID is missing (legacy support)
            if not actor:
                actor = next((c for c in game.players + game.enemies if c.name == db_character.name), None)

            if not actor:
                raise ValueError(f"Character {char_id} not found in active game state")

            if request.action_type == "attack":
                if not request.target_id:
                    raise ValueError("Target ID required for attack action")

                # Find target in game instance
                # Assume target_id is DB ID. We need to check if dnd_game supports IDs or just names
                # With our refactor, Character has .id
                target = next((c for c in game.players + game.enemies if c.id == request.target_id), None)
                if not target:
                    raise ValueError(f"Target character {request.target_id} not found")

                result = actor.attack_target(target)

                return {
                    "action": "attack",
                    "attacker": actor.name,
                    "target": target.name,
                    "damage": result.get("damage_dealt", 0),
                    "description": f"{actor.name} attacks {target.name}",
                    "success": True,
                    "loot_collected": result.get("loot_collected")
                }

            elif request.action_type == "heal":
                # Implement heal logic via GameService/Engine
                # For now, reuse simple logic or call actor abilities if available
                if "Heal" in actor.abilities:
                    # Heal self or target
                    target = actor # Default to self
                    if request.target_id:
                        target = next((c for c in game.players + game.enemies if c.id == request.target_id), actor)

                    old_hp = target.hp
                    actor.abilities["Heal"](target)
                    healed = target.hp - old_hp

                    return {
                        "action": "heal",
                        "attacker": actor.name,
                        "target": target.name,
                        "healing": healed,
                        "description": f"{actor.name} heals {target.name}",
                        "success": True
                    }
                else:
                    # Fallback generic heal
                    return {
                        "action": "heal",
                        "attacker": actor.name,
                        "description": "Character cannot heal",
                        "success": False
                    }

            else:
                raise ValueError(f"Unknown action type: {request.action_type}")

        # Execute via GameService
        result = await GameService.get_instance().execute_action(session_id, combat_action)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc)
        ) from exc

    return CombatResult(**result)


@router.get("/sessions/{session_id}/combat/status")
async def get_combat_status(session_id: str):
    """Get current combat status for all characters"""
    # This should ideally read from the GameService cache or DB
    # For consistency, we can reload the game state via service to ensure latest snapshot
    # But that might be heavy for a status poll.
    # Better: Read from DB which is updated by GameService snapshotting

    db = next(get_db()) # Get session manually or use dependency injection pattern if refactored
    try:
        characters = db.query(DBCharacter).filter(
            DBCharacter.session_id == session_id,
            DBCharacter.deleted_at == None
        ).all()

        alive_characters = [c for c in characters if c.alive]

        return {
            "session_id": session_id,
            "total_characters": len(characters),
            "alive_characters": len(alive_characters),
            "characters": [
                {
                    "id": c.id,
                    "name": c.name,
                    "hp": c.hp,
                    "max_hp": c.max_hp,
                    "alive": c.alive,
                    "team": c.team
                }
                for c in characters
            ]
        }
    finally:
        db.close()


# ========== Quest System ==========

@router.post("/sessions/{session_id}/quests", response_model=QuestResponse)
async def create_quest(
    session_id: str,
    request: QuestCreateRequest,
    db: Session = Depends(get_db)
):
    """Create a new quest for the session"""
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

    quest_id = f"quest_{uuid.uuid4().hex[:12]}"
    quest_data = {
        "id": quest_id,
        "title": request.title,
        "description": request.description,
        "status": "active",
        "objectives": request.objectives,
        "reward_type": request.reward_type,
        "reward_value": request.reward_value,
        "created_at": datetime.now().isoformat(),
        "completed_at": None
    }

    # Add to session quest progress
    if not db_session.quest_progress:
        db_session.quest_progress = {}

    db_session.quest_progress[quest_id] = quest_data
    db.commit()

    return QuestResponse(**quest_data)


@router.get("/sessions/{session_id}/quests", response_model=List[QuestResponse])
async def get_quests(
    session_id: str,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all quests for the session"""
    db_session = db.query(GameSession).filter(
        GameSession.id == session_id,
        GameSession.deleted_at == None
    ).first()

    if not db_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Game session {session_id} not found"
        )

    quests = []
    if db_session.quest_progress:
        for quest_data in db_session.quest_progress.values():
            if not status or quest_data.get("status") == status:
                quests.append(QuestResponse(**quest_data))

    return quests
