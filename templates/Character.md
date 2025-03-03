---
name: {{ name }}
class: {{ char_class }}
status: {{ status }}
hp: {{ hp }}
max_hp: {{ max_hp }}
attack: {{ attack }}
defense: {{ defense }}
team: {{ team }}
---

# {{ name }}

> {{ status_summary }}

## Character Stats
- **Class**: {{ char_class }}
- **HP**: {{ hp }}/{{ max_hp }}
- **Attack**: {{ attack }}
- **Defense**: {{ defense }}
- **Status**: {{ status }}

## Abilities
{% if abilities %}
{% for ability in abilities %}
- **{{ ability }}**
{% endfor %}
{% else %}
- No special abilities
{% endif %}

## Status Effects
{% if status_effects %}
{% for effect in status_effects %}
- {{ effect }}
{% endfor %}
{% else %}
- No current status effects
{% endif %}

## Biography
{{ bio }}

## Inventory
{% if inventory %}
{% for item in inventory %}
- [[{{ item }}]]
{% endfor %}
{% else %}
- No items
{% endif %}

## History
{% if actions %}
{% for action in actions %}
- {{ action }}
{% endfor %}
{% else %}
- No recorded actions yet
{% endif %}

## Relationships
{% if relationships %}
{% for relationship in relationships %}
- **{{ relationship.name }}**: {{ relationship.description }}
{% endfor %}
{% else %}
- No established relationships
{% endif %}

## Associated Events
{% if events %}
{% for event in events %}
- [[{{ event }}]]
{% endfor %}
{% else %}
- No associated events
{% endif %}