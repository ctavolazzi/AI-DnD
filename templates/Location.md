---
name: {{ name }}
type: {{ type }}
discovered: {{ discovered_date }}
---

# {{ name }}

> {{ description }}

## Overview
{{ overview }}

## Notable Features
{% if features %}
{% for feature in features %}
- {{ feature }}
{% endfor %}
{% else %}
- No notable features discovered yet
{% endif %}

## Connected Locations
{% if connections %}
{% for connection in connections %}
- [[{{ connection }}]] - {{ connections[connection] }}
{% endfor %}
{% else %}
- No known connections to other locations
{% endif %}

## Characters Present
{% if characters %}
{% for character in characters %}
- [[{{ character }}]]
{% endfor %}
{% else %}
- No characters currently present
{% endif %}

## Items Found
{% if items %}
{% for item in items %}
- [[{{ item }}]]
{% endfor %}
{% else %}
- No items discovered
{% endif %}

## History
{% if events %}
{% for event in events %}
- {{ event }}
{% endfor %}
{% else %}
- No recorded history
{% endif %}

## Dangers
{% if dangers %}
{% for danger in dangers %}
- {{ danger }}
{% endfor %}
{% else %}
- No known dangers
{% endif %}

## Notes
{{ notes }}