# Gemini Chat Interface

A simple, modern chat interface for interacting with Google's Gemini 2.5 Flash model.

## Features

✅ **Modern Design** - Clean, gradient-based UI with smooth animations
✅ **Conversation History** - Context-aware responses that remember the conversation
✅ **API Key Management** - Secure storage using localStorage
✅ **Real-time Updates** - Loading indicators and error handling
✅ **Keyboard Shortcuts** - Enter to send, Shift+Enter for new lines
✅ **Responsive Layout** - Works on desktop and mobile devices
🆕 **6 Beautiful Themes** - Instant theme switching with persistence:
  - 🟣 Purple (default) - Professional gradient
  - 🌊 Ocean - Cool blue-teal vibes
  - 🌅 Sunset - Pink to blue creative
  - 🌲 Forest - Dark green nature
  - 🌙 Dark - Night mode coding
  - 🔥 Fire - Warm orange energy
🆕 **Advanced Console Logging** - Comprehensive Chrome DevTools logging with:
  - 🎨 Styled, color-coded logs
  - 📊 Token usage tracking and visualization
  - ⏱️ Performance timing
  - 💾 Memory usage monitoring
  - 📈 Session statistics
  - 🔍 Detailed API response analysis

## Quick Start

### 1. Choose Your Theme

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

### 2. Get Your API Key

Visit [Google AI Studio](https://aistudio.google.com/app/apikey) to get a free Gemini API key.

### 3. Open the Chat Interface

Simply open `gemini-chat.html` in your web browser:

```bash
open gemini-chat.html
# or double-click the file in Finder/Explorer
```

### 4. Enter Your API Key

- Paste your API key in the input field at the top
- Click "Connect"
- Your key is stored locally in your browser (not sent anywhere except Google's API)

### 5. Start Chatting!

Type your message and press Enter (or click Send).

## Technical Details

### Library Used

This project uses the **modern Google GenAI SDK**:
- Package: `@google/genai`
- Repository: [googleapis/js-genai](https://github.com/googleapis/js-genai)
- Status: General Availability (GA) as of May 2025

⚠️ **Important:** This does NOT use the legacy `@google/generativeai` library which is deprecated.

### Model

- **Model:** `gemini-2.5-flash`
- **Features:** Fast responses, context-aware, supports long conversations

### How It Works

1. **ES Modules via CDN:**
   ```javascript
   import { GoogleGenAI } from 'https://esm.run/@google/genai';
   ```

2. **Client Initialization:**
   ```javascript
   const client = new GoogleGenAI({ apiKey });
   ```

3. **Generate Content:**
   ```javascript
   const response = await client.models.generateContent({
       model: 'gemini-2.5-flash',
       contents: conversationHistory
   });
   ```

## Conversation History

The chat maintains a full conversation history:

```javascript
conversationHistory = [
    { role: 'user', parts: [{ text: 'Hello!' }] },
    { role: 'model', parts: [{ text: 'Hi! How can I help?' }] },
    // ... more messages
];
```

This allows Gemini to provide context-aware responses throughout the conversation.

## API Key Storage

Your API key is stored securely in your browser's `localStorage`:

- ✅ Persists across page reloads
- ✅ Only accessible to this specific page
- ✅ Never sent to any server except Google's API
- ✅ Can be cleared by running `clearApiKey()` in the browser console

To manually clear your API key:
```javascript
// In browser console:
clearApiKey()
```

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Enter` | Send message |
| `Shift + Enter` | New line in message |

## UI States

### Status Indicator

The colored dot in the header shows connection status:
- 🔴 **Red:** Not connected (API key not set)
- 🟢 **Green:** Connected and ready to chat

### Message Types

- **User messages:** Purple gradient background, right-aligned
- **Assistant messages:** Light gray background, left-aligned
- **Error messages:** Pink background with error details
- **Loading:** Animated dots while waiting for response

## Error Handling

The chat handles common errors gracefully:

- **Missing API key:** Prompts you to enter one
- **Invalid API key:** Shows error message
- **Network issues:** Displays connection errors
- **Rate limits:** Shows API rate limit messages

## Browser Compatibility

Works in all modern browsers that support:
- ES6 modules
- Async/await
- Fetch API
- CSS Grid/Flexbox

Tested in:
- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+

## Privacy & Security

- **API key:** Stored locally in your browser only
- **Messages:** Sent directly to Google's Gemini API
- **No backend:** All processing happens client-side
- **No tracking:** No analytics or third-party scripts

## Troubleshooting

### "Please enter a valid API key"

Make sure you:
1. Have a valid API key from [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Copied the entire key (no extra spaces)
3. The key hasn't been revoked or expired

### "Failed to initialize client"

- Check your internet connection
- Verify the API key is correct
- Try refreshing the page

### "Error: 429 - Rate limit exceeded"

You've exceeded the free tier limits. Either:
- Wait a few minutes
- Upgrade to a paid plan

### No response after sending message

- Check browser console for errors (F12)
- Verify internet connection
- Try refreshing the page and reconnecting

## Advanced Console Logging 🎯

The chat interface includes a **comprehensive console logging system** that provides deep insights into every aspect of the application.

### Opening Chrome DevTools

1. Open `gemini-chat.html` in Chrome
2. Press `F12` or `Cmd+Option+J` (Mac) / `Ctrl+Shift+J` (Windows)
3. Go to the "Console" tab

You'll see a beautiful ASCII art banner and comprehensive logging!

### What's Logged

#### 📊 Session Statistics
- Messages sent/received
- Total tokens used
- Cache hit rate
- API call count
- Error tracking
- Session duration

#### 🎯 Token Usage Analysis
- **Per-message breakdown:**
  - Prompt tokens
  - Cached tokens (with % savings)
  - Output tokens
  - Total tokens
- **Visual progress bars** showing token distribution
- **Cumulative session totals**
- **Cache efficiency metrics**

#### ⚡ Performance Metrics
- API response times (ms)
- Characters/tokens per second
- Request duration tracking
- Memory usage monitoring

#### 💾 Memory Tracking
- JavaScript heap usage
- Visual memory bars
- Automatic periodic checks
- Memory leak detection

### Console Commands

The interface exposes several commands you can type in the console:

```javascript
// View session statistics
getSessionStats()

// View conversation history in a table
getConversationHistory()

// Check current memory usage
showMemory()

// Clear conversation history
clearHistory()

// Clear API key and reload
clearApiKey()

// Export conversation to JSON
exportConversation()

// Start performance profiling
startProfiling()

// Stop performance profiling
stopProfiling()
```

### Advanced Console Features Used

The logging system demonstrates **little-known Chrome DevTools features**:

✅ **Styled Logs with CSS** - Color-coded, badge-style logs
```javascript
console.log('%c🔧 SYSTEM %c Message',
  'background: #667eea; color: white; ...',
  'color: #667eea; ...'
);
```

✅ **console.table()** - Display data as beautiful tables
```javascript
console.table({
  'Messages Sent': 5,
  'Total Tokens': 1234,
  'Cache Hit Rate': '71.6%'
});
```

✅ **console.group() / groupCollapsed()** - Organize logs hierarchically
```javascript
console.group('🎯 API Call Details');
  console.log('Model: gemini-2.5-flash');
  console.log('Tokens: 42');
console.groupEnd();
```

✅ **console.time() / timeEnd()** - Precision timing
```javascript
console.time('API Response');
// ... API call ...
console.timeEnd('API Response'); // Shows duration
```

✅ **console.count()** - Track occurrences
```javascript
console.count('Messages Sent'); // Messages Sent: 1
console.count('Messages Sent'); // Messages Sent: 2
```

✅ **console.trace()** - Stack traces for debugging
```javascript
console.trace('Error occurred here');
```

✅ **console.assert()** - Conditional logging
```javascript
console.assert(apiKey !== null, 'API key must be set');
```

✅ **console.dir()** - Interactive object inspection
```javascript
console.dir(response, { depth: 5 });
```

✅ **console.profile() / profileEnd()** - Performance profiling
```javascript
console.profile('Performance Analysis');
// ... code to profile ...
console.profileEnd('Performance Analysis');
```

✅ **performance.memory** - Memory usage tracking
```javascript
if (performance.memory) {
  console.log('Heap used:', performance.memory.usedJSHeapSize);
}
```

### Example Console Output

When you send a message, you'll see:

```
╔══════════════════════════════════════════════════════════╗
║          🚀 Advanced Chat Interface v1.0 🚀              ║
║          💬 Powered by Gemini 2.5 Flash                 ║
╚══════════════════════════════════════════════════════════╝

🔧 SYSTEM Application initialized
💡 TIP: Type getSessionStats() to see statistics

💬 Message Send Operation
  👤 USER New message "Tell me about tokens"
  📨 Messages Sent: 1
  🌐 API Calls Made: 1
  🌐 API 🚀 Sending request to Gemini API...
  ⏱️ API Response Time: 1234.56ms
  ⚡ PERF API responded in 1234.56ms

  📦 API Response Details
    🎯 Token Usage Analysis
    ┌─────────────────────┬───────┐
    │ Prompt Tokens       │   42  │
    │ Cached Tokens       │   30  │
    │ Candidates Tokens   │   18  │
    │ Total Tokens        │   60  │
    └─────────────────────┴───────┘

    💾 CACHE Cache hit rate: 50.00%
    💾 CACHE 💚 30 tokens served from cache!

    Token Distribution:
    [███████████████████░░░░░░░░░░░░░░░░░░░░░]
    █ = Cached | ▓ = Prompt | ░ = Output

📊 Session Statistics
┌─────────────────────┬───────────┐
│ Messages Sent       │     1     │
│ Total Tokens        │    60     │
│ Cached Tokens       │    30     │
│ Cache Hit Rate      │  50.00%   │
└─────────────────────┴───────────┘
```

### Auto-Logging

The system includes automatic periodic logging:

- **Memory checks:** Every 30 seconds
- **Session stats:** Every 60 seconds

These appear as collapsed groups so they don't spam your console.

## Development

### File Structure

```
gemini-chat.html
└── Single-file application
    ├── HTML (structure)
    ├── CSS (styles)
    └── JavaScript (logic + advanced logging)
```

### Customization

You can easily customize:

**Colors:**
```css
/* Change gradient colors */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```

**Model:**
```javascript
// Use a different model
model: 'gemini-2.5-pro'  // More powerful but slower
```

**Max History:**
```javascript
// Limit conversation history
if (conversationHistory.length > 20) {
    conversationHistory = conversationHistory.slice(-20);
}
```

## Related Documentation

- [Gemini API Docs](https://ai.google.dev/gemini-api/docs)
- [Google GenAI SDK (JS)](https://github.com/googleapis/js-genai)
- [Get API Key](https://aistudio.google.com/app/apikey)

## License

Part of the AI-DnD project. See main project LICENSE.

---

**Questions or Issues?**
Check the [Gemini API docs](https://ai.google.dev/gemini-api/docs) or open an issue in the project repository.

