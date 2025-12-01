# Complete Integration Guide: Stats Adapter + GameManager + Pixel UI

This guide shows how to integrate the D&D Stats Adapter with your Game Manager and Pixel UI components to create a fully functional character stat display system.

## Overview

```
Game State (Character)
    ↓
StatsAdapter
    ↓ (converts to D&D format)
GameManager
    ↓ (manages game flow)
PixelInventoryScreen
    ↓ (displays stats)
Screen
```

## Step 1: Update Character Class (Optional)

If your Character class doesn't have a `char_class` attribute, add it:

**File:** `pygame_mvp/game/systems.py`

```python
from enum import Enum

class Character:
    def __init__(self, name: str, level: int = 1, max_hp: int = 20):
        self.name = name
        self.level = level
        self.char_class = None  # ADD THIS LINE
        self.base_stats = Stats()
        # ... rest of init
```

## Step 2: Use the StatsAdapter in Your GameManager

**File:** `pygame_mvp/game/game_manager.py`

```python
import pygame
from pygame_mvp.game.systems import Character, CharacterClass, Stats
from pygame_mvp.game.stats_adapter import StatsAdapter
from pygame_mvp.ui.pixel_inventory import PixelInventoryScreen

class GameManager:
    def __init__(self, width: int, height: int, surface: pygame.Surface):
        self.width = width
        self.height = height
        self.screen = surface
        self.state = GameState()

        # Player and UI
        self.player: Character = None
        self.stats_adapter: StatsAdapter = None
        self.inventory_screen = PixelInventoryScreen(width, height)

        self.show_inventory = False

    def create_new_game(self, player_name: str, char_class: CharacterClass):
        """
        Initialize a new game with player character.

        Called from TitleScreen when "New Game" is selected.
        """
        # 1. Create character
        self.player = Character(player_name, level=1, max_hp=20)
        self.player.char_class = char_class

        # 2. Set class-specific base stats
        base_stats = self._get_class_base_stats(char_class)
        self.player.base_stats = base_stats

        # 3. Create stats adapter
        self.stats_adapter = StatsAdapter(self.player)

        # 4. Update UI with initial state
        self._update_inventory_display()

    def _get_class_base_stats(self, char_class: CharacterClass) -> Stats:
        """Return starting stats for each class."""
        class_stats = {
            CharacterClass.FIGHTER: Stats(
                strength=15,
                dexterity=10,
                intelligence=10,
                constitution=14
            ),
            CharacterClass.WIZARD: Stats(
                strength=8,
                dexterity=10,
                intelligence=15,
                constitution=10
            ),
            CharacterClass.ROGUE: Stats(
                strength=10,
                dexterity=15,
                intelligence=12,
                constitution=10
            ),
            CharacterClass.CLERIC: Stats(
                strength=13,
                dexterity=10,
                intelligence=10,
                constitution=12
            ),
        }
        return class_stats.get(char_class, Stats())

    def _update_inventory_display(self):
        """Sync inventory screen with current character state."""
        if not self.player or not self.stats_adapter:
            return

        # Get D&D stats
        d20_stats = self.stats_adapter.get_d20_stats()

        # Update basic info
        self.inventory_screen.set_player_name(self.player.name)
        self.inventory_screen.set_player_class(self.player.char_class.value)
        self.inventory_screen.set_player_level(self.player.level)
        self.inventory_screen.set_player_hp(self.player.current_hp, self.player.max_hp)

        # Update D&D stats (THIS IS THE KEY PART)
        self.inventory_screen.set_stats({
            "STR": d20_stats.strength,
            "DEX": d20_stats.dexterity,
            "CON": d20_stats.constitution,
            "INT": d20_stats.intelligence,
            "WIS": d20_stats.wisdom,
            "CHA": d20_stats.charisma,
        })

        # Update inventory items
        for idx, item in enumerate(self.player.inventory):
            if idx >= 15:  # Grid max
                break
            self.inventory_screen.add_item_to_grid(idx, item)

    def handle_input(self, event: pygame.event.Event):
        """Process user input."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_i:
                self.show_inventory = not self.show_inventory
                if self.show_inventory:
                    self._update_inventory_display()

        # Forward input to inventory screen if open
        if self.show_inventory:
            self.inventory_screen.handle_event(event)

    def update(self):
        """Update game state."""
        if not self.show_inventory and self.player:
            # Game logic here
            pass

    def render(self, surface: pygame.Surface):
        """Render all visual elements."""
        # Clear screen
        surface.fill((20, 20, 30))

        # Render game world
        # ... (your existing render code)

        # Render inventory overlay if open
        if self.show_inventory:
            self.inventory_screen.render(surface)
```

## Step 3: Update Main Entry Point

**File:** `pygame_mvp/main.py`

```python
import pygame
import sys
from pygame_mvp.config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from pygame_mvp.ui.title_screen import TitleScreen
from pygame_mvp.game.game_manager import GameManager
from pygame_mvp.game.systems import CharacterClass

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Quest for the Golden Bunch")
clock = pygame.time.Clock()

# States
STATE_TITLE = "title"
STATE_GAME = "game"
current_state = STATE_TITLE

# Components
title_screen = TitleScreen(SCREEN_WIDTH, SCREEN_HEIGHT)
game_manager = GameManager(SCREEN_WIDTH, SCREEN_HEIGHT, screen)

# Title screen callbacks
def start_new_game():
    global current_state

    # For now, create a default character
    # Later, add a class selection screen
    player_name = "Hero"
    player_class = CharacterClass.FIGHTER

    game_manager.create_new_game(player_name, player_class)
    current_state = STATE_GAME

def load_game():
    global current_state
    # TODO: Implement save/load
    start_new_game()

def exit_game():
    pygame.quit()
    sys.exit()

title_screen.on_new_game = start_new_game
title_screen.on_load_game = load_game
title_screen.on_exit = exit_game

# Main loop
running = True
while running:
    # 1. Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if current_state == STATE_TITLE:
            title_screen.handle_event(event)
        elif current_state == STATE_GAME:
            game_manager.handle_input(event)

    # 2. Update
    if current_state == STATE_TITLE:
        title_screen.update()
    elif current_state == STATE_GAME:
        game_manager.update()

    # 3. Render
    if current_state == STATE_TITLE:
        title_screen.render(screen)
    elif current_state == STATE_GAME:
        game_manager.render(screen)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
```

## Step 4: Add Character Class Selection Screen (Optional)

For a more polished experience, create a class selection screen:

**File:** `pygame_mvp/ui/class_selection_screen.py`

```python
import pygame
from pygame_mvp.game.systems import CharacterClass

class ClassSelectionScreen:
    """Screen for selecting character class."""

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.selected_class = None
        self.on_class_selected = None

        # Class buttons
        self.classes = [
            CharacterClass.FIGHTER,
            CharacterClass.WIZARD,
            CharacterClass.ROGUE,
            CharacterClass.CLERIC,
        ]

        # Button positions
        self.buttons = []
        button_width = 150
        button_height = 50
        start_x = (width - (button_width * 4 + 30 * 3)) // 2
        start_y = height // 2

        for i, char_class in enumerate(self.classes):
            x = start_x + i * (button_width + 30)
            self.buttons.append({
                "class": char_class,
                "rect": pygame.Rect(x, start_y, button_width, button_height),
            })

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle input and return True if class was selected."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            for button in self.buttons:
                if button["rect"].collidepoint(event.pos):
                    self.selected_class = button["class"]
                    if self.on_class_selected:
                        self.on_class_selected(self.selected_class)
                    return True
        return False

    def render(self, surface: pygame.Surface):
        """Render the class selection screen."""
        surface.fill((20, 20, 30))

        # Title
        pygame.font.init()
        title_font = pygame.font.Font(None, 48)
        title = title_font.render("Select Your Class", True, (255, 215, 0))
        surface.blit(title, (self.width // 2 - title.get_width() // 2, 100))

        # Buttons
        button_font = pygame.font.Font(None, 32)
        for button in self.buttons:
            # Draw button background
            pygame.draw.rect(surface, (100, 80, 60), button["rect"])
            pygame.draw.rect(surface, (139, 90, 43), button["rect"], 2)

            # Draw text
            text = button_font.render(
                button["class"].value,
                True,
                (255, 245, 220)
            )
            text_rect = text.get_rect(center=button["rect"].center)
            surface.blit(text, text_rect)

        # Description
        desc_font = pygame.font.Font(None, 18)
        descriptions = {
            CharacterClass.FIGHTER: "Strong and durable",
            CharacterClass.WIZARD: "Intelligent spellcaster",
            CharacterClass.ROGUE: "Quick and cunning",
            CharacterClass.CLERIC: "Wise and holy",
        }

        for button in self.buttons:
            desc = desc_font.render(
                descriptions[button["class"]],
                True,
                (200, 200, 200)
            )
            desc_rect = desc.get_rect(
                centerx=button["rect"].centerx,
                top=button["rect"].bottom + 10
            )
            surface.blit(desc, desc_rect)
```

Then update main.py to use it:

```python
# In main.py, after current_state = STATE_TITLE

STATE_CLASS_SELECT = "class_select"
class_selection = ClassSelectionScreen(SCREEN_WIDTH, SCREEN_HEIGHT)

def on_class_selected(char_class):
    global current_state
    game_manager.create_new_game("Hero", char_class)
    current_state = STATE_GAME

class_selection.on_class_selected = on_class_selected

# In event loop:
if current_state == STATE_CLASS_SELECT:
    class_selection.handle_event(event)

# In update loop:
if current_state == STATE_CLASS_SELECT:
    pass  # No update needed

# In render loop:
if current_state == STATE_CLASS_SELECT:
    class_selection.render(screen)

# And add button to title screen to go to class selection:
def on_new_game_clicked():
    global current_state
    current_state = STATE_CLASS_SELECT

title_screen.on_new_game = on_new_game_clicked
```

## Complete Data Flow

```
┌─────────────────────────────────────────┐
│ TitleScreen                             │
│ [NEW GAME] [LOAD] [EXIT]                │
└──────────────┬──────────────────────────┘
               │
               ├──► [NEW GAME] pressed
               │
        ┌──────▼──────────────────┐
        │ ClassSelectionScreen    │
        │ [FIGHTER] [WIZARD]      │
        │ [ROGUE] [CLERIC]        │
        └──────┬──────────────────┘
               │
               ├──► Class selected (e.g., FIGHTER)
               │
        ┌──────▼──────────────────────────┐
        │ GameManager.create_new_game()   │
        │ 1. Create Character             │
        │ 2. Set base_stats               │
        │ 3. Create StatsAdapter          │
        │ 4. Update UI                    │
        └──────┬──────────────────────────┘
               │
        ┌──────▼──────────────────────────┐
        │ StatsAdapter                    │
        │ • Maps STR/DEX/INT/CON          │
        │ • Adds WIS/CHA                  │
        │ • Calculates modifiers          │
        │ • Formats for display           │
        └──────┬──────────────────────────┘
               │
        ┌──────▼──────────────────────────┐
        │ PixelInventoryScreen            │
        │ • Shows character sheet         │
        │ • Displays all 6 stats          │
        │ • Shows inventory               │
        │ • Updates on press [I]          │
        └─────────────────────────────────┘
```

## Testing the Stats Adapter

Run this to verify your stats adapter is working:

```bash
python -c "
import sys
sys.path.insert(0, '.')
from pygame_mvp.game.systems import Character, Stats, CharacterClass
from pygame_mvp.game.stats_adapter import StatsAdapter

# Create a fighter
char = Character('Test Fighter', level=5, max_hp=30)
char.char_class = CharacterClass.FIGHTER
char.base_stats = Stats(strength=14, dexterity=10, intelligence=8, constitution=14)

# Get D&D stats
adapter = StatsAdapter(char)

print('Fighter Stats:')
for line in adapter.get_stat_display_lines():
    print(line)
"
```

Expected output:
```
Fighter Stats:
STR: 16 (+3)
DEX: 9 (-1)
CON: 15 (+2)
INT: 8 (-1)
WIS: 10 (+0)
CHA: 10 (+0)

AC: 9
Initiative: -1
Proficiency: +3
```

## Summary

You now have:

1. **StatsAdapter** (`pygame_mvp/game/stats_adapter.py`)
   - Converts game stats to D&D format
   - Handles all 6 attributes
   - Calculates modifiers
   - Class-specific adjustments

2. **GameManager Integration** (`pygame_mvp/game/game_manager_integration.py`)
   - Shows how to create characters
   - Demonstrates stats adapter usage
   - Includes inventory management
   - Example implementation

3. **Complete Integration Guide** (this document)
   - Main.py setup
   - GameManager implementation
   - Character selection flow
   - Data flow diagrams

Next steps:
- [ ] Update Character class with `char_class` attribute
- [ ] Implement the GameManager with StatsAdapter
- [ ] Create ClassSelectionScreen
- [ ] Wire main.py with all screens
- [ ] Test character creation flow
- [ ] Deploy with real images (APIImageProvider)
