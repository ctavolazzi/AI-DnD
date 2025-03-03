# Narrative Engine Analysis

## Overview

The narrative engine (`narrative_engine.py`) is a critical component of the AI-DnD project, providing AI-powered storytelling and dynamic narrative generation. This document analyzes its architecture, capabilities, and integration with the rest of the system.

## Key Components

### NarrativeEngine Class

The `NarrativeEngine` class is the central component that:

1. Interfaces with the Ollama AI model
2. Generates narrative content
3. Handles different narrative contexts (scenes, combat, dialogue, etc.)

#### Initialization

The engine initializes with:
- A model selection (defaulting to "mistral")
- A system prompt that directs the AI to act as a D&D Dungeon Master with concise responses

```python
def __init__(self, model="mistral"):
    self.model = model
    self.system_prompt = "You are a D&D Dungeon Master. Keep all responses under 15 words and focus on action and atmosphere."
```

#### AI Integration

The engine uses a subprocess to call the Ollama CLI command:

```python
def _call_ollama(self, prompt):
    try:
        full_prompt = f"{self.system_prompt}\n\n{prompt}"
        cmd = ["ollama", "run", self.model, full_prompt]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.stdout.strip()
    except Exception as e:
        logger.error(f"Error calling Ollama: {e}")
        return "The story continues..."
```

This approach allows the game to use local AI models without requiring an API key or internet connection.

## Narrative Capabilities

The engine provides several narrative functions:

### 1. Scene Description

```python
def describe_scene(self, location, characters):
    prompt = f"Set the scene in 10 words: {location}, {len(characters)} characters present."
    return self._call_ollama(prompt)
```

This generates concise descriptions of the current game location and characters present.

### 2. Combat Narration

```python
def describe_combat(self, attacker, defender, action, damage=None):
    prompt = f"{attacker} {action} {defender}" + (f" ({damage} damage)" if damage else "")
    return self._call_ollama(prompt)
```

This creates vivid descriptions of combat actions and their effects.

### 3. NPC Dialogue

```python
def generate_npc_dialogue(self, npc_name, npc_type, situation):
    prompt = f"Generate dialogue for {npc_name}, a {npc_type}, in this situation: {situation}"
    return self._call_ollama(prompt)
```

This generates contextually appropriate dialogue for non-player characters.

### 4. Player Action Response

```python
def handle_player_action(self, player_name, action, context):
    prompt = f"The player {player_name} attempts to {action}. Context: {context}"
    return self._call_ollama(prompt)
```

This responds to player actions with appropriate narrative consequences.

### 5. Quest Generation

```python
def generate_quest(self, difficulty="medium", theme=None):
    prompt = f"Generate a {difficulty} difficulty D&D quest"
    if theme:
        prompt += f" with the theme: {theme}"
    return self._call_ollama(prompt)
```

This creates dynamic quests with varying difficulty and themes.

### 6. Random Encounters

```python
def generate_random_encounter(self, party_level, environment):
    prompt = f"Generate a random encounter for a level {party_level} party in a {environment} environment."
    return self._call_ollama(prompt)
```

This creates surprise encounters appropriate to the party's level and current environment.

### 7. Combat Summarization

```python
def summarize_combat(self, combat_log):
    prompt = f"Summarize this battle in 10 words or less."
    return self._call_ollama(prompt)
```

This provides concise summaries of combat outcomes.

## Design Approach

The narrative engine follows several design principles:

1. **Conciseness**: All prompts encourage brief, impactful responses (under 15 words)
2. **Atmosphere**: Focus on action and atmosphere rather than exposition
3. **Context-sensitivity**: Each function provides relevant context to the AI
4. **Graceful degradation**: Falls back to generic responses on errors
5. **Local processing**: Uses Ollama for offline AI capabilities

## Integration Points

The narrative engine integrates with:

1. **Game Engine**: Providing narrative context to game events
2. **Combat System**: Describing combat actions and results
3. **World System**: Describing locations and environments

## Strengths

1. Local AI processing without external API dependencies
2. Focused, concise narrative generation
3. Variety of narrative contexts covered
4. Simple yet effective prompt engineering
5. Error handling with fallback responses

## Improvement Opportunities

1. More sophisticated prompt engineering for better AI responses
2. Memory/history for contextual continuity in storytelling
3. Character-aware narration that reflects character traits
4. Support for alternative AI models or APIs
5. Caching or optimization for repeated prompts

## Next Steps for Analysis

1. Testing the quality and consistency of generated narratives
2. Analyzing prompt effectiveness and potential refinements
3. Exploring performance impacts of local AI model use
4. Investigating integration with other narrative systems

---

*This analysis will be updated as we explore the narrative engine in more depth.*