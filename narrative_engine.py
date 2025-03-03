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