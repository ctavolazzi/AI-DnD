# 🎭 D&D Narrative Theater - Comprehensive Tracking System

## Overview

This tracking system provides **real-time monitoring and comprehensive analysis** of D&D Narrative Theater adventures. It captures frontend events, backend API calls, performance metrics, and generates detailed reports for analysis and optimization.

---

## 🎯 Features

### Frontend Tracking (Browser)
- ✅ **Live Adventure Viewer** - Embedded iframe with real-time game display
- ✅ **Real-Time Stats Dashboard** - API calls, images, timing, status
- ✅ **Event Timeline** - Chronological list of all events
- ✅ **API Call Monitor** - Track all HTTP requests and responses
- ✅ **Image Gallery** - View all generated images as they appear
- ✅ **Comprehensive Reporting** - Download full analysis as Markdown

### Backend Monitoring (Python)
- ✅ **Log File Analysis** - Parse and track all server logs
- ✅ **Performance Metrics** - Response times, error rates, throughput
- ✅ **Health Checks** - Verify server status and API availability
- ✅ **Error Tracking** - Capture and categorize all errors
- ✅ **JSON + Markdown Reports** - Dual-format comprehensive analysis

---

## 🚀 Quick Start

### Option 1: Simple Browser Tracking
```bash
# Open the tracker directly
open live-adventure-tracker.html
# or on Linux: xdg-open live-adventure-tracker.html

# Then click "🚀 Start Tracked Adventure"
```

### Option 2: Full Tracked Adventure (RECOMMENDED)
```bash
# Run the automated test script
./run_tracked_adventure.sh

# Choose option 3 for full tracking
# Follow on-screen instructions
```

### Option 3: Backend Monitoring Only
```bash
# Start monitoring server logs
python3 monitor_adventure.py

# Play adventure in browser normally
# Press Ctrl+C when done to generate report
```

---

## 📋 Complete Workflow

### 1. Prerequisites
Ensure servers are running:
```bash
./start_theater.sh
```

Check server status:
```bash
curl http://localhost:5000/health  # Nano Banana
curl http://localhost:5001/health  # PixelLab
curl http://localhost:5002/health  # Narrative Server
```

### 2. Start Tracking Session
```bash
./run_tracked_adventure.sh
```

**You will be prompted to choose:**
- **Option 1:** Browser-only (frontend tracking)
- **Option 2:** Backend-only (server log monitoring)
- **Option 3:** Full tracking (BOTH - recommended)

### 3. Run Adventure

**If using browser tracker:**
1. Tracker opens automatically
2. Click "🚀 Start Tracked Adventure"
3. Adventure loads in embedded frame
4. Interact with the game normally
5. Watch real-time stats update

**All tracking happens automatically:**
- API calls captured as they occur
- Images logged when generated
- Timeline updates in real-time
- Performance metrics calculated

### 4. Generate Report

**Browser tracker:**
- Click "📊 Generate Full Report"
- Markdown report downloads automatically

**Backend monitor:**
- Press Ctrl+C to stop
- Reports generate automatically
- JSON + Markdown formats

### 5. Review Analysis

Reports are saved to `tracking_sessions/session_TIMESTAMP/`

Files generated:
- `adventure_analysis_TIMESTAMP.md` - Human-readable report
- `adventure_analysis_TIMESTAMP.json` - Machine-readable data
- `backend_monitor.log` - Backend monitoring log

---

## 📊 What Gets Tracked

### Frontend Metrics
| Category | Details |
|----------|---------|
| **API Calls** | URL, method, status code, response time, payload |
| **Images** | Source, prompt, timing, base64 data |
| **Timeline** | Event name, timestamp, elapsed time, description |
| **Performance** | Total time, average response time, success rate |
| **User Actions** | Button clicks, form submissions, choices made |

### Backend Metrics
| Category | Details |
|----------|---------|
| **Server Logs** | All log entries from 3 servers |
| **Request Stats** | Total, successful, failed, by endpoint |
| **Error Analysis** | Error messages, stack traces, frequency |
| **Health Status** | Server availability, API key status |
| **Image Generation** | Prompts used, generation time, success rate |

---

## 🎨 Live Tracker Interface

### Dashboard Layout

```
┌─────────────────────────────────────────────────────────┐
│              Live Adventure Tracker                     │
│  [Start] [Generate Report] [Clear] [Stop]              │
└─────────────────────────────────────────────────────────┘

┌──────────────────────┬──────────────────────────────────┐
│  Live Adventure      │  Real-Time Stats                 │
│  (Embedded Game)     │  • API Calls: 12                 │
│                      │  • Images: 4                     │
│                      │  • Time: 45s                     │
│                      │  • Status: Running               │
│                      │                                  │
│                      │  Timeline                        │
│                      │  ○ Adventure Started             │
│                      │  ○ Character Created             │
│                      │  ● Image Generating...           │
└──────────────────────┴──────────────────────────────────┘

┌──────────────────────┬──────────────────────────────────┐
│  Event Log           │  API Calls                       │
│  [10:23:45] INFO:... │  POST /start-adventure [200]     │
│  [10:23:46] API:...  │  POST /generate [200]            │
│  [10:23:47] SUCCESS  │  GET /health [200]               │
└──────────────────────┴──────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  Generated Images                                       │
│  [IMG1] [IMG2] [IMG3] [IMG4]                           │
└─────────────────────────────────────────────────────────┘
```

### Real-Time Updates
- **Green pulsing dot** = Currently running
- **Gray dot** = Idle/stopped
- **Red dot** = Error detected
- **Timeline items** = Active (green) or completed (blue)
- **API calls** = Color-coded by status (green=success, red=error)

---

## 📈 Report Contents

### Generated Markdown Report Includes:

#### 1. Executive Summary
- Test duration
- Total events
- Overall success rate
- Key metrics

#### 2. Performance Metrics
- API call breakdown
- Response time statistics
- Error rate analysis
- Image generation stats

#### 3. Timeline of Events
- Chronological event list
- Elapsed time for each event
- Event descriptions

#### 4. API Call Details
- Every request made
- Status codes
- Response times
- Payloads (if available)

#### 5. Generated Images
- Image sources (Gemini, PixelLab)
- Prompts used
- Generation timing

#### 6. Error Analysis
- All errors encountered
- Stack traces
- Frequency by type

#### 7. Performance Insights
- Automated analysis
- Bottleneck identification
- Optimization suggestions

---

## 🔍 Use Cases

### Development & Debugging
```bash
# Track while developing new features
./run_tracked_adventure.sh

# Review backend logs for errors
python3 monitor_adventure.py

# Check specific API endpoint performance
grep "/generate" tracking_sessions/*/adventure_analysis*.md
```

### Performance Testing
```bash
# Run multiple adventures and compare
for i in {1..5}; do
    ./run_tracked_adventure.sh
    sleep 10
done

# Analyze results
ls -lh tracking_sessions/
```

### User Experience Analysis
```bash
# Track frontend interactions
open live-adventure-tracker.html

# Measure user journey timing
# - Time to first image
# - Story load time
# - Response time per action
```

### Bug Reproduction
```bash
# Enable full tracking
./run_tracked_adventure.sh  # Option 3

# Reproduce bug
# Complete analysis captured automatically
# Share JSON report with developers
```

---

## 🛠️ Advanced Configuration

### Custom Tracking Intervals

Edit `live-adventure-tracker.html`:
```javascript
// Change stats update frequency (default: 1000ms)
trackingInterval = setInterval(updateElapsedTime, 500);  // Update every 0.5s
```

### Backend Monitor Customization

Edit `monitor_adventure.py`:
```python
# Change display refresh rate (default: 2s)
time.sleep(1)  # Update every 1s

# Change number of recent items shown
for call in self.api_calls[-10:]:  # Show last 10 instead of 5
```

### Log File Retention

```bash
# Keep logs from specific session
cp -r tracking_sessions/session_TIMESTAMP my_important_test/

# Archive old sessions
tar -czf tracking_archive_$(date +%Y%m%d).tar.gz tracking_sessions/

# Clean up old sessions (keep last 10)
ls -t tracking_sessions/ | tail -n +11 | xargs rm -rf
```

---

## 📊 Sample Report Excerpt

```markdown
# 🎭 D&D Narrative Theater - Live Adventure Analysis Report

**Generated:** 2025-10-29 10:45:23
**Test Duration:** 47.3s
**Total Events:** 23

## 📊 Performance Metrics

| Metric | Value |
|--------|-------|
| Total API Calls | 15 |
| Successful Calls | 15 |
| Failed Calls | 0 |
| Success Rate | 100.0% |
| Total Images Generated | 4 |

## ⏱️ Timeline of Events

1. **Test Started** (0.0s)
   - Initializing adventure tracker

2. **Adventure Initiated** (0.5s)
   - Sending start request

3. **API Call: POST /start-adventure** (1.2s)
   - Status: 200 | Time: 234ms

4. **Character Created** (2.1s)
   - Hero: Thorin the Brave

5. **Image Generated** (8.3s)
   - Source: Gemini | Prompt: "fantasy RPG character portrait..."
```

---

## 🎯 Best Practices

### For Development
1. ✅ Always run with full tracking during feature development
2. ✅ Review error logs immediately after each test
3. ✅ Compare metrics before/after changes
4. ✅ Archive important test sessions

### For Testing
1. ✅ Run multiple adventures to get average metrics
2. ✅ Test with different story prompts
3. ✅ Verify all image sources working
4. ✅ Check error rates remain < 5%

### For Production
1. ✅ Monitor backend logs continuously
2. ✅ Set up alerts for error rate spikes
3. ✅ Track performance trends over time
4. ✅ Regular health checks on all servers

---

## 🐛 Troubleshooting

### Tracker not capturing data
**Problem:** Browser tracker shows no API calls

**Solutions:**
1. Check if iframe loaded correctly
2. Verify CORS enabled on backend
3. Open browser console (F12) for errors
4. Refresh and click "Start Tracked Adventure" again

### Backend monitor not seeing logs
**Problem:** Python monitor shows "No log files found"

**Solutions:**
```bash
# Verify servers running
curl http://localhost:5002/health

# Check log directory exists
ls -la logs/

# Start servers if needed
./start_theater.sh

# Verify log files created
ls -la logs/*.log
```

### Reports not generating
**Problem:** No report downloaded after clicking "Generate Report"

**Solutions:**
1. Check browser's download folder
2. Look for browser popup blocker
3. Verify tracking data collected (check stats)
4. Try browser console: `generateReport()`

### Missing images in report
**Problem:** Image gallery empty despite images generating

**Solutions:**
1. Images may still be loading (wait 30s)
2. Check browser console for errors
3. Verify image generation endpoints working:
   ```bash
   curl -X POST http://localhost:5000/generate -H "Content-Type: application/json" -d '{"prompt":"test"}'
   ```

---

## 📁 File Structure

```
AI-DnD/
├── live-adventure-tracker.html       # Frontend tracking UI
├── monitor_adventure.py              # Backend monitoring script
├── run_tracked_adventure.sh          # Unified test runner
├── tracking_sessions/                # Session data directory
│   ├── session_20251029_104523/
│   │   ├── adventure_analysis_*.md
│   │   ├── adventure_analysis_*.json
│   │   └── backend_monitor.log
│   └── session_20251029_110245/
│       └── ...
└── logs/                             # Server logs
    ├── nano_banana.log
    ├── pixellab_bridge.log
    └── narrative_server.log
```

---

## 🔮 Future Enhancements

Planned features for v2.2.0:
- [ ] WebSocket-based real-time streaming
- [ ] Automated performance regression testing
- [ ] Image quality analysis (resolution, artifacts)
- [ ] User interaction heatmaps
- [ ] A/B testing framework
- [ ] Export reports to PDF
- [ ] Integration with CI/CD pipelines
- [ ] Cloud storage for session archives

---

## 🎉 Summary

The D&D Narrative Theater tracking system provides:

✅ **Complete Visibility** - See everything happening in real-time
✅ **Comprehensive Analysis** - Detailed reports for optimization
✅ **Easy to Use** - One command to start tracking
✅ **Developer-Friendly** - JSON + Markdown formats
✅ **Production-Ready** - Monitor live systems

**Start tracking your adventures today:**
```bash
./run_tracked_adventure.sh
```

---

*Last Updated: 2025-10-29*
*Version: 1.0.0*
*Part of D&D Narrative Theater v2.1.0*



