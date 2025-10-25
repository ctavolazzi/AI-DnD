# Design Architecture & Implementation Plan
## The Emberpeak Expedition - Browser Game MVP

**Document Type**: Design-to-Engineering Handoff  
**Version**: 1.0  
**Date**: October 25, 2025  
**Status**: MVP Planning Phase

---

## EXECUTIVE SUMMARY

This document outlines the transformation of The Emberpeak Expedition from a prototype into a fully functional browser-based RPG. We present a critical analysis of the current state, define the complete production vision, and establish a phased MVP approach for iterative development.

**Key Objectives**:
- Transform prototype into production-ready game
- Establish robust component architecture
- Create MVP for testing and validation
- Enable continuous development toward full version

---

## 1. CURRENT STATE CRITIQUE

### 1.1 Strengths of Current Implementation

#### 1.1.a Visual Design
- 1.1.a.1 Strong retro aesthetic established
- 1.1.a.2 Consistent color palette
- 1.1.a.3 Professional typography choices
- 1.1.a.4 Good use of visual hierarchy

#### 1.1.b User Experience
- 1.1.b.1 Clear action categorization
- 1.1.b.2 Logical information grouping
- 1.1.b.3 Responsive layout considerations
- 1.1.b.4 Keyboard shortcuts implemented

#### 1.1.c Code Structure
- 1.1.c.1 Modular CSS with variables
- 1.1.c.2 Semantic HTML structure
- 1.1.c.3 Event-driven JavaScript
- 1.1.c.4 Documented functions

### 1.2 Critical Gaps & Issues

#### 1.2.a Architectural Issues
- 1.2.a.1 **No state management system** - Game state scattered across DOM and JS variables
- 1.2.a.2 **No data persistence** - No save/load functionality
- 1.2.a.3 **Hard-coded content** - All narrative content embedded in code
- 1.2.a.4 **No component isolation** - Monolithic HTML structure
- 1.2.a.5 **No game engine** - No core loop, turn management, or event system

#### 1.2.b Functional Limitations
- 1.2.b.1 **Static map system** - Map is hidden in tabs, not a live navigation tool
- 1.2.b.2 **Mock interactions** - Actions don't trigger real game mechanics
- 1.2.b.3 **No combat system** - Attack button exists but no combat logic
- 1.2.b.4 **No inventory mechanics** - Items displayed but no use/equip/drop functionality
- 1.2.b.5 **No quest tracking** - Quest log is static content
- 1.2.b.6 **No character progression** - Stats are hardcoded, no leveling system

#### 1.2.c Technical Debt
- 1.2.c.1 **No build system** - Single HTML file limits scalability
- 1.2.c.2 **No asset management** - Images inline as data URIs or placeholders
- 1.2.c.3 **No API structure** - No backend communication layer
- 1.2.c.4 **No testing framework** - No unit or integration tests
- 1.2.c.5 **No error handling** - Minimal try-catch blocks
- 1.2.c.6 **No analytics** - No event tracking or user behavior monitoring

#### 1.2.d Content & Design Issues
- 1.2.d.1 **Map visibility** - Critical navigation tool hidden in tabs (per user feedback)
- 1.2.d.2 **Scene viewer underutilized** - Large space for single avatar image
- 1.2.d.3 **No dynamic content** - All text is static
- 1.2.d.4 **Limited feedback** - Many actions don't provide clear outcomes
- 1.2.d.5 **No tutorial** - No onboarding for new players

#### 1.2.e Scalability Concerns
- 1.2.e.1 **Single file architecture** - Difficult to maintain as complexity grows
- 1.2.e.2 **No data separation** - Logic, presentation, and content mixed
- 1.2.e.3 **Global namespace pollution** - No module system
- 1.2.e.4 **Performance not optimized** - No lazy loading or code splitting

### 1.3 User Experience Friction Points

#### 1.3.a Navigation Issues
- 1.3.a.1 Map hidden in tabs requires extra clicks to access
- 1.3.a.2 No visual indication of current location on map
- 1.3.a.3 Compass and map not synchronized
- 1.3.a.4 No breadcrumb trail or location history

#### 1.3.b Information Overload
- 1.3.b.1 Too many panels competing for attention
- 1.3.b.2 No progressive disclosure of complexity
- 1.3.b.3 Adventure log can become cluttered quickly
- 1.3.b.4 All UI visible at once regardless of context

#### 1.3.c Feedback Gaps
- 1.3.c.1 Actions complete instantly with no sense of consequence
- 1.3.c.2 No indication of game state changes
- 1.3.c.3 Unclear what actions are available in current context
- 1.3.c.4 No confirmation for important decisions

---

## 2. FULL PRODUCTION VISION

### 2.1 Complete Feature Set (Target State)

#### 2.1.a Core Game Systems
- 2.1.a.1 **Game Engine**
  - 2.1.a.1.1 Turn-based game loop
  - 2.1.a.1.2 Event system with pub/sub pattern
  - 2.1.a.1.3 State machine for game phases
  - 2.1.a.1.4 Command pattern for actions
  - 2.1.a.1.5 Undo/redo system for turns

- 2.1.a.2 **Combat System**
  - 2.1.a.2.1 Turn-based tactical combat
  - 2.1.a.2.2 Damage calculation with stats
  - 2.1.a.2.3 Status effects (poison, stun, buffs)
  - 2.1.a.2.4 Enemy AI with behavior trees
  - 2.1.a.2.5 Loot drops and rewards

- 2.1.a.3 **Character Progression**
  - 2.1.a.3.1 Experience points and leveling
  - 2.1.a.3.2 Skill trees and abilities
  - 2.1.a.3.3 Equipment system with stat modifiers
  - 2.1.a.3.4 Character classes with unique abilities
  - 2.1.a.3.5 Achievement system

- 2.1.a.4 **Inventory Management**
  - 2.1.a.4.1 Item pickup, use, equip, drop
  - 2.1.a.4.2 Item categories (weapons, armor, consumables, quest items)
  - 2.1.a.4.3 Weight/capacity limits
  - 2.1.a.4.4 Item combining/crafting
  - 2.1.a.4.5 Item durability

- 2.1.a.5 **Quest System**
  - 2.1.a.5.1 Main storyline quests
  - 2.1.a.5.2 Side quests
  - 2.1.a.5.3 Quest stages and branching
  - 2.1.a.5.4 Quest completion rewards
  - 2.1.a.5.5 Quest journal with tracking

#### 2.1.b World & Navigation
- 2.1.b.1 **World Map**
  - 2.1.b.1.1 Interactive visual map
  - 2.1.b.1.2 Fog of war (reveals as explored)
  - 2.1.b.1.3 Location markers and icons
  - 2.1.b.1.4 Fast travel between discovered locations
  - 2.1.b.1.5 Map zooming and panning

- 2.1.b.2 **Location System**
  - 2.1.b.2.1 Procedurally described rooms
  - 2.1.b.2.2 Dynamic encounters based on location
  - 2.1.b.2.3 Environmental storytelling
  - 2.1.b.2.4 Interactive objects in scenes
  - 2.1.b.2.5 Weather and time-of-day effects

#### 2.1.c Narrative & Content
- 2.1.c.1 **Dialogue System**
  - 2.1.c.1.1 Branching conversation trees
  - 2.1.c.1.2 NPC personalities and relationships
  - 2.1.c.1.3 Persuasion checks based on stats
  - 2.1.c.1.4 Consequences of dialogue choices
  - 2.1.c.1.5 Voice acting (text-to-speech or audio files)

- 2.1.c.2 **Content Management**
  - 2.1.c.2.1 JSON-based content database
  - 2.1.c.2.2 Modular story chapters
  - 2.1.c.2.3 Random event pool
  - 2.1.c.2.4 Localization support (multiple languages)
  - 2.1.c.2.5 Content editor for non-programmers

#### 2.1.d Multiplayer Features
- 2.1.d.1 **Social Systems**
  - 2.1.d.1.1 User accounts and authentication
  - 2.1.d.1.2 Player profiles
  - 2.1.d.1.3 Leaderboards
  - 2.1.d.1.4 Achievement sharing
  - 2.1.d.1.5 Co-op multiplayer mode

#### 2.1.e Monetization (If Applicable)
- 2.1.e.1 **Freemium Model**
  - 2.1.e.1.1 Free core game
  - 2.1.e.1.2 Premium content packs
  - 2.1.e.1.3 Cosmetic items
  - 2.1.e.1.4 Optional ads for bonuses
  - 2.1.e.1.5 Supporter tier

### 2.2 Technical Infrastructure (Full Version)

#### 2.2.a Frontend Architecture
- 2.2.a.1 **Framework**: React or Vue.js
- 2.2.a.2 **State Management**: Redux or Vuex
- 2.2.a.3 **Build System**: Vite or Webpack
- 2.2.a.4 **Type Safety**: TypeScript
- 2.2.a.5 **Styling**: CSS Modules or Styled Components
- 2.2.a.6 **Testing**: Jest + React Testing Library

#### 2.2.b Backend Architecture
- 2.2.b.1 **API Server**: Node.js + Express or Python + FastAPI
- 2.2.b.2 **Database**: PostgreSQL for relational data
- 2.2.b.3 **Cache**: Redis for session data
- 2.2.b.4 **File Storage**: AWS S3 or similar
- 2.2.b.5 **Authentication**: JWT tokens
- 2.2.b.6 **WebSocket**: Real-time multiplayer

#### 2.2.c DevOps & Deployment
- 2.2.c.1 **Version Control**: Git + GitHub
- 2.2.c.2 **CI/CD**: GitHub Actions
- 2.2.c.3 **Hosting**: Vercel, Netlify, or AWS
- 2.2.c.4 **Monitoring**: Sentry for errors, Google Analytics
- 2.2.c.5 **CDN**: Cloudflare for assets
- 2.2.c.6 **SSL**: HTTPS with Let's Encrypt

---

## 3. MVP SCOPE DEFINITION

### 3.1 MVP Philosophy

**Goal**: Create a fully playable, single-player, browser-based RPG that demonstrates core gameplay loop and can be tested locally for continuous development.

**Constraints**:
- 3.1.1 No backend server required (local storage only)
- 3.1.2 No multiplayer features
- 3.1.3 Limited content (1 chapter, 5-7 locations)
- 3.1.4 Core mechanics proven, advanced features deferred
- 3.1.5 Can be opened directly in browser (no complex build step required for testing)

### 3.2 MVP Feature List (In Scope)

#### 3.2.a Core Gameplay Loop
- 3.2.a.1 ✅ Explore locations via map and compass
- 3.2.a.2 ✅ Read narrative descriptions
- 3.2.a.3 ✅ Make choices through actions
- 3.2.a.4 ✅ Basic combat encounters
- 3.2.a.5 ✅ Collect items and manage inventory
- 3.2.a.6 ✅ Complete one main quest with 3-5 stages
- 3.2.a.7 ✅ Character progression (gain 1-2 levels)

#### 3.2.b Essential Systems
- 3.2.b.1 **Game Engine MVP**
  - 3.2.b.1.1 Turn-based game loop
  - 3.2.b.1.2 Basic state management
  - 3.2.b.1.3 Event system for game updates
  - 3.2.b.1.4 Save/load to localStorage

- 3.2.b.2 **Combat MVP**
  - 3.2.b.2.1 Player vs single enemy
  - 3.2.b.2.2 Attack/defend/use item actions
  - 3.2.b.2.3 HP damage and death states
  - 3.2.b.2.4 Simple loot on enemy defeat
  - 3.2.b.2.5 No status effects or complex mechanics

- 3.2.b.3 **Inventory MVP**
  - 3.2.b.3.1 Pick up items
  - 3.2.b.3.2 Use consumables (health potions)
  - 3.2.b.3.3 Equip weapons (stat boost)
  - 3.2.b.3.4 Drop items
  - 3.2.b.3.5 No weight limits or crafting

- 3.2.b.4 **Map System MVP** ⭐ (Per user requirement)
  - 3.2.b.4.1 Permanent visual map panel
  - 3.2.b.4.2 Shows current location highlighted
  - 3.2.b.4.3 Shows discovered locations
  - 3.2.b.4.4 Click to navigate (if adjacent)
  - 3.2.b.4.5 Simple grid-based layout (5x3 grid)
  - 3.2.b.4.6 Undiscovered locations shown as "???"

- 3.2.b.5 **Character System MVP**
  - 3.2.b.5.1 Name, class selection at start
  - 3.2.b.5.2 Three core stats (STR, DEX, CON)
  - 3.2.b.5.3 HP based on CON
  - 3.2.b.5.4 XP and leveling (2 levels total)
  - 3.2.b.5.5 Stat increases on level up

- 3.2.b.6 **Quest System MVP**
  - 3.2.b.6.1 One main quest: "Rescue the Miners"
  - 3.2.b.6.2 5 stages with clear objectives
  - 3.2.b.6.3 Quest log shows current objective
  - 3.2.b.6.4 Completion triggers win state
  - 3.2.b.6.5 No side quests in MVP

#### 3.2.c UI Components (MVP)
- 3.2.c.1 **Permanent Map Panel** (NEW)
  - 3.2.c.1.1 Always visible on screen
  - 3.2.c.1.2 Compact size (250x300px)
  - 3.2.c.1.3 Shows 5-7 locations
  - 3.2.c.1.4 Current location indicator
  - 3.2.c.1.5 Clickable navigation

- 3.2.c.2 **Adventure Log** (Existing, Enhanced)
  - 3.2.c.2.1 Scrollable narrative history
  - 3.2.c.2.2 Color-coded message types
  - 3.2.c.2.3 Auto-scroll to latest
  - 3.2.c.2.4 Clear/reset option

- 3.2.c.3 **Character Panel** (Existing, Enhanced)
  - 3.2.c.3.1 Stats display with tooltips
  - 3.2.c.3.2 HP bar with visual indicators
  - 3.2.c.3.3 XP bar (new)
  - 3.2.c.3.4 Level indicator
  - 3.2.c.3.5 Equipped weapon/armor display

- 3.2.c.4 **Scene Viewer** (Existing, Repurposed)
  - 3.2.c.4.1 Location illustration or AI-generated image
  - 3.2.c.4.2 Current location name
  - 3.2.c.4.3 Brief description
  - 3.2.c.4.4 Available NPCs/objects listed

- 3.2.c.5 **Action Panel** (Existing, Enhanced)
  - 3.2.c.5.1 Context-aware action buttons
  - 3.2.c.5.2 Actions enabled/disabled based on state
  - 3.2.c.5.3 Hover descriptions
  - 3.2.c.5.4 Keyboard shortcuts

- 3.2.c.6 **Inventory Panel** (Existing, Functional)
  - 3.2.c.6.1 Grid of item slots
  - 3.2.c.6.2 Click item to use/equip/drop
  - 3.2.c.6.3 Item tooltips with stats
  - 3.2.c.6.4 Capacity indicator

- 3.2.c.7 **Quest Log** (Existing, Simplified)
  - 3.2.c.7.1 Current quest objective
  - 3.2.c.7.2 Progress indicator
  - 3.2.c.7.3 Completed objectives marked
  - 3.2.c.7.4 No multiple quests in MVP

#### 3.2.d Content (MVP)
- 3.2.d.1 **7 Locations**
  - 3.2.d.1.1 Starting Tavern
  - 3.2.d.1.2 Town Square
  - 3.2.d.1.3 Mine Entrance
  - 3.2.d.1.4 Mine Level 1
  - 3.2.d.1.5 Mine Level 2
  - 3.2.d.1.6 Boss Chamber
  - 3.2.d.1.7 Crystal Cavern (ending)

- 3.2.d.2 **3 NPCs**
  - 3.2.d.2.1 Tavern Keeper (quest giver)
  - 3.2.d.2.2 Rogue (hireable companion - stretch goal)
  - 3.2.d.2.3 Trapped Miner (rescue target)

- 3.2.d.3 **5 Enemy Types**
  - 3.2.d.3.1 Cave Goblin (weak)
  - 3.2.d.3.2 Dark Bat (fast)
  - 3.2.d.3.3 Stone Golem (tanky)
  - 3.2.d.3.4 Corrupted Miner (mid-tier)
  - 3.2.d.3.5 Rune Guardian (boss)

- 3.2.d.4 **10 Items**
  - 3.2.d.4.1 Rusty Sword (starting weapon)
  - 3.2.d.4.2 Iron Sword (upgrade)
  - 3.2.d.4.3 Leather Armor (starting armor)
  - 3.2.d.4.4 Chain Mail (upgrade)
  - 3.2.d.4.5 Health Potion (Small) - restores 20 HP
  - 3.2.d.4.6 Health Potion (Large) - restores 50 HP
  - 3.2.d.4.7 Torch (quest item)
  - 3.2.d.4.8 Mine Map (quest item)
  - 3.2.d.4.9 Crystal Shard (quest item)
  - 3.2.d.4.10 Gold Coins (currency - not implemented in MVP)

### 3.3 MVP Feature List (Out of Scope / Deferred)

#### 3.3.a Deferred Features
- 3.3.a.1 ❌ Multiple character classes with unique abilities
- 3.3.a.2 ❌ Skill trees
- 3.3.a.3 ❌ Status effects (poison, stun, etc.)
- 3.3.a.4 ❌ Companion NPCs
- 3.3.a.5 ❌ Side quests
- 3.3.a.6 ❌ Crafting system
- 3.3.a.7 ❌ Shop/merchant system
- 3.3.a.8 ❌ Fast travel
- 3.3.a.9 ❌ Achievements
- 3.3.a.10 ❌ Multiple save slots
- 3.3.a.11 ❌ Settings persistence
- 3.3.a.12 ❌ Sound effects
- 3.3.a.13 ❌ Background music
- 3.3.a.14 ❌ Animations beyond CSS transitions
- 3.3.a.15 ❌ Procedural content generation

#### 3.3.b Technical Debt Accepted in MVP
- 3.3.b.1 No TypeScript (vanilla JS acceptable)
- 3.3.b.2 No framework (vanilla JS with simple module pattern)
- 3.3.b.3 No build step (optional ES6 modules if supported)
- 3.3.b.4 No automated testing (manual testing only)
- 3.3.b.5 No backend (localStorage only)
- 3.3.b.6 No CI/CD pipeline
- 3.3.b.7 Limited browser compatibility (modern browsers only)

---

## 4. MVP ARCHITECTURE

### 4.1 Component Structure

#### 4.1.a Core Game Components

```
game/
├── engine/
│   ├── GameEngine.js          // Main game loop and state management
│   ├── StateManager.js        // Centralized state with pub/sub
│   ├── EventBus.js           // Event system for decoupling
│   ├── SaveManager.js        // LocalStorage save/load
│   └── TurnManager.js        // Turn-based mechanics
│
├── systems/
│   ├── CombatSystem.js       // Combat mechanics
│   ├── InventorySystem.js    // Item management
│   ├── QuestSystem.js        // Quest tracking
│   ├── LocationSystem.js     // Navigation and map
│   └── CharacterSystem.js    // Stats, XP, leveling
│
├── ui/
│   ├── MapComponent.js       // ⭐ NEW: Permanent map display
│   ├── AdventureLog.js       // Message history
│   ├── CharacterPanel.js     // Stats, HP, XP display
│   ├── SceneViewer.js        // Current location view
│   ├── ActionPanel.js        // Action buttons
│   ├── InventoryPanel.js     // Inventory grid
│   ├── QuestLog.js           // Quest objectives
│   ├── CombatUI.js           // Combat-specific UI
│   └── UIManager.js          // Coordinates all UI updates
│
├── data/
│   ├── locations.js          // Location definitions
│   ├── enemies.js            // Enemy stats and behaviors
│   ├── items.js              // Item database
│   ├── quests.js             // Quest definitions
│   └── dialogues.js          // NPC conversations
│
└── utils/
    ├── dice.js               // Random number generation
    ├── logger.js             // Debug logging
    └── helpers.js            // Utility functions
```

#### 4.1.b Component Relationships

```
GameEngine (Top Level)
    ├─ StateManager (holds all game state)
    │   └─ EventBus (publishes state changes)
    │
    ├─ Systems (business logic)
    │   ├─ CombatSystem
    │   ├─ InventorySystem
    │   ├─ QuestSystem
    │   ├─ LocationSystem
    │   └─ CharacterSystem
    │
    ├─ UIManager (presentation layer)
    │   ├─ MapComponent ⭐
    │   ├─ AdventureLog
    │   ├─ CharacterPanel
    │   ├─ SceneViewer
    │   ├─ ActionPanel
    │   ├─ InventoryPanel
    │   ├─ QuestLog
    │   └─ CombatUI
    │
    └─ Data (content layer)
        ├─ locations
        ├─ enemies
        ├─ items
        ├─ quests
        └─ dialogues
```

### 4.2 State Management Architecture

#### 4.2.a Global State Structure

```javascript
GameState = {
  meta: {
    version: "1.0.0",
    saveTimestamp: Date,
    playtime: Number
  },
  
  player: {
    name: String,
    class: String,
    level: Number,
    xp: Number,
    xpToNext: Number,
    stats: {
      str: Number,
      dex: Number,
      con: Number
    },
    hp: {
      current: Number,
      max: Number
    },
    equipped: {
      weapon: Item | null,
      armor: Item | null
    }
  },
  
  inventory: {
    items: Array<Item>,
    capacity: Number
  },
  
  location: {
    current: String,        // location ID
    discovered: Array<String>,
    available: Array<String> // adjacent locations
  },
  
  quests: {
    active: Quest | null,
    completed: Array<String>,
    objectives: Array<Objective>
  },
  
  combat: {
    active: Boolean,
    enemy: Enemy | null,
    turn: "player" | "enemy",
    log: Array<String>
  },
  
  flags: {
    // Story flags
    metRogue: Boolean,
    hasMapItem: Boolean,
    minersRescued: Boolean,
    // etc...
  }
}
```

#### 4.2.b State Update Flow

```
User Action
    ↓
Action Handler (UI)
    ↓
System Method (e.g., CombatSystem.attack())
    ↓
StateManager.update()
    ↓
EventBus.emit('stateChanged', delta)
    ↓
UI Components listen and re-render
    ↓
Visual Update
```

### 4.3 File Structure (MVP)

```
retro-adventure-mvp/
│
├── index.html                 // Main HTML file
├── styles/
│   ├── main.css              // Core styles
│   ├── components.css        // Component-specific styles
│   ├── map.css               // Map component styles ⭐
│   └── combat.css            // Combat UI styles
│
├── js/
│   ├── main.js               // Entry point, initialization
│   │
│   ├── engine/
│   │   ├── GameEngine.js
│   │   ├── StateManager.js
│   │   ├── EventBus.js
│   │   ├── SaveManager.js
│   │   └── TurnManager.js
│   │
│   ├── systems/
│   │   ├── CombatSystem.js
│   │   ├── InventorySystem.js
│   │   ├── QuestSystem.js
│   │   ├── LocationSystem.js
│   │   └── CharacterSystem.js
│   │
│   ├── ui/
│   │   ├── UIManager.js
│   │   ├── MapComponent.js   ⭐
│   │   ├── AdventureLog.js
│   │   ├── CharacterPanel.js
│   │   ├── SceneViewer.js
│   │   ├── ActionPanel.js
│   │   ├── InventoryPanel.js
│   │   ├── QuestLog.js
│   │   └── CombatUI.js
│   │
│   ├── data/
│   │   ├── locations.js
│   │   ├── enemies.js
│   │   ├── items.js
│   │   ├── quests.js
│   │   └── dialogues.js
│   │
│   └── utils/
│       ├── dice.js
│       ├── logger.js
│       └── helpers.js
│
├── assets/
│   ├── images/
│   │   ├── locations/        // Location scene images
│   │   ├── characters/       // Character portraits
│   │   ├── items/           // Item icons
│   │   └── map/             // Map graphics ⭐
│   │
│   └── data/
│       └── gamedata.json    // Optional: external data file
│
└── docs/
    ├── ARCHITECTURE.md       // This document
    ├── API.md               // System APIs
    └── TESTING.md           // Test plan
```

---

## 5. IMPLEMENTATION PLAN (MVP)

### 5.1 Phase 1: Foundation (Week 1)

#### 5.1.a Setup & Architecture
- **5.1.a.1** Create project structure
  - 5.1.a.1.1 Set up folder hierarchy
  - 5.1.a.1.2 Initialize Git repository
  - 5.1.a.1.3 Create README with project overview
  - 5.1.a.1.4 Set up basic HTML skeleton

- **5.1.a.2** Implement Core Engine
  - 5.1.a.2.1 Build EventBus (pub/sub pattern)
  - 5.1.a.2.2 Build StateManager with getters/setters
  - 5.1.a.2.3 Implement state update flow
  - 5.1.a.2.4 Add state validation
  - 5.1.a.2.5 Test state updates with console logs

- **5.1.a.3** Create Data Layer
  - 5.1.a.3.1 Define location data structure
  - 5.1.a.3.2 Create 7 location objects
  - 5.1.a.3.3 Define item data structure
  - 5.1.a.3.4 Create 10 item objects
  - 5.1.a.3.5 Define enemy data structure
  - 5.1.a.3.6 Create 5 enemy objects

- **5.1.a.4** Deliverables
  - 5.1.a.4.1 Working EventBus with unit tests (console)
  - 5.1.a.4.2 StateManager that holds and updates game state
  - 5.1.a.4.3 Complete data files for locations, items, enemies
  - 5.1.a.4.4 Basic HTML structure for UI components

#### 5.1.b UI Foundation
- **5.1.b.1** Layout Design
  - 5.1.b.1.1 Design 3-column responsive layout
    - Column 1 (Left): Adventure Log + Actions
    - Column 2 (Center): Scene Viewer + Quest Log
    - Column 3 (Right): Map ⭐ + Character Panel + Inventory
  - 5.1.b.1.2 Create CSS grid system
  - 5.1.b.1.3 Add responsive breakpoints
  - 5.1.b.1.4 Test on multiple screen sizes

- **5.1.b.2** Build UIManager
  - 5.1.b.2.1 Create UIManager class
  - 5.1.b.2.2 Implement render() method
  - 5.1.b.2.3 Subscribe to state changes
  - 5.1.b.2.4 Add component registration system

- **5.1.b.3** Build Adventure Log Component
  - 5.1.b.3.1 Create AdventureLog class
  - 5.1.b.3.2 Implement addMessage() method
  - 5.1.b.3.3 Add message type styling
  - 5.1.b.3.4 Add auto-scroll functionality
  - 5.1.b.3.5 Add clear log option

- **5.1.b.4** Deliverables
  - 5.1.b.4.1 Responsive layout working in browser
  - 5.1.b.4.2 Adventure log displaying messages
  - 5.1.b.4.3 UIManager coordinating updates

### 5.2 Phase 2: Core Systems (Week 2)

#### 5.2.a Character System
- **5.2.a.1** Character Creation
  - 5.2.a.1.1 Create character creation modal
  - 5.2.a.1.2 Name input validation
  - 5.2.a.1.3 Class selection (Warrior, Rogue, Mage)
  - 5.2.a.1.4 Starting stats calculation
  - 5.2.a.1.5 Initialize player in state

- **5.2.a.2** Character Panel Component
  - 5.2.a.2.1 Build CharacterPanel class
  - 5.2.a.2.2 Display name, class, level
  - 5.2.a.2.3 Render stats with tooltips
  - 5.2.a.2.4 HP bar with color gradient
  - 5.2.a.2.5 XP bar with level progress
  - 5.2.a.2.6 Equipped items display

- **5.2.a.3** Leveling System
  - 5.2.a.3.1 XP gain on enemy defeat
  - 5.2.a.3.2 Level up calculation
  - 5.2.a.3.3 Stat increases on level up
  - 5.2.a.3.4 HP refill on level up
  - 5.2.a.3.5 Level up notification

- **5.2.a.4** Deliverables
  - 5.2.a.4.1 Working character creation flow
  - 5.2.a.4.2 Character panel updating on state change
  - 5.2.a.4.3 Leveling system functional

#### 5.2.b Location & Navigation System
- **5.2.b.1** LocationSystem Class
  - 5.2.b.1.1 Build LocationSystem
  - 5.2.b.1.2 loadLocation() method
  - 5.2.b.1.3 getAvailableExits() method
  - 5.2.b.1.4 move(direction) method
  - 5.2.b.1.5 discoverLocation() method

- **5.2.b.2** Map Component ⭐ (CRITICAL)
  - 5.2.b.2.1 Create MapComponent class
  - 5.2.b.2.2 Design map visual layout
    - 5.2.b.2.2.1 3x3 grid representation
    - 5.2.b.2.2.2 Location nodes as clickable cells
    - 5.2.b.2.2.3 Connections shown as lines/paths
  - 5.2.b.2.3 Render discovered locations
  - 5.2.b.2.4 Render undiscovered as "???"
  - 5.2.b.2.5 Highlight current location (glow effect)
  - 5.2.b.2.6 Show available paths from current location
  - 5.2.b.2.7 Click handler for navigation
  - 5.2.b.2.8 Hover tooltips on locations
  - 5.2.b.2.9 Position map in right column (always visible)

- **5.2.b.3** Scene Viewer Component
  - 5.2.b.3.1 Build SceneViewer class
  - 5.2.b.3.2 Display location name
  - 5.2.b.3.3 Display location description
  - 5.2.b.3.4 Show location image (placeholder or real)
  - 5.2.b.3.5 List NPCs present
  - 5.2.b.3.6 List interactive objects

- **5.2.b.4** Action Panel Updates
  - 5.2.b.4.1 Context-aware action buttons
  - 5.2.b.4.2 Enable/disable based on location
  - 5.2.b.4.3 "Talk" button if NPC present
  - 5.2.b.4.4 "Examine" shows location details
  - 5.2.b.4.5 "Rest" restores HP (if safe location)

- **5.2.b.5** Deliverables
  - 5.2.b.5.1 Functional map component always visible ⭐
  - 5.2.b.5.2 Click on map to navigate to adjacent locations
  - 5.2.b.5.3 Current location highlighted
  - 5.2.b.5.4 Scene viewer updates on location change
  - 5.2.b.5.5 Adventure log shows movement messages

#### 5.2.c Inventory System
- **5.2.c.1** InventorySystem Class
  - 5.2.c.1.1 Build InventorySystem
  - 5.2.c.1.2 addItem() method
  - 5.2.c.1.3 removeItem() method
  - 5.2.c.1.4 useItem() method
  - 5.2.c.1.5 equipItem() method
  - 5.2.c.1.6 canAddItem() capacity check

- **5.2.c.2** Inventory Panel Component
  - 5.2.c.2.1 Build InventoryPanel class
  - 5.2.c.2.2 Render 4x5 item grid
  - 5.2.c.2.3 Show item icons
  - 5.2.c.2.4 Empty slot indicators
  - 5.2.c.2.5 Click item for context menu
  - 5.2.c.2.6 Context menu: Use/Equip/Drop
  - 5.2.c.2.7 Item tooltips with stats
  - 5.2.c.2.8 Capacity indicator

- **5.2.c.3** Item Interactions
  - 5.2.c.3.1 Use consumable (potion restores HP)
  - 5.2.c.3.2 Equip weapon (increase damage)
  - 5.2.c.3.3 Equip armor (increase defense)
  - 5.2.c.3.4 Drop item removes from inventory
  - 5.2.c.3.5 Pick up item from location

- **5.2.c.4** Deliverables
  - 5.2.c.4.1 Functional inventory grid
  - 5.2.c.4.2 Items can be used, equipped, dropped
  - 5.2.c.4.3 Stats update when equipment changes
  - 5.2.c.4.4 Character panel shows equipped items

### 5.3 Phase 3: Combat System (Week 3)

#### 5.3.a Combat Core
- **5.3.a.1** CombatSystem Class
  - 5.3.a.1.1 Build CombatSystem
  - 5.3.a.1.2 startCombat() method
  - 5.3.a.1.3 endCombat() method
  - 5.3.a.1.4 playerAttack() method
  - 5.3.a.1.5 enemyAttack() method
  - 5.3.a.1.6 calculateDamage() method
  - 5.3.a.1.7 checkVictory() method
  - 5.3.a.1.8 checkDefeat() method

- **5.3.a.2** Turn Management
  - 5.3.a.2.1 Turn order (player always goes first in MVP)
  - 5.3.a.2.2 Turn switching logic
  - 5.3.a.2.3 Action validation
  - 5.3.a.2.4 Turn count tracking

- **5.3.a.3** Combat Calculations
  - 5.3.a.3.1 Base damage formula: weaponDamage + STR modifier
  - 5.3.a.3.2 Defense calculation: armor + DEX modifier
  - 5.3.a.3.3 Hit chance (always 100% in MVP for simplicity)
  - 5.3.a.3.4 Critical hit (10% chance, 2x damage)
  - 5.3.a.3.5 Enemy AI (simple: attack 80%, defend 20%)

#### 5.3.b Combat UI
- **5.3.b.1** CombatUI Component
  - 5.3.b.1.1 Build CombatUI class
  - 5.3.b.1.2 Show when combat is active
  - 5.3.b.1.3 Hide when combat ends
  - 5.3.b.1.4 Display enemy info (name, HP, image)
  - 5.3.b.1.5 Combat action buttons (Attack, Defend, Use Item, Flee)
  - 5.3.b.1.6 Combat log (separate from main log)
  - 5.3.b.1.7 Turn indicator (Player Turn / Enemy Turn)

- **5.3.b.2** Combat Actions
  - 5.3.b.2.1 Attack button deals damage
  - 5.3.b.2.2 Defend button reduces damage taken (next turn)
  - 5.3.b.2.3 Use Item opens inventory (consumables only)
  - 5.3.b.2.4 Flee button (50% success, only in non-boss fights)

- **5.3.b.3** Combat Resolution
  - 5.3.b.3.1 Victory screen (XP gained, loot)
  - 5.3.b.3.2 Defeat screen (respawn at last safe location, lose some XP)
  - 5.3.b.3.3 Loot collection after victory
  - 5.3.b.3.4 Return to exploration mode

#### 5.3.c Combat Integration
- **5.3.c.1** Trigger Combat
  - 5.3.c.1.1 Random encounters in certain locations
  - 5.3.c.1.2 Boss encounters (scripted)
  - 5.3.c.1.3 Combat entrance transition
  - 5.3.c.1.4 Save state before combat

- **5.3.c.2** Deliverables
  - 5.3.c.2.1 Fully functional turn-based combat
  - 5.3.c.2.2 Player can attack, defend, use items
  - 5.3.c.2.3 Enemy AI takes actions
  - 5.3.c.2.4 Victory grants XP and loot
  - 5.3.c.2.5 Defeat respawns player

### 5.4 Phase 4: Quest System (Week 4)

#### 5.4.a Quest Infrastructure
- **5.4.a.1** QuestSystem Class
  - 5.4.a.1.1 Build QuestSystem
  - 5.4.a.1.2 startQuest() method
  - 5.4.a.1.3 updateObjective() method
  - 5.4.a.1.4 completeQuest() method
  - 5.4.a.1.5 checkConditions() method

- **5.4.a.2** Quest Definition
  - 5.4.a.2.1 Define "Rescue the Miners" quest
  - 5.4.a.2.2 Create 5 objectives:
    - 5.4.a.2.2.1 Talk to Tavern Keeper
    - 5.4.a.2.2.2 Find Mine Entrance
    - 5.4.a.2.2.3 Defeat 3 enemies in mine
    - 5.4.a.2.2.4 Defeat Rune Guardian boss
    - 5.4.a.2.2.5 Rescue trapped miner
  - 5.4.a.2.3 Set objective conditions
  - 5.4.a.2.4 Define rewards (XP, items)

- **5.4.a.3** Quest Log Component
  - 5.4.a.3.1 Build QuestLog class
  - 5.4.a.3.2 Display active quest
  - 5.4.a.3.3 Show current objective
  - 5.4.a.3.4 Mark completed objectives
  - 5.4.a.3.5 Progress bar for quest stages

#### 5.4.b Quest Integration
- **5.4.b.1** NPC Interactions
  - 5.4.b.1.1 Create simple dialogue system
  - 5.4.b.1.2 Tavern Keeper gives quest
  - 5.4.b.1.3 Trapped Miner triggers completion
  - 5.4.b.1.4 Dialogue choices (basic: Accept/Decline)

- **5.4.b.2** Quest Triggers
  - 5.4.b.2.1 Location-based triggers
  - 5.4.b.2.2 Combat-based triggers (defeat count)
  - 5.4.b.2.3 Item-based triggers (pickup key item)
  - 5.4.b.2.4 NPC interaction triggers

- **5.4.b.3** Deliverables
  - 5.4.b.3.1 Main quest playable start to finish
  - 5.4.b.3.2 Quest log updates as objectives complete
  - 5.4.b.3.3 Quest completion triggers win state
  - 5.4.b.3.4 Rewards granted on completion

### 5.5 Phase 5: Polish & Integration (Week 5)

#### 5.5.a Save System
- **5.5.a.1** SaveManager Class
  - 5.5.a.1.1 Build SaveManager
  - 5.5.a.1.2 saveGame() method (serialize state to localStorage)
  - 5.5.a.1.3 loadGame() method (deserialize from localStorage)
  - 5.5.a.1.4 Auto-save on state change (debounced)
  - 5.5.a.1.5 Manual save button
  - 5.5.a.1.6 New game confirmation (delete save)

- **5.5.a.2** Deliverables
  - 5.5.a.2.1 Game saves automatically
  - 5.5.a.2.2 Game loads on page reload
  - 5.5.a.2.3 New game option available

#### 5.5.b Game Flow
- **5.5.b.1** Title Screen
  - 5.5.b.1.1 Create title screen
  - 5.5.b.1.2 New Game button
  - 5.5.b.1.3 Continue button (if save exists)
  - 5.5.b.1.4 Credits
  - 5.5.b.1.5 How to Play

- **5.5.b.2** Win/Lose States
  - 5.5.b.2.1 Victory screen on quest completion
  - 5.5.b.2.2 Show final stats
  - 5.5.b.2.3 Play Again button
  - 5.5.b.2.4 Game over screen on defeat
  - 5.5.b.2.5 Restart option

- **5.5.b.3** Tutorial
  - 5.5.b.3.1 First-time player hints
  - 5.5.b.3.2 Tooltips on first actions
  - 5.5.b.3.3 Help overlay
  - 5.5.b.3.4 Can be dismissed/skipped

#### 5.5.c UI Polish
- **5.5.c.1** Animations
  - 5.5.c.1.1 Combat hit animations
  - 5.5.c.1.2 HP bar smooth transitions
  - 5.5.c.1.3 Item pickup animation
  - 5.5.c.1.4 Level up celebration
  - 5.5.c.1.5 Map location highlight pulse

- **5.5.c.2** Feedback Improvements
  - 5.5.c.2.1 Loading states for actions
  - 5.5.c.2.2 Confirmation modals for destructive actions
  - 5.5.c.2.3 Toast notifications for events
  - 5.5.c.2.4 Sound effect hooks (silent by default, ready for audio)

- **5.5.c.3** Accessibility
  - 5.5.c.3.1 Keyboard navigation audit
  - 5.5.c.3.2 ARIA labels on interactive elements
  - 5.5.c.3.3 Focus indicators
  - 5.5.c.3.4 Color contrast verification

#### 5.5.d Testing & Bug Fixes
- **5.5.d.1** Functional Testing
  - 5.5.d.1.1 Complete playthrough (start to end)
  - 5.5.d.1.2 Test all combat scenarios
  - 5.5.d.1.3 Test inventory edge cases
  - 5.5.d.1.4 Test save/load functionality
  - 5.5.d.1.5 Test quest progression

- **5.5.d.2** Browser Testing
  - 5.5.d.2.1 Chrome
  - 5.5.d.2.2 Firefox
  - 5.5.d.2.3 Safari
  - 5.5.d.2.4 Edge

- **5.5.d.3** Responsive Testing
  - 5.5.d.3.1 Desktop (1920x1080)
  - 5.5.d.3.2 Laptop (1366x768)
  - 5.5.d.3.3 Tablet (768x1024)
  - 5.5.d.3.4 Mobile (375x667)

- **5.5.d.4** Deliverables
  - 5.5.d.4.1 Bug-free playthrough
  - 5.5.d.4.2 All systems integrated and working
  - 5.5.d.4.3 Responsive on all screen sizes
  - 5.5.d.4.4 Accessible with keyboard

---

## 6. DETAILED COMPONENT SPECIFICATIONS

### 6.1 MapComponent ⭐ (PRIORITY COMPONENT)

#### 6.1.a Purpose
Provide permanent, always-visible navigation interface that shows player position, discovered locations, and allows click-to-navigate.

#### 6.1.b Layout & Position
- **6.1.b.1** Position: Top of right column, above character panel
- **6.1.b.2** Dimensions: 280px width × 320px height
- **6.1.b.3** Grid Layout: 3 columns × 3 rows = 9 cells
- **6.1.b.4** Each cell: 80px × 80px with 10px gaps

#### 6.1.c Visual Design
- **6.1.c.1** Container
  - Border: 3px solid gold
  - Background: Parchment texture
  - Padding: 15px
  - Box shadow for depth

- **6.1.c.2** Location Nodes
  - Discovered: Show location icon + name
  - Undiscovered: Show "???" placeholder
  - Current: Gold glow/pulse animation
  - Adjacent: Clickable, hover highlight
  - Not adjacent: Grayed out, not clickable

- **6.1.c.3** Connections
  - Lines connecting adjacent locations
  - Dashed lines for undiscovered paths
  - Solid lines for discovered paths
  - Color: Brown for standard, gold for current path

#### 6.1.d Functionality
- **6.1.d.1** Click Handler
  - Check if location is adjacent to current
  - If yes, trigger navigation
  - If no, show tooltip: "Too far to reach from here"

- **6.1.d.2** Hover Behavior
  - Show location name tooltip
  - Show "Click to travel" if adjacent
  - Show "Discover this location first" if undiscovered

- **6.1.d.3** Update Triggers
  - On location change (move to new location)
  - On location discovery (after first visit)
  - On quest progress (unlock new paths)

#### 6.1.e Map Data Structure

```javascript
MapData = {
  grid: [
    [null,          "tavern",      "town-square"],
    ["forest-path", "mine-entrance", "guard-post"],
    [null,          "mine-level1",  "mine-level2"]
  ],
  
  locations: {
    "tavern": {
      name: "Misty Tavern",
      icon: "🍺",
      discovered: true,
      adjacent: ["town-square"]
    },
    "town-square": {
      name: "Town Square",
      icon: "🏛️",
      discovered: false,
      adjacent: ["tavern", "guard-post", "mine-entrance"]
    },
    // ... other locations
  },
  
  currentLocation: "tavern"
}
```

#### 6.1.f Implementation Example

```javascript
class MapComponent {
  constructor(containerId) {
    this.container = document.getElementById(containerId);
    this.gameState = null;
  }
  
  init(gameState) {
    this.gameState = gameState;
    this.render();
    this.attachEventListeners();
  }
  
  render() {
    const mapData = this.gameState.location.map;
    let html = '<div class="map-grid">';
    
    for (let row = 0; row < 3; row++) {
      for (let col = 0; col < 3; col++) {
        const locationId = mapData.grid[row][col];
        html += this.renderCell(locationId, row, col);
      }
    }
    
    html += '</div>';
    this.container.innerHTML = html;
  }
  
  renderCell(locationId, row, col) {
    if (!locationId) {
      return '<div class="map-cell empty"></div>';
    }
    
    const location = this.gameState.location.locations[locationId];
    const isCurrent = locationId === this.gameState.location.current;
    const isDiscovered = location.discovered;
    const isAdjacent = this.isAdjacent(locationId);
    
    let classes = ['map-cell'];
    if (isCurrent) classes.push('current');
    if (isDiscovered) classes.push('discovered');
    if (isAdjacent && !isCurrent) classes.push('adjacent');
    
    return `
      <div class="${classes.join(' ')}" 
           data-location="${locationId}"
           data-row="${row}" 
           data-col="${col}">
        <div class="map-cell-icon">${isDiscovered ? location.icon : '❓'}</div>
        <div class="map-cell-name">${isDiscovered ? location.name : '???'}</div>
      </div>
    `;
  }
  
  isAdjacent(locationId) {
    const current = this.gameState.location.current;
    const currentLocation = this.gameState.location.locations[current];
    return currentLocation.adjacent.includes(locationId);
  }
  
  attachEventListeners() {
    this.container.querySelectorAll('.map-cell.adjacent').forEach(cell => {
      cell.addEventListener('click', (e) => {
        const locationId = e.currentTarget.dataset.location;
        this.handleNavigation(locationId);
      });
    });
  }
  
  handleNavigation(locationId) {
    // Dispatch navigation event
    window.EventBus.emit('navigate', { to: locationId });
  }
  
  update(gameState) {
    this.gameState = gameState;
    this.render();
    this.attachEventListeners();
  }
}
```

---

### 6.2 Other Key Components (Brief Specs)

#### 6.2.a AdventureLog
- Displays narrative history
- Auto-scrolls to newest message
- Color-codes message types
- Clear/filter options

#### 6.2.b CharacterPanel
- Shows stats, HP, XP
- Displays equipped items
- Real-time updates on state change

#### 6.2.c SceneViewer
- Shows current location
- Displays location image/description
- Lists NPCs and objects

#### 6.2.d ActionPanel
- Context-aware buttons
- Enables/disables based on state
- Keyboard shortcuts

#### 6.2.e InventoryPanel
- Grid of items
- Click for context menu
- Drag-and-drop (stretch goal)

#### 6.2.f QuestLog
- Shows active quest
- Progress bar
- Objective checklist

#### 6.2.g CombatUI
- Enemy display
- Combat actions
- Combat log
- Turn indicator

---

## 7. TESTING PLAN

### 7.1 Unit Testing (Manual)

#### 7.1.a State Management
- 7.1.a.1 Test state initialization
- 7.1.a.2 Test state updates
- 7.1.a.3 Test event emission
- 7.1.a.4 Test state validation

#### 7.1.b Combat System
- 7.1.b.1 Test damage calculation
- 7.1.b.2 Test turn management
- 7.1.b.3 Test victory/defeat conditions
- 7.1.b.4 Test loot drops

#### 7.1.c Inventory System
- 7.1.c.1 Test add/remove items
- 7.1.c.2 Test capacity limits
- 7.1.c.3 Test equipment effects
- 7.1.c.4 Test consumable usage

### 7.2 Integration Testing

#### 7.2.a Complete Playthrough
- 7.2.a.1 Start new game
- 7.2.a.2 Navigate all locations
- 7.2.a.3 Complete all combat encounters
- 7.2.a.4 Complete main quest
- 7.2.a.5 Reach victory screen

#### 7.2.b Edge Cases
- 7.2.b.1 Inventory full scenarios
- 7.2.b.2 HP at zero (defeat)
- 7.2.b.3 Rapid state changes
- 7.2.b.4 Save/load mid-game

### 7.3 User Testing

#### 7.3.a Usability Testing
- 7.3.a.1 First-time player experience
- 7.3.a.2 Navigation intuitiveness
- 7.3.a.3 Action clarity
- 7.3.a.4 UI comprehension

#### 7.3.b Feedback Collection
- 7.3.b.1 Survey after playthrough
- 7.3.b.2 Identify pain points
- 7.3.b.3 Measure completion time
- 7.3.b.4 Assess enjoyment

---

## 8. SUCCESS METRICS (MVP)

### 8.1 Technical Metrics
- **8.1.1** Zero critical bugs
- **8.1.2** Load time < 3 seconds
- **8.1.3** Playable on 4 major browsers
- **8.1.4** Responsive on 4 screen sizes
- **8.1.5** Save/load works 100% of time

### 8.2 Gameplay Metrics
- **8.2.1** Completable in 20-30 minutes
- **8.2.2** Clear progression path
- **8.2.3** Balanced difficulty
- **8.2.4** No dead-ends or soft locks
- **8.2.5** All systems integrated smoothly

### 8.3 User Experience Metrics
- **8.3.1** 80% of testers complete game
- **8.3.2** 90% understand map navigation immediately
- **8.3.3** 85% satisfaction rating
- **8.3.4** < 5 clicks to any common action
- **8.3.5** Zero accessibility violations

---

## 9. POST-MVP ROADMAP

### 9.1 Phase 6: Content Expansion
- 9.1.1 Add 5-10 more locations
- 9.1.2 Add 2-3 side quests
- 9.1.3 Add 10 more items
- 9.1.4 Add 5 more enemy types
- 9.1.5 Add 3-5 NPCs

### 9.2 Phase 7: Advanced Features
- 9.2.1 Skill trees
- 9.2.2 Crafting system
- 9.2.3 Merchant/shop system
- 9.2.4 Companion system
- 9.2.5 Multiple save slots

### 9.3 Phase 8: Polish & Audio
- 9.3.1 Sound effects
- 9.3.2 Background music
- 9.3.3 Advanced animations
- 9.3.4 Particle effects
- 9.3.5 Voice acting (optional)

### 9.4 Phase 9: Backend Integration
- 9.4.1 Set up Node.js server
- 9.4.2 PostgreSQL database
- 9.4.3 User accounts
- 9.4.4 Cloud saves
- 9.4.5 Leaderboards

### 9.5 Phase 10: Multiplayer
- 9.5.1 WebSocket infrastructure
- 9.5.2 Co-op mode design
- 9.5.3 Synchronization system
- 9.5.4 Lobby system
- 9.5.5 Chat functionality

---

## 10. TECHNICAL CONSIDERATIONS

### 10.1 Performance Optimization
- **10.1.a** Use event delegation for UI listeners
- **10.1.b** Debounce save operations
- **10.1.c** Throttle render updates
- **10.1.d** Lazy load images
- **10.1.e** Minimize DOM manipulations

### 10.2 Code Quality
- **10.2.a** Consistent naming conventions
- **10.2.b** Comprehensive comments
- **10.2.c** Modular architecture
- **10.2.d** DRY principle adherence
- **10.2.e** Error handling everywhere

### 10.3 Browser Compatibility
- **10.3.a** ES6+ features with fallbacks
- **10.3.b** CSS Grid with Flexbox fallback
- **10.3.c** LocalStorage with error handling
- **10.3.d** Console.log for debugging (remove in production)

---

## 11. RISK ASSESSMENT

### 11.1 Technical Risks
| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| LocalStorage limitations | Medium | Medium | Implement data compression |
| Browser compatibility issues | Low | Medium | Test early and often |
| State synchronization bugs | High | High | Robust state management, extensive testing |
| Performance on low-end devices | Medium | Low | Optimize render cycles |

### 11.2 Scope Risks
| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Feature creep | High | High | Strict MVP scope enforcement |
| Timeline overruns | Medium | Medium | Weekly milestone reviews |
| Content creation bottleneck | Medium | Medium | Pre-define all content early |

---

## 12. DELIVERABLES CHECKLIST

### 12.1 MVP Deliverables
- [ ] **12.1.1** Fully functional game engine
- [ ] **12.1.2** 7 explorable locations
- [ ] **12.1.3** Permanent map component ⭐
- [ ] **12.1.4** Turn-based combat system
- [ ] **12.1.5** Inventory management
- [ ] **12.1.6** Character progression
- [ ] **12.1.7** Quest system with main quest
- [ ] **12.1.8** Save/load functionality
- [ ] **12.1.9** Responsive UI
- [ ] **12.1.10** Complete playthrough (20-30 min)

### 12.2 Documentation Deliverables
- [ ] **12.2.1** README with setup instructions
- [ ] **12.2.2** Code documentation (comments)
- [ ] **12.2.3** Player guide
- [ ] **12.2.4** Testing report
- [ ] **12.2.5** Post-mortem analysis

### 12.3 Testing Deliverables
- [ ] **12.3.1** Browser compatibility report
- [ ] **12.3.2** Responsive design verification
- [ ] **12.3.3** Accessibility audit
- [ ] **12.3.4** User testing results
- [ ] **12.3.5** Bug tracking log

---

## 13. CONCLUSION

This design architecture document provides a comprehensive plan for transforming The Emberpeak Expedition from a prototype into a fully functional MVP. The plan prioritizes:

1. **Solid Architecture**: Modular, maintainable, scalable code
2. **Core Gameplay**: Complete game loop that's fun to play
3. **Map-First Navigation**: Permanent map component for intuitive navigation ⭐
4. **Iterative Development**: MVP approach allows for continuous improvement
5. **Clear Scope**: Defined boundaries prevent feature creep

By following this phased approach, we can deliver a polished, playable MVP in 5 weeks that serves as a foundation for continuous development toward the full production version.

---

**Next Steps**:
1. Review and approve this plan
2. Set up development environment
3. Begin Phase 1: Foundation
4. Weekly progress reviews
5. Iterate based on testing feedback

**Questions for Design Review**:
- Is the MVP scope appropriate?
- Is the 5-week timeline realistic?
- Are there any must-have features missing from MVP?
- Is the permanent map design satisfactory? ⭐
- Should we prioritize any post-MVP features?

---

**Document Status**: ✅ Ready for Engineering Review  
**Approval Required From**: Product Owner, Lead Designer, Technical Lead  
**Target Start Date**: [To be determined]  
**Target MVP Completion**: [To be determined]
