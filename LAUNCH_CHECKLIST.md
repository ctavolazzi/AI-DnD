# 🚀 Launch Checklist - Narrative Theater

Use this checklist before your first launch!

---

## ✅ Pre-Launch Validation

Run the validation script:
```bash
./validate_narrative_theater.sh
```

**Expected result**: "✅ VALIDATION PASSED!"

---

## 🔑 Step 1: API Keys (REQUIRED)

Set your API keys in the terminal:

```bash
export PIXELLAB_API_KEY=your_pixellab_api_key_here
export GEMINI_API_KEY=your_gemini_api_key_here
```

**Verify they're set:**
```bash
echo $PIXELLAB_API_KEY
echo $GEMINI_API_KEY
```

> **Note**: You'll need to set these in each new terminal session, or add them to your `~/.zshrc` or `~/.bashrc` for persistence.

---

## 🤖 Step 2: Ollama (REQUIRED)

**Install Ollama** (if not already installed):
```bash
# Visit: https://ollama.ai
# Download and install
```

**Pull the Mistral model:**
```bash
ollama pull mistral
```

**Test it works:**
```bash
ollama run mistral "Generate a short quest for adventurers"
```

---

## 🎭 Step 3: Launch Servers

Start all three servers with one command:
```bash
./start_narrative_theater.sh
```

**You should see:**
```
✅ All servers started!

Server Status:
  🎨 Nano Banana:       http://localhost:5000
  🎮 PixelLab Bridge:   http://localhost:5001
  📖 Narrative Server:  http://localhost:5002
```

**Verify servers are running:**
```bash
curl http://localhost:5002/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "DnD Narrative Theater Server",
  "port": 5002,
  "active_sessions": 0
}
```

---

## 🌐 Step 4: Open the Theater

**Option 1**: Double-click `dnd-narrative-theater.html` in Finder

**Option 2**: From terminal:
```bash
open dnd-narrative-theater.html
```

**Option 3**: Drag the file into your browser

---

## 🎮 Step 5: Start Your Adventure!

In the browser:
1. Click **"Start Adventure"** button
2. Wait ~5-10 seconds for initialization
3. You should see:
   - Quest card appears
   - 2 character cards with stats
   - First scene narrative
   - "Next Scene" button enabled
   - Character images generating in gallery

4. Click **"Next Scene"** to progress
5. Click **"Visualize This!"** to generate images for any scene
6. Enjoy your adventure! 🎲

---

## 🐛 Troubleshooting

### Server Won't Start

**Check ports are available:**
```bash
lsof -i :5000
lsof -i :5001
lsof -i :5002
```

**Kill any existing processes:**
```bash
./stop_narrative_theater.sh
./start_narrative_theater.sh
```

### No Character Images

**Check PixelLab API key:**
```bash
echo $PIXELLAB_API_KEY
```

**Check PixelLab server logs:**
```bash
tail -f logs/pixellab_bridge.log
```

### No Enhanced Images

**Check Gemini API key:**
```bash
echo $GEMINI_API_KEY
```

**Check Nano Banana logs:**
```bash
tail -f logs/nano_banana.log
```

### Narrative Not Generating

**Check Ollama is running:**
```bash
ollama list
ollama run mistral "test"
```

**Check narrative server logs:**
```bash
tail -f logs/narrative_server.log
```

### Browser Shows "Cannot connect"

**Verify servers are running:**
```bash
curl http://localhost:5002/health
curl http://localhost:5001/health
curl http://localhost:5000/health
```

If any fail, restart servers:
```bash
./stop_narrative_theater.sh
./start_narrative_theater.sh
```

---

## 📊 Monitor Logs

**Watch all logs in real-time:**
```bash
# Terminal 1
tail -f logs/narrative_server.log

# Terminal 2
tail -f logs/pixellab_bridge.log

# Terminal 3
tail -f logs/nano_banana.log
```

---

## 🛑 Stop Everything

When you're done:
```bash
./stop_narrative_theater.sh
```

Or press `Ctrl+C` in the terminal running the servers.

---

## ✅ Quick Reference

| Action | Command |
|--------|---------|
| **Validate** | `./validate_narrative_theater.sh` |
| **Start** | `./start_narrative_theater.sh` |
| **Stop** | `./stop_narrative_theater.sh` |
| **Open** | `open dnd-narrative-theater.html` |
| **Health Check** | `curl http://localhost:5002/health` |
| **View Logs** | `tail -f logs/narrative_server.log` |

---

## 🎯 Expected First Run

1. **Start servers** → ~10 seconds
2. **Open browser** → Immediate
3. **Click "Start Adventure"** → ~5 seconds
   - Ollama generates quest: ~3 sec
   - Characters created: ~1 sec
   - First scene generated: ~1 sec
4. **Character images appear** → ~10-15 seconds
   - PixelLab generates 2 sprites
5. **Ready to play!** → Click "Next Scene"

**Total time from launch to playing: ~30 seconds**

---

## 🎭 Enjoy Your Adventure!

Everything is ready. The theater awaits your command!

**Happy adventuring!** 🎲✨

