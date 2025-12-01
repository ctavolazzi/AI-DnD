# Implementing Game UI Designs - Implementation Guide

## Overview

The three retro game designs can be implemented using the existing pygame_mvp architecture. This guide maps each design to codebase components and provides specific implementation code.

---

## Design 1: Inventory/Character Status Screen

### Current Status
- ✅ **Implemented**: Portrait, stat bars, grid layout, components
- ⚠️ **Partially Implemented**: Stats display, inventory structure
- ❌ **Missing**: Inventory population, item details, category tabs

### Where It Fits in the Codebase

The inventory screen should integrate with **MainGameScreen** (pygame_mvp/ui/screens.py) or create a dedicated **InventoryScreen** modal.

**Current flow:**
```
GameState.inventory (InventoryState)
    ↓
MainGameScreen.update_from_state() ← TODO: Populate inventory here
    ↓
InventoryGrid.set_slot(index, image, quantity)
    ↓
Render on screen
```

### Implementation Steps

#### Step 1: Populate Inventory Grid (Quick Win)

**File**: `pygame_mvp/ui/screens.py:418-420`

**Current code:**
```python
# Update inventory (simplified - just show gold for now)
self.inv_grid.clear_all()
# TODO: Populate from actual inventory
```

**Replace with:**
```python
# Update inventory from game state
self.inv_grid.clear_all()
if self.state.inventory and self.state.inventory.items:
    for idx, item in enumerate(self.state.inventory.items):
        if idx >= self.inv_grid.num_slots:
            break  # Don't exceed grid capacity

        # Get item image from image provider or placeholder
        if item:
            try:
                item_image = self.image_provider.get_item_image(
                    item.name,
                    self.inv_grid.slot_size,
                    self.inv_grid.slot_size
                )
                # Get quantity if item supports it
                quantity = getattr(item, 'quantity', 1)
                self.inv_grid.set_slot(idx, item_image, quantity)
            except:
                # Fallback to placeholder if image generation fails
                self.inv_grid.set_slot(idx, None, 1)
```

#### Step 2: Create Categorized Inventory View

**File**: Create `pygame_mvp/ui/screens.py` → Add new class

```python
class CategorizedInventoryPanel(Panel):
    """
    Inventory panel with category tabs (Weapons, Armor, Potions, etc.)
    """

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, title="Inventory")

        # Category tabs
        self.categories = {
            "All": [],
            "Weapons": [],
            "Armor": [],
            "Potions": [],
            "Materials": [],
            "Key Items": []
        }

        self.current_category = "All"
        self.category_buttons = {}
        self._create_category_buttons()

        # Inventory grid for current category
        self.category_grid = InventoryGrid(
            x + PADDING,
            y + 60,  # Below category buttons
            slots_per_row=5,
            num_slots=15
        )

        # Item details panel
        self.item_details = Panel(
            x,
            y + self.category_grid.height + 80,
            width,
            120,
            title="Item Details"
        )

    def _create_category_buttons(self):
        """Create category selection buttons."""
        button_y = self.y + PADDING + 24  # Header height
        button_x_start = self.x + PADDING

        for i, category in enumerate(self.categories.keys()):
            btn = Button(
                button_x_start + i * 80,
                button_y,
                70,
                24,
                text=category,
                on_click=lambda cat=category: self.select_category(cat)
            )
            self.category_buttons[category] = btn

    def select_category(self, category: str):
        """Switch to a different item category."""
        self.current_category = category
        self.update_grid()

    def update_grid(self):
        """Populate grid with items from current category."""
        self.category_grid.clear_all()
        items = self.categories[self.current_category]

        for idx, item in enumerate(items):
            if idx >= self.category_grid.num_slots:
                break
            # Set item in grid (would need image from provider)
            # self.category_grid.set_slot(idx, item_image, quantity)

    def categorize_items(self, inventory_items):
        """Sort inventory items into categories."""
        for category in self.categories:
            self.categories[category].clear()

        for item in inventory_items:
            item_type = getattr(item, 'item_type', 'Materials')

            # Map item types to categories
            if item_type == "weapon":
                self.categories["Weapons"].append(item)
            elif item_type == "armor":
                self.categories["Armor"].append(item)
            elif item_type == "potion" or item_type == "consumable":
                self.categories["Potions"].append(item)
            elif item_type == "key_item":
                self.categories["Key Items"].append(item)
            else:
                self.categories["Materials"].append(item)

            # Add to "All"
            self.categories["All"].append(item)
```

#### Step 3: Add Item Details Display

**File**: `pygame_mvp/ui/components.py` → Add new class

```python
class ItemDetailsPanel(Panel):
    """
    Shows detailed information about a selected inventory item.

    Displays:
    - Item name and type
    - Effect/description
    - Value
    - Stats modifications (if equipment)
    """

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, title="Item Details")
        self.item = None
        self.detail_text = TextBox(
            x + PADDING,
            y + 28,  # Below header
            width - PADDING * 2,
            height - 60
        )

    def set_item(self, item):
        """Update display for a new item."""
        self.item = item
        if item:
            lines = self._format_item_details(item)
            self.detail_text.set_lines(lines)
        else:
            self.detail_text.set_lines(["No item selected"])

    def _format_item_details(self, item):
        """Format item data into display lines."""
        lines = []

        lines.append(f"{item.name}")
        lines.append(f"Type: {getattr(item, 'item_type', 'Unknown')}")
        lines.append("")

        # Show effect/description
        description = getattr(item, 'description', '')
        if description:
            lines.append(description)
            lines.append("")

        # Show value
        value = getattr(item, 'value', 0)
        lines.append(f"Value: {value} gold")

        # Show stat bonuses if equipment
        if hasattr(item, 'stats_bonus'):
            lines.append("")
            lines.append("Stats Bonus:")
            stats = item.stats_bonus
            if stats.strength > 0:
                lines.append(f"  +{stats.strength} STR")
            if stats.dexterity > 0:
                lines.append(f"  +{stats.dexterity} DEX")
            if stats.intelligence > 0:
                lines.append(f"  +{stats.intelligence} INT")
            if stats.constitution > 0:
                lines.append(f"  +{stats.constitution} CON")

        # Show damage if weapon
        if hasattr(item, 'damage_min'):
            lines.append("")
            lines.append(f"Damage: {item.damage_min}-{item.damage_max}")

        return lines

    def render(self, surface):
        super().render(surface)
        self.detail_text.render(surface)
```

---

## Design 2: Main Menu Screen

### Implementation

**File**: Create `pygame_mvp/ui/screens.py` → Add new class

```python
class MenuScreen:
    """
    Main menu screen with title and options.

    Features:
    - Background image (from APIImageProvider or static)
    - Title text with styling
    - Menu buttons: New Game, Load Game, Options
    - Version/Credits footer
    """

    def __init__(self, width: int, height: int, image_provider: ImageProvider):
        self.width = width
        self.height = height
        self.image_provider = image_provider

        # Background - use APIImageProvider for title screen
        self.background = image_provider.get_scene_image(
            "main menu - fantasy adventure title screen",
            width,
            height
        )

        # Menu buttons
        button_width = 200
        button_height = 50
        button_x = (width - button_width) // 2

        self.buttons = [
            Button(
                button_x,
                height // 2 - 80,
                button_width,
                button_height,
                text="NEW GAME",
                on_click=self.on_new_game
            ),
            Button(
                button_x,
                height // 2,
                button_width,
                button_height,
                text="LOAD GAME",
                on_click=self.on_load_game
            ),
            Button(
                button_x,
                height // 2 + 80,
                button_width,
                button_height,
                text="OPTIONS",
                on_click=self.on_options
            )
        ]

        self.callback_new_game = None
        self.callback_load_game = None
        self.callback_options = None

    def on_new_game(self):
        """Called when New Game button clicked."""
        if self.callback_new_game:
            self.callback_new_game()

    def on_load_game(self):
        """Called when Load Game button clicked."""
        if self.callback_load_game:
            self.callback_load_game()

    def on_options(self):
        """Called when Options button clicked."""
        if self.callback_options:
            self.callback_options()

    def render(self, surface: pygame.Surface) -> None:
        """Render the menu screen."""
        # Draw background
        if self.background:
            surface.blit(self.background, (0, 0))
        else:
            surface.fill((20, 15, 10))  # Dark brown fallback

        # Draw title with shadow effect
        pygame.font.init()
        title_font = pygame.font.Font(None, 72)

        title_text = "QUEST FOR THE GOLDEN BUNCH"

        # Shadow
        shadow = title_font.render(title_text, True, (0, 0, 0))
        surface.blit(shadow, (self.width // 2 - shadow.get_width() // 2 + 3, 103))

        # Main text
        title = title_font.render(title_text, True, (255, 215, 0))  # Gold
        surface.blit(title, (self.width // 2 - title.get_width() // 2, 100))

        # Render buttons
        for button in self.buttons:
            button.render(surface)

        # Footer
        footer_font = pygame.font.Font(None, 14)
        footer = footer_font.render("Mano Banana Games", True, (160, 160, 160))
        surface.blit(footer, (self.width - footer.get_width() - 10, self.height - 20))

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle menu input."""
        for button in self.buttons:
            if button.handle_event(event):
                return True
        return False
```

**Integration into main game loop** (`pygame_mvp/main.py`):

```python
from pygame_mvp.ui.screens import MainGameScreen, MenuScreen

class GameManager:
    def __init__(self):
        self.current_screen = None
        self.game_state = None
        self.show_menu()

    def show_menu(self):
        """Display main menu."""
        image_provider = APIImageProvider(api_key=os.getenv("PIXELLAB_API_KEY"))
        self.current_screen = MenuScreen(SCREEN_WIDTH, SCREEN_HEIGHT, image_provider)

        self.current_screen.callback_new_game = self.start_new_game
        self.current_screen.callback_load_game = self.load_game
        self.current_screen.callback_options = self.show_options

    def start_new_game(self):
        """Initialize new game."""
        self.game_state = GameState()
        self.current_screen = MainGameScreen(
            self.game_state,
            APIImageProvider(api_key=os.getenv("PIXELLAB_API_KEY"))
        )

    def load_game(self):
        """Load saved game."""
        # TODO: Implement save/load system
        pass

    def show_options(self):
        """Show options screen."""
        # TODO: Implement options screen
        pass

    def handle_events(self):
        """Process input."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            self.current_screen.handle_event(event)

        return True

    def render(self, surface):
        """Draw current screen."""
        self.current_screen.render(surface)
```

---

## Design 3: Dungeon Gameplay Screen

### Current Status
- ✅ **Implemented**: Tile map rendering, character sprite, HP/Mana bars
- ✅ **Implemented**: Adventure log (bottom dialogue)
- ⚠️ **Partially**: Minimap (currently shows stats instead of map)
- ❌ **Missing**: NPC portraits in dialogue, proper minimap rendering

### Improvements

#### Enhance Minimap Display

**File**: `pygame_mvp/ui/screens.py` → Modify existing code

**Current code** (assuming it shows stats):
```python
# Create minimap panel
self.minimap_panel = Panel(
    RIGHT_SIDEBAR_X,
    CHARACTER_PANEL_Y + CHARACTER_PANEL_HEIGHT + MARGIN,
    RIGHT_SIDEBAR_WIDTH,
    200,
    title="Minimap"
)
```

**Enhanced version with actual map rendering:**

```python
class MinimapPanel(Panel):
    """
    Shows a zoomed-out view of the current dungeon/map.
    """

    def __init__(self, x, y, width, height, tile_map: TileMap):
        super().__init__(x, y, width, height, title="Minimap")
        self.tile_map = tile_map
        self.zoom = 4  # pixels per tile
        self.player_pos = (0, 0)

    def set_player_position(self, grid_x: int, grid_y: int):
        """Update player position on minimap."""
        self.player_pos = (grid_x, grid_y)

    def render(self, surface: pygame.Surface) -> None:
        """Render minimap."""
        super().render(surface)  # Draw panel border/background

        # Calculate viewport within minimap
        content_x = self.x + PADDING
        content_y = self.y + 28 + PADDING  # Below header
        content_width = self.width - PADDING * 2
        content_height = self.height - 28 - PADDING * 2

        # Get map tiles to display (centered on player)
        tiles_per_row = self.tile_map.width
        tiles_per_col = self.tile_map.height

        # Draw tiles
        for row in range(tiles_per_col):
            for col in range(tiles_per_row):
                tile = self.tile_map.tiles[row][col]

                x = content_x + col * self.zoom
                y = content_y + row * self.zoom

                # Draw based on tile type
                if tile.walkable:
                    color = (100, 100, 100)  # Gray floor
                else:
                    color = (50, 50, 50)  # Dark wall

                pygame.draw.rect(surface, color, (x, y, self.zoom, self.zoom))
                pygame.draw.rect(surface, (30, 30, 30), (x, y, self.zoom, self.zoom), 1)

        # Draw player position
        player_x = content_x + self.player_pos[0] * self.zoom + self.zoom // 2
        player_y = content_y + self.player_pos[1] * self.zoom + self.zoom // 2
        pygame.draw.circle(surface, (255, 215, 0), (int(player_x), int(player_y)), 3)
```

#### Add NPC Portraits to Dialogue

**File**: `pygame_mvp/ui/components.py` → Modify DialogueBox or create DialoguePanel

```python
class DialoguePanel(Panel):
    """
    Displays dialogue with NPC portrait and text.
    """

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, title="")

        # NPC portrait (left side)
        self.portrait = ImageFrame(
            x + PADDING,
            y + PADDING,
            80,
            100
        )

        # Dialogue text (right side)
        self.dialogue_text = TextBox(
            x + 100,
            y + PADDING,
            width - 120,
            height - PADDING * 2
        )

        self.npc_name = ""

    def set_dialogue(self, npc_name: str, portrait_image: pygame.Surface,
                     dialogue_text: str):
        """
        Update dialogue display.

        Args:
            npc_name: Name of NPC speaking
            portrait_image: Portrait of NPC
            dialogue_text: What NPC is saying
        """
        self.npc_name = npc_name
        self.portrait.set_image(portrait_image)
        self.dialogue_text.set_lines(dialogue_text.split('\n'))

    def render(self, surface: pygame.Surface) -> None:
        """Render dialogue with portrait."""
        super().render(surface)  # Draw background/border

        # Draw NPC name
        pygame.font.init()
        name_font = pygame.font.Font(None, FONT_SIZE_NORMAL)
        name_text = name_font.render(self.npc_name, True, (255, 215, 0))
        surface.blit(name_text, (self.x + PADDING + 80, self.y + PADDING))

        # Render portrait and text
        self.portrait.render(surface)
        self.dialogue_text.render(surface)
```

**Usage in MainGameScreen:**

```python
def update_from_state(self):
    # ... existing code ...

    # Update dialogue if NPC present
    current_location = self.state.location
    if current_location and current_location.npc:
        npc = current_location.npc
        npc_portrait = self.image_provider.get_character_portrait(
            npc.name,
            npc.char_class,
            80,
            100
        )
        self.dialogue_panel.set_dialogue(
            npc.name,
            npc_portrait,
            current_location.dialogue
        )
```

---

## Component Compatibility Matrix

| Component | Design 1 | Design 2 | Design 3 | Status |
|-----------|----------|----------|----------|--------|
| Portrait Frame | ✅ | ❌ | ✅ | Existing |
| StatBar | ✅ | ❌ | ✅ | Existing |
| Panel | ✅ | ✅ | ✅ | Existing |
| Button | ✅ | ✅ | ✅ | Existing |
| TextBox | ✅ | ✅ | ✅ | Existing |
| InventoryGrid | ✅ | ❌ | ❌ | Existing (needs population) |
| ItemDetailsPanel | ✅ | ❌ | ❌ | Needs creation |
| CategorizedInventory | ✅ | ❌ | ❌ | Needs creation |
| MenuScreen | ❌ | ✅ | ❌ | Needs creation |
| MinimapPanel | ❌ | ❌ | ✅ | Needs enhancement |
| DialoguePanel | ❌ | ❌ | ✅ | Needs creation |

---

## Implementation Priority

### Phase 1: Quick Wins (30 minutes)
1. **Populate inventory grid** - Just modify screens.py:420
2. **Enhance minimap** - Create MinimapPanel class
3. **Add item details display** - Create ItemDetailsPanel class

### Phase 2: Major Features (2-3 hours)
4. **Menu screen** - Create MenuScreen class
5. **Categorized inventory** - Create CategorizedInventoryPanel class
6. **Dialogue with portraits** - Create DialoguePanel class

### Phase 3: Polish (Optional)
7. **Screen transitions** - Add fade/slide effects
8. **Drag & drop items** - Extend InventoryGrid event handling
9. **Save/Load system** - Implement persistent storage
10. **Animation** - Add sprite animations using PixelLab API

---

## Code Integration Checklist

- [ ] Populate inventory grid in MainGameScreen.update_from_state()
- [ ] Create ItemDetailsPanel class in components.py
- [ ] Create CategorizedInventoryPanel class in screens.py
- [ ] Create MenuScreen class in screens.py
- [ ] Enhance MinimapPanel with tile rendering
- [ ] Create DialoguePanel with NPC portraits
- [ ] Integrate MenuScreen into main game loop
- [ ] Add screen transition logic to GameManager
- [ ] Test all screens with MockImageProvider
- [ ] Deploy real images with APIImageProvider

---

## Example: Complete Inventory Screen in 50 Lines

```python
def update_inventory_display(self):
    """Populate inventory grid with items from game state."""
    self.inv_grid.clear_all()

    inventory = self.state.inventory
    if not inventory or not inventory.items:
        return

    for idx, item in enumerate(inventory.items):
        if idx >= self.inv_grid.num_slots:
            break

        # Get item image
        item_image = self.image_provider.get_item_image(
            item.name,
            self.inv_grid.slot_size,
            self.inv_grid.slot_size
        )

        # Get quantity
        quantity = getattr(item, 'quantity', 1)

        # Set in grid
        self.inv_grid.set_slot(idx, item_image, quantity)

        # When slot is selected, show details
        if self.inv_grid.selected_index == idx:
            self.show_item_details(item)

def show_item_details(self, item):
    """Display item details in side panel."""
    details = f"""
{item.name}
Type: {item.item_type}

{item.description}

Value: {item.value} gold
"""
    self.item_details_panel.set_text(details)
```

This gives you all the pieces needed to implement the three game designs using the existing pygame_mvp architecture!
