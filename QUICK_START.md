# 🎬 Quick Start - Interactive Story Theater

## What You Got

A complete **AI-powered story theater** that creates expandable, illustrated D&D adventures. Your choices drive the narrative, and images are automatically generated and placed throughout like an illustrated novel.

## The 3 Things You Asked For ✅

### 1. Story Generated First → Used for Image Prompts ✅
- Backend generates the story text FIRST
- AI analyzes the text and extracts 2-3 visual scenes
- Images are created FROM the story (not the other way around)
- Smart prompts based on actual narrative content

### 2. Banner + Peppered Images (Book/Article Layout) ✅
- Big banner image across the top (16:9 widescreen)
- Story styled like a book (beautiful typography, proper spacing)
- Images automatically peppered throughout chapters
- Positioned at start, middle, or end based on scene analysis

### 3. Chat Window for Continuation ✅
- Fixed sidebar chat on the right
- Type what you do, press Enter
- AI generates the next chapter with new images
- Story expands downward like a living document
- Save to Obsidian anytime with one click

## Launch It (3 Commands)

```bash
# 1. Make sure you have a Gemini API key in .env
echo "GEMINI_API_KEY=your_key_here" > .env

# 2. Run the start script
./start_story_theater.sh

# 3. That's it! Browser opens automatically
```

## Or Start Manually

```bash
# Terminal 1: Story engine
python3 dnd_narrative_server.py

# Terminal 2: Image generator
python3 nano_banana_server.py

# Open in browser
open interactive-story-theater.html
```

## How It Works

```
You type in chat: "I enter the dark cave"
    ↓
AI generates chapter: "You step into the darkness. Ancient runes
glow on the walls. A dragon's roar echoes from deep within..."
    ↓
AI extracts scenes:
  - Scene 1 (start): "Ancient runes glow on the walls"
  - Scene 2 (end): "Dragon's roar echoes from within"
    ↓
Images generated and inserted at those points
    ↓
You see the complete illustrated chapter
    ↓
You type next action: "I cast Light spell"
    ↓
Process repeats, story grows...
```

## Key Features

- **Story-First:** Text before images (your requirement #1)
- **Book Layout:** Banner + peppered images (your requirement #2)
- **Chat-Driven:** Sidebar chat expands story (your requirement #3)
- **Save Anywhere:** One-click save to Obsidian
- **D&D Rules:** Backed by actual game system
- **Smart Images:** AI finds visual moments in your story
- **Beautiful:** Book-style typography, smooth animations

## What Got Created

1. **`interactive-story-theater.html`** - The main app
2. **`/generate-chapter` endpoint** - Story-first backend
3. **`/save-story` endpoint** - Obsidian integration
4. **Scene extraction logic** - Intelligent image placement
5. **Complete documentation** - INTERACTIVE_STORY_THEATER_README.md

## Try It Now

1. Start the servers (see commands above)
2. Open the page
3. Enter a character name
4. Describe a story (or leave blank for random)
5. Click "Begin Your Story"
6. Type what you do in the chat
7. Watch the illustrated story grow!

## Example Adventure

```
Character: Aldric
Story: "A wizard defending his tower from invaders"

Chat: "I look out the window at the approaching army"
→ Chapter 1 generates with:
   - Banner: The tower under siege
   - Start image: View from the window
   - End image: The approaching army

Chat: "I prepare a massive fireball spell"
→ Chapter 2 generates with:
   - Start image: Aldric gathering magical energy
   - Middle image: The spell forming
   - End image: Fireball ready to launch

And so on... your story grows!
```

## Files You Can Explore

- `interactive-story-theater.html` - Main interface
- `INTERACTIVE_STORY_THEATER_README.md` - Full documentation
- `IMPLEMENTATION_COMPLETE.md` - Technical details
- `decision-matrix-story-theater.md` - Architecture decisions

## Troubleshooting

**No images?**
- Check that nano_banana_server.py is running
- Verify GEMINI_API_KEY in .env

**Can't save?**
- Make sure ai-dnd-test-vault/ directory exists
- Check backend logs

**Need help?**
- Read INTERACTIVE_STORY_THEATER_README.md
- Check logs/ directory for error messages

---

## 🎉 You're Ready!

Everything you asked for is implemented and working:

✅ Story text generates first, then used for smart image prompts
✅ Beautiful book layout with banner and peppered images
✅ Chat window drives an expandable, living story

**Start creating adventures!** 🎲✨

