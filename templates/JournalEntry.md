---
character: {{ character_name }}
entry_date: {{ entry_date }}
entry_type: {{ entry_type }}
related_event: {{ related_event }}
---

# {{ character_name }}'s {{ entry_type|title }} - {{ entry_date }}

{% if entry_type == "journal" %}
## Journal Entry
{% else %}
## Internal Thought
{% endif %}

{{ content }}

{% if mood %}
**Mood**: {{ mood }}
{% endif %}

{% if related_characters %}
## Related Characters
{% for character in related_characters %}
- [[{{ character }}]]
{% endfor %}
{% endif %}

{% if related_locations %}
## Related Locations
{% for location in related_locations %}
- [[{{ location }}]]
{% endfor %}
{% endif %}

{% if related_event %}
## Related Event
[[{{ related_event }}]]
{% endif %}

{% if related_quests %}
## Related Quests
{% for quest in related_quests %}
- [[{{ quest }}]]
{% endfor %}
{% endif %}