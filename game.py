# game.py
import importlib
import random
from character import Character
from module_loader import ModuleLoader

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


    def update_character(self, character):
        self.player_characters[character.name] = character

    def start(self):
        self.main_loop()

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
