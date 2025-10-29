# 🎨 Gemini Chat Interface

A beautiful, production-ready chat interface for Google's Gemini 2.5 Flash model with advanced console logging and theme switching.

## 📁 Project Structure

```
gemini-chat/
├── index.html           # Clean HTML structure
├── css/
│   └── styles.css      # All styles and themes
├── js/
│   ├── main.js         # Core application logic
│   ├── logging.js      # Advanced console logging system
│   └── themes.js       # Theme management
└── README.md           # This file
```

## ✨ Features

- **Modern Design** - Clean, gradient-based UI with smooth animations
- **Conversation History** - Context-aware responses that remember the conversation
- **API Key Management** - Secure storage using localStorage
- **Real-time Updates** - Loading indicators and error handling
- **Keyboard Shortcuts** - Enter to send, Shift+Enter for new lines
- **Responsive Layout** - Works on desktop and mobile devices
- **6 Beautiful Themes** - Instant theme switching with persistence:
  - 🟣 Purple (default) - Professional gradient
  - 🌊 Ocean - Cool blue-teal vibes
  - 🌅 Sunset - Pink to blue creative
  - 🌲 Forest - Dark green nature
  - 🌙 Dark - Night mode coding
  - 🔥 Fire - Warm orange energy
- **Advanced Console Logging** - Comprehensive Chrome DevTools logging with:
  - 🎨 Styled, color-coded logs
  - 📊 Token usage tracking and visualization
  - ⏱️ Performance timing
  - 💾 Memory usage monitoring
  - 📈 Session statistics
  - 🔍 Detailed API response analysis

## 🚀 Quick Start

### 1. Get Your API Key

Visit [Google AI Studio](https://aistudio.google.com/app/apikey) to get a free Gemini API key.

### 2. Start the Local Server

**⚠️ Important:** This app uses ES6 modules and **must be served over HTTP** (not opened directly as a file).

Choose one of these methods:

#### Option A: Use the start script (recommended)
```bash
cd gemini-chat
./start.sh
```

#### Option B: Use the Python server
```bash
cd gemini-chat
python3 server.py
# or: ./server.py
```

#### Option C: Use Python's built-in server
```bash
cd gemini-chat
python3 -m http.server 8000
# Then open: http://localhost:8000
```

#### Option D: Use Node.js (if you have it)
```bash
cd gemini-chat
npx serve
```

### 3. Enter Your API Key

- Paste your API key in the input field at the top
- Click "Connect"
- Your key is stored locally in your browser

### 4. Start Chatting!

Type your message and press Enter (or click Send).

> **Why a server?** Modern browsers block ES6 module imports from `file://` URLs for security reasons. A local HTTP server solves this.

## 🎨 Themes

Click the **🎨 Theme** button in the top-right to switch between 6 beautiful themes:

| Theme | Colors | Best For |
|-------|--------|----------|
| 🟣 Purple | Blue-purple gradient | Professional, default |
| 🌊 Ocean | Blue-teal | Calm, focused work |
| 🌅 Sunset | Pink-cyan | Creative sessions |
| 🌲 Forest | Dark green | Nature lovers |
| 🌙 Dark | Dark blue-purple | Night coding |
| 🔥 Fire | Orange-yellow | Energetic vibes |

Your theme choice is **automatically saved** and persists across sessions!

## 🛠️ Advanced Console Features

Open your browser's developer console (F12 or Cmd+Opt+I) to access powerful debugging features:

### Available Commands

```javascript
getSessionStats()         // View current session statistics
getConversationHistory()  // View conversation history
showMemory()             // Check memory usage
clearHistory()           // Clear conversation history
clearApiKey()            // Clear API key and reload
exportConversation()     // Export conversation to JSON
startProfiling()         // Start performance profiling
stopProfiling()          // Stop performance profiling
```

### What's Logged

- **Every API request and response**
- **Token usage breakdown** (prompt, cached, output)
- **Cache hit rates** and cost savings
- **Performance metrics** (response times, throughput)
- **Memory usage** with visual bars
- **Session statistics** in formatted tables
- **Error details** with stack traces
- **User interactions** and keyboard shortcuts

## 🔧 Technical Details

- **Model**: Gemini 2.5 Flash (1 million token context)
- **SDK**: `@google/genai` (official Google SDK)
- **No Backend Required**: Runs entirely in the browser
- **Caching**: Automatic implicit caching enabled
- **Storage**: localStorage for API key and theme preference

## 📝 Files Explained

### `index.html`
Clean HTML structure with semantic markup and minimal inline code. All logic is externalized.

### `css/styles.css`
Complete stylesheet with:
- CSS variables for theming
- Responsive layout rules
- Smooth animations and transitions
- 6 theme definitions

### `js/main.js`
Core application logic:
- API client initialization
- Message sending and receiving
- Conversation history management
- Session state tracking
- UI updates and interactions

### `js/logging.js`
Advanced logging system:
- Styled console messages
- Session statistics tracking
- Memory usage monitoring
- Performance profiling helpers
- ASCII art banners

### `js/themes.js`
Theme management:
- Theme switching logic
- localStorage persistence
- Active state management
- Click-outside detection

## 🎯 Best Practices

### Security
- API key is stored in localStorage only
- Never committed to version control
- Only sent to Google's API

### Performance
- Conversation history is maintained in memory
- Automatic caching reduces API calls
- Token usage tracked to optimize costs

### Development
- Open console for debugging (F12)
- Use `getSessionStats()` to monitor usage
- Export conversations for analysis

## 🐛 Troubleshooting

### API Key Issues
- Make sure you're using a valid Gemini API key
- Check console for detailed error messages
- Try `clearApiKey()` and re-enter

### Theme Not Saving
- Check browser localStorage is enabled
- Clear browser cache and try again
- Check console for errors

### Console Logging Not Working
- Make sure you're viewing the correct tab in DevTools
- Try refreshing the page
- Check that console filters aren't hiding logs

## 📚 Learn More

- [Gemini API Documentation](https://ai.google.dev/docs)
- [Google GenAI SDK](https://www.npmjs.com/package/@google/genai)
- [Chrome DevTools Guide](https://developer.chrome.com/docs/devtools/)

## 🎉 Enjoy!

This is a **production-ready** interface with enterprise-grade features. Have fun chatting with Gemini!

