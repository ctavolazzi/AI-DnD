
from module_interface import ModuleInterface
from module_loader import ModuleLoader
from game import Game
from game_state import GameState
from character import Character
from combat_module import CombatModule
from dialogue_module import DialogueModule
from main_menu import MainMenu
from player_menu import PlayerMenu
from config import config
from world import World


import time
import random

# Helper function to stream text to the console, character by character
def stc(text, delay=0.05):
    for character in text:
        print(character, end='', flush=True)
        time.sleep(delay)
    print()

# Function to display the backstory from a file
def display_backstory(backstory_path="backstory.txt"):
    try:
        with open(backstory_path, "r") as file:
            backstory = file.read()
        stc(backstory)
    except FileNotFoundError:
        print("Backstory file not found. Please ensure 'backstory.txt' exists.")
# Function to create a random character by selecting a random name
def create_character(config):
    return Character(config)

def create_random_character(config=None):
    names = ["Ariadne", "Theron", "Kael", "Mira"]
    if config == None:
        config = {"name": random.choice(names)}
    random_character = create_character(config)
    return random_character

# main.py

def create_custom_character():
    print("Let's create your character!")
    name = input("What is your character's name? ")
    race = input("Choose your race [Human, Elf, Dwarf, Orc]: ")
    character_class = input("Choose your class [Warrior, Mage, Rogue]: ")

    # You can add input validation or loops to ensure correct input
    # For now, let's assume the player inputs are valid

    attributes = {}
    for attr in ['strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma']:
        value = int(input(f"Assign points to {attr} (1-20): "))
        attributes[attr] = value

    config = {
        "name": name,
        "race": race,
        "character_class": character_class,
        **attributes
    }

    new_character = Character(config)
    print(f"You have created {new_character}")
    return new_character

def test_character_creation():
    character = create_custom_character()
    character.save('character.json')
    loaded_character = Character.load('character.json')
    assert str(character) == str(loaded_character)
    print("Character creation test passed!")

# Function to set up the game state and modules
def setup_game(config):
    # The config can be a parameter if different configurations are needed per game setup.
    game = Game(config)
    # Initialize the world and assign it to the game
    game.world = World(config)
    game.world.load_world()
    return game

# Main menu function to greet the player and offer choices
def main_menu(game):
    print("Welcome to the DnD Game!")
    print("1. Start Game")
    print("2. Load Game")
    print("3. Save Game")  # New option to save the game
    print("4. Options")    # Placeholder for future functionality
    print("5. Exit")
    choice = input("Select an option: ")
    if choice == "3":
        save_game_state(game)
    elif choice == "2":
        load_game_state(game)
    return choice

def render_game_state(game):
    # Get the character's current location and print its description
    current_location = game.world.get_location(game.player_character.position)
    print(current_location.description)

    # Print the character's current stats and inventory
    print(f"HP: {game.player_character.state['hp']}, MP: {game.player_character.state['mp']}")
    print(f"Inventory: {game.player_character.state['inventory']}")

# Function to handle the start of the game, including character creation
def start_game(game):
    print("Loading backstory...")
    display_backstory()
    print("Character Creation:")
    print("1. Create Custom Character")
    print("2. Load Random Character")
    choice = input("Select an option: ")
    if choice == "1":
        custom_character = create_custom_character()
        game.update_character(custom_character)
        stc(f"Welcome, {custom_character.config['name']}!")
    elif choice == "2":
        random_character = create_random_character()
        game.update_character(random_character)
        stc(f"Welcome, {random_character.config['name']}!")
    else:
        stc("Invalid option. Returning to main menu...")
        return
    # Placeholder for presenting story options
    stc("Please be advised: This game is HIGHLY UNSTABLE. Story options are being developed. Play at your own risk...")
    game_loop(game)


def game_loop(game):
    command_map = {
        'w': 'north',
        'a': 'west',
        's': 'south',
        'd': 'east',
    }

    while game.is_running:
        command = input("Enter 'WASD' to move, 'Q' to quit: ").lower()
        if command in command_map:
            # Move the player in the specified direction
            game.move_player(command_map[command])
        elif command == 'q':
            print("Exiting game...")
            game.is_running = False
        else:
            print("Invalid command.")

        # Update and render game state after each action
        game.render_game_state()

        # Sleep might be required to control loop speed if necessary
        # time.sleep(0.1)


# The main function that ties everything together and runs the game loop
def main(config):
    game = setup_game(config)
    while True:
        choice = main_menu(game)
        if choice == "1":
            start_game(game)
        elif choice == "5":
            print("Exiting game. Goodbye!")
            break
        else:
            print("Invalid option. Please try again.")

def save_game_state(game):
    # Save the current game state to a file
    game.save_state('savegame.json')
    print("Game saved successfully.")

def load_game_state(game):
    # Load the game state from a file
    game.load_state('savegame.json')
    print("Game loaded successfully.")

if __name__ == "__main__":
    print(config)
    main(config)