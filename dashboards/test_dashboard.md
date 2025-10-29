# PixelLab Dashboard Testing Guide

## ✅ Pre-Test Checklist

1. **Backend Server Status:** ✓ Running on port 8787
2. **API Key:** ✓ Detected
3. **Balance:** $0.00 (Note: May need credits for actual generation)
4. **Dashboard:** ✓ Opened in browser

## 🧪 Test Scenarios

### Test 1: Application Initialization
**What to Check:**
1. Open Browser Console (F12 / Cmd+Option+I)
2. Look for startup logs:
   - `🎮 PixelLab Command Center` header
   - `Modular Architecture v2.0`
   - Module initialization logs
   - System information display
   - Helpful console commands list

**Expected Output:**
```
🎮 PixelLab Command Center
Modular Architecture v2.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

INFO [SYSTEM] +0.000s DOM Content Loaded
INFO [SYSTEM] +0.001s Initializing application modules...
INFO [UI] +0.002s UI Manager initialized
...

📊 System Information
  User Agent: ...
  Platform: ...
  ...

💡 Helpful Console Commands
  app.getState() - View current application state
  app.getMetrics() - View job queue metrics
  ...
```

### Test 2: Diagnostics Check
**What to Check:**
1. Look at "System Diagnostics" panel at bottom
2. Verify all three status indicators:
   - Actions Server: Should be "Online" (green)
   - API Key: Should be "Detected" (green)
   - Balance: Should show "$0.00" (green)

**Console Logs to Watch:**
```
🔧 DIAGNOSTICS UPDATE
  Server Status: { status: 'ok', message: 'Online' }
  API Key: { status: 'ok', message: 'Detected' }
  Balance: { status: 'ok', message: '$0.00' }
```

### Test 3: Create Single Job
**Actions:**
1. Leave default preset ("heroic knight with glowing sword...")
2. Click "➕ Add Job to Queue"

**Expected Console Logs:**
```
🆕 JOB CREATED
  Job ID: job-1
  Prompt: heroic knight with glowing sword, blue cape, ready stance
  Dimensions: 64×64px
  Seed: Random
  Status: idle
  Full Job Object: { ... }

▶️ JOB STARTED
  Job ID: job-1
  Prompt: heroic knight with glowing sword, blue cape, ready stance
  Start Time: 2025-10-29T...
  Request Payload: {
    prompt: "heroic knight with glowing sword, blue cape, ready stance",
    width: 64,
    height: 64,
    seed: null
  }

🌐 API REQUEST
  Method: POST
  URL: http://127.0.0.1:8787/generate-character
  Payload: { ... }
  Timestamp: ...

📥 API RESPONSE [200]  (or [402] if no credits)
  URL: http://127.0.0.1:8787/generate-character
  Status: 200
  Response Data: { ... }

✅ JOB COMPLETED  (or ❌ JOB FAILED if no credits)
  Job ID: job-1
  Status: success
  Duration: 2.45s
  ...
```

**UI Checks:**
- Job box appears with "job-1" ID
- Status indicator changes: ⚪ Idle → 🔵 Running → 🟢 Success (or 🔴 Error)
- Duration displays after completion
- Image preview appears (if successful)

### Test 4: Multiple Parallel Jobs
**Actions:**
1. Click "➕➕ Add 3 Jobs"

**Expected Behavior:**
- 3 job boxes appear immediately
- Max 3 run simultaneously (configurable)
- Console shows interleaved logs from all jobs
- Queue processing logs show slot management

**Console Logs to Watch:**
```
📊 QUEUE STATUS
  Total Jobs: 3
  Running: 3
  Completed: 0
  Failed: 0
  Idle/Queued: 0

(As jobs complete...)

📊 QUEUE STATUS
  Total Jobs: 3
  Running: 1
  Completed: 2
  Failed: 0
  Idle/Queued: 0
```

**UI Stats Should Update:**
- Total: 3
- Running: Changes from 3 → 2 → 1 → 0
- Completed: Changes from 0 → 1 → 2 → 3
- Failed: 0 (or >0 if errors)

### Test 5: Console API Commands
**Try These Commands:**

```javascript
// View current state
app.getState()
// Should show full state tree with jobs, diagnostics, config, stats

// View queue metrics
app.getMetrics()
// Should show: total, running, completed, failed, totalDuration, avgDuration

// Create test job
app.createTestJob()
// Should create job with "test pixel art character" prompt

// Change parallel job limit
app.setMaxParallelJobs(5)
// Should update config and log the change

// Inspect individual loggers
systemLogger.info("Testing system logger", { test: true })
jobLogger.debug("Testing job logger")
apiLogger.info("Testing API logger")
```

### Test 6: Error Handling (If No Credits)
**Expected Behavior:**
- Job status turns 🔴 Error
- Error message displays in job box
- Console shows detailed error logs:

```
❌ JOB FAILED
  Job ID: job-1
  Status: error
  Duration: 0.34s
  Error Message: Insufficient credits or API error
  Error Object: Error { ... }
  Full Job Object: { ... }
```

### Test 7: Job Management
**Actions to Test:**

1. **Run Button:**
   - Click ▶️ Run on a failed job
   - Should reset and rerun the job

2. **Remove Button:**
   - Click 🗑️ Remove on any job
   - Job box fades out and disappears
   - Console shows removal log

3. **Clear All:**
   - Click "🗑️ Clear All Jobs"
   - Confirm dialog appears
   - All jobs cleared
   - Console shows cleanup log

### Test 8: Preset Switching
**Actions:**
1. Click different preset buttons:
   - ⚔️ Heroic Knight
   - 🔮 Cyberpunk Mage
   - 🐉 Pixel Dragon
   - 🛡️ Warrior
   - 🧙 Wizard

**Expected:**
- Prompt textarea updates with preset text
- Width/Height update to preset values
- Console logs preset application

### Test 9: State Event Monitoring
**In Console, Run:**
```javascript
// Monitor all job updates
state.subscribe('job:updated', (job) => {
  console.log('🔔 Job Update Event:', job.id, job.status)
})

// Monitor stats updates
state.subscribe('stats:updated', (stats) => {
  console.log('📈 Stats Update:', stats)
})

// Create job to see events fire
app.createTestJob()
```

**Expected:**
- See event logs for every state change
- Events fire in correct order

### Test 10: Performance Check
**Actions:**
1. Create 10 jobs rapidly (use console):
```javascript
for (let i = 0; i < 10; i++) {
  app.createTestJob()
}
```

**Watch For:**
- UI remains responsive
- Logs are organized and grouped
- Queue processes correctly
- Memory doesn't spike excessively
- All jobs complete or fail gracefully

## 📋 Checklist Summary

- [ ] Application initializes with welcome logs
- [ ] System diagnostics show correct status
- [ ] Single job creates and runs
- [ ] Console logs show complete job lifecycle
- [ ] Multiple jobs run in parallel (max 3)
- [ ] Queue status updates correctly
- [ ] UI stats update in real-time
- [ ] Console API commands work
- [ ] Error handling displays properly
- [ ] Job management (run/remove/clear) works
- [ ] Presets switch correctly
- [ ] State events fire correctly
- [ ] Performance is acceptable under load
- [ ] No JavaScript errors in console
- [ ] All loggers produce output

## 🐛 Common Issues & Fixes

### Issue: Blank Console Logs
**Fix:** Ensure console log levels include all types (not filtered)

### Issue: "Module not found" errors
**Fix:** Check browser supports ES6 modules (modern browsers only)
- Served from file:// may have CORS issues
- Use local server: `python3 -m http.server 8000` in dashboards/

### Issue: Jobs hang in "Running" status
**Fix:** Check backend server logs for errors
- May need API credits
- Check network tab for failed requests

### Issue: UI not updating
**Fix:** Check browser console for errors
- Verify event listeners are attached
- Try `app.getState()` to inspect state

### Issue: No API response logs
**Fix:** Verify backend is running and accessible
- Test: `curl http://127.0.0.1:8787/health`
- Check CORS if served from different origin

## 🎯 Success Criteria

✅ All console logs are detailed and informative
✅ Job lifecycle is fully tracked from creation to completion
✅ Parallel execution works correctly
✅ UI updates reflect state changes immediately
✅ Error handling is graceful and informative
✅ Console API provides useful debugging tools
✅ No memory leaks or performance issues
✅ Code is modular and maintainable

## 📊 Expected Results

With **valid API credits:**
- Jobs complete successfully
- Images appear in job boxes
- Duration shows realistic times (2-5s typically)
- All status indicators green

With **no API credits:**
- Jobs fail gracefully
- Error messages explain the issue
- System remains stable
- Can still test all UI/queue features

---

**Current Status:** Ready to test! 🚀
**Date:** 2025-10-29
**Version:** Modular Architecture v2.0

