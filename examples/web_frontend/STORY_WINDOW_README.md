# Story Window Component

A fully-featured modal storytelling component for interactive narratives, character dialogues, and choice-based gameplay. Perfect for RPGs, visual novels, and narrative-driven games.

![Story Window Demo](https://img.shields.io/badge/demo-live-brightgreen)

## 📋 Table of Contents

- [Features](#features)
- [Quick Start](#quick-start)
- [Core API](#core-api)
- [Story Patterns](#story-patterns)
- [Story Loader](#story-loader)
- [JSON Story Format](#json-story-format)
- [Examples](#examples)
- [Styling](#styling)

---

## ✨ Features

- 🖼️ **Image Display** - Show character portraits, scenes, and environments
- 📝 **Rich Text** - Multi-line narrative content with variable substitution
- 🎮 **Four Buttons** - Customizable player choices (1-4 buttons)
- 📚 **History Tracking** - Automatically tracks all interactions
- 🔄 **Multiple Rounds** - Seamless dialogue chains
- 🎨 **Retro Aesthetic** - Matches cyberpunk console theme
- 📱 **Responsive** - Works on mobile and desktop
- 🎭 **Pre-built Patterns** - Common dialogue scenarios ready to use
- 📖 **JSON Stories** - Write branching narratives in simple JSON
- 💾 **Save/Load** - Persist story progress

---

## 🚀 Quick Start

### Basic Usage

```javascript
// Show a simple story window
window.StoryWindow.show({
  image: 'images/wizard.jpg',
  text: 'A mysterious wizard appears before you.',
  buttons: ['Talk', 'Attack', 'Flee', 'Wait']
});

// Update the current window
window.StoryWindow.update({
  text: 'The wizard raises his staff...',
  buttons: ['Defend', 'Cast Spell']
});

// Close the window
window.StoryWindow.close();
```

### Demo

Open `story_window_demo.html` in your browser to see interactive examples.

---

## 🎯 Core API

### window.StoryWindow.show(options)

Display a new story window.

```javascript
window.StoryWindow.show({
  image: 'url',              // Optional: Image URL
  text: 'Story text',        // Required: Narrative content
  buttons: ['A', 'B', 'C'],  // Optional: Button labels (1-4)
  onChoice: (index, history) => {
    // index: button clicked (0-3)
    // history: current interaction data
  },
  allowDismiss: true         // Optional: Click outside to close (default: true)
});
```

### window.StoryWindow.update(options)

Update the current window without closing it.

```javascript
window.StoryWindow.update({
  image: 'new-image.jpg',    // Optional: Change image
  text: 'New text',          // Optional: Change text
  buttons: ['New', 'Choices'] // Optional: Change buttons
});
```

### window.StoryWindow.close()

Close the story window.

```javascript
window.StoryWindow.close();
```

### window.StoryWindow.clearHistory()

Clear all tracked interactions.

```javascript
window.StoryWindow.clearHistory();
```

### window.StoryWindow.getHistory()

Get array of all past interactions.

```javascript
const history = window.StoryWindow.getHistory();
// Returns: [{image, text, buttons, timestamp}, ...]
```

---

## 🎭 Story Patterns

Pre-built helpers for common scenarios. Include `story-patterns.js` to use.

```html
<script src="story-patterns.js"></script>
```

### Available Patterns

#### Simple Dialogue

```javascript
const wizard = {
  name: 'Gandalf',
  portrait: 'images/gandalf.jpg'
};

StoryPatterns.dialogue(wizard, 'You shall not pass!', () => {
  console.log('Player clicked continue');
});
```

#### Narrator Text

```javascript
StoryPatterns.narrate(
  'You enter a dark forest. Strange sounds echo around you.',
  () => { /* next scene */ }
);
```

#### Yes/No Decision

```javascript
StoryPatterns.yesNo(
  'Do you want to open the mysterious chest?',
  () => { /* yes action */ },
  () => { /* no action */ },
  'images/chest.jpg' // optional
);
```

#### Multiple Choice

```javascript
StoryPatterns.multipleChoice(
  'What do you do?',
  [
    { text: 'Attack', callback: () => startCombat() },
    { text: 'Defend', callback: () => defend() },
    { text: 'Flee', callback: () => flee() }
  ],
  'images/enemy.jpg'
);
```

#### Combat Encounter

```javascript
const goblin = {
  name: 'Goblin Warrior',
  image: 'images/goblin.jpg',
  hp: 25,
  maxHp: 40
};

StoryPatterns.encounter(goblin, (actionIndex) => {
  // 0=Attack, 1=Defend, 2=Item, 3=Flee
});
```

#### Shop Interface

```javascript
const merchant = {
  name: 'Ye Olde Merchant',
  image: 'images/merchant.jpg'
};

const items = [
  { name: 'Sword', price: 50 },
  { name: 'Potion', price: 20 },
  { name: 'Shield', price: 75 }
];

StoryPatterns.shop(
  merchant,
  items,
  (itemIndex) => { /* purchase */ },
  () => { /* leave */ }
);
```

#### Quest Offer

```javascript
const quest = {
  title: 'Slay the Dragon',
  description: 'A dragon terrorizes the village.',
  reward: '1000 gold',
  giver: { portrait: 'images/mayor.jpg' }
};

StoryPatterns.questOffer(
  quest,
  () => { /* accept */ },
  () => { /* decline */ }
);
```

### All Patterns

- `dialogue(character, text, onContinue)` - Simple dialogue
- `narrate(text, onContinue)` - Narrator text
- `yesNo(text, yesCallback, noCallback, image)` - Binary choice
- `multipleChoice(text, choices, image)` - Multiple options
- `encounter(enemy, onAction)` - Combat interface
- `shop(merchant, items, onPurchase, onLeave)` - Shopping
- `itemFound(item, onTake, onLeave)` - Item discovery
- `location(location, actions, onAction)` - Location description
- `meet(character, meetingText, responses, onResponse)` - Meeting
- `questOffer(quest, onAccept, onDecline)` - Quest prompt
- `gameEnd(victory, message, onRestart, onQuit)` - End screen
- `confirm(action, onConfirm, onCancel)` - Confirmation dialog
- `info(text, image)` - Information display

---

## 📖 Story Loader

Load and play JSON-based story scripts. Include `story-loader.js` to use.

```html
<script src="story-loader.js"></script>
```

### Basic Usage

```javascript
// Load from JSON file
storyLoader.loadFromFile('stories/my-quest.json')
  .then(() => storyLoader.play('start'));

// Or load from object
const storyData = { /* story JSON */ };
storyLoader.load(storyData).play('start');
```

### Features

- ✅ Variable substitution
- ✅ Conditional choices
- ✅ Conditional branches
- ✅ Action execution
- ✅ Save/load progress
- ✅ Visited node tracking

---

## 📄 JSON Story Format

Stories are defined in JSON with nodes and choices.

### Basic Structure

```json
{
  "start": {
    "text": "Story text here...",
    "image": "images/scene.jpg",
    "choices": [
      { "text": "Choice 1", "goto": "node1" },
      { "text": "Choice 2", "goto": "node2" }
    ]
  },
  "node1": {
    "text": "Next scene...",
    "choices": [
      { "text": "Continue", "goto": "node3" }
    ]
  }
}
```

### Variables

Set and use variables:

```json
{
  "found_key": {
    "text": "You found a key!",
    "action": "hasKey=true",
    "choices": [{ "text": "Continue", "goto": "door" }]
  },
  "door": {
    "text": "You reach a locked door.",
    "choices": [
      {
        "text": "Use key",
        "goto": "unlock",
        "condition": "hasKey==true"
      },
      { "text": "Go back", "goto": "start" }
    ]
  }
}
```

### Variable Substitution

Use `{varName}` in text:

```json
{
  "greeting": {
    "text": "Welcome, {playerName}! You have {gold} gold.",
    "choices": [{ "text": "Continue", "goto": "next" }]
  }
}
```

### Actions

Execute actions when showing a node:

```json
{
  "node": {
    "text": "You gain 50 gold!",
    "action": {
      "increment": { "gold": 50 },
      "set": { "foundTreasure": true }
    },
    "choices": [...]
  }
}
```

### Conditional Branches

Branch based on conditions:

```json
{
  "check_gold": {
    "text": "Can you afford it?",
    "condition": "gold>=100",
    "else_goto": "too_poor",
    "choices": [{ "text": "Buy", "goto": "purchase" }]
  }
}
```

### Conditional Choices

Show choices based on conditions:

```json
{
  "node": {
    "text": "What do you want to do?",
    "choices": [
      { "text": "Use magic", "goto": "cast", "condition": "hasMagic==true" },
      { "text": "Attack", "goto": "fight" },
      { "text": "Flee", "goto": "run" }
    ]
  }
}
```

### End Nodes

Mark ending nodes:

```json
{
  "victory": {
    "text": "You win!",
    "end": true,
    "choices": []
  }
}
```

### Complete Example

See `stories/simple-quest.json` and `stories/tavern-meeting.json` for full examples.

---

## 💡 Examples

### Multi-Round Dialogue

```javascript
function talkToWizard() {
  const wizard = {
    name: 'Eldrin',
    portrait: 'images/wizard.jpg'
  };

  StoryPatterns.dialogue(wizard, 'Greetings, traveler!', () => {
    StoryPatterns.dialogue(wizard, 'I have a quest for you.', () => {
      StoryPatterns.yesNo(
        'Will you help me find the ancient artifact?',
        () => acceptQuest(),
        () => declineQuest()
      );
    });
  });
}
```

### Interactive Story Chain

```javascript
function startChapter1() {
  window.StoryWindow.show({
    image: 'scenes/forest.jpg',
    text: 'You enter the Darkwood Forest. Mist swirls around ancient trees.',
    buttons: ['Go deeper', 'Turn back', 'Call out', 'Light torch'],
    onChoice: (choice) => {
      if (choice === 0) showChapter2();
      else if (choice === 1) returnToVillage();
      else if (choice === 2) wolfAppears();
      else lightTorch();
    }
  });
}
```

### Using Story Loader

```javascript
// Load and play a JSON story
async function playQuest() {
  await storyLoader.loadFromFile('stories/simple-quest.json');
  storyLoader.setVariable('gold', 100);
  storyLoader.setVariable('playerName', 'Aragorn');
  storyLoader.play('start');
}

// Save progress
storyLoader.save('myQuest');

// Load progress later
if (storyLoader.loadSave('myQuest')) {
  console.log('Progress loaded!');
}
```

---

## 🎨 Styling

The component automatically inherits the retro cyberpunk theme from `styles.css`.

### CSS Classes

- `.story-window-overlay` - Full-screen backdrop
- `.story-window` - Main window container
- `.story-image-container` - Image display area
- `.story-image` - The actual image
- `.story-text-container` - Text area
- `.story-text` - Text paragraph
- `.story-button-row` - Button container
- `.story-button` - Individual button

### Customization

Override CSS to customize appearance:

```css
.story-window {
  border: 10px solid gold;
  border-radius: 20px;
}

.story-button {
  background: linear-gradient(to bottom, #ff6b6b, #ee5a6f);
  color: white;
}
```

---

## 📁 Files

```
examples/web_frontend/
├── index.html                    # Main app (includes template)
├── app.js                        # Core StoryWindow API
├── styles.css                    # Component styling
├── story-patterns.js             # Pre-built patterns
├── story-loader.js               # JSON story loader
├── story_window_demo.html        # Interactive demo
└── stories/
    ├── simple-quest.json         # Example quest
    └── tavern-meeting.json       # Example dialogue
```

---

## 🔧 Advanced Usage

### Custom Animations

Add typing effect:

```javascript
function showWithTyping(text, speed = 50) {
  window.StoryWindow.show({ text: '', buttons: [] });

  let index = 0;
  const interval = setInterval(() => {
    if (index < text.length) {
      window.StoryWindow.update({
        text: text.substring(0, index + 1)
      });
      index++;
    } else {
      clearInterval(interval);
      window.StoryWindow.update({
        buttons: ['Continue']
      });
    }
  }, speed);
}
```

### Audio Integration

```javascript
function showWithSound(options) {
  const { audio, ...rest } = options;

  if (audio) {
    new Audio(audio).play();
  }

  window.StoryWindow.show(rest);
}

// Usage
showWithSound({
  image: 'dragon.jpg',
  text: 'The dragon roars!',
  audio: 'sounds/roar.mp3',
  buttons: ['Fight', 'Flee']
});
```

### Game State Integration

```javascript
class GameStoryManager {
  constructor(gameState) {
    this.gameState = gameState;
  }

  showContextual(storyOptions) {
    // Add conditional buttons based on game state
    let buttons = [...storyOptions.buttons];

    if (this.gameState.hasKey) {
      buttons.push('Use Key');
    }

    window.StoryWindow.show({
      ...storyOptions,
      buttons
    });
  }
}
```

---

## 🤝 Contributing

This component is part of the AI-DnD project. Contributions welcome!

---

## 📝 License

Part of AI-DnD project. See main repository for license details.

---

## 🎮 Tips

1. **Keep text concise** - Players should be able to read it quickly
2. **Use images wisely** - Visual storytelling is powerful
3. **Limit button text** - Short labels work best (1-3 words)
4. **Test mobile** - Ensure buttons don't overflow on small screens
5. **Track state** - Use history or variables for branching stories
6. **Provide feedback** - Update window after choices to show impact

---

**Made with ❤️ for interactive storytelling**
