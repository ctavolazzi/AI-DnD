---
character: {{ character_name }}
date_created: {{ date_created }}
class: {{ character_class }}
race: {{ character_race }}
---

# {{ character_name }}'s Journal

## Journal Entries

{% if journal_entries %}
{% for entry in journal_entries %}
### {{ entry.date }}

{{ entry.content }}

{% endfor %}
{% else %}
*No journal entries yet*
{% endif %}

## Internal Thoughts

{% if internal_thoughts %}
{% for thought in internal_thoughts %}
### {{ thought.date }}

{{ thought.content }}

{% endfor %}
{% else %}
*No recorded thoughts yet*
{% endif %}

## Related Events
{% if related_events %}
{% for event in related_events %}
- [[{{ event }}]]
{% endfor %}
{% else %}
*No related events recorded*
{% endif %}

## Related Characters
{% if related_characters %}
{% for character in related_characters %}
- [[{{ character }}]]
{% endfor %}
{% else %}
*No character connections recorded*
{% endif %}

## Active Quests
{% if related_quests %}
{% for quest in related_quests %}
- [[{{ quest }}]]
{% endfor %}
{% else %}
*No active quests*
{% endif %}