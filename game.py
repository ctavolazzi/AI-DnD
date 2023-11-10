# game.py
import importlib
import random
import json
from character import Character
from module_loader import ModuleLoader
from game_state_manager import GameStateManager
from main_menu import MainMenu
from default_map import DefaultMap

class Game:
    direction_mapping = {'w': 'north', 'a': 'west', 's': 'south', 'd': 'east'}
    movement_deltas = {'north': (0, -1), 'south': (0, 1), 'west': (-1, 0), 'east': (1, 0)}

    def __init__(self, config):
        self.config = config
        self.is_running = True
        self.characters = {}
        self.modules = {}
        self.player_position = (0, 0)  # Starting position
        self.map = DefaultMap(10)  # Assuming a 10x10 world for simplicity
        self.map.mark_as_explored(self.player_position)
        # Additional initialization code can go here

    def move_player(self, direction):
        # Using the direction parameter as a key to get the movement delta
        dx, dy = self.movement_deltas[direction]
        x, y = self.player_position
        new_x, new_y = x + dx, y + dy

        # Check if the new position is within the map boundaries
        if 0 <= new_x < self.map.size and 0 <= new_y < self.map.size:
            self.player_position = (new_x, new_y)
            self.map.mark_as_explored(self.player_position)
        else:
            print("You can't move in that direction.")

    def game_loop(self):
        while self.is_running:
            self.render_game_state()  # Display the map before asking for the next command
            command = input("Enter 'WASD' to move, 'Q' to quit: ").lower()

            if command in self.direction_mapping:
                # Translate command to direction before passing to move_player
                self.move_player(self.direction_mapping[command])
            elif command == 'q':
                print("Exiting game...")
                self.is_running = False
            else:
                print("Invalid command. Use 'WASD' to move or 'Q' to quit.")

    def render_game_state(self):
        self.map.display(self.player_position)
        # Additional game state rendering can go here

    def update_character(self, character):
        self.characters[character.config['name']] = character
        # self.state.update_character(character)  # Change from game_state to state

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