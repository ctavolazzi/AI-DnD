# Integration Checklist - Pixel UI + Stats Adapter + API

**Status**: ✅ All Components Ready
**Last Updated**: December 1, 2025
**Branch**: `claude/add-image-generation-api-015iCntQJERMAJnYLyfoWMxJ`

---

## Pre-Integration Verification

- [x] Repository is clean (git status shows "nothing to commit")
- [x] Feature branch merged with main (includes Pixel UI components)
- [x] All Pixel UI files present (5 components, 1,808 lines)
- [x] StatsAdapter implemented (240 lines)
- [x] GameManager integration example provided (270 lines)
- [x] Complete documentation (3,000+ lines across 5 guides)
- [x] PixelLab API integration tested (9/9 tests passing)

---

## Integration Checklist

### Phase 1: Foundation Setup (1-2 hours)

**Goal**: Wire the stats adapter with game manager and Pixel UI

#### 1.1 Update Character Class
- [ ] Open `pygame_mvp/game/systems.py`
- [ ] Add `self.char_class = None` to `Character.__init__()`
- [ ] Verify Character now has:
  - `name`, `level`, `max_hp`, `current_hp`
  - `base_stats` (Stats object with STR, DEX, INT, CON)
  - `char_class` (CharacterClass enum)
  - `inventory` (list of items)
  - `equipment` (dict of equipped items)

#### 1.2 Implement GameManager
- [ ] Create or update `pygame_mvp/game/game_manager.py`
- [ ] Copy code from `game_manager_integration.py` example
- [ ] Implement methods:
  - `__init__(width, height, surface)`
  - `create_new_game(player_name, char_class)`
  - `_update_inventory_display()`
  - `handle_input(event)`
  - `update()`
  - `render(surface)`
- [ ] Verify GameManager has:
  - PixelInventoryScreen instance
  - PixelGameHUD instance
  - PixelDialogueBox instance
  - StatsAdapter instance

#### 1.3 Create ClassSelectionScreen
- [ ] Create `pygame_mvp/ui/class_selection_screen.py`
- [ ] Copy code from STATS_ADAPTER_INTEGRATION.md
- [ ] Implement:
  - Button layout for each class (FIGHTER, WIZARD, ROGUE, CLERIC)
  - Class descriptions
  - Selection callback
  - Display/render methods

#### 1.4 Update Main Entry Point
- [ ] Update `pygame_mvp/main.py`
- [ ] Implement screen state machine:
  - `STATE_TITLE` → TitleScreen
  - `STATE_CLASS_SELECT` → ClassSelectionScreen
  - `STATE_GAME` → GameManager
- [ ] Add screen transitions
- [ ] Wire callbacks for:
  - New Game → Class Selection → Gameplay
  - Load Game → Gameplay
  - Exit → Quit
- [ ] Test basic flow works without crashes

### Phase 2: Data Population (30-60 minutes)

**Goal**: Connect game state to UI display

#### 2.1 Hook StatsAdapter to UI
- [ ] In GameManager._update_inventory_display():
  - Get D&D stats from `self.stats_adapter.get_d20_stats()`
  - Call `inventory_screen.set_stats({...})`
  - Verify stats display updates

#### 2.2 Populate Inventory Grid
- [ ] In GameManager._update_inventory_display():
  - Loop through `self.player.inventory`
  - For each item, call `inventory_screen.add_item_to_grid(idx, item)`
  - Verify items appear in grid

#### 2.3 Update HUD with Game State
- [ ] Connect GameManager to PixelGameHUD:
  - `hud.set_hp(current_hp, max_hp)`
  - `hud.set_mp(current_mp, max_mp)`
  - `hud.set_player_pos(grid_x, grid_y)`
  - `hud.update()` each frame

#### 2.4 Test UI Updates
- [ ] Create test character:
  ```python
  manager = GameManager(1280, 720, screen)
  manager.create_new_game("Aragorn", CharacterClass.FIGHTER)
  ```
- [ ] Verify character sheet displays:
  - Name: "Aragorn"
  - Class: "Fighter"
  - STR: 15, DEX: 10, CON: 14, INT: 10, WIS: 10, CHA: 10
  - HP: 20/20
  - AC: 10, Initiative: +0, Proficiency: +2
- [ ] Verify inventory grid shows starting items

### Phase 3: Integration Testing (30 minutes)

**Goal**: Test complete flow from title to gameplay

#### 3.1 Title Screen Testing
- [ ] Run game
- [ ] Verify title screen appears
- [ ] Click "New Game"
- [ ] Verify transitions to class selection

#### 3.2 Class Selection Testing
- [ ] Verify all 4 class buttons appear
- [ ] Click each class
- [ ] Verify correct stats for each:
  - **Fighter**: High STR/CON, Low DEX/INT
  - **Wizard**: High INT, Low STR
  - **Rogue**: High DEX, Low STR/CON
  - **Cleric**: High WIS, Balanced others
- [ ] Select one class
- [ ] Verify transitions to gameplay

#### 3.3 Gameplay Testing
- [ ] Verify character sheet displays correctly
- [ ] Press [I] to show/hide inventory
- [ ] Verify stats update if you damage player:
  ```python
  manager.damage_player(5)  # Should update HP display
  ```
- [ ] Test level up:
  ```python
  manager.level_up()  # Should update proficiency bonus
  ```

#### 3.4 Dialogue Testing
- [ ] Create test NPC dialogue:
  ```python
  from pygame_mvp.ui.pixel_dialogue import DialogueSequence
  seq = DialogueSequence()
  seq.add("Wizard", "Hello, adventurer!", "happy")
  seq.add("Wizard", "Welcome to the game!", "neutral")
  manager.dialogue_box.start_sequence(seq)
  ```
- [ ] Verify typewriter effect works
- [ ] Verify NPC portrait displays (if provided)

### Phase 4: Image Generation (Optional, 30 minutes)

**Goal**: Deploy real images from PixelLab API

#### 4.1 Setup API Key
- [ ] Get PIXELLAB_API_KEY from PixelLab dashboard
- [ ] Set environment variable:
  ```bash
  export PIXELLAB_API_KEY="your_key_here"
  ```

#### 4.2 Switch to API Provider
- [ ] In `pygame_mvp/main.py` or GameManager:
  ```python
  import os
  api_key = os.getenv("PIXELLAB_API_KEY")
  if api_key:
      image_provider = APIImageProvider(api_key=api_key)
  else:
      image_provider = MockImageProvider()  # Fallback
  ```
- [ ] Pass image_provider to GameManager

#### 4.3 Generate Character Images
- [ ] Character portraits auto-generate when:
  ```python
  image_provider.get_character_portrait(name, class, width, height)
  ```
- [ ] Item images auto-generate when:
  ```python
  image_provider.get_item_image(name, width, height)
  ```
- [ ] Scene backgrounds auto-generate when:
  ```python
  image_provider.get_scene_image(location, width, height)
  ```

#### 4.4 Test Real Images
- [ ] Run game with API key
- [ ] Create character
- [ ] Wait for portrait to load (first time)
- [ ] Verify portrait appears (subsequent loads use cache)
- [ ] Check console for any API errors

---

## File Locations Reference

### Pixel UI Components
- `pygame_mvp/ui/pixel_theme.py` - Color palette
- `pygame_mvp/ui/title_screen.py` - Menu screen
- `pygame_mvp/ui/pixel_inventory.py` - Character/inventory screen
- `pygame_mvp/ui/pixel_hud.py` - In-game HUD
- `pygame_mvp/ui/pixel_dialogue.py` - NPC dialogue box

### Integration Files
- `pygame_mvp/game/stats_adapter.py` - D&D stat converter
- `pygame_mvp/game/game_manager.py` - Main game manager (to implement)
- `pygame_mvp/ui/class_selection_screen.py` - Class picker (to create)

### Image Generation
- `pygame_mvp/services/image_provider.py` - API/Mock provider
- Environment: `PIXELLAB_API_KEY` - Your API token

### Documentation
- `STATS_ADAPTER_INTEGRATION.md` - Complete integration guide
- `IMPLEMENTATION_GUIDE.md` - Design mapping to code
- `UI_ARCHITECTURE_VISUAL.md` - Architecture diagrams
- `PIXELLAB_API.md` - Image API reference

---

## Common Issues & Solutions

### Issue: Character stats not displaying
**Solution**:
- Verify StatsAdapter created: `self.stats_adapter = StatsAdapter(self.player)`
- Verify `set_stats()` called on PixelInventoryScreen
- Check that `char_class` is set before creating adapter

### Issue: Inventory grid empty
**Solution**:
- Add items to player.inventory in create_new_game()
- Call `inventory_screen.add_item_to_grid(idx, item)` for each item
- Verify item has a `name` attribute

### Issue: Image generation slow
**Solution**:
- First call generates image (500-1000ms)
- Subsequent calls use cache (<1ms)
- Use MockImageProvider during development
- Deploy APIImageProvider for production

### Issue: Screen transition freezes
**Solution**:
- Ensure GameManager.render() called every frame
- Check for infinite loops in event handlers
- Verify pygame.display.flip() called

---

## Testing Checklist

- [ ] Character creation works for all 4 classes
- [ ] Stats display correctly with D&D format (with modifiers)
- [ ] Inventory grid shows items with quantities
- [ ] UI colors match pixel theme (warm parchment)
- [ ] Screen transitions work smoothly
- [ ] No crashes when testing each screen
- [ ] Image provider works (mock or real)
- [ ] NPC dialogue displays correctly
- [ ] HUD updates when player stats change
- [ ] All buttons are clickable and responsive

---

## Performance Targets

| Component | Load Time | Memory | Notes |
|-----------|-----------|--------|-------|
| Character creation | <100ms | <5MB | StatsAdapter is fast |
| UI render | <16ms | 10MB | 60 FPS target |
| Image gen (mock) | <1ms | 5MB | Instant placeholders |
| Image gen (API) | 500-1000ms | 10MB | First time only, cached |
| Dialogue display | <50ms | 1MB | Typewriter effect |
| Inventory update | <10ms | 2MB | Grid layout |

---

## Success Criteria

✅ **Phase 1 Complete**: Game manager wired, character class selection works
✅ **Phase 2 Complete**: Stats display in UI, inventory shows items
✅ **Phase 3 Complete**: Full gameplay flow tested, no crashes
✅ **Phase 4 Complete**: (Optional) Real images generated from API

---

## Next Steps After Integration

Once integration is complete:

1. **Scene Management**
   - Create TileMap instances for each location
   - Implement scene transitions
   - Add environmental interactions

2. **Combat System**
   - Implement turn-based combat
   - Display combat actions and results
   - Integrate with HUD status display

3. **Progression System**
   - Level up mechanics
   - Equipment/stat growth
   - Quest tracking

4. **NPC System**
   - NPC dialogue branching
   - Relationship tracking
   - Shop/trading mechanics

5. **Save/Load System**
   - Serialize character state
   - Save game slots
   - Load game recovery

---

## Quick Reference: API Usage

### Create Character
```python
from pygame_mvp.game.systems import Character, CharacterClass, Stats
from pygame_mvp.game.stats_adapter import StatsAdapter

character = Character("Aragorn", level=1, max_hp=20)
character.char_class = CharacterClass.FIGHTER
character.base_stats = Stats(strength=15, dexterity=10, intelligence=10, constitution=14)
adapter = StatsAdapter(character)
```

### Get D&D Stats
```python
d20_stats = adapter.get_d20_stats()
print(f"STR: {d20_stats.strength} ({d20_stats.get_modifier('strength'):+d})")
print(f"AC: {d20_stats.ac}")
```

### Update UI
```python
inventory_screen.set_player_name(character.name)
inventory_screen.set_player_class(character.char_class.value)
inventory_screen.set_stats({
    "STR": d20_stats.strength,
    "DEX": d20_stats.dexterity,
    # ... etc
})
```

### Generate Images
```python
from pygame_mvp.services.image_provider import APIImageProvider

provider = APIImageProvider(api_key=os.getenv("PIXELLAB_API_KEY"))
portrait = provider.get_character_portrait("Aragorn", "Fighter", 80, 100)
```

---

**You are now ready to integrate everything! Start with Phase 1 and work through each phase systematically.**
