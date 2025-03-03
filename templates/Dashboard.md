# Adventure Dashboard

> **Last Updated:** {{timestamp}}
> **Current Run ID:** {{run_id}}

## Current Status
- **Game Turn:** {{turn_count|default(0)}}
- **Active Characters:** {{character_count|default(0)}}
- **Locations Discovered:** {{location_count|default(0)}}
- **Current Quest:** {{current_quest|default("*No active quest*")}}

## Party Status
```
{{party_status|default("No party members yet")}}
```

## Recent Events
```
{{recent_events|default("No recent events")}}
```

## Quick Navigation

### 📌 Main Pages
- `[[Start]]` - How to Follow Along
- `[[Current Run]]` - Active Game Session
- `[[Index]]` - Complete Content Catalog
- `[[Runs/Archived/README|Archived Runs]]` - Previous Sessions

### 🎮 Game Content
- `[[Characters/]]` - 👤 Characters
- `[[Locations/]]` - 🗺️ Locations
- `[[Quests/]]` - ⚔️ Quests
- `[[Events/]]` - 📜 Events
- `[[Items/]]` - 💎 Items
- `[[Sessions/]]` - 📝 Session Logs

---

> [!NOTE]
> This dashboard automatically updates as the game progresses.