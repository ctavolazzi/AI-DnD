# PixelLab Command Center

This directory contains the interactive dashboard and supporting artifacts for the
PixelLab testing command center.

## Files

- `pixellab_dashboard.html` – the main testing console. Open it in a browser
  after starting the actions server (see below).
- `generated/` – images created via on-demand actions are stored here.
- `history.json` – automatically generated summary of historical test runs
  (created when you run `python3 enhanced_test_results_display.py`).

## Usage

1. **Start the actions server**
   ```bash
   python3 scripts/pixellab_actions.py --serve
   ```
   The server listens on `http://127.0.0.1:8787` and exposes endpoints the
   dashboard can call.

2. **Refresh history (optional)**
   ```bash
   python3 enhanced_test_results_display.py
   ```
   This regenerates the enhanced per-run report and updates `history.json` with
   metadata about every `test_results_*` directory.

3. **Open the dashboard**
   ```bash
   open dashboards/pixellab_dashboard.html
   ```
   Use the controls to trigger the PixFlux character generation function. Each
   run captures duration, status, and output assets, appending them to the
   "Latest Attempts" section. Historical runs appear below the live results.

## Extending

The dashboard is intentionally modular. To add more functions:

- Create new endpoints in `scripts/pixellab_actions.py`.
- Add corresponding components to `pixellab_dashboard.html`, following the
  PixFlux module as a template.
- Update `history.json` generation if the new functionality captures
  additional metadata.
