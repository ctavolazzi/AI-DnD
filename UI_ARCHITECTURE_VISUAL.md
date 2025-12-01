# UI Architecture Visual Map

## Game Screen Hierarchy

```
┌─────────────────────────────────────────────────────────────────┐
│                          Game Manager                            │
│ - Manages screen transitions                                     │
│ - Handles input routing                                          │
│ - Manages game state lifecycle                                   │
└────────────┬──────────────────────┬──────────────────┬──────────┘
             │                      │                  │
      ┌──────▼──────┐         ┌─────▼─────┐      ┌────▼─────┐
      │ MenuScreen  │◄────────►│MainGame   │◄────►│Options   │
      │             │          │Screen     │      │Screen    │
      │ NEW GAME    │          │           │      │(Future)  │
      │ LOAD GAME   │          │ (Active)  │      └──────────┘
      │ OPTIONS     │          │           │
      └─────────────┘          └───────────┘
                                     │
                    ┌────────────────┼────────────────┐
                    │                │                │
              ┌─────▼─────┐  ┌───────▼──────┐ ┌─────▼─────┐
              │  Inventory│  │Main Game     │ │Dungeon    │
              │ Overlay   │  │Panels        │ │Screen     │
              │ (Press I) │  │              │ │           │
              └───────────┘  └──────────────┘ └───────────┘
```

---

## MainGameScreen Component Layout

```
┌──────────────────────────────────────────────────────────────────────┐
│                         1280 x 720 px                                 │
├──────────────────────────────────────────────────────────────────────┤
│ Left 250px   │ Center 700px           │ Right 280px                   │
├──────────────────────────────────────────────────────────────────────┤
│              │                        │                               │
│ ┌──────────┐ │ ┌─────────────────┐   │ ┌─────────────────────────┐  │
│ │   MAP    │ │ │  SCENE VIEWER   │   │ │  CHARACTER PANEL        │  │
│ │ PANEL    │ │ │  (320x420px)    │   │ │  • Portrait (80x100)    │  │
│ │          │ │ │                 │   │ │  • HP/Mana Bars         │  │
│ │ 180x200  │ │ │ Generated from  │   │ │  • Stat display         │  │
│ │          │ │ │ APIImageProvider│   │ │  • Level/XP             │  │
│ └──────────┘ │ └─────────────────┘   │ └─────────────────────────┘  │
│              │                        │                               │
│ ┌──────────┐ │ ┌─────────────────┐   │ ┌─────────────────────────┐  │
│ │NAV PANEL │ │ │ ADVENTURE LOG   │   │ │ INVENTORY PANEL         │  │
│ │          │ │ │ (Scrolling text)│   │ │ • 5x3 grid (15 slots)   │  │
│ │ Exits    │ │ │                 │   │ │ • 44x44 per slot        │  │
│ │ Points   │ │ │ Recent events   │   │ │ • Item quantities       │  │
│ │ of Int   │ │ │ Dialogue        │   │ │ • Drag & drop ready     │  │
│ └──────────┘ │ └─────────────────┘   │ └─────────────────────────┘  │
│              │                        │                               │
│              │                        │ ┌─────────────────────────┐  │
│              │                        │ │ QUEST PANEL             │  │
│              │                        │ │ • Current quest         │  │
│              │                        │ │ • Objectives            │  │
│              │                        │ │ • Rewards               │  │
│              │                        │ └─────────────────────────┘  │
├──────────────────────────────────────────────────────────────────────┤
│ Status: Turn 5 / Phase: PLAYER_TURN / Gold: 250                      │
│ [ Next Turn ] [ Attack ] [ Cast Spell ] [ Use Item ]                 │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Inventory System Architecture

```
┌─ GameState.inventory ─┐
│   InventoryState      │
│   • items: List[Item] │
│   • equipped: Dict    │
│   • gold: int         │
│   • capacity: int     │
└───────────┬───────────┘
            │
    ┌───────▼─────────┐
    │ Update from     │
    │ game state flow │
    └───────┬─────────┘
            │
            ├─────────────────────────┬────────────────────┐
            │                         │                    │
       ┌────▼────────┐   ┌───────────▼──────┐   ┌────────▼──────┐
       │InventoryGrid│   │ItemDetailsPanel  │   │EquipmentPanel │
       │ (5x3 grid)   │   │ (Item info/stats)│   │(Equipped items)│
       │             │   │                  │   │                │
       │ 15 slots    │   │ - Name           │   │ - Helmet       │
       │ 44x44 each  │   │ - Type           │   │ - Chest        │
       │             │   │ - Description    │   │ - Hands        │
       │ Click →     │   │ - Stats bonus    │   │ - Feet         │
       │ Select      │   │ - Damage (if wpn)│   │ - Weapon       │
       │ item        │   │ - Value          │   │ - Shield       │
       └─────────────┘   └──────────────────┘   └────────────────┘
                                │
                    ┌───────────▼──────────────┐
                    │ Categorized View         │
                    │ (Optional add-on)        │
                    │ • All                    │
                    │ • Weapons                │
                    │ • Armor                  │
                    │ • Potions                │
                    │ • Materials              │
                    │ • Key Items              │
                    └──────────────────────────┘
```

---

## Image Generation Pipeline

```
┌──────────────────────────────────────────────────────────────┐
│              Game State (Characters, Items, Scenes)          │
└────────────────────────┬─────────────────────────────────────┘
                         │
                    ┌────▼──────────────────┐
                    │  APIImageProvider     │
                    │  (or MockImageProvider)
                    └────┬──────────────────┘
                         │
         ┌───────────────┼──────────────────┬──────────────────┐
         │               │                  │                  │
    ┌────▼────┐  ┌───────▼────┐  ┌────────▼─────┐  ┌─────────▼─────┐
    │Pixflux  │  │ Bitforge   │  │ Animate      │  │ Rotate/Inpaint│
    │ Gen     │  │ (Style-    │  │ (Skeleton or │  │ (Transform)    │
    │         │  │ based)     │  │  Text)       │  │                │
    │Text→IMG │  │Ref.→Styled │  │Char→Animation│  │Sprite↔Direction│
    └────┬────┘  └───────┬────┘  └────────┬─────┘  └─────────┬─────┘
         │               │                │                  │
         └───────────────┼────────────────┴──────────────────┘
                         │
              ┌──────────▼──────────────┐
              │ pygame.Surface (cached) │
              │ for display in UI       │
              └────────────────────────┘
                         │
         ┌───────────────┼────────────────┐
         │               │                │
    ┌────▼─────┐  ┌─────▼──────┐  ┌─────▼────┐
    │Character │  │  Item Icon  │  │Scene View │
    │Portrait  │  │ (44x44px)   │  │(320x420px)│
    │(80x100px)│  │ in Inventory│  │ in center │
    └──────────┘  └─────────────┘  └──────────┘
```

---

## Component Relationships

```
UIComponent (Abstract Base)
  ├─ Panel
  │   ├─ MainGameScreen
  │   │   ├─ CharacterPanel (contains Portrait + StatBars)
  │   │   ├─ InventoryPanel (contains InventoryGrid)
  │   │   ├─ MapPanel
  │   │   ├─ NavigationPanel
  │   │   ├─ AdventureLogPanel (contains TextBox)
  │   │   ├─ QuestPanel (contains TextBox)
  │   │   └─ MinimapPanel (NEW)
  │   │
  │   ├─ CategorizedInventoryPanel (NEW)
  │   │   ├─ Category buttons (Button list)
  │   │   ├─ InventoryGrid (current category)
  │   │   └─ ItemDetailsPanel (NEW)
  │   │
  │   ├─ MenuScreen (NEW)
  │   │   ├─ Title image (ImageFrame)
  │   │   └─ Menu buttons (Button list)
  │   │
  │   └─ DialoguePanel (NEW)
  │       ├─ NPC Portrait (ImageFrame)
  │       └─ Dialogue text (TextBox)
  │
  ├─ Button
  │   └─ Used in: MenuScreen, CategorizedInventoryPanel, Actions
  │
  ├─ TextBox
  │   └─ Used in: Log, Quest, Dialogue, Item Details
  │
  ├─ ImageFrame
  │   └─ Used in: Character Portrait, NPC Portrait, Scene Viewer
  │
  ├─ StatBar
  │   └─ Used in: HP/Mana display in Character Panel
  │
  └─ InventoryGrid
      ├─ InventorySlot (5x3 grid, 44x44 per slot)
      └─ Used in: Inventory Panel, Categorized Inventory
```

---

## Data Flow: Item to Display

```
1. Game State
   └─ inventory.items = [Health Potion, Sword, Leather Armor, ...]

2. MainGameScreen.update_from_state()
   └─ Calls: image_provider.get_item_image("Health Potion", 44, 44)

3. APIImageProvider.get_item_image()
   ├─ Create prompt: "Health Potion, pixel art item icon, ..."
   ├─ Call: _generate_pixflux(prompt, 44, 44)
   ├─ Get response: PixelLab API response with base64 image
   └─ Decode: base64 → pygame.Surface

4. Cache & Return
   └─ Store in _cache[(item, 44, 44)] for reuse

5. InventoryGrid.set_slot(index=0, image, quantity=1)
   ├─ Create InventorySlot
   ├─ Set item image
   └─ Store quantity badge

6. Render
   ├─ InventoryGrid.render(surface)
   │  └─ For each slot: slot.render(surface)
   │     ├─ Draw background/border
   │     ├─ Draw item image centered
   │     ├─ Draw quantity badge (bottom right)
   │     └─ Highlight if selected
   │
   └─ Display on screen
```

---

## Screen Transition Flow

```
START
  │
  └─► MenuScreen
       │
       ├─ NEW GAME ──────────────────┐
       │                             │
       ├─ LOAD GAME ────────────────┐│
       │                            ││
       └─ OPTIONS ──────────────────┐││
                                    │││
                              ┌─────▼▼▼──┐
                              │Initialize │
                              │Game State │
                              └─────┬────┘
                                    │
                                    └──► MainGameScreen (GAMEPLAY)
                                          │
                                    ┌─────┴──────────┬──────┐
                                    │                │      │
                                  [I] key        [C] key   [Q] quit
                                    │                │      │
                                ┌───▼────┐      ┌────▼───┐  │
                                │Inventory│      │Character│  │
                                │Overlay  │      │Overlay  │  │
                                └────┬────┘      └────┬────┘  │
                                     │                │       │
                                     ├────────┬───────┘       │
                                     │        │               │
                            (Press I/C again to close)       │
                                     │        │               │
                                     └────┬───┘               │
                                          │                   │
                                          └───────────────────┘
                                                   │
                                                   └─► EXIT
```

---

## Customization Points

### Theme System
```python
CURRENT_THEME = {
    "panel_bg": (45, 35, 30),           # Brown
    "panel_border": (139, 90, 43),      # Bronze
    "text_primary": (255, 245, 220),    # Cream
    "text_highlight": (255, 215, 0),    # Gold
    "hp_bar": (180, 40, 40),            # Red
    "mana_bar": (40, 80, 180),          # Blue
    # Can be overridden per screen or component
}
```

### Configuration
```python
# pygame_mvp/config.py controls all layout
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
PORTRAIT_WIDTH = 80
PORTRAIT_HEIGHT = 100
INVENTORY_SLOTS_PER_ROW = 5
INVENTORY_SLOT_SIZE = 44
# ... many more customizable values
```

### Image Provider
```python
# Switch between real API and mock
if USE_API:
    provider = APIImageProvider(api_key=os.getenv("PIXELLAB_API_KEY"))
else:
    provider = MockImageProvider()  # For development

# All screens use same provider interface
screen = MainGameScreen(game_state, provider)
```

---

## Extension Points

### Adding New Panels
1. Create class extending `Panel`
2. Add to `MainGameScreen.panels` list
3. Implement `update_from_state()` method
4. Implement `render()` method
5. Optionally handle events with `handle_event()`

### Adding New Screens
1. Create class extending `Screen` or implement interface
2. Implement `render(surface)` and `handle_event(event)`
3. Register in `GameManager.screens` dict
4. Add transition logic to `GameManager.transition_to(screen_name)`

### Adding Item Categories
1. Extend `Item` data class with `category` field
2. Add category to `CategorizedInventoryPanel.categories` dict
3. Update `categorize_items()` logic
4. Add category button in UI

---

## Performance Considerations

```
Image Generation Cost:
  ├─ First call to get_item_image("Sword", 44, 44)
  │  ├─ API request to PixelLab: ~500ms
  │  └─ Cache result
  │
  └─ Second call with same params
     └─ Return from cache: <1ms

Inventory Rendering:
  ├─ 15 slots × simple draw operations: ~5ms
  └─ No API calls after caching

Recommendation:
  • Generate all item images once during game startup
  • Pre-cache common character portraits
  • Use MockImageProvider for testing (instant)
  • Lazy load on-demand for optional items
```

---

This visual map shows how all three designs (Inventory, Menu, and Dungeon screens) fit together
into a cohesive architecture that leverages the existing pygame_mvp component system!
