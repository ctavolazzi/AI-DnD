# AI-DnD Showcase Demo

This folder contains a lightweight, fully-offline project that lets you watch a
few turns of the AI-DnD engine play out without needing an Ollama install or
any of the long-running background services that the full application expects.
It swaps in a deterministic narrative engine and renders a Rich-based HUD so
you can quickly verify the core combat loop and event logging.

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r ../../requirements.txt  # or pip install rich
python demo_app.py --turns 4
```

By default the showcase animates four turns with a short pause between each
update. Use `--turns`, `--delay`, or `--seed` to adjust the length, pacing, and
randomness of the output.

## What you will see

- A quest hook, party roster, and adversary roster generated from the existing
  `dnd_game` module.
- Reusable canned narrative beats standing in for the LLM responses that the
  real game would request from Ollama.
- A live log panel that scrolls through the key combat events and encounters.

Because the demo piggybacks on the production game classes, it is a convenient
place to add new sample encounters or HUD ideas without touching the main entry
points.
