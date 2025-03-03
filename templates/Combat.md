---
name: {{ name }}
location: {{ location }}
timestamp: {{ timestamp }}
---

# {{ name }}

*Combat at [[{{ location }}]] - {{ timestamp }}*

## Overview
{{ overview }}

## Participants

### Player Team
{% if player_team %}
{% for character in player_team %}
- [[{{ character }}]]
{% endfor %}
{% else %}
- No player characters recorded
{% endif %}

### Enemy Team
{% if enemy_team %}
{% for enemy in enemy_team %}
- {{ enemy }}
{% endfor %}
{% else %}
- No enemies recorded
{% endif %}

## Combat Log
{% if combat_log %}
{% for turn in combat_log %}
### Turn {{ turn.number }}
{% for action in turn.actions %}
- {{ action }}
{% endfor %}
{% endfor %}
{% else %}
- No combat actions recorded
{% endif %}

## Outcome
{{ outcome }}

## Rewards
{% if rewards %}
{% for reward in rewards %}
- {{ reward }}
{% endfor %}
{% else %}
- No rewards recorded
{% endif %}

## Related Events
{% if related_events %}
{% for event in related_events %}
- [[{{ event }}]]
{% endfor %}
{% else %}
- No related events
{% endif %}