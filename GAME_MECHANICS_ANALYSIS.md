# GAME MECHANICS & EVENT LOOP ANALYSIS

## Question 1: Is This Following D&D 5e Rules?

### ✅ WHAT FOLLOWS 5e RULES

**Ability Scores & Modifiers (100% Accurate)**
```python
# Ability scores: STR, DEX, CON, INT, WIS, CHA
ability_scores = {"STR": 16, "DEX": 12, "CON": 14, "INT": 10, "WIS": 12, "CHA": 10}

# Modifier calculation (CORRECT 5e formula)
def get_ability_modifier(ability):
    score = ability_scores[ability]
    return (score - 10) // 2  # E.g., 16 STR = +3 modifier
```

**D20 Rolling with Advantage/Disadvantage (100% Accurate)**
```python
def roll_d20(advantage=False, disadvantage=False):
    roll1 = random.randint(1, 20)

    if advantage:
        roll2 = random.randint(1, 20)
        return max(roll1, roll2)  # Take higher roll
    elif disadvantage:
        roll2 = random.randint(1, 20)
        return min(roll1, roll2)  # Take lower roll
    else:
        return roll1
```

**Skill Checks (95% Accurate)**
```python
# Formula: d20 + ability modifier + proficiency bonus (if proficient)
roll = roll_d20()
modifier = get_ability_modifier(ability)

if skill in skill_proficiencies:
    modifier += proficiency_bonus  # +2 at level 1-4

total = roll + modifier
success = total >= DC  # Must meet or exceed DC
```

**Natural 20s and Natural 1s (Detected)**
```python
if roll == 20:
    logger.info("NATURAL 20! Critical success!")
elif roll == 1:
    logger.info("NATURAL 1! Critical failure!")
```

**Skill Proficiencies by Class (Correct)**
- Fighter: Athletics, Intimidation
- Wizard: Arcana, Investigation
- Rogue: Stealth, Sleight of Hand, Perception
- Cleric: Medicine, Insight

---

### ⚠️ WHAT'S SIMPLIFIED/MODIFIED FROM 5e

**Combat System (Simplified)**

5e Rules:
```
Attack Roll = d20 + STR/DEX modifier + proficiency bonus
Compare to target's AC (Armor Class)
If hit: Roll damage dice (e.g., 1d8 + STR modifier for longsword)
```

This Game:
```python
# Attack uses d6 instead of d20, no AC
roll = random.randint(1, 6)
damage = self.attack + roll  # attack is a stat (5-15), not a modifier
actual_damage = damage - target.defense  # defense reduces damage
```

**Differences:**
- ❌ No AC (Armor Class) - uses "defense" stat instead
- ❌ Attack roll uses d6, not d20
- ❌ No "to-hit" vs "damage" separation
- ❌ Damage isn't dice-based (no 1d8, 2d6, etc.)
- ✅ BUT: Damage reduction by defense works like DR (Damage Reduction)

**Character Stats (Simplified)**
- ❌ No levels (everyone is ~level 3)
- ❌ No hit dice
- ❌ No proficiency bonus scaling
- ❌ No feats or ASIs
- ✅ Fixed proficiency bonus of +2

**Missing 5e Mechanics**
- ❌ Saving throws (DEX save, CON save, etc.)
- ❌ Spell slots
- ❌ Death saves
- ❌ Conditions (beyond "stunned")
- ❌ Initiative order
- ❌ Actions/Bonus Actions/Reactions
- ❌ Concentration
- ❌ Opportunity attacks

---

### 🎯 VERDICT: ~60% 5e Compliant

**What it is:**
- A **simplified, streamlined version** of D&D 5e
- Focuses on the core d20 mechanic
- Perfect for a **narrative-focused text game**
- Keeps ability scores, skill checks, proficiency

**What it's not:**
- Not a full 5e combat simulator
- Not suitable for tactical battle maps
- Not a replacement for D&D Beyond

**Comparison:**
- More 5e-like than: Skyrim, Dragon Age
- Less 5e-like than: Baldur's Gate 3, Solasta
- Similar to: Early computer RPGs (Gold Box games, Ultima)

---

## Question 2: How Are Dice Rolls Calculated & Displayed?

### DICE ROLLING SYSTEM

**No External Libraries - All Custom Code**

```python
import random  # Python's built-in random module

# D20 rolls (skill checks, ability checks)
def roll_d20(advantage=False, disadvantage=False):
    roll1 = random.randint(1, 20)  # Roll 1-20

    if advantage and not disadvantage:
        roll2 = random.randint(1, 20)
        result = max(roll1, roll2)
        logger.info(f"Rolling with advantage: {roll1}, {roll2} -> {result}")
        return result
    elif disadvantage and not advantage:
        roll2 = random.randint(1, 20)
        result = min(roll1, roll2)
        logger.info(f"Rolling with disadvantage: {roll1}, {roll2} -> {result}")
        return result
    else:
        logger.info(f"Rolling d20: {roll1}")
        return roll1

# D6 rolls (damage)
damage_roll = random.randint(1, 6)

# Healing (d20, but used as healing amount)
heal_amount = random.randint(1, 20)
```

### HOW RESULTS ARE DISPLAYED

**Console/Log Output:**
```
Hero 1 DEX check (Stealth, proficient): 15 + 6 = 21 vs DC 12 -> SUCCESS
NATURAL 20! Critical success!

Combat Stats:
- Attacker (Hero 1): Attack = 7, HP = 50/50
- Defender (Monster 1): Defense = 3, HP = 31/38
Attack Roll: 4
Total Damage = 7 (base) + 4 (roll) = 11

Damage Calculation:
- Incoming Damage: 11
- Target Defense: 3
- Final Damage: 11 - 3 = 8
Result: Monster 1 takes 8 damage! (HP: 31 -> 23)
```

**Obsidian Vault Output (Markdown):**
- Logged to character journals
- Logged to event logs
- Logged to session notes
- All timestamped

**Frontend Display:**
- Currently NOT displayed in retro UI
- UI shows fake/hardcoded rolls
- **Needs integration work**

---

## Question 3: External Frameworks or Open Source Solutions?

### ANSWER: Almost ZERO Game Frameworks!

**Dependencies Breakdown:**

```plaintext
GAME MECHANICS:
✗ No dice rolling libraries (python-dice, dice-py, etc.)
✗ No D&D frameworks (dnd-character, python-dnd, etc.)
✗ No game engines (Pygame, Panda3D, Godot, Unity)
✗ No RPG frameworks
✗ No combat simulators
✓ 100% custom Python code using only `random` module

WEB/API:
✓ FastAPI - REST API framework
✓ Uvicorn - ASGI server
✓ Pydantic - Data validation

AI/NARRATIVE:
✓ Ollama - Local LLM (mistral, llama2, etc.)
✗ No OpenAI (optional dependency, not used)

DATA/TEMPLATES:
✓ Jinja2 - Markdown template rendering
✗ No database (everything is in-memory or Markdown files)

UI:
✗ No React, Vue, Angular
✗ No Phaser.js, PixiJS (game frameworks)
✓ Pure HTML/CSS/JavaScript (custom retro UI)
```

### POTENTIAL FRAMEWORKS YOU COULD USE

**If you want to use existing tools:**

**1. Dice Rolling Libraries**
```bash
pip install dice  # Popular dice notation parser
```
```python
from dice import roll

result = roll('2d6+3')  # Roll 2 six-sided dice plus 3
result = roll('1d20')    # Standard d20
```

**2. D&D 5e Libraries**
```bash
pip install dnd-character  # Character creation
pip install python-dnd     # 5e data (spells, items, etc.)
```

**3. Game State Management**
```bash
pip install redis          # For persistent game state
pip install sqlalchemy     # For database storage
```

**4. Frontend Frameworks**
```bash
npm install phaser         # 2D game framework
npm install three.js       # 3D graphics
npm install rpg-awesome    # RPG icon font
```

---

## Question 4: FULL Event Loop & Game Functioning

### THE COMPLETE GAME ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────┐
│                    APPLICATION STARTUP                      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  main.py                                                    │
│  ├─ Parse command line args (--turns, --model, --reset)    │
│  ├─ Initialize DungeonMaster(vault_path, model)            │
│  └─ Call dm.run_game(max_turns)                            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  DungeonMaster.run_game()                                   │
│  ├─ initialize_run()                                        │
│  ├─ initialize_game()                                       │
│  └─ run_game_loop(max_turns)                               │
└─────────────────────────────────────────────────────────────┘
```

---

### PHASE 1: INITIALIZATION (Runs Once)

```python
def initialize_run():
    """Set up the game session"""

    # 1. Create/extract run ID
    run_id = extract_run_id() or generate_new_id()

    # 2. Initialize managers
    self.event_manager = GameEventManager(obsidian, run_data, self)
    self.game_manager = GameManager(obsidian, event_manager)
    self.quest_manager = QuestManager()

    # 3. Create Obsidian vault structure
    obsidian.create_vault_structure()

    # 4. Update Current Run.md
    update_current_run()

    return run_id
```

```python
def initialize_game():
    """Set up the actual D&D game"""

    # 1. Create DnDGame instance
    self.game = DnDGame(model=self.model)
    # This auto-creates 2 players (Rogue, Fighter)
    # and 2 enemies (Skeleton, Orc)

    # 2. Generate quest via AI
    quest_intro = narrative_engine.generate_quest()

    # 3. Parse quest and create objectives
    quest = Quest(
        quest_id="main_quest",
        title="The Emberpeak Expedition",
        objectives=[
            QuestObjective("Gather your party", "talk", "companions", 2),
            QuestObjective("Reach Emberpeak Mines", "explore", "mines", 1),
            ...
        ]
    )
    quest_manager.add_quest(quest)

    # 4. Log quest to Obsidian
    obsidian.log_quest(quest_data)

    # 5. Create character journals
    for player in game.players:
        journal_manager.create_character_journal(player)

    # 6. Generate character introductions via AI
    game.generate_character_introductions()

    # 7. Log session start
    obsidian.log_session(session_data)

    # 8. Update dashboard
    update_dashboard()
```

---

### PHASE 2: MAIN GAME LOOP (Runs for max_turns)

```python
def run_game_loop(max_turns=10):
    """The core game loop - runs every turn"""

    for turn in range(max_turns):
        current_run_data["turn_count"] = turn + 1

        # ═══════════════════════════════════════════════════════
        # STEP 1: GENERATE SCENE DESCRIPTION (AI)
        # ═══════════════════════════════════════════════════════
        scene = narrative_engine.describe_scene(
            location=game.current_location,
            characters=game.players
        )
        logger.info(f"Scene: {scene}")

        # Log scene to Obsidian
        obsidian.log_event({
            "name": f"Scene {scene_counter}",
            "type": "Scene",
            "description": scene,
            ...
        })

        # ═══════════════════════════════════════════════════════
        # STEP 2: DISPLAY ACTIVE QUEST OBJECTIVES
        # ═══════════════════════════════════════════════════════
        active_objectives = quest_manager.get_all_active_objectives()
        for quest_title, objective in active_objectives:
            logger.info(f"- {objective.description} ({objective.progress}/{objective.quantity})")

        # ═══════════════════════════════════════════════════════
        # STEP 3: PROCESS EACH PLAYER'S TURN
        # ═══════════════════════════════════════════════════════
        for player in game.players:
            if not player.alive:
                continue

            # ─────────────────────────────────────────────────
            # 3a. Generate 3 AI-powered choices
            # ─────────────────────────────────────────────────
            choices = narrative_engine.generate_player_choices(
                player.name,
                player.char_class,
                game.current_location,
                scene
            )
            # Returns:
            # [
            #   {"text": "Search for secret doors", "requires_check": True, "skill": "Investigation", "dc": 12},
            #   {"text": "Talk to the innkeeper", "requires_check": False},
            #   {"text": "Attack the goblin", "requires_check": False}
            # ]

            logger.info(f"{player.name} considers:")
            for i, choice in enumerate(choices, 1):
                logger.info(f"  {i}. {choice['text']}")

            # ─────────────────────────────────────────────────
            # 3b. AI auto-selects a choice (autonomous play)
            # ─────────────────────────────────────────────────
            selected_choice = random.choice(choices)
            logger.info(f"{player.name} chooses: {selected_choice['text']}")

            # ─────────────────────────────────────────────────
            # 3c. Resolve choice (skill check if required)
            # ─────────────────────────────────────────────────
            if selected_choice.get('requires_check'):
                ability = selected_choice.get('ability', 'WIS')
                skill = selected_choice.get('skill')
                dc = selected_choice.get('dc', 12)

                # MAKE SKILL CHECK
                check_data = player.ability_check(ability, dc, skill)
                # Returns:
                # {
                #   "roll": 15,
                #   "modifier": 6,  # ability mod + prof bonus
                #   "total": 21,
                #   "dc": 12,
                #   "success": True,
                #   "natural_20": False,
                #   ...
                # }

                success = check_data['success']

                # Log to Obsidian
                obsidian.log_skill_check(check_data)
            else:
                success = None

            # ─────────────────────────────────────────────────
            # 3d. Generate outcome narrative (AI)
            # ─────────────────────────────────────────────────
            outcome = narrative_engine.describe_choice_outcome(
                player.name,
                selected_choice,
                success,
                scene
            )
            logger.info(f"Outcome: {outcome}")

            # ─────────────────────────────────────────────────
            # 3e. Log action to Obsidian
            # ─────────────────────────────────────────────────
            obsidian.log_event({
                "name": f"{player.name}'s Choice - Turn {turn+1}",
                "type": "Player Choice",
                "description": f"{selected_choice['text']}\n{outcome}",
                "skill_check": check_data,
                ...
            })

            # ─────────────────────────────────────────────────
            # 3f. Update quest progress
            # ─────────────────────────────────────────────────
            quest_manager.check_objective_triggers(
                "player_action",
                {"player": player.name, "choice": selected_choice, "success": success}
            )

            # ─────────────────────────────────────────────────
            # 3g. Theory of Mind - notify other characters
            # ─────────────────────────────────────────────────
            game_manager.notify_entities_at_location(
                game.current_location,
                action_data,
                exclude=[player.name]
            )
            # This adds journal entries to other characters
            # who witnessed this action

        # ═══════════════════════════════════════════════════════
        # STEP 4: RANDOM ENCOUNTERS (30% chance)
        # ═══════════════════════════════════════════════════════
        if random.random() < 0.3:
            logger.info("=== ENCOUNTER ===")
            game.process_encounter()
            # This creates enemies and runs combat

            # Update quest for combat
            quest_manager.check_objective_triggers(
                "combat_victory",
                {"location": game.current_location}
            )

        # ═══════════════════════════════════════════════════════
        # STEP 5: CHECK QUEST COMPLETION
        # ═══════════════════════════════════════════════════════
        for quest in quest_manager.get_active_quests():
            if quest.check_completion():
                logger.info(f"🎉 QUEST COMPLETED: {quest.title}")
                logger.info(f"Rewards: {quest.rewards}")

                # Log completion
                obsidian.log_event({
                    "name": f"Quest Complete: {quest.title}",
                    "type": "Quest Completion",
                    ...
                })

        # ═══════════════════════════════════════════════════════
        # STEP 6: UPDATE OBSIDIAN FILES
        # ═══════════════════════════════════════════════════════
        update_current_run()   # Update Current Run.md
        update_dashboard()     # Update Dashboard.md

        # ═══════════════════════════════════════════════════════
        # STEP 7: RATE LIMITING (for AI calls)
        # ═══════════════════════════════════════════════════════
        time.sleep(1)  # Pause between turns
```

---

### PHASE 3: CONCLUSION (After all turns)

```python
# Generate final narrative
conclusion = narrative_engine.generate_conclusion()
logger.info(f"CONCLUSION: {conclusion}")

# Update run status
current_run_data["status"] = "completed"
current_run_data["conclusion"] = conclusion

# Log conclusion event
obsidian.log_event({
    "name": "Adventure Conclusion",
    "type": "Conclusion",
    "description": conclusion,
    ...
})

# Final vault updates
update_current_run()
update_dashboard()
```

---

### PARALLEL SYSTEMS RUNNING

While the main loop runs, these systems are active:

**1. Event Manager**
```python
# Every event triggers:
event_manager.publish_event(event_data)
  ├─ Update Current Run.md
  ├─ Notify subscribers
  └─ Track in run_data
```

**2. Journal Manager**
```python
# Every action creates journal entries:
journal_manager.add_entry(character, event)
  ├─ Filter by "theory of mind" (what they know)
  ├─ Generate internal thoughts
  └─ Write to character's journal file
```

**3. Obsidian Logger**
```python
# Every turn creates/updates:
obsidian.log_X()
  ├─ Characters/*.md
  ├─ Locations/*.md
  ├─ Events/*.md
  ├─ Quests/*.md
  ├─ Sessions/*.md
  ├─ Journals/Entries/*.md
  └─ Current Run.md
```

---

### COMBAT SUB-LOOP (When Encounter Triggers)

```python
def process_encounter():
    # 1. Generate encounter via AI
    encounter = narrative_engine.generate_random_encounter(
        party_level=3,
        environment=current_location
    )

    # 2. Create enemy characters
    enemies = [
        Character("Goblin Scout", "Goblin"),
        Character("Goblin Warrior", "Goblin")
    ]

    # 3. Combat loop
    while any_players_alive() and any_enemies_alive():
        # Each combatant attacks
        for character in all_combatants:
            if not character.alive:
                continue

            target = select_target(character)

            # Roll attack
            roll = random.randint(1, 6)
            damage = character.attack + roll

            logger.info(f"{character.name} attacks {target.name}")
            logger.info(f"Attack Roll: {roll}")
            logger.info(f"Total Damage: {character.attack} + {roll} = {damage}")

            # Apply damage (reduced by defense)
            target.take_damage(damage)

            if target.hp <= 0:
                target.alive = False
                logger.info(f"{target.name} has fallen!")

        # Log combat round
        obsidian.log_combat_event(round_data)

    # 4. Victory/defeat
    if all_enemies_dead():
        logger.info("Victory!")
        # Update quest progress
        quest_manager.update_objective("defeat", enemy_type, len(enemies))
```

---

## DATA FLOW DIAGRAM

```
┌──────────────┐
│     User     │
│ (via CLI)    │
└──────┬───────┘
       │ python main.py --turns 10
       ▼
┌──────────────────────────────────────────────────────────┐
│  DungeonMaster (Orchestrator)                            │
│  ├─ Manages game state                                   │
│  ├─ Coordinates all systems                              │
│  └─ Runs main event loop                                 │
└───┬──────────────────────────────────────────────────────┘
    │
    ├───► DnDGame (Game Logic)
    │     ├─ Characters (players, enemies)
    │     ├─ Combat resolution
    │     └─ Location tracking
    │
    ├───► NarrativeEngine (AI)
    │     ├─ Ollama (mistral/llama2)
    │     ├─ Scene descriptions
    │     ├─ Player choices
    │     ├─ Quest generation
    │     └─ Outcome narration
    │
    ├───► QuestManager
    │     ├─ Quest tracking
    │     ├─ Objective progress
    │     └─ Completion checks
    │
    ├───► GameManager
    │     ├─ Entity tracking
    │     ├─ Relationship management
    │     └─ Theory of mind
    │
    ├───► JournalManager
    │     ├─ Character journals
    │     ├─ Event filtering
    │     └─ Thought generation
    │
    ├───► GameEventManager
    │     ├─ Event publishing
    │     ├─ Run data sync
    │     └─ Subscriber notification
    │
    └───► ObsidianLogger (Output)
          ├─ Markdown files
          ├─ Character profiles
          ├─ Location pages
          ├─ Event logs
          ├─ Quest documents
          └─ Current Run.md

          ▼
    ┌─────────────────┐
    │ Obsidian Vault  │
    │ (Markdown files)│
    └─────────────────┘
```

---

## SUMMARY

**D&D 5e Compliance:** ~60% - Uses core d20 mechanic, ability scores, skill checks, but simplifies combat

**Dice Rolling:** 100% custom Python code using `random.randint()`, no external libraries

**External Frameworks:** NONE for game mechanics! Uses FastAPI for web, Ollama for AI, everything else is custom

**Event Loop:** Turn-based with AI-generated narrative, player choices, skill checks, encounters, and quest tracking - all logged to Obsidian Markdown

**Philosophy:** A **narrative-first, AI-powered** D&D experience focused on storytelling over tactical combat simulation
