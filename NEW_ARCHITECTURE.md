# AI-DnD New Architecture

## Overview

This document describes the new, clean architecture built for AI-DnD with proper data persistence, state management, and a modern frontend.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (game-client.html)              │
│  - Modern UI with welcome screen                            │
│  - Game interface with narrative & characters               │
│  - Save/Load functionality                                  │
│  - Real-time state updates                                  │
└─────────────────────────────────────────────────────────────┘
                            ↕ HTTP/JSON API
┌─────────────────────────────────────────────────────────────┐
│                FastAPI Backend (backend/app/)                │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  API Endpoints (/api/v1/game/*)                      │   │
│  │  - POST   /sessions          Create new game         │   │
│  │  - GET    /sessions          List saved games        │   │
│  │  - GET    /sessions/:id      Get session details     │   │
│  │  - POST   /sessions/:id/load Load game state         │   │
│  │  - POST   /sessions/:id/save Save game state         │   │
│  │  - GET    /sessions/:id/state Get full state         │   │
│  │  - POST   /sessions/:id/turns/next Advance turn      │   │
│  │  - GET    /sessions/:id/characters Get characters    │   │
│  │  - PUT    /sessions/:id/characters/:id Update char   │   │
│  │  - GET    /sessions/:id/events Get event history     │   │
│  └──────────────────────────────────────────────────────┘   │
│                            ↕                                  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  GameStateManager (In-Memory)                        │   │
│  │  - Fast access to game state                         │   │
│  │  - JSON serialization                                │   │
│  │  - Integrity checksums                               │   │
│  │  - Character/Location/Event management               │   │
│  └──────────────────────────────────────────────────────┘   │
│                            ↕                                  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  SQLAlchemy Models + SQLite Database                 │   │
│  │  - GameSession (session metadata + state snapshot)   │   │
│  │  - Character (persistent character data)             │   │
│  │  - Location (world locations)                        │   │
│  │  - Event (narrative history with integrity checks)   │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Key Improvements

### 1. **Data Persistence** ✅

**Problem Solved:** Game state was lost when process exited

**Solution:**
- SQLite database with SQLAlchemy ORM
- Proper migrations with Alembic
- Auto-save functionality
- Load game from any point

### 2. **State Management** ✅

**Problem Solved:** Multiple sources of truth, manual synchronization

**Solution:**
- `GameStateManager` class handles all in-memory state
- Single source of truth pattern
- Automatic JSON serialization
- Fast read/write operations

### 3. **Data Integrity** ✅

**Problem Solved:** No way to verify data consistency

**Solution:**
- SHA-256 checksums for state snapshots
- Event sourcing pattern for audit trail
- State snapshots with timestamps
- Verification on load

### 4. **API Architecture** ✅

**Problem Solved:** Direct file manipulation, no CRUD operations

**Solution:**
- RESTful FastAPI endpoints
- Proper HTTP verbs (GET/POST/PUT/DELETE)
- Pydantic schemas for validation
- CORS enabled for browser clients

### 5. **Modern Frontend** ✅

**Problem Solved:** Complex UI, poor user experience

**Solution:**
- Clean, gradient-based design
- Welcome screen with new/load game
- Real-time state updates
- Responsive layout

## Data Flow

### Creating a New Game

```
User clicks "New Adventure"
  ↓
Frontend → POST /api/v1/game/sessions
  ↓
Backend creates:
  - GameSession record in DB
  - GameStateManager in memory
  - Returns session_id
  ↓
Frontend → GET /api/v1/game/sessions/{id}/state
  ↓
Backend returns initial state
  ↓
Frontend displays game screen
```

### Playing a Turn

```
User clicks "Next Turn"
  ↓
Frontend → POST /api/v1/game/sessions/{id}/turns/next
  {
    events: [...]
  }
  ↓
Backend:
  - Increments turn in GameStateManager
  - Adds events to in-memory state
  - Persists events to database
  - Auto-saves state snapshot
  ↓
Frontend → GET /api/v1/game/sessions/{id}/state
  ↓
Backend returns updated state
  ↓
Frontend updates UI (narrative, characters)
```

### Saving Game

```
User clicks "Save"
  ↓
Frontend → POST /api/v1/game/sessions/{id}/save
  ↓
Backend:
  - Gets state from GameStateManager
  - Creates snapshot with checksum
  - Updates GameSession.state_snapshot
  - Commits to database
  ↓
Returns success with checksum
```

### Loading Game

```
User selects saved game
  ↓
Frontend → POST /api/v1/game/sessions/{id}/load
  ↓
Backend:
  - Reads GameSession from database
  - Creates/updates GameStateManager
  - Loads state_snapshot into memory
  - Verifies integrity (optional)
  - Updates last_played_at
  ↓
Returns loaded state summary
  ↓
Frontend displays game screen with loaded state
```

## Database Schema

### GameSession Table

```sql
CREATE TABLE game_sessions (
    id VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_played_at TIMESTAMP,
    turn_count INTEGER DEFAULT 0,
    status VARCHAR DEFAULT 'active',
    current_location_id VARCHAR,
    state_snapshot JSON,  -- Complete game state
    current_quest TEXT,
    quest_progress JSON,
    difficulty VARCHAR DEFAULT 'medium',
    ai_model VARCHAR DEFAULT 'mistral',
    deleted_at TIMESTAMP
);
```

### Character Table

```sql
CREATE TABLE characters (
    id VARCHAR PRIMARY KEY,
    session_id VARCHAR REFERENCES game_sessions(id) ON DELETE CASCADE,
    name VARCHAR NOT NULL,
    char_class VARCHAR NOT NULL,
    team VARCHAR DEFAULT 'players',
    hp INTEGER NOT NULL,
    max_hp INTEGER NOT NULL,
    mana INTEGER DEFAULT 0,
    max_mana INTEGER DEFAULT 0,
    attack INTEGER NOT NULL,
    defense INTEGER NOT NULL,
    ability_scores JSON,
    alive BOOLEAN DEFAULT TRUE,
    current_location_id VARCHAR,
    status_effects JSON DEFAULT '[]',
    inventory JSON DEFAULT '{}',
    spells JSON DEFAULT '[]',
    proficiency_bonus INTEGER DEFAULT 2,
    skill_proficiencies JSON DEFAULT '[]',
    bio TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);
```

### Location Table

```sql
CREATE TABLE locations (
    id VARCHAR PRIMARY KEY,
    session_id VARCHAR REFERENCES game_sessions(id) ON DELETE CASCADE,
    name VARCHAR NOT NULL,
    description TEXT,
    location_type VARCHAR DEFAULT 'wilderness',
    connections JSON DEFAULT '{}',
    npcs JSON DEFAULT '[]',
    services JSON DEFAULT '[]',
    encounter_chance INTEGER DEFAULT 30,
    encounter_types JSON DEFAULT '[]',
    visited INTEGER DEFAULT 0,
    cleared BOOLEAN DEFAULT FALSE,
    character_ids JSON DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);
```

### Event Table

```sql
CREATE TABLE events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id VARCHAR REFERENCES game_sessions(id) ON DELETE CASCADE,
    event_type VARCHAR NOT NULL,
    turn_number INTEGER NOT NULL,
    summary VARCHAR NOT NULL,
    description TEXT,
    location_id VARCHAR,
    character_ids JSON DEFAULT '[]',
    data JSON DEFAULT '{}',
    state_before JSON,  -- For reconstruction
    state_after JSON,   -- For reconstruction
    checksum VARCHAR,   -- Integrity verification
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## GameStateManager API

### Core Methods

```python
# Session Management
manager = GameStateManager(session_id)
state = manager.get_state()  # Get full state dict
json_str = manager.to_json()  # Serialize to JSON
manager.from_json(json_str)  # Load from JSON

# Snapshots & Integrity
snapshot = manager.snapshot()  # Create snapshot with checksum
is_valid = manager.verify_integrity(snapshot, checksum)

# Character Management
manager.add_character(char_id, char_data)
char = manager.get_character(char_id)
manager.update_character(char_id, {'hp': 50})
manager.remove_character(char_id)
alive_chars = manager.get_alive_characters()

# Location Management
manager.add_location(loc_id, loc_data)
loc = manager.get_location(loc_id)
manager.update_location(loc_id, {'visited': True})
manager.set_current_location(loc_id)
current_loc = manager.get_current_location()

# Event Management
manager.add_event(event_data)
recent = manager.get_recent_events(limit=10)
turn_events = manager.get_events_by_turn(5)

# Turn Management
new_turn = manager.next_turn()
turn = manager.get_turn()

# Status Management
manager.set_status('completed')
status = manager.get_status()

# Utility
summary = manager.get_summary()  # Quick overview
```

## API Endpoints Reference

### Game Session Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST   | `/api/v1/game/sessions` | Create new game session |
| GET    | `/api/v1/game/sessions` | List all saved games |
| GET    | `/api/v1/game/sessions/{id}` | Get session details |
| DELETE | `/api/v1/game/sessions/{id}` | Delete session (soft delete) |

### State Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET    | `/api/v1/game/sessions/{id}/state` | Get full game state |
| POST   | `/api/v1/game/sessions/{id}/save` | Save state to database |
| POST   | `/api/v1/game/sessions/{id}/load` | Load state from database |

### Turn Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST   | `/api/v1/game/sessions/{id}/turns/next` | Advance to next turn |

### Character Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET    | `/api/v1/game/sessions/{id}/characters` | Get all characters |
| PUT    | `/api/v1/game/sessions/{id}/characters/{char_id}` | Update character |

### Narrative History

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET    | `/api/v1/game/sessions/{id}/events` | Get event history |

### Utility

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET    | `/api/v1/game/active-sessions` | Get active in-memory sessions |
| GET    | `/api/v1/game/sessions/{id}/summary` | Get quick summary |

## Running the System

### 1. Start the Backend

```bash
cd backend
# Install dependencies (if needed)
pip install -r requirements.txt

# Run FastAPI server
python -m app.main
# Or: uvicorn app.main:app --reload

# Backend runs on http://localhost:8000
# API docs: http://localhost:8000/docs
```

### 2. Open the Frontend

```bash
# Simply open in a browser:
open game-client.html

# Or serve with a simple HTTP server:
python -m http.server 8080
# Then visit: http://localhost:8080/game-client.html
```

### 3. Test the System

```bash
# Health check
curl http://localhost:8000/health

# Create a new game
curl -X POST http://localhost:8000/api/v1/game/sessions \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Adventure", "difficulty": "medium"}'

# List games
curl http://localhost:8000/api/v1/game/sessions
```

## Development Guide

### Adding a New Feature

1. **Update Model** (if needed)
   - Edit `backend/app/models/*.py`
   - Create migration: `alembic revision --autogenerate -m "description"`
   - Run migration: `alembic upgrade head`

2. **Update State Manager** (if needed)
   - Edit `backend/app/services/game_state_manager.py`
   - Add methods for new data

3. **Add API Endpoint**
   - Edit `backend/app/api/game.py`
   - Add route with proper HTTP verb
   - Add Pydantic schemas for validation

4. **Update Frontend**
   - Edit `game-client.html`
   - Add UI components
   - Add API calls

### Example: Adding Location Movement

```python
# 1. State Manager (game_state_manager.py)
def move_character(self, char_id: str, new_location_id: str):
    char = self.get_character(char_id)
    if char:
        old_location = char.get('current_location_id')
        self.update_character(char_id, {'current_location_id': new_location_id})
        self.add_event({
            'type': 'movement',
            'summary': f"{char['name']} moved to {new_location_id}",
            'character_ids': [char_id],
            'data': {'from': old_location, 'to': new_location_id}
        })

# 2. API Endpoint (api/game.py)
@router.post("/sessions/{session_id}/characters/{char_id}/move")
async def move_character(session_id: str, char_id: str, new_location_id: str):
    manager = get_session(session_id)
    if not manager:
        raise HTTPException(404, "Session not found")

    manager.move_character(char_id, new_location_id)
    return {"moved": True, "new_location": new_location_id}

# 3. Frontend (game-client.html)
async function moveCharacter(charId, locationId) {
    await apiCall(`/sessions/${currentSession.id}/characters/${charId}/move?new_location_id=${locationId}`, 'POST');
    await refreshGameState();
}
```

## Benefits of New Architecture

### ✅ Data Persistence
- Games saved to SQLite database
- Resume from any point
- Multiple save slots
- No data loss on crash

### ✅ Performance
- In-memory state for fast access
- Database only for persistence
- Async operations don't block
- Efficient JSON serialization

### ✅ Maintainability
- Clear separation of concerns
- RESTful API design
- Type-safe with Pydantic
- Easy to add new features

### ✅ Scalability
- Can migrate to PostgreSQL easily
- Can add Redis cache layer
- Can add authentication
- Can add multiplayer

### ✅ Data Integrity
- SHA-256 checksums
- Event sourcing audit trail
- State verification on load
- Cascade deletes prevent orphans

### ✅ Developer Experience
- Interactive API docs at `/docs`
- Clear error messages
- Type hints everywhere
- Well-documented code

## Migration Path from Old System

To integrate the old game logic with the new architecture:

1. **Character Creation**: Instead of creating Character objects directly, call the API
2. **Game Loop**: Replace turn execution with API calls to `/turns/next`
3. **State Updates**: Use `PUT /characters/{id}` instead of direct object modification
4. **Event Logging**: Use the events API instead of Obsidian logger
5. **Narrative Generation**: Keep Ollama calls, but send results through API

## Future Enhancements

- [ ] WebSocket support for real-time multiplayer
- [ ] User authentication with JWT
- [ ] Image generation integration
- [ ] Advanced combat system
- [ ] Quest system API
- [ ] World exploration mechanics
- [ ] Character customization
- [ ] Export/import game data

## Conclusion

This new architecture provides:
- ✅ Clean separation of frontend/backend
- ✅ Proper data persistence
- ✅ Fast in-memory state management
- ✅ Data integrity verification
- ✅ Modern, maintainable codebase
- ✅ Easy to extend and modify
- ✅ Production-ready foundation

You now have a solid, scalable foundation for AI-DnD that can grow with your needs!
