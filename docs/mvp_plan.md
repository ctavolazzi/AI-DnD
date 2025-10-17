# AI-DnD MVP Blueprint

## 1. Product Vision
- **Who**: Internal designers, narrative engineers, and early external playtesters validating the AI-driven Dungeon Master experience.
- **What**: A playable, text-forward RPG session where a human party collaborates with an AI Dungeon Master through a rich yet lightweight interface.
- **Why**: Provide confidence that the AI can orchestrate compelling sessions while enabling the team to observe, debug, and iterate on storytelling mechanics quickly.

## 2. Core MVP Goals
1. **Live Session Loop** – Allow a facilitator or player to initiate, progress, and conclude a session with the AI DM in real time.
2. **Playable Combat & Narrative** – Support alternating story beats and tactical encounters, including choices, dice checks, and combat resolution.
3. **Transparent State Tracking** – Surface party status, initiative, conditions, and quest objectives so testers can evaluate pacing and balance.
4. **Session Logging** – Persist structured transcripts and telemetry for review, regression tests, and model fine-tuning.

## 3. Primary Use Cases
- **Facilitated Playtest**: A designer runs a session with the AI DM, guiding human playtesters through story branches and battles.
- **Solo Regression Run**: QA loads scripted prompts to validate that mechanics behave deterministically across releases.
- **Narrative Review**: Writers review captured logs to flag pacing or tone issues and feed improvements back into prompt design.

## 4. Scope & Feature Outline
| Layer | Must Have | Nice to Have (Post-MVP) |
| --- | --- | --- |
| **Session Service** | REST/WebSocket API to create sessions, send player inputs, and stream AI responses. Deterministic mode toggles for tests. | Multi-session lobby, authentication, persistent campaign storage. |
| **Game Engine** | Rules engine covering story turns, skill checks, initiative order, combat resolution, loot summaries. Hooks for logging and observers. | Advanced subsystems (crafting, exploration maps), full character builder, dynamic audio cues. |
| **Front End** | Chronomancer console upgraded to consume live data, capture player actions, display logs, and manage turns. Offline mode still available for demos. | Visual assets, animated sprites, drag-and-drop inventory, mobile layout. |
| **Tooling** | CLI + scripts for generating deterministic showcases, seeding sessions, replaying transcripts, and exporting analytics. | Telemetry dashboards, automated A/B narrative experiments. |

## 5. Technical Requirements
- **API Layer**
  - Session lifecycle endpoints (`POST /sessions`, `POST /sessions/{id}/turn`, `GET /sessions/{id}/state`).
  - Streaming channel (WebSocket or Server-Sent Events) for incremental narration and combat updates.
  - Pluggable storage for session state (in-memory with snapshot serialization for MVP).
- **Engine Integration**
  - Bridge existing `ShowcaseSimulator` patterns with the production `DungeonMaster` classes to support live decisions.
  - Deterministic seed handling for QA and transcript replay.
  - Structured event schema (JSON) aligning engine outputs with UI expectations: turn metadata, actor roster, HP/conditions, log entries, and pending choices.
- **Front-End Client**
  - State management layer for live updates (e.g., minimal reactive store or vanilla JS event bus to avoid premature framework adoption).
  - Input components for player choices, dice rolls, and timeline review (history scrubbing, but read-only while session active).
  - Accessibility considerations: semantic markup, ARIA updates for live narration, keyboard navigation retained.
- **Logging & Storage**
  - Persistent transcript repository (JSONL or SQLite) with metadata (session id, seed, participants).
  - Export commands to bundle transcripts with engine configs for reproducibility.
- **Testing & Observability**
  - Contract tests covering API schema vs. UI consumption.
  - Load-light soak test to ensure AI calls and state storage stay responsive.
  - Feature flags to swap between offline demo data and live service.

## 6. Non-Goals / Deferrals
- Multiplayer networking beyond hot-seat/local handoff.
- Rich media assets (sprites, audio, cutscenes).
- Campaign persistence across multiple sessions with save/load trees.
- Complex account systems or monetization hooks.

## 7. MVP Milestones
1. **Service Skeleton (Week 1-2)**
   - Expose session lifecycle API.
   - Wrap AI DM call chain with deterministic harness.
   - Basic logging pipeline.
2. **Interactive Console Upgrade (Week 3-4)**
   - Adapt Chronomancer console to consume live session state.
   - Implement player input widgets and validation.
   - Introduce session status indicators (active, awaiting input, resolving).
3. **Narrative & Combat Fidelity (Week 5-6)**
   - Ensure combat turns sync between engine and UI (HP bars, initiative).
   - Add branching choices, skill checks, loot events.
   - Harden error handling (fallback narration, retry prompts).
4. **QA Readiness (Week 7)**
   - Regression scripts comparing live runs to stored transcripts.
   - Documentation + onboarding guide for designers and QA.
   - Final polish pass on retro UI (readability, responsiveness).

## 8. Risks & Mitigations
- **AI Latency**: Introduce optimistic UI states and background prefetch of likely next prompts; cache deterministic seeds for quick replays.
- **Schema Drift**: Maintain shared TypeScript/JSON schema definitions or Python dataclasses exported to the front end.
- **Model Output Variability**: Include guardrails (temperature control, post-processing) and deterministic fixtures for QA.
- **Team Onboarding**: Provide sample sessions, API docs, and scripts to bootstrap playtests without manual setup.

## 9. Expert Recommendations for Next Steps
1. **Stabilize the Engine Interface**: Formalize an event schema shared by `game_state_manager.py` and the showcase simulator so the UI consumes one contract whether data is simulated or live.
2. **Prototype Session Service**: Stand up a lightweight FastAPI or Flask app that wraps the engine, starting with deterministic responses. Aim for stateless endpoints with session ids before introducing websockets.
3. **Refactor the Front End into Modules**: Split current `app.js` into loader, renderer, and controls modules. Introduce a small store to manage live vs. replay modes and pending player choices.
4. **Implement Player Input Flow**: Extend the UI to send decisions (choose action, target) back to the service; fall back to auto-resolve for demo mode.
5. **Enhance Logging Pipeline**: Capture structured logs from both service and client to a shared transcript format, enabling playback in the existing static viewer.
6. **Gradual Feature Hardening**: As combat fidelity improves, add fail-safes (timeout handling, default actions) so live sessions never stall.

These steps keep the MVP attainable while avoiding premature optimization—focusing on a reliable live session loop, shared data contracts, and tooling that empowers designers to iterate quickly.

## 10. MVP Progress Snapshot
- ✅ Session service skeleton implemented with FastAPI and deterministic showcase frames.
- ✅ Chronomancer console upgraded to request live turns, autoplay across API responses, and advertise session status.
- ✅ Documentation refreshed with setup steps for the service and console workflow.
- ⏳ Integrating the full Dungeon Master loop, persistent storage, and player input capture remain future milestones.

## 11. Handoff Checklist
- Run `make mvp-data` to regenerate the deterministic chronicle consumed by the console and session service.
- Launch the API with `make mvp-session` (or `python -m session_service --host 127.0.0.1 --port 8001`).
- Serve the retro console via `make mvp-serve` and verify the **Session service** field reflects your host before starting live mode.
- Use `make mvp-demo` for a reminder of the full sequence and to confirm documentation remains aligned with the one-command workflow.
