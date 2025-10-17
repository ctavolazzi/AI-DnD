# AI-DnD Chronomancer Console

This static front end leans into a glowing 90s CRPG command desk complete with
CRT scanlines, pixel-grid chrome, and cassette-deck controls. Pair it with the
deterministic showcase from `examples/simple_demo` to watch an AI-driven dungeon
crawl unfold with neon gauges, dossier tabs, and digest cards that make every
round easy to review.

## Quickstart

```bash
cd examples/web_frontend
python generate_data.py --turns 4 --seed 7
python -m http.server 8000
```

Open http://127.0.0.1:8000/ in your browser and load `index.html`.

- **Load fresh chronicle** pulls in `data/demo_run.json` (regenerate it whenever
  you want a new run).
- **Import ledger** accepts any exported showcase file if you want to compare
  multiple battles.

From the project root you can also use the helper targets:

```bash
make mvp-data              # Generate demo_run.json with default seed/turns
make mvp-session           # Start the FastAPI MVP session service
make mvp-serve             # Serve this console via python -m http.server
```

Override defaults like `make mvp-data MVP_TURNS=6 MVP_SEED=21` or
`MVP_CONSOLE_PORT=9001 make mvp-serve` to tweak the loop.

## Live MVP session service

The console now speaks to a lightweight FastAPI service that streams the same
deterministic showcase frames in real time. This gives designers a taste of the
MVP session loop while we wire up the full Dungeon Master stack.

1. Install dependencies (FastAPI and Uvicorn are included in the project
   `requirements.txt`).
2. Run the service from the project root:

   ```bash
   python -m session_service --host 127.0.0.1 --port 8001
   ```

3. Serve the static console as shown above.
4. Update the **Session service** field if you're running the API on a different
   host/port, then click **Start live session** (or open `index.html?mode=live`
   to connect automatically).

The console will request a session, reveal turns as they arrive, and keep the
timeline, digest cards, and dossier synchronized. When the session finishes you
can restart at any time to generate a fresh deterministic chronicle. The
**Session service** field mirrors the `service` query parameter so you can point
at any accessible host without editing the URL.

## Controls & Features

- **Turn brief** summarizes the current phase, alive combatants, and the
  momentum meter so you can read the state of play at a glance.
- **Timeline deck** provides slider, labels, and turn cards so you can hop to
  any round or finale with a single click.
- **Rewind/Advance** buttons emulate cassette-deck step controls for testing.
- **Auto-run** replays the battle every few seconds, while keyboard shortcuts
  (`←`, `→`, `space`, `home`, `end`) keep testing fast.
- **Company ledger & dossier** surface party and opposition HP bars with
  auto-generated pixel portraits and an inspectable profile for each combatant.
- **Retro finish** keeps the console bathed in CRT scanlines, radial glow, and
  chunky pixel borders so QA feels like they are back on a 90s adventure rig.
- **Chronicle notebook** lets you swap between the current turn log and the
  full campaign history without leaving the console.
- **Quest briefing & conclusion** keep the hook and outcome framed like a retro
  dossier without clutter.

Because everything is static HTML/CSS/JS, you can drop these files onto any host
or open them directly from disk without additional tooling.
