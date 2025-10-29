# Life RPG Asset Gallery

A collection of pixel art assets designed for a Life RPG prototype application. This project demonstrates asset organization and generation for a gamified life tracking application.

## Overview

The Life RPG is a gamification concept that turns real-life goals and achievements into an RPG-style progression system. This asset collection includes:

- **Achievement Badges** (10 assets) - Trophy icons for milestones like "First Dollar", "The Flipper", "Boss Mode"
- **Quest Line Icons** (5 assets) - Icons representing quest lines like "Van Life", "Land Fund", "Workshop Path"
- **Stat Icons** (8 assets) - Visual indicators for stats like Cash, Skills, Connections, XP Gain
- **Character Sprites** (4 assets) - Player character and environment sprites
- **UI Elements** (6 assets) - Trophies, quest completion banners, and decorative elements

**Total Assets: 33**

## Project Structure

```
life-rpg-imagery/
├── README.md                          # This file
├── index.html                         # Interactive gallery viewer
├── generate_life_rpg_assets.py        # PixelLab API generator (requires API key)
├── generate_placeholder_assets.py     # Placeholder generator (no API required)
└── generated/
    ├── metadata.json                  # Asset metadata
    ├── achievements/                  # 10 achievement badge icons
    ├── quests/                        # 5 quest line icons
    ├── stats/                         # 8 stat and progress icons
    ├── characters/                    # 4 character/environment sprites
    └── ui/                            # 6 UI decorative elements
```

## Viewing the Gallery

Open `index.html` in a web browser to view the interactive asset gallery. The gallery features:

- Organized categories with color-coded sections
- Hover effects and interactive cards
- Click any asset to view it enlarged
- Responsive grid layout
- Asset metadata including names and descriptions

### Local Server (Recommended)

For best results, serve the gallery through a local web server:

```bash
# Using Python
python3 -m http.server 8000

# Then visit http://localhost:8000 in your browser
```

## Generating Assets

### Method 1: PixelLab API (Production Quality)

The `generate_life_rpg_assets.py` script generates high-quality pixel art using the PixelLab API:

```bash
python3 generate_life_rpg_assets.py
```

**Requirements:**
- Valid PixelLab API key (configured in `../.mcp.json`)
- `pip install pillow pixellab`

This script creates:
- 64x64px icons with customizable outlines and shading
- 128x128px character sprites
- Transparent backgrounds
- Isometric and front-view perspectives

### Method 2: Placeholder Generator (No API Required)

The `generate_placeholder_assets.py` script creates labeled placeholder images:

```bash
python3 generate_placeholder_assets.py
```

**Features:**
- No API key required
- Color-coded by category
- Text labels for easy identification
- Instant generation

## Asset Categories

### 🏆 Achievement Badges (Gold Theme)

Milestone achievements that unlock as the player progresses:

- **First Dollar** - Earned first dollar from content
- **The Flipper** - Completed first furniture flip
- **Consistent Creator** - Posted daily for 7 days
- **Four Figures** - Saved $1,000
- **Ten Grand** - Hit $10K in land fund
- **Workshop Dreamer** - Created detailed workshop plan
- **Custom Creator** - Completed first custom commission
- **YouTube Partner** - Achieved monetization
- **Landowner** - Purchased land
- **Boss Mode** - Hired first employee

### 🎯 Quest Line Icons (Cyan Theme)

Major storylines that progress through multiple stages:

- **Van Life** - "Van Down By The River" quest line
- **Land Fund** - "The Land Fund" quest line
- **Workshop Path** - "Building the Workshop" quest line
- **Content Empire** - Content creation quest line
- **Business Builder** - Business empire quest line

### 📊 Stat Icons (Green Theme)

Visual indicators for player statistics:

- **Cash** - Cash on hand
- **Land Fund** - Land fund savings
- **Content Pieces** - Content pieces created
- **Restorations** - Restoration projects completed
- **Skills** - Skills learned
- **Connections** - Connections made
- **Level Up** - Level up effect
- **XP Gain** - XP gain indicator

### 👤 Character Sprites (Purple Theme)

Player character and environment sprites (128x128px):

- **Protagonist Front** - Main character front view
- **Protagonist Side** - Main character side view
- **Van Asset** - Player's van home
- **Workshop Building** - Workshop location

### 🎨 UI Elements (Orange Theme)

Decorative UI elements and icons:

- **Trophy Gold** - First place achievement trophy
- **Trophy Silver** - Second place achievement trophy
- **Trophy Bronze** - Third place achievement trophy
- **Quest Complete** - Quest completion banner
- **Daily Streak** - Daily streak fire indicator
- **Money Bag** - Money bag icon

## Integration with Life RPG Prototype

These assets are designed to match the React-based Life RPG prototype. Key features:

- **Transparent backgrounds** for easy overlay
- **Consistent sizing** (64x64 for icons, 128x128 for sprites)
- **Color-coded categories** matching the prototype's design system
- **Pixel art style** with crisp edges for retro gaming aesthetic
- **Scalable design** - can be upscaled without quality loss

### Usage in React

```jsx
import firstDollarBadge from './life-rpg-imagery/generated/achievements/first_dollar.png';

function AchievementBadge({ achievement }) {
  return (
    <div className="achievement">
      <img
        src={firstDollarBadge}
        alt="First Dollar"
        style={{ imageRendering: 'pixelated' }}
      />
      <span>{achievement.name}</span>
    </div>
  );
}
```

## Technical Details

### Image Specifications

- **Format**: PNG with alpha transparency
- **Icon Size**: 64x64 pixels
- **Sprite Size**: 128x128 pixels
- **Rendering**: Pixel-perfect, crisp edges
- **Color Depth**: 32-bit RGBA

### PixelLab API Parameters

When using the PixelLab generator, assets are created with:

- **Outline**: Thick (for clarity at small sizes)
- **Shading**: Smooth (for depth and dimension)
- **View**: Front (for consistent facing direction)
- **Background**: Transparent (for easy compositing)

### Metadata Format

All generated assets include metadata in `generated/metadata.json`:

```json
{
  "generated_at": "2025-10-29T12:00:00",
  "total_images": 33,
  "categories": {
    "achievements": [
      {
        "name": "First Dollar",
        "description": "Earned your first dollar from content",
        "category": "achievements",
        "filename": "first_dollar.png",
        "path": "generated/achievements/first_dollar.png",
        "timestamp": "2025-10-29T12:00:00"
      }
    ]
  }
}
```

## Future Enhancements

Potential additions to the asset collection:

- **Animated sprites** - Walk cycles, idle animations, level-up effects
- **Multi-directional sprites** - 8-directional character movement
- **Environmental tiles** - Workshop interiors, van interiors, land views
- **Item icons** - Tools, materials, equipment
- **Skill tree graphics** - Visual skill progression trees
- **Progress bars** - Custom styled progress indicators
- **Particle effects** - Sparkles, glow effects, impact effects

## Related Files

- **React Prototype**: See the inline React component in the original request
- **PixelLab Integration**: `../pixellab_integration/` - Main PixelLab client
- **API Configuration**: `../.mcp.json` - MCP server configuration

## Credits

- **Asset Generation**: PixelLab API (when available) / Custom placeholder generator
- **Design Concept**: Based on Life RPG prototype by user "Crispy"
- **Part of**: AI-DnD Project

## License

Part of the AI-DnD project. Assets are generated for prototype demonstration purposes.

---

**Note**: Current assets are placeholders. For production use, regenerate with a valid PixelLab API key for high-quality pixel art.
