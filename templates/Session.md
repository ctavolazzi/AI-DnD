---
name: {{ name }}
date: {{ date }}
run_id: {{ run_id }}
---

# {{ name }}

*Session Date: {{ date }}*

## Summary
{{ summary }}

## Characters Present
{% if characters %}
{% for character in characters %}
- [[{{ character }}]]
{% endfor %}
{% else %}
- No characters recorded for this session
{% endif %}

## Locations Visited
{% if locations %}
{% for location in locations %}
- [[{{ location }}]]
{% endfor %}
{% else %}
- No locations visited during this session
{% endif %}

## Quests
{% if quests %}
{% for quest in quests %}
- [[{{ quest }}]] - {{ quest_status[quest] }}
{% endfor %}
{% else %}
- No quests active during this session
{% endif %}

## Key Events
{% if events %}
{% for event in events %}
- [[{{ event }}]]
{% endfor %}
{% else %}
- No key events recorded
{% endif %}

## Combat Encounters
{% if combat %}
{% for encounter in combat %}
- [[{{ encounter }}]]
{% endfor %}
{% else %}
- No combat occurred during this session
{% endif %}

## Discoveries
{% if discoveries %}
{% for discovery in discoveries %}
- {{ discovery }}
{% endfor %}
{% else %}
- No notable discoveries
{% endif %}

## Character Development
{% if character_development %}
{% for character, development in character_development.items() %}
- **[[{{ character }}]]**: {{ development }}
{% endfor %}
{% else %}
- No character development noted
{% endif %}

## Items Acquired
{% if items_acquired %}
{% for item in items_acquired %}
- [[{{ item }}]]
{% endfor %}
{% else %}
- No items acquired
{% endif %}

## Next Steps
{{ next_steps }}