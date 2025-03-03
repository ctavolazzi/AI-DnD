---
name: {{ name }}
type: {{ type }}
timestamp: {{ timestamp }}
location: {{ location }}
---

# {{ name }}

*{{ timestamp }} at [[{{ location }}]]*

## Summary
{{ summary }}

## Detailed Description
{{ description }}

## Participants
{% if participants %}
{% for participant in participants %}
- [[{{ participant }}]]
{% endfor %}
{% else %}
- No recorded participants
{% endif %}

## Outcomes
{% if outcomes %}
{% for outcome in outcomes %}
- {{ outcome }}
{% endfor %}
{% else %}
- No outcomes recorded
{% endif %}

## Related Items
{% if items %}
{% for item in items %}
- [[{{ item }}]]
{% endfor %}
{% else %}
- No related items
{% endif %}

## Related Events
{% if related_events %}
{% for event in related_events %}
- [[{{ event }}]]
{% endfor %}
{% else %}
- No related events
{% endif %}

## Quest Progress
{% if quest_progress %}
{% for quest, progress in quest_progress.items() %}
- [[{{ quest }}]]: {{ progress }}
{% endfor %}
{% else %}
- No quest progress associated with this event
{% endif %}