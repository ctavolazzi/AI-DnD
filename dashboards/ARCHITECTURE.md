# PixelLab Command Center - Architecture Documentation

## Module Dependency Graph

```
┌─────────────────────────────────────────────────────────────┐
│                         app.js                              │
│                  (Application Coordinator)                   │
│  - Initializes all modules                                  │
│  - Sets up periodic tasks                                   │
│  - Provides console API                                     │
└─────────────────────┬───────────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┬──────────────┐
        │             │             │              │
        ▼             ▼             ▼              ▼
  ┌─────────┐   ┌─────────┐   ┌──────────┐  ┌─────────┐
  │ logger  │   │  state  │   │   api    │  │   ui    │
  │  .js    │   │  .js    │   │   .js    │  │  .js    │
  └────┬────┘   └────┬────┘   └────┬─────┘  └────┬────┘
       │             │              │             │
       │             │              │             │
       └─────────────┼──────────────┼─────────────┘
                     │              │
                     ▼              │
              ┌─────────────┐       │
              │  jobQueue   │◄──────┘
              │    .js      │
              └─────────────┘
```

## Module Relationships

### Core Dependencies

```javascript
// logger.js - No dependencies (pure utility)
export { systemLogger, jobLogger, apiLogger, uiLogger, queueLogger }

// state.js - Depends on: logger
import { systemLogger } from './logger.js'
export { state }

// api.js - Depends on: logger, state
import { apiLogger } from './logger.js'
import { state } from './state.js'
export { api }

// jobQueue.js - Depends on: logger, state, api
import { jobLogger, queueLogger } from './logger.js'
import { state } from './state.js'
import { api } from './api.js'
export { jobQueue, Job }

// ui.js - Depends on: logger, state, jobQueue
import { uiLogger } from './logger.js'
import { state } from './state.js'
import { jobQueue } from './jobQueue.js'
export { ui }

// app.js - Depends on: ALL modules
import { systemLogger } from './logger.js'
import { state } from './state.js'
import { api } from './api.js'
import { jobQueue } from './jobQueue.js'
import { ui } from './ui.js'
export default app
```

## Data Flow

### Job Creation Flow

```
1. USER INTERACTION
   └─► ui.addJob()
       └─► Validates input
           └─► Calls jobQueue.createJob()

2. JOB CREATION
   └─► jobQueue.createJob()
       └─► Creates new Job instance
           └─► state.addJob()
               └─► Emits 'job:added' event
                   └─► ui receives event
                       └─► ui.renderJob() creates DOM

3. QUEUE PROCESSING
   └─► jobQueue.processQueue()
       └─► Checks available slots
           └─► Calls jobQueue.runJob() for idle jobs

4. JOB EXECUTION
   └─► jobQueue.runJob()
       ├─► Updates state: status = 'running'
       ├─► Calls api.generateCharacter()
       │   └─► Makes HTTP request
       │       └─► Returns result or throws error
       └─► Updates state: status = 'success' or 'error'
           └─► Emits 'job:updated' event
               └─► ui.updateJobUI() updates DOM

5. NEXT QUEUE CYCLE
   └─► jobQueue.processQueue() called again
       └─► Starts next idle job if slots available
```

### State Update Flow

```
STATE CHANGE
    │
    ├─► state.updateJob(id, changes)
    │       │
    │       ├─► Merges changes into job object
    │       ├─► Recalculates stats
    │       └─► Emits events:
    │           ├─► 'job:updated' (specific job)
    │           ├─► 'state:updated' (full state)
    │           └─► 'stats:updated' (statistics)
    │
    └─► Event listeners respond
            │
            ├─► ui.updateJobUI() - Updates DOM
            ├─► ui.updateStats() - Updates counters
            └─► Any custom listeners
```

### Event Propagation

```
STATE EVENTS              UI RESPONSES              DOM UPDATES
─────────────────────────────────────────────────────────────────
job:added        ────►    ui.renderJob()      ────► Create job box
                                                     Insert into grid

job:updated      ────►    ui.updateJobUI()    ────► Update class
                                                     Update status badge
                                                     Update result area
                                                     Update duration

job:removed      ────►    ui.removeJobUI()    ────► Fade out animation
                                                     Remove from DOM

stats:updated    ────►    ui.updateStats()    ────► Update counters
                                                     Total/Running/Done/Fail

diagnostics:     ────►    ui.updateDiagnostics() ──► Update status pills
updated                                               Server/API/Balance
```

## Logging Architecture

### Logger Instances

```
┌──────────────────────────────────────────────────────────────┐
│                         logger.js                            │
├──────────────────────────────────────────────────────────────┤
│  Class: Logger(moduleName)                                   │
│    - _log(level, message, data)                             │
│    - info(), success(), warning(), error(), debug()         │
│    - jobCreated(), jobStarted(), jobCompleted(), etc.       │
├──────────────────────────────────────────────────────────────┤
│  Singleton Instances:                                        │
│    • systemLogger  ─────► System-wide events                │
│    • jobLogger     ─────► Job lifecycle tracking            │
│    • apiLogger     ─────► API requests/responses            │
│    • uiLogger      ─────► UI updates/interactions           │
│    • queueLogger   ─────► Queue processing events           │
└──────────────────────────────────────────────────────────────┘
```

### Log Event Types

```javascript
// SYSTEM LOGS (systemLogger)
- Application initialization
- Module setup
- Configuration changes
- Global errors

// JOB LOGS (jobLogger)
- Job created
- Job started
- Job progress
- Job completed
- Job failed

// API LOGS (apiLogger)
- Request sent
- Response received
- API errors
- Network issues

// UI LOGS (uiLogger)
- User interactions (clicks, inputs)
- DOM rendering
- Event subscriptions
- UI errors

// QUEUE LOGS (queueLogger)
- Queue processing
- Parallel slots management
- Job scheduling
- Queue status updates
```

## State Management

### State Structure

```javascript
{
  jobs: [
    {
      id: "job-1",
      prompt: "heroic knight",
      width: 64,
      height: 64,
      seed: null,
      status: "success",
      result: "data:image/png;base64...",
      error: null,
      startTime: 1698589123456,
      endTime: 1698589125901,
      duration: 2.445,
      createdAt: 1698589120000
    }
  ],

  diagnostics: {
    server: { status: "ok", message: "Online" },
    api: { status: "ok", message: "Detected" },
    balance: { status: "ok", message: "$10.00" },
    lastChecked: Date
  },

  config: {
    maxParallelJobs: 3,
    serverUrl: "http://127.0.0.1:8787"
  },

  stats: {
    total: 5,
    running: 2,
    completed: 2,
    failed: 1
  }
}
```

### State Methods

```javascript
// Subscriptions
state.subscribe(event, callback)
state.emit(event, data)

// Job Management
state.addJob(job)
state.updateJob(jobId, updates)
state.removeJob(jobId)
state.clearAllJobs()
state.getJob(jobId)
state.getJobsByStatus(status)

// Diagnostics
state.updateDiagnostics(diagnostics)

// Configuration
state.getConfig(key)
state.setConfig(key, value)

// State Access
state.getState()
state.updateStats()
```

## API Layer

### Endpoints

```javascript
// Health Check
GET /health
Response: {
  status: "ok",
  api_key_detected: true,
  balance: {
    status: "ok",
    usd: 10.00,
    type: "USD"
  }
}

// Generate Character
POST /generate-character
Body: {
  prompt: string,
  width: number,
  height: number,
  seed?: string
}
Response: {
  image_data_url: string,
  image_path?: string
}
```

### API Client Methods

```javascript
// Internal
api.request(method, endpoint, data)

// Public
api.generateCharacter(prompt, width, height, seed)
api.checkHealth()
api.getBalance()
```

## UI Components

### DOM Structure

```html
<body>
  <div class="header">
    <h1>PixelLab Command Center</h1>
    <p>Description...</p>
  </div>

  <div class="controls">
    <!-- Presets, form inputs, action buttons -->
  </div>

  <div class="jobs-header">
    <!-- Stats: Total, Running, Completed, Failed -->
  </div>

  <div class="jobs-grid" id="jobs-grid">
    <!-- Job boxes rendered here dynamically -->
    <div class="job-box status-{status}" id="{job.id}">
      <div class="job-header">...</div>
      <div class="job-prompt">...</div>
      <div class="job-meta">...</div>
      <div class="job-result">...</div>
      <div class="job-actions">...</div>
    </div>
  </div>

  <div class="diagnostics">
    <!-- Server, API, Balance status -->
  </div>
</body>
```

### UI Manager Methods

```javascript
// Initialization
ui.init()
ui.setupEventListeners()
ui.subscribeToState()

// User Actions
ui.applyPreset(presetName)
ui.addJob()
ui.addMultipleJobs(count)
ui.clearAllJobs()

// Rendering
ui.renderJob(job)
ui.updateJobUI(job)
ui.removeJobUI(job)
ui.clearAllJobsUI()
ui.updateStats(stats)
ui.updateDiagnostics(diagnostics)
```

## Performance Considerations

### Efficient Rendering
- Jobs rendered on-demand (not full re-render)
- Individual job updates (not grid re-render)
- CSS transitions for smooth animations
- Event delegation where possible

### Memory Management
- Jobs removed from DOM when deleted
- No memory leaks from event listeners
- Proper cleanup on removal

### Parallel Execution
- Configurable max parallel jobs (default: 3)
- Automatic queue processing
- Slot-based execution management

## Security Considerations

### Client-Side
- Input validation before API calls
- Error message sanitization
- No sensitive data in logs
- CORS handling

### API Communication
- API key handled server-side
- No credentials in client code
- HTTPS recommended for production

## Testing Strategy

### Manual Testing
```javascript
// Console commands for testing
app.createTestJob()
app.setMaxParallelJobs(1)
jobQueue.createMultipleJobs(5, "test", 32, 32)
```

### Automated Testing (Future)
- Unit tests for each module
- Integration tests for workflows
- E2E tests for user flows

## Deployment

### Development
1. Start backend: `python3 scripts/pixellab_actions.py --serve`
2. Open HTML in browser (no build needed)
3. Enable browser console for logs

### Production
1. Serve static files via web server
2. Configure serverUrl in state.js
3. Ensure CORS headers on backend
4. Consider minification (optional)

## Extension Points

### Adding New Job Types
1. Extend `Job` class in `jobQueue.js`
2. Add new API method in `api.js`
3. Create custom rendering in `ui.js`

### Custom Loggers
```javascript
import { Logger } from './logger.js'
const customLogger = new Logger('CUSTOM')
```

### State Events
```javascript
state.subscribe('custom:event', (data) => {
  // Handle custom event
})

state.emit('custom:event', data)
```

### New UI Components
```javascript
// In ui.js
renderCustomComponent(data) {
  // Create and insert DOM elements
  // Subscribe to relevant state events
}
```

