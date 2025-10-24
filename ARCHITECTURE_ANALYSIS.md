# ARCHITECTURE ANALYSIS
## Data Structures, Flow, and Integrity

**Generated:** 2025-10-24
**Purpose:** Identify architectural issues, data conflicts, and design improvements

---

# 1. DATA STRUCTURES INVENTORY

## Core Game Data

### Character Data (MULTIPLE DEFINITIONS - ⚠️ CONFLICT!)

**Definition 1: `dnd_game.py` - Character class**
```python
class Character:
    name: str
    char_class: str  # "Fighter", "Wizard", "Rogue", "Cleric", "Goblin", etc.
    team: str | None
    hp: int
    max_hp: int
    attack: int
    defense: int
    alive: bool
    status_effects: List[str]
    ability_scores: dict  # STR, DEX, CON, INT, WIS, CHA
    proficiency_bonus: int
    skill_proficiencies: List[str]
    abilities: dict  # Special abilities
    # NO INVENTORY FIELD
```

**Definition 2: `character.py` - Character class**
```python
class Character:
    config: dict
    # Contains:
    #   "character_class": "Warrior"  # ⚠️ Different from char_class!
    #   "inventory": [{"id": "journal", "entries": []}, {"gold": 0}]
    #   Various other fields
```

**Definition 3: `session_service/schemas.py` - CharacterModel**
```python
class CharacterModel(BaseModel):
    name: str
    char_class: str
    hp: int
    max_hp: int
    alive: bool
    # NO inventory, NO abilities
```

**🚨 PROBLEM: Three different Character representations with incompatible fields!**

---

### Inventory Data (NEW - NOT INTEGRATED)

**Definition: `items.py` - Inventory class**
```python
class Inventory:
    capacity: int = 20
    items: Dict[str, int]  # item_id: quantity
    equipped: Dict[str, str]  # slot: item_id
    gold: int
```

**🚨 PROBLEM: Character in dnd_game.py has NO inventory field!**

---

### Location/World Data (MULTIPLE DEFINITIONS - ⚠️ CONFLICT!)

**Definition 1: `world.py` - Location class**
```python
class Location:
    name: str
    description: str
    connections: dict  # direction: location_name
```

**Definition 2: `world_builder.py` - Location class**
```python
class Location:
    location_id: str
    name: str
    location_type: LocationType
    description: str
    connections: Dict[str, str]  # direction: location_id
    encounter_chance: float
    encounter_table: str
    npcs: List[str]
    services: List[str]
    items: List[str]
    visited: bool
    cleared: bool
    coordinates: Tuple[int, int]
```

**🚨 PROBLEM: Two incompatible Location classes!**

---

### Quest Data

**Definition: `quest_system.py`**
```python
class QuestObjective:
    description: str
    objective_type: str  # defeat, collect, explore, talk
    target: str | None
    quantity: int
    progress: int
    status: ObjectiveStatus

class Quest:
    quest_id: str
    title: str
    description: str
    objectives: List[QuestObjective]
    rewards: Dict[str, Any]  # {"exp": 500, "gold": 100}
    status: QuestStatus
    giver: str | None
    completion_time: datetime | None
```

**✅ GOOD: Single source of truth**

---

### Game State Data (MULTIPLE DEFINITIONS - ⚠️ CONFLICT!)

**Definition 1: `game_state.py`**
```python
class GameState:
    current_turn: int = 0
    player_position: tuple = (0, 0)
    inventory: list = []
    # Very basic
```

**Definition 2: `dungeon_master.py` - current_run_data**
```python
current_run_data = {
    "run_id": str,
    "start_time": str,
    "status": str,
    "turn_count": int,
    "characters": List,
    "events": List,
    "combat": List,
    "locations": List,
    "sessions": List,
    "conclusion": str | None,
    "error_details": str | None
}
```

**Definition 3: `dnd_game.py` - DnDGame state**
```python
class DnDGame:
    players: List[Character]
    enemies: List[Character]
    narrative_engine: NarrativeEngine
    current_location: str  # Just a string!
    current_quest: Quest | None
    scene_counter: int
```

**🚨 PROBLEM: Game state scattered across 3 places!**

---

### Item Data (NEW - ISOLATED)

**Definition: `items.py`**
```python
class Item:
    item_id: str
    name: str
    item_type: ItemType
    description: str
    value: int  # Gold value
    rarity: ItemRarity
    effects: List[ItemEffect]
    stackable: bool
    max_stack: int
    equippable: bool
    slot: str | None
    stats: Dict[str, int]  # {"attack": 5, "defense": 2}

# Global dictionary
ITEMS: Dict[str, Item] = {...}
```

**✅ GOOD: Single source of truth**
**⚠️ WARNING: Not connected to Character or Inventory yet**

---

# 2. DATA FLOW ANALYSIS

## Current Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    INITIALIZATION                               │
└─────────────────────────────────────────────────────────────────┘
main.py
  ↓
DungeonMaster.__init__()
  ↓
DungeonMaster.initialize_run()
  ├─→ Creates current_run_data (dict)  ← SOURCE OF TRUTH #1
  ├─→ Creates GameEventManager(run_data)
  ├─→ Creates GameManager
  └─→ Creates QuestManager
  ↓
DungeonMaster.initialize_game()
  ├─→ Creates DnDGame()  ← SOURCE OF TRUTH #2
  │    ├─→ Creates Character objects (dnd_game.py version)
  │    └─→ Stores in game.players, game.enemies
  └─→ Creates Quest objects via QuestManager


┌─────────────────────────────────────────────────────────────────┐
│                    MAIN GAME LOOP                               │
└─────────────────────────────────────────────────────────────────┘
For each turn:
  ↓
  DungeonMaster.run_game_loop()
    ↓
    ┌─────────────────────────────────────────┐
    │ 1. Update turn counter                   │
    │    current_run_data["turn_count"] += 1   │
    └─────────────────────────────────────────┘
    ↓
    ┌─────────────────────────────────────────┐
    │ 2. Generate scene (AI)                   │
    │    narrative_engine.describe_scene()     │
    │    ↓                                     │
    │    Log to Obsidian (Markdown files)      │
    └─────────────────────────────────────────┘
    ↓
    ┌─────────────────────────────────────────┐
    │ 3. For each player:                      │
    │    - Generate choices (AI)               │
    │    - Make skill check                    │
    │      ↓                                   │
    │      Modify Character.hp (in-memory)     │
    │      ↓                                   │
    │      Log to Obsidian                     │
    │      ↓                                   │
    │      Update quest progress               │
    └─────────────────────────────────────────┘
    ↓
    ┌─────────────────────────────────────────┐
    │ 4. Check for encounters                  │
    │    - Create enemy Characters             │
    │    - Run combat                          │
    │      ↓                                   │
    │      Modify Character.hp                 │
    │      ↓                                   │
    │      Set Character.alive = False         │
    │      ↓                                   │
    │      Log to Obsidian                     │
    └─────────────────────────────────────────┘
    ↓
    ┌─────────────────────────────────────────┐
    │ 5. Update Obsidian files                 │
    │    - Current Run.md                      │
    │    - Dashboard.md                        │
    │    - Character journals                  │
    │    - Event logs                          │
    └─────────────────────────────────────────┘
```

---

# 3. SOURCES OF TRUTH ANALYSIS

## Current Architecture (⚠️ MULTIPLE SOURCES OF TRUTH)

| Data Type | Source of Truth | Secondary Copies | Sync Mechanism |
|-----------|-----------------|------------------|----------------|
| **Character HP** | `Character.hp` (in-memory) | Obsidian MD files | Manual write |
| **Character Stats** | `Character` object | Obsidian MD files | Manual write |
| **Quest Progress** | `Quest.objectives[].progress` | Obsidian MD files | Manual write |
| **Turn Count** | `current_run_data["turn_count"]` | Obsidian MD files | Manual write |
| **Game Events** | Obsidian MD files | `current_run_data["events"]` | Append-only |
| **Inventory** | ❌ NONE - doesn't exist yet | N/A | N/A |
| **Location** | `game.current_location` (string) | N/A | N/A |
| **World State** | ❌ NONE | N/A | N/A |

**🚨 CRITICAL ISSUES:**

1. **No Single Source of Truth**: Character data lives in memory, Obsidian files are not authoritative
2. **No Persistence**: Game state lost when process ends
3. **No Rollback**: Can't undo actions or reload state
4. **Sync Issues**: Obsidian files can diverge from in-memory state

---

## Recommended Architecture (✅ SINGLE SOURCE OF TRUTH)

```
┌─────────────────────────────────────────────────────────┐
│              SINGLE SOURCE OF TRUTH                     │
│                  GameState Object                       │
│  ┌──────────────────────────────────────────────────┐   │
│  │ run_id: str                                      │   │
│  │ turn: int                                        │   │
│  │ characters: Dict[str, Character]                 │   │
│  │ world: WorldState                                │   │
│  │ quests: Dict[str, Quest]                         │   │
│  │ events: List[Event]                              │   │
│  │ metadata: dict                                   │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
              ↓ Serialize to
┌─────────────────────────────────────────────────────────┐
│                 PERSISTENT STORAGE                       │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐       │
│  │   JSON     │  │  Obsidian  │  │  Database  │       │
│  │   File     │  │  Markdown  │  │  (future)  │       │
│  │ (autosave) │  │  (export)  │  │            │       │
│  └────────────┘  └────────────┘  └────────────┘       │
└─────────────────────────────────────────────────────────┘
```

---

# 4. CRUD OPERATIONS ANALYSIS

## Current CRUD Operations

### Character CRUD

**CREATE:**
```python
# dnd_game.py - Line 286
def _create_characters(self):
    self.players.append(Character("Hero 1", "Rogue"))
    self.enemies.append(Character("Monster 1", "Skeleton"))
```
- ✅ Simple
- ⚠️ No validation
- ❌ No persistence
- ❌ No ID tracking

**READ:**
```python
# Access via list iteration
for player in game.players:
    print(player.name, player.hp)
```
- ⚠️ Linear search required
- ❌ No indexing by ID

**UPDATE:**
```python
# Direct mutation
character.hp -= damage
character.alive = False
character.status_effects.append("stunned")
```
- ⚠️ No validation
- ⚠️ No event emission
- ❌ No change tracking
- ❌ Obsidian files manually synced afterward

**DELETE:**
```python
# Not implemented - characters just marked as alive=False
character.alive = False
```
- ⚠️ Dead characters remain in memory
- ⚠️ No cleanup

---

### Quest CRUD

**CREATE:**
```python
# quest_system.py - Line 177
quest = Quest("main_quest", "Title", "Description", objectives, rewards)
quest_manager.add_quest(quest)
```
- ✅ Good encapsulation
- ✅ Validation in QuestManager
- ❌ No persistence

**READ:**
```python
quest = quest_manager.get_quest(quest_id)
active_quests = quest_manager.get_active_quests()
```
- ✅ Good API
- ✅ Indexed by ID

**UPDATE:**
```python
objective.update_progress(1)
quest.check_completion()
```
- ✅ Good encapsulation
- ⚠️ No event emission
- ❌ Obsidian files manually synced

**DELETE:**
```python
# Not implemented
```
- ❌ Can't remove quests

---

### Item/Inventory CRUD (NEW SYSTEM)

**CREATE:**
```python
# items.py - Global ITEMS dictionary (immutable)
ITEMS["health_potion"] = Item(...)
```
- ✅ Items are pre-defined (good for game data)
- ⚠️ Can't create items at runtime (might be intentional)

**READ:**
```python
item = ITEMS.get("health_potion")
```
- ✅ Fast dictionary lookup
- ⚠️ No validation if item doesn't exist

**UPDATE:**
```python
# Items are immutable - can't update
# Inventory can be updated:
inventory.add_item("health_potion", 3)
inventory.remove_item("health_potion", 1)
```
- ✅ Good API
- ⚠️ No event emission
- ❌ Not persisted
- ❌ Not integrated with Character

**DELETE:**
```python
# Can't delete items from global ITEMS dict
# Can remove from inventory
inventory.remove_item("health_potion", 99)
```
- ✅ Remove from inventory works
- ⚠️ No bounds checking (returns False but no exception)

---

### Location/World CRUD (NEW SYSTEM)

**CREATE:**
```python
# world_builder.py - create_emberpeak_world()
locations = {
    "thornhaven_tavern": Location(...),
    ...
}
```
- ✅ Locations pre-defined (good for game world)
- ⚠️ Can't create locations dynamically

**READ:**
```python
location = world_manager.get_current_location()
available_dirs = world_manager.get_available_directions()
```
- ✅ Good API
- ✅ Indexed by ID

**UPDATE:**
```python
location.mark_visited()
location.mark_cleared()
world_manager.move("north")
```
- ✅ Good API
- ⚠️ No event emission
- ❌ Not persisted
- ❌ Not integrated with DungeonMaster

**DELETE:**
```python
# Not implemented (probably don't need it)
```

---

# 5. POTENTIAL CONFLICTS & CROSSED WIRES

## 🚨 CRITICAL CONFLICTS

### Conflict #1: Multiple Character Classes

**File:** `dnd_game.py` vs `character.py`

**Problem:**
```python
# dnd_game.py
char1 = Character("Hero", "Fighter")  # Uses char_class
char1.ability_scores  # Has D&D stats

# character.py
char2 = Character(config={"character_class": "Warrior"})  # Uses character_class
char2.inventory  # Has inventory field
```

**Impact:**
- Can't use both simultaneously
- Import conflicts
- Different APIs

**Resolution Needed:**
- ✅ **Recommend:** Use `dnd_game.Character` everywhere (it's more complete)
- ✅ **Deprecate:** `character.py` or merge its inventory feature

---

### Conflict #2: Location Class Duplication

**File:** `world.py` vs `world_builder.py`

**Problem:**
```python
# world.py
location1 = Location(name, description, connections)  # Simple

# world_builder.py
location2 = Location(
    location_id, name, location_type, description,
    connections, encounter_chance, npcs, services, ...
)  # Comprehensive
```

**Impact:**
- Can't import both
- Different feature sets

**Resolution Needed:**
- ✅ **Recommend:** Use `world_builder.Location` (much more complete)
- ✅ **Deprecate:** `world.py`

---

### Conflict #3: No Integration Between Systems

**Problem:**
```python
# Character has no inventory field
character = Character("Hero", "Fighter")
character.inventory  # ❌ AttributeError!

# DnDGame has no world manager
game = DnDGame()
game.world  # ❌ AttributeError!
game.current_location  # ✅ Just a string, no Location object

# Inventory not integrated
inventory = Inventory()
# How does it connect to Character? ❌ It doesn't!
```

**Impact:**
- Systems are isolated
- Can't use new features (items, world) in main game
- Manual integration required

**Resolution Needed:**
- ✅ Add `inventory: Inventory` field to Character
- ✅ Add `world: WorldManager` field to DungeonMaster
- ✅ Replace `current_location: str` with `current_location: Location`

---

### Conflict #4: GameState Fragmentation

**Problem:**
```python
# State stored in 3 places:
dungeon_master.current_run_data["turn_count"]  # Turn count
dungeon_master.game.players  # Character data
dungeon_master.quest_manager.quests  # Quest data

# No unified state object
```

**Impact:**
- Can't save/load game easily
- Can't serialize state
- Can't rollback
- Hard to debug

**Resolution Needed:**
- ✅ Create unified `GameState` class
- ✅ Move all state into single object
- ✅ Implement save/load

---

### Conflict #5: Event System Not Transactional

**Problem:**
```python
# Character takes damage
character.hp -= damage
# ↓ What if this fails?
obsidian.log_event(...)
# Character is modified but event not logged!

# Quest progress updated
objective.progress += 1
# ↓ What if this fails?
obsidian.log_quest(...)
# Progress updated but not logged!
```

**Impact:**
- State and logs can diverge
- No rollback on failure
- Debugging is hard

**Resolution Needed:**
- ✅ Use event sourcing pattern
- ✅ Emit events BEFORE modifying state
- ✅ State changes are result of events, not direct mutations

---

# 6. DESIGN PATTERN ANALYSIS

## Current Patterns

### ✅ GOOD PATTERNS IN USE

**1. Manager Pattern (Quest, Event, Game)**
```python
class QuestManager:
    def add_quest(self, quest)
    def get_quest(self, id)
    def get_active_quests()
```
- ✅ Good: Centralized management
- ✅ Good: Clear API
- ⚠️ Could improve: Add event emission

**2. Observer Pattern (Partial - GameEventManager)**
```python
class GameEventManager:
    def publish_event(self, event)
    def add_subscriber(self, callback)
```
- ✅ Good: Event-driven architecture started
- ⚠️ Partial: Not used everywhere
- ⚠️ Could improve: Use for all state changes

**3. Factory Pattern (Item creation)**
```python
ITEMS = {
    "health_potion": Item(...),
    ...
}
```
- ✅ Good: Centralized item definitions
- ✅ Good: Immutable game data

---

### ⚠️ PATTERNS THAT NEED IMPROVEMENT

**1. God Object Anti-Pattern (DungeonMaster)**
```python
class DungeonMaster:
    # Too many responsibilities:
    def initialize_run()       # Setup
    def initialize_game()      # More setup
    def run_game_loop()        # Main loop
    def update_current_run()   # File I/O
    def update_dashboard()     # More file I/O
    def extract_run_id()       # ID management
    # ... 700+ lines
```

**Problem:** Violates Single Responsibility Principle

**Recommendation:**
```python
class GameEngine:          # Runs game loop
class StateManager:        # Manages game state
class PersistenceManager:  # Saves/loads
class DungeonMaster:       # Coordinates (much simpler)
```

---

**2. Anemic Domain Model (Character)**
```python
# Character is mostly data, little behavior
character.hp -= damage  # External code modifies state
character.alive = False  # External code changes state

# Better:
character.take_damage(damage)  # Character manages its own state
character.is_alive()           # Character knows its own logic
```

**Problem:** Business logic scattered outside objects

**Recommendation:** Move logic into domain objects

---

**3. No Repository Pattern**

```python
# Current: Direct access to lists
for player in game.players:
    ...

# Better: Repository pattern
player_repo.find_by_name("Hero 1")
player_repo.find_alive()
player_repo.save(player)
```

**Problem:** No abstraction for data access

**Recommendation:** Add repository layer

---

**4. No Strategy Pattern (AI Decisions)**

```python
# Current: Random choice
selected_choice = random.choice(choices)

# Better: Pluggable strategy
strategy = PlayerStrategy()  # Could be: AggressiveStrategy, CautiousStrategy, etc.
selected_choice = strategy.select_choice(choices, context)
```

**Problem:** Hard to change AI behavior

**Recommendation:** Use Strategy pattern for flexibility

---

# 7. RECOMMENDED DESIGN PATTERNS

## Event Sourcing (CRITICAL)

**Current:**
```python
character.hp = 50
# State changed, no record of WHY
```

**Recommended:**
```python
# Emit event
event = DamageTakenEvent(character_id="hero1", damage=10, source="goblin_attack")
event_store.append(event)

# Event handler updates state
def on_damage_taken(event):
    character = repo.find(event.character_id)
    character.hp -= event.damage
    repo.save(character)
```

**Benefits:**
- Complete audit trail
- Can replay events
- Can undo/redo
- Easy debugging

---

## Repository Pattern (HIGH PRIORITY)

**Recommended:**
```python
class CharacterRepository:
    def find_by_id(self, id: str) -> Character
    def find_alive(self) -> List[Character]
    def save(self, character: Character)
    def delete(self, id: str)

class QuestRepository:
    def find_by_id(self, id: str) -> Quest
    def find_active(self) -> List[Quest]
    def save(self, quest: Quest)

# Usage:
character_repo.save(hero)
# Behind the scenes: saves to JSON, DB, Obsidian, etc.
```

**Benefits:**
- Centralized data access
- Easy to add persistence
- Testable

---

## State Pattern (Game States)

**Recommended:**
```python
class GameState:
    # Current: Just data
    pass

class IdleState(GameState):
    def handle_input(self, game, input) -> GameState:
        if input == "start":
            return ExplorationState()

class ExplorationState(GameState):
    def handle_input(self, game, input) -> GameState:
        if input.startswith("move"):
            return self  # Stay in exploration
        elif input == "attack":
            return CombatState()

class CombatState(GameState):
    def handle_input(self, game, input) -> GameState:
        if all_enemies_dead():
            return ExplorationState()
```

**Benefits:**
- Clear state transitions
- No invalid state combinations
- Easy to add new states

---

# 8. OVERLOOKED ISSUES

## 🚨 Critical Issues

### 1. No Error Recovery
```python
# If this fails:
character.hp -= damage
# Character state is corrupted, no rollback
```
**Fix:** Use transactions or event sourcing

### 2. No Validation
```python
character.hp = -100  # ❌ Allowed but invalid!
inventory.add_item("fake_item", 999)  # ❌ No validation
```
**Fix:** Add validation in setters or use value objects

### 3. No Concurrency Control
```python
# If two threads modify same character:
character.hp -= 10  # Thread 1
character.hp -= 5   # Thread 2
# Lost update! Final HP could be wrong
```
**Fix:** Add locking or use immutable objects

### 4. Memory Leaks
```python
# Dead characters stay in memory forever
character.alive = False
# Still in game.players list, never removed
```
**Fix:** Clean up or use weak references

### 5. No Input Sanitization
```python
# User could inject malicious data
player_name = "<script>alert('xss')</script>"
# Logged to Obsidian files, could execute
```
**Fix:** Sanitize all user input

### 6. Tight Coupling
```python
# DungeonMaster directly calls ObsidianLogger
self.obsidian.log_event(...)
# Hard to test, hard to change persistence layer
```
**Fix:** Use dependency injection and interfaces

### 7. No Versioning
```python
# Save game format can't change without breaking old saves
# No version field in serialized data
```
**Fix:** Add version numbers to all serialized data

### 8. Race Conditions in Event Publishing
```python
event_manager.publish_event(event)
# What if multiple events published simultaneously?
# Event order might be wrong
```
**Fix:** Use queue with guaranteed ordering

---

# 9. RECOMMENDED IMPROVEMENTS

## Immediate (Next 2-4 hours)

1. ✅ **Merge Character classes**
   - Use `dnd_game.Character` everywhere
   - Add `inventory: Inventory` field to it
   - Delete `character.py`

2. ✅ **Merge Location classes**
   - Use `world_builder.Location` everywhere
   - Delete `world.py`

3. ✅ **Integrate WorldManager with DungeonMaster**
   - Add `self.world = WorldManager()` to DungeonMaster
   - Replace `current_location: str` with `current_location_id: str`
   - Use `world.get_current_location()` to get full Location object

4. ✅ **Add loot drops to combat**
   - After enemy dies, call `get_loot_from_enemy(enemy.char_class)`
   - Add loot to player inventory

---

## Short-term (Next 1-2 days)

5. ✅ **Create unified GameState class**
```python
class GameState:
    run_id: str
    turn: int
    characters: Dict[str, Character]
    world_state: WorldState
    quests: Dict[str, Quest]

    def save(self, path: str)
    def load(self, path: str)
```

6. ✅ **Add Repository pattern**
7. ✅ **Add validation to all data mutations**
8. ✅ **Implement event sourcing for critical state changes**

---

## Long-term (Next 1-2 weeks)

9. ✅ **Refactor DungeonMaster into smaller classes**
10. ✅ **Add comprehensive error handling**
11. ✅ **Implement save/load system**
12. ✅ **Add concurrency control**

---

# 10. SUMMARY

## Critical Conflicts Found

1. ❌ **Multiple Character classes** (dnd_game.py vs character.py)
2. ❌ **Multiple Location classes** (world.py vs world_builder.py)
3. ❌ **No integration** (Inventory, WorldManager isolated)
4. ❌ **Fragmented state** (data in 3+ places)
5. ❌ **No persistence** (all in-memory, lost on restart)
6. ❌ **No error recovery** (state can corrupt)
7. ❌ **No validation** (invalid data allowed)

## Design Pattern Issues

1. ⚠️ **God Object** (DungeonMaster too big)
2. ⚠️ **Anemic Domain Model** (logic outside objects)
3. ⚠️ **No Repository** (direct list access)
4. ⚠️ **No Event Sourcing** (can't track changes)
5. ⚠️ **Tight Coupling** (hard to test/change)

## Recommended Actions (Priority Order)

**CRITICAL (Do First):**
1. Merge duplicate classes (Character, Location)
2. Integrate new systems (Inventory, WorldManager)
3. Add validation to prevent invalid state

**HIGH PRIORITY (Do Soon):**
4. Create unified GameState
5. Add Repository pattern
6. Implement save/load

**MEDIUM PRIORITY (Do Eventually):**
7. Refactor DungeonMaster
8. Add event sourcing
9. Add error recovery

---

**Bottom Line:** You have good foundations but need integration work and architectural cleanup before scaling further.
