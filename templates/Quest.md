---
name: {{ name }}
difficulty: {{ difficulty }}
status: {{ status }}
started: {{ start_date }}
---

# {{ name }}

> {{ description }}

## Overview
{{ overview }}

## Status: {{ status }}

## Difficulty: {{ difficulty }}

## Objectives
{% if objectives %}
{% for objective in objectives %}
- {% if objective.completed %}✅{% else %}⬜{% endif %} {{ objective.description }}
{% endfor %}
{% else %}
- No defined objectives
{% endif %}

## Involved Characters
{% if characters %}
{% for character in characters %}
- [[{{ character }}]]
{% endfor %}
{% else %}
- No characters currently involved
{% endif %}

## Locations
{% if locations %}
{% for location in locations %}
- [[{{ location }}]]
{% endfor %}
{% else %}
- No locations associated with this quest
{% endif %}

## Related Items
{% if items %}
{% for item in items %}
- [[{{ item }}]]
{% endfor %}
{% else %}
- No items associated with this quest
{% endif %}

## Progress
{% if events %}
{% for event in events %}
- {{ event.date }} - {{ event.description }}
{% endfor %}
{% else %}
- No progress recorded yet
{% endif %}

## Rewards
{% if rewards %}
{% for reward in rewards %}
- {{ reward }}
{% endfor %}
{% else %}
- Rewards unknown
{% endif %}

## Notes
{{ notes }}