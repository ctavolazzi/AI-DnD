# Changelog

All notable changes to this project will be documented in this file.

## [v0.2.0-ui-modal] - 2025-10-25

### Added
- NPC Dialogue Modal (`#npc-modal`) with `openNPCModal(locationKey, linesOverride)` helper.
- TALK action now opens NPC modal when NPCs are present; disabled otherwise with tooltip.
- Favicon added via inline SVG to remove 404 noise.
- New MVP scaffold at `retro-adventure-mvp/` (engine, systems, ui, data, utils) for browser MVP work.

### Changed
- Throttled SAVE logs in `saveGameState()` to reduce console noise while retaining traceability.
- Context gating for ATTACK: enabled only during combat; disabled otherwise with tooltip.

### Internal
- LocationSystem integrated into MVP engine; interactive map with tooltips and movement logs.

Tag: v0.2.0-ui-modal
