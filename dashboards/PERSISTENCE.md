# PixelLab Dashboard - Persistence System

## Overview

The PixelLab Command Center uses a **hybrid storage approach** combining:
1. **localStorage** - Fast, client-side caching
2. **Server JSON File** - Persistent, shareable storage

This gives you the best of both worlds: instant load times + persistent history across devices and sessions.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                       Browser                                │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  state.js (State Manager)                            │  │
│  │                                                       │  │
│  │  ┌─────────────┐          ┌──────────────┐          │  │
│  │  │ localStorage│◄────────►│   Server     │          │  │
│  │  │   (Cache)   │   Sync   │  (Source of  │          │  │
│  │  │             │          │    Truth)     │          │  │
│  │  └─────────────┘          └──────────────┘          │  │
│  │                                                       │  │
│  │  Load: localStorage first, then sync from server    │  │
│  │  Save: Both simultaneously (async)                   │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  Python Server   │
                    │  (Port 8787)     │
                    └────────┬─────────┘
                             │
                    ┌────────▼──────────────────┐
                    │  dashboards/              │
                    │    job_history.json       │
                    │    job_history.json.backup│
                    └───────────────────────────┘
```

## API Endpoints

### GET /load-jobs
Load job history from server.

**Response:**
```json
{
  "status": "ok",
  "jobs": [...],
  "lastJobId": 5,
  "savedAt": "2025-10-29T04:30:00.000Z",
  "message": "Loaded 5 jobs"
}
```

### POST /save-jobs
Save job history to server.

**Request:**
```json
{
  "jobs": [...],
  "lastJobId": 5
}
```

**Response:**
```json
{
  "status": "ok",
  "message": "Saved 5 jobs",
  "savedAt": "2025-10-29T04:30:00.000Z",
  "fileSize": 12345
}
```

## Storage Flow

### On Page Load:
```
1. Read from localStorage (instant)
   ├─► Jobs found: Display immediately
   └─► Jobs not found: Show empty state

2. Load from server (async)
   ├─► Server has newer data: Update UI
   ├─► Server matches localStorage: No change
   └─► Server fails: Keep localStorage data
```

### On Job Change (Add/Update/Remove):
```
1. Update in-memory state
2. Save to localStorage (instant)
3. Save to server (async)
   ├─► Success: Log confirmation
   └─► Failure: Still have localStorage
```

## File Format

### dashboards/job_history.json
```json
{
  "jobs": [
    {
      "id": "job-1",
      "prompt": "heroic knight with glowing sword",
      "width": 64,
      "height": 64,
      "seed": null,
      "status": "success",
      "result": "data:image/png;base64,...",
      "error": null,
      "startTime": 1698589123456,
      "endTime": 1698589125901,
      "duration": 2.445,
      "createdAt": 1698589120000
    }
  ],
  "lastJobId": 1,
  "savedAt": "2025-10-29T04:30:00.000Z",
  "version": "1.0"
}
```

## Backup System

Every time `job_history.json` is saved, the previous version is automatically backed up to `job_history.json.backup`.

**To restore from backup:**
```bash
cd /Users/ctavolazzi/Code/AI-DnD/dashboards
cp job_history.json.backup job_history.json
```

## Benefits

✅ **Fast Loading** - localStorage provides instant UI updates
✅ **Persistent Storage** - Server file survives browser cache clears
✅ **Automatic Backups** - Previous version always saved
✅ **Human Readable** - JSON file can be manually edited
✅ **Shareable** - Copy job_history.json to share your work
✅ **Version Control** - Can commit to git (optional)
✅ **Resilient** - Works even if server is down

## Usage

### View Current Storage Location
```bash
# Server file
ls -lh /Users/ctavolazzi/Code/AI-DnD/dashboards/job_history.json

# Backup file
ls -lh /Users/ctavolazzi/Code/AI-DnD/dashboards/job_history.json.backup
```

### Clear All History
```javascript
// In browser console
app.clearHistory()
```

### Export History
```bash
# Copy job history to desktop
cp /Users/ctavolazzi/Code/AI-DnD/dashboards/job_history.json ~/Desktop/my_jobs.json
```

### Import History
```bash
# Copy from another location
cp ~/Desktop/my_jobs.json /Users/ctavolazzi/Code/AI-DnD/dashboards/job_history.json

# Refresh browser to load
```

### Manual Editing
```bash
# Edit the JSON file directly
code /Users/ctavolazzi/Code/AI-DnD/dashboards/job_history.json
```

## Console Commands

```javascript
// View current state
app.getState()

// Get metrics
app.getMetrics()

// Clear all jobs (also deletes server file)
app.clearHistory()

// Manual sync from server
state.loadFromServer()

// Manual save to server
state.saveToStorage()
```

## Troubleshooting

### Jobs not saving to server
**Check:**
1. Server is running: `curl http://127.0.0.1:8787/health`
2. Console logs for errors
3. File permissions: `ls -l dashboards/job_history.json`

**Fix:**
```bash
# Restart server
cd /Users/ctavolazzi/Code/AI-DnD
python3 scripts/pixellab_actions.py --serve
```

### Jobs not loading from server
**Check:**
1. Console shows "Loaded jobs from server"
2. File exists: `cat dashboards/job_history.json`

**Fix:**
```bash
# Test endpoint
curl http://127.0.0.1:8787/load-jobs
```

### localStorage out of sync
**Fix:**
```javascript
// In browser console
state.loadFromServer()
```

### Corrupted job_history.json
**Fix:**
```bash
# Restore from backup
cd dashboards
cp job_history.json.backup job_history.json

# Or start fresh
rm job_history.json
```

## Implementation Details

### State Manager (state.js)

**Key Methods:**
- `loadFromStorage()` - Loads from localStorage, triggers server sync
- `loadFromServer()` - Async loads from server API
- `saveToStorage()` - Saves to both localStorage and server
- `saveToLocalStorage()` - localStorage only (for caching)

### Backend (pixellab_actions.py)

**Key Functions:**
- `load_job_history()` - Reads JSON file, returns jobs
- `save_job_history(jobs, last_job_id)` - Writes JSON with backup

**Endpoints:**
- `GET /load-jobs` - Returns job history
- `POST /save-jobs` - Saves job history

## Migration from localStorage-only

The hybrid system is backward compatible. Existing localStorage data will:
1. Load normally on first page load
2. Automatically sync to server on next save
3. Continue working even if server is down

No manual migration needed! 🎉

## Future Enhancements

Potential improvements:
- [ ] Compression for large job histories
- [ ] Pagination for 1000+ jobs
- [ ] Export as CSV/Excel
- [ ] Cloud sync (Dropbox, Google Drive)
- [ ] Multi-user support
- [ ] Job history search/filter
- [ ] Job analytics dashboard

## Version History

- **v1.0** (2025-10-29): Initial hybrid localStorage + server persistence
  - Automatic backups
  - Fast localStorage caching
  - Server-side JSON storage
  - Backward compatible

