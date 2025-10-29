# PixelLab Command Center - Modular Architecture

A modern, modular web application for managing parallel pixel art generation jobs with comprehensive logging.

## Architecture Overview

```
dashboards/
├── pixellab_dashboard.html   # Main HTML entry point
├── js/
│   ├── app.js                 # Application initialization & coordination
│   ├── logger.js              # Comprehensive logging system
│   ├── state.js               # Centralized state management
│   ├── api.js                 # API communication layer
│   ├── jobQueue.js            # Job queue & lifecycle management
│   └── ui.js                  # DOM rendering & user interactions
└── README.md                  # This file
```

## Module Responsibilities

### 🚀 `app.js` - Application Entry Point
- Initializes all modules in correct order
- Sets up periodic tasks (diagnostics refresh)
- Provides console API for debugging
- Handles global error catching

**Console Commands:**
```javascript
app.getState()              // View current state
app.getMetrics()            // View queue metrics
app.refreshDiagnostics()    // Refresh server status
app.createTestJob()         // Create test job
app.setMaxParallelJobs(5)   // Change parallel job limit
```

### 📝 `logger.js` - Comprehensive Logging System
- Structured console logging with levels (INFO, SUCCESS, WARNING, ERROR, DEBUG)
- Job lifecycle tracking
- API request/response logging
- Visual grouping and timestamps
- Stack traces for debugging

**Features:**
- Color-coded log levels
- Collapsible log groups
- Timestamp and elapsed time tracking
- Rich data inspection
- Dedicated loggers per module

### 🗂️ `state.js` - State Management
- Centralized application state
- Event-driven architecture
- Subscribe/emit pattern for reactive updates
- Job state tracking
- Diagnostics state
- Configuration management

**Events:**
- `job:added` - New job created
- `job:updated` - Job status changed
- `job:removed` - Job deleted
- `jobs:cleared` - All jobs cleared
- `stats:updated` - Statistics recalculated
- `diagnostics:updated` - Server status changed
- `state:updated` - General state change

### 🌐 `api.js` - API Layer
- HTTP communication with backend
- Request/response logging
- Error handling
- Health check management

**Methods:**
- `generateCharacter(prompt, width, height, seed)` - Generate sprite
- `checkHealth()` - Get server diagnostics
- `getBalance()` - Check API balance

### 📋 `jobQueue.js` - Job Queue Manager
- Job creation and lifecycle
- Parallel execution management
- Queue processing logic
- Job state transitions

**Job States:**
- `idle` - Waiting to start
- `queued` - In queue but blocked by parallel limit
- `running` - Currently processing
- `success` - Completed successfully
- `error` - Failed with error

**Features:**
- Automatic queue processing
- Configurable parallel job limit
- Manual job triggering
- Job removal and cleanup

### 🎨 `ui.js` - UI Manager
- DOM manipulation
- Event listener setup
- Job box rendering
- Stats and diagnostics display
- User interaction handling

## Logging Output

### Job Creation
```javascript
🆕 JOB CREATED
  Job ID: job-1
  Prompt: heroic knight with glowing sword
  Dimensions: 64×64px
  Seed: Random
  Status: idle
  Full Job Object: {...}
```

### Job Started
```javascript
▶️ JOB STARTED
  Job ID: job-1
  Prompt: heroic knight with glowing sword
  Start Time: 2025-10-29T12:34:56.789Z
  Request Payload: {
    prompt: "heroic knight with glowing sword",
    width: 64,
    height: 64,
    seed: null
  }
```

### API Request
```javascript
🌐 API REQUEST
  Method: POST
  URL: http://127.0.0.1:8787/generate-character
  Payload: {...}
  Timestamp: 2025-10-29T12:34:56.789Z
```

### API Response
```javascript
📥 API RESPONSE [200]
  URL: http://127.0.0.1:8787/generate-character
  Status: 200
  Response Data: {...}
  Timestamp: 2025-10-29T12:34:57.123Z
```

### Job Completed
```javascript
✅ JOB COMPLETED
  Job ID: job-1
  Status: success
  Duration: 2.45s
  End Time: 2025-10-29T12:34:58.234Z
  Result URL: data:image/png;base64...
  Full Job Object: {...}
  🖼️ Preview Image
    Image loaded: {
      width: 64,
      height: 64,
      size: "12.34 KB"
    }
```

### Queue Status
```javascript
📊 QUEUE STATUS
  Total Jobs: 5
  Running: 3
  Completed: 1
  Failed: 0
  Idle/Queued: 1
```

## Usage

### Starting the Application

1. Start the backend server:
```bash
python3 scripts/pixellab_actions.py --serve
```

2. Open `pixellab_dashboard.html` in your browser

3. Open browser console to see detailed logs

### Creating Jobs

**Via UI:**
1. Enter prompt and parameters
2. Click "Add Job to Queue" or "Add 3 Jobs"
3. Watch jobs process automatically

**Via Console:**
```javascript
// Create single test job
app.createTestJob()

// Access job queue directly (advanced)
jobQueue.createJob("wizard with staff", 64, 64)
jobQueue.createMultipleJobs(5, "warrior", 32, 32)
```

### Monitoring

**Console Logs:**
- All job lifecycle events are logged
- API requests/responses are tracked
- Queue status updates automatically

**UI Stats:**
- Total jobs
- Running count
- Completed count
- Failed count

**Diagnostics:**
- Server status
- API key status
- Account balance

## Configuration

### Max Parallel Jobs
Default: 3

**Change at runtime:**
```javascript
app.setMaxParallelJobs(5)
```

**Change in code:**
Edit `state.js`:
```javascript
config: {
  maxParallelJobs: 5,  // Change here
  serverUrl: 'http://127.0.0.1:8787'
}
```

### Server URL
Default: `http://127.0.0.1:8787`

**Change in code:**
Edit `state.js`:
```javascript
config: {
  maxParallelJobs: 3,
  serverUrl: 'http://your-server:port'  // Change here
}
```

## Development

### Adding New Features

1. **New State:** Add to `state.js` and emit events
2. **New API Endpoint:** Add method to `api.js`
3. **New UI Element:** Add rendering to `ui.js`
4. **New Job Type:** Extend `Job` class in `jobQueue.js`

### Debugging

**Enable verbose logging:**
```javascript
// All loggers are available globally
systemLogger.debug("Debug message", data)
jobLogger.debug("Job debug", job)
apiLogger.debug("API debug", response)
```

**Inspect state:**
```javascript
app.getState()     // Full state tree
app.getMetrics()   // Queue metrics
```

**Monitor events:**
```javascript
state.subscribe('job:updated', (job) => {
  console.log('Job updated:', job)
})
```

## Benefits of Modular Architecture

✅ **Separation of Concerns** - Each module has single responsibility
✅ **Maintainability** - Easy to find and fix bugs
✅ **Testability** - Modules can be tested independently
✅ **Scalability** - Easy to add new features
✅ **Debugging** - Comprehensive logging at every level
✅ **Reusability** - Modules can be used in other projects
✅ **No Build Process** - Native ES6 modules, no bundler needed

## Troubleshooting

### Jobs Not Starting
1. Check browser console for errors
2. Verify backend server is running: `app.refreshDiagnostics()`
3. Check API key status in diagnostics
4. Look for `❌ JOB FAILED` logs

### No Console Logs
1. Ensure browser console is open (F12)
2. Check console filters - ensure all levels visible
3. Look for JavaScript errors preventing module load

### State Not Updating
1. Check `state:updated` events in console
2. Verify event listeners: `state.listeners`
3. Check for errors in module loading

## Future Enhancements

- [ ] Job templates/presets system
- [ ] Job history persistence (localStorage)
- [ ] Batch operations (pause/resume all)
- [ ] Export job results
- [ ] Job priority queue
- [ ] Rate limiting visualization
- [ ] Performance metrics dashboard
- [ ] WebSocket support for real-time updates
- [ ] Dark/light theme toggle
- [ ] Mobile responsive improvements

## License

Part of the AI-DnD project.
