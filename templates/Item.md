---
name: {{ name }}
type: {{ type }}
rarity: {{ rarity }}
discovered: {{ discovered_date }}
---

# {{ name }}

> {{ description }}

## Properties
- **Type**: {{ type }}
- **Rarity**: {{ rarity }}
- **Value**: {{ value }}
{% if equipped_by %}
- **Currently Equipped By**: [[{{ equipped_by }}]]
{% endif %}

## Effects
{% if effects %}
{% for effect in effects %}
- {{ effect }}
{% endfor %}
{% else %}
- No known effects
{% endif %}

## Abilities
{% if abilities %}
{% for ability in abilities %}
- **{{ ability.name }}**: {{ ability.description }}
{% endfor %}
{% else %}
- No special abilities
{% endif %}

## History
{% if history %}
{% for event in history %}
- {{ event }}
{% endfor %}
{% else %}
- No recorded history
{% endif %}

## Notes
{{ notes }}