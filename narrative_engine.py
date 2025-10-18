import subprocess
import logging

logger = logging.getLogger(__name__)

class NarrativeEngine:
    def __init__(self, model="mistral"):
        self.model = model
        self.system_prompt = "You are a D&D Dungeon Master. Keep all responses under 15 words and focus on action and atmosphere."

    def _call_ollama(self, prompt):
        try:
            full_prompt = f"{self.system_prompt}\n\n{prompt}"
            cmd = ["ollama", "run", self.model, full_prompt]
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.stdout.strip()
        except Exception as e:
            logger.error(f"Error calling Ollama: {e}")
            return "The story continues..."

    def describe_scene(self, location, characters):
        prompt = f"Set the scene in 10 words: {location}, {len(characters)} characters present."
        return self._call_ollama(prompt)

    def describe_combat(self, attacker, defender, action, damage=None):
        prompt = f"{attacker} {action} {defender}" + (f" ({damage} damage)" if damage else "")
        return self._call_ollama(prompt)

    def generate_npc_dialogue(self, npc_name, npc_type, situation):
        prompt = f"Generate dialogue for {npc_name}, a {npc_type}, in this situation: {situation}"
        return self._call_ollama(prompt)

    def handle_player_action(self, player_name, action, context):
        prompt = f"The player {player_name} attempts to {action}. Context: {context}"
        return self._call_ollama(prompt)

    def generate_quest(self, difficulty="medium", theme=None):
        prompt = f"Generate a {difficulty} difficulty D&D quest"
        if theme:
            prompt += f" with the theme: {theme}"
        return self._call_ollama(prompt)

    def generate_random_encounter(self, party_level, environment):
        prompt = f"Generate a random encounter for a level {party_level} party in a {environment} environment."
        return self._call_ollama(prompt)

    def summarize_combat(self, combat_log):
        prompt = f"Summarize this battle in 10 words or less."
        return self._call_ollama(prompt)

    def generate_conclusion(self):
        prompt = "Conclude this D&D adventure with an epic final scene."
        return self._call_ollama(prompt)

    def generate_player_choices(self, player_name: str, char_class: str,
                               location: str, context: str, num_choices: int = 3) -> list:
        """
        Generate meaningful choices for a player character.

        Args:
            player_name: Name of the player
            char_class: Character's class
            location: Current location
            context: Current situation context
            num_choices: Number of choices to generate

        Returns:
            List of choice dictionaries
        """
        # For now, return predefined contextual choices
        # In a full implementation, this would call the AI

        base_choices = [
            {
                "id": "investigate",
                "text": "Investigate the surroundings carefully",
                "type": "action",
                "requires_check": True,
                "ability": "WIS",
                "skill": "Perception",
                "dc": 12
            },
            {
                "id": "talk",
                "text": "Try to communicate with any nearby beings",
                "type": "dialogue",
                "requires_check": True,
                "ability": "CHA",
                "skill": None,
                "dc": 10
            },
            {
                "id": "prepare",
                "text": "Take a defensive stance and prepare for danger",
                "type": "tactical",
                "requires_check": False
            },
            {
                "id": "search",
                "text": "Search for useful items or resources",
                "type": "action",
                "requires_check": True,
                "ability": "INT",
                "skill": "Investigation",
                "dc": 13
            },
            {
                "id": "rest",
                "text": "Take a moment to rest and recover",
                "type": "rest",
                "requires_check": False
            }
        ]

        # Customize based on class
        class_specific = {
            "Fighter": {
                "id": "intimidate",
                "text": "Use your martial presence to intimidate potential threats",
                "type": "social",
                "requires_check": True,
                "ability": "STR",
                "skill": "Intimidation",
                "dc": 12
            },
            "Wizard": {
                "id": "arcana",
                "text": "Examine the area for magical traces or anomalies",
                "type": "knowledge",
                "requires_check": True,
                "ability": "INT",
                "skill": "Arcana",
                "dc": 14
            },
            "Rogue": {
                "id": "stealth",
                "text": "Move stealthily to scout ahead",
                "type": "stealth",
                "requires_check": True,
                "ability": "DEX",
                "skill": "Stealth",
                "dc": 13
            },
            "Cleric": {
                "id": "insight",
                "text": "Seek divine guidance about the situation",
                "type": "divine",
                "requires_check": True,
                "ability": "WIS",
                "skill": "Insight",
                "dc": 11
            }
        }

        # Include class-specific choice if available
        choices = base_choices[:num_choices-1]
        if char_class in class_specific:
            choices.append(class_specific[char_class])
        else:
            choices.append(base_choices[num_choices-1])

        return choices[:num_choices]

    def describe_choice_outcome(self, player_name: str, choice: dict,
                               success: bool = None, context: str = "") -> str:
        """
        Generate a narrative description of a choice outcome.

        Args:
            player_name: Name of the player
            choice: The choice that was made
            success: Whether a skill check succeeded (if applicable)
            context: Additional context

        Returns:
            Narrative description of the outcome
        """
        choice_text = choice.get("text", "takes action")

        if choice.get("requires_check") and success is not None:
            if success:
                prompt = f"{player_name} successfully {choice_text}. Describe the positive outcome in 15 words."
            else:
                prompt = f"{player_name} attempts to {choice_text} but fails. Describe the setback in 15 words."
        else:
            prompt = f"{player_name} {choice_text}. Describe what happens in 15 words."

        return self._call_ollama(prompt)