# game.py
import importlib
import random
import json
from character import Character
from module_loader import ModuleLoader
from game_state_manager import GameStateManager

class Game:
    """
    The Game class encapsulates all the operations related to game flow and state.

    Attributes:
        config (dict): Configuration for the game.
        is_running (bool): Indicates if the game is currently running.
        modules (dict): Holds the loaded game modules.
        game_state (GameState): The current state of the game.
    """

    def __init__(self, config):
        self.config = config
        self.is_running = True
        self.characters = {}
        self.modules = {}
        self.load_config(config)
        self.state = GameStateManager()


    def update_character(self, character):
        self.characters[character.config['name']] = character
        self.state.update_character(character)  # Change from game_state to state


    def main_loop(self):
        while self.is_running:
            # Run the game loop
            pass

    def game_over(self):
        # Implement logic to determine if the game should end
        return True

    def load_config(self, config):
        # Predefined config options that are allowed to be set.
        allowed_config_options = {'option1', 'option2', 'option3'}
        for key, value in config.items():
            if key in allowed_config_options:
                setattr(self, key, value)

    def save_state(self, file_path):
        with open(file_path, 'w') as file:
            # Serialize necessary components of game state, e.g., characters, world state
            game_state = {
                "characters": {name: char.to_dict() for name, char in self.characters.items()},
                # Include other necessary state information
            }
            json.dump(game_state, file)

    def load_state(self, file_path):
        with open(file_path, 'r') as file:
            # Deserialize the game state and restore it
            game_state = json.load(file)
            for name, char_data in game_state['characters'].items():
                self.characters[name] = Character.from_dict(char_data)
            # Restore other state information
            self.is_running = True