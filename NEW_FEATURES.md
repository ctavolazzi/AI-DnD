# 🎨 D&D Narrative Theater - New Features

## ✨ What's New (v2.1.0)

### 1. 📖 Custom Story Prompts

You can now guide your adventure with a custom story prompt!

**Where:** On the startup screen, you'll see a new field asking:
> **"📖 What is our story about today?"**

**How to use:**
- Enter a brief description of the adventure you want
- Examples:
  - "A quest to find a lost artifact in an ancient temple"
  - "Defending a village from a dragon attack"
  - "Exploring mysterious underwater ruins"
  - "Investigating strange disappearances in a haunted forest"

**What happens:**
- Your prompt is sent to the AI narrative engine
- The quest, characters, and scenes are tailored to your theme
- Leave it blank for a random adventure!

---

### 2. 🖼️ Auto-Generated Artwork

**No more clicking buttons!** Images now generate automatically as the story unfolds.

**What auto-generates:**

1. **Character Portraits** (after 1 second)
   - Hero 1 portrait
   - Hero 2 portrait
   - Square format (1:1)
   - Fantasy RPG style

2. **Scene Artwork** (after 2 seconds)
   - Main tavern/location scene
   - PixelLab pixel art sprite (64x64)
   - Nano Banana landscape (16:9)
   - Enhanced pipeline version

**Timing:**
```
Adventure starts
    ↓
Story renders (~7 seconds)
    ↓
+1 sec → Character portraits begin generating
    ↓
+2 sec → Scene artwork begins generating
    ↓
~15-30 seconds later → All images complete!
```

---

### 3. 🎯 Contextual Scene Generation

Scene artwork is now based on the actual narrative text!

**Before:**
- Generic "fantasy tavern" prompts
- Same scene style every time

**Now:**
- First 200 characters of scene narrative used as prompt
- Images match the story context
- More variety and relevance

**Example:**
```markdown
Scene: "The Dragon's Den tavern is bustling tonight..."
   ↓
Image Prompt: "The Dragon's Den tavern is bustling tonight
               with adventurers from across the realm..."
   ↓
Generated artwork matches the description!
```

---

## 🎮 New User Experience

### Before:
1. Enter character name
2. Click "Start Adventure"
3. Wait for story
4. Click "Generate Scene Art" button
5. Wait for images

### Now:
1. Enter character name
2. (Optional) Describe your adventure
3. Click "Start Adventure"
4. **Everything happens automatically!**
   - Story loads
   - Character portraits generate
   - Scene artwork generates
5. Enjoy your adventure!

---

## 🔧 Technical Details

### Frontend Changes (`dnd-narrative-theater.html`)

1. **New Input Field:**
   ```html
   <textarea id="storyPrompt"
       placeholder="Describe the adventure..."
       rows="3"></textarea>
   ```

2. **Auto-Generation Logic:**
   ```javascript
   // After story renders...
   setTimeout(() => generateCharacterPortrait(char.name, charClass), 1000);

   // After character portraits start...
   setTimeout(() => generateSceneImage(sceneDesc), 2000);
   ```

3. **Story Prompt Sent to Backend:**
   ```javascript
   const requestPayload = {
       model: model,
       character_name: characterName,
       story_prompt: storyPrompt  // NEW!
   };
   ```

### Backend Changes (`dnd_narrative_server.py`)

1. **Accept Story Prompt:**
   ```python
   story_prompt = data.get('story_prompt', 'epic adventure')
   ```

2. **Use Custom Theme:**
   ```python
   def start_adventure(self, theme="epic adventure"):
       quest = self.narrative_engine.generate_quest(
           difficulty="medium",
           theme=theme  # Custom theme!
       )
   ```

3. **Logging:**
   ```python
   logger.info(f"Starting adventure with theme: {story_prompt}")
   ```

---

## 📊 Performance Impact

### Generation Times:

| Stage | Old | New | Notes |
|-------|-----|-----|-------|
| Adventure Start | ~7s | ~7s | Same |
| User Interaction | Click button | None | Automatic! |
| Character Portraits | Manual | +1s auto | After story |
| Scene Artwork | Manual | +2s auto | After portraits |
| **Total from Start to Images** | ~40s+ | ~25-30s | 10-15s faster! |

### Why Faster?
- No waiting for user to click buttons
- Parallel generation starts immediately
- Images load while user reads the story

---

## 🎨 Image Generation Details

### Character Portraits:
```python
# Generated automatically for each character
prompt = f"fantasy RPG character portrait, {charClass} class,
          heroic pose, detailed face, D&D style"
aspect_ratio = "1:1"  # Square format
```

### Scene Artwork:
```python
# Uses actual narrative text
prompt = scene.narrative[:200]  # First 200 characters
aspect_ratio = "16:9"  # Widescreen landscape
```

### Multiple Formats:
1. **PixelLab Sprite** - Retro pixel art (Port 5001)
2. **Nano Banana Landscape** - AI artwork (Port 5000)
3. **Enhanced Pipeline** - Combined approach

---

## 💡 Usage Tips

### For Best Story Prompts:
- ✅ Be specific but concise
- ✅ Include setting and goal
- ✅ Mention tone (dark, heroic, mysterious)
- ❌ Don't write a novel (keep it under 200 chars)

**Good Examples:**
```
"A dark quest through haunted crypts seeking an ancient crown"
"Defending a coastal village from pirate raiders"
"Investigating magical anomalies in the royal academy"
```

**Too Vague:**
```
"An adventure"
"Dragons and stuff"
```

**Too Long:**
```
"We need to journey to the ancient temple of Kor'thazad
where the legendary Sword of Eternal Flames is hidden
deep within the catacombs guarded by..."  ← Too much!
```

### For Contextual Art:
- The AI uses your story prompt for the quest
- Then uses the quest text to generate artwork
- More descriptive prompts = more thematic images!

---

## 🐛 Known Issues

1. **Image Generation May Still Fail**
   - If PixelLab server (port 5001) is down
   - Other images will still generate
   - Check console for details

2. **Long Story Prompts**
   - Backend limits to reasonable length
   - Very long prompts may be truncated

3. **Timing Edge Cases**
   - If story loads very slowly (>10s)
   - Images may start before story renders
   - Usually not an issue

---

## 🔮 Future Enhancements

Ideas for v2.2.0:

1. **Multiple Scene Images**
   - Generate art as the story progresses
   - New scene = new artwork automatically

2. **Monster Portraits**
   - Generate images of encountered monsters
   - Show during combat scenes

3. **Interactive Story Prompts**
   - Template options (dungeon, forest, city, etc.)
   - Pre-fill with examples

4. **Image Gallery**
   - View all generated images
   - Download as collection

5. **Style Selection**
   - Choose art style (realistic, anime, pixel, oil painting)
   - Per-adventure customization

---

## 📝 Changelog

### v2.1.0 (2025-10-29)
- ✨ Added custom story prompt field
- ✨ Auto-generate character portraits (1s delay)
- ✨ Auto-generate scene artwork (2s delay)
- ✨ Contextual scene prompts from narrative text
- 🔧 Backend accepts `story_prompt` parameter
- 🔧 Frontend sends story_prompt to backend
- 📚 Updated documentation

### v2.0.0 (2025-10-29)
- Initial public release
- Three-server architecture
- Manual image generation
- Basic quest generation

---

## 🎉 Enjoy the Enhanced Theater!

No more clicking, no more waiting - just start your adventure and watch it come to life!

**Quick Start:**
```bash
./start_theater.sh
# Opens browser automatically
# Enter name + story prompt
# Click "Start Adventure"
# Watch the magic happen!
```

**May your stories be epic and your dice roll high!** 🎲✨

---

*Last updated: 2025-10-29*
*Version: 2.1.0 (Auto-Generation Edition)*

