---
run_id: {{run_id}}
timestamp: {{timestamp}}
status: active
turn_count: 0
---

# Current Game Run: {{run_id}}

> **Started:** {{timestamp}}
> **Last Updated:** {{timestamp}}
> **Current Turn:** {{turn_count|default(0)}}

## Active Game Progress
This page tracks the progress of the current game session as it unfolds. It is automatically updated by the AI-DnD system as the game progresses.

## Game Status
- Status: Active
- Turn: {{turn_count|default(0)}}
- Players: {{character_count|default(0)}}

## Current Quest
{{current_quest|default("*No active quest*")}}

## Party Members
{{party_status|default("*No characters yet*")}}

## Recent Events
{{recent_events|default("*No events recorded yet*")}}

---

> [!TIP]
> - For game instructions: `[[Start]]`
> - For navigation: `[[Dashboard]]`
