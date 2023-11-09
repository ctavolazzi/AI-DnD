import time
import random
from module_interface import ModuleInterface
from module_loader import ModuleLoader
from game import Game
from game_state import GameState
from character import Character
from combat_module import CombatModule
from dialogue_module import DialogueModule
from menu import Menu
from config import config

# Helper function to stream text to the console, character by character
def stc(text, delay=0.05):
    for character in text:
        print(character, end='', flush=True)
        time.sleep(delay)
    print()  # for newline

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

# Function to set up the game state and modules
def setup_game(config):
    # Initialize the Game object and give it state
    game = Game(config)
    return game

# Main menu function to greet the player and offer choices
def main_menu():
    print("Welcome to the DnD Game!")
    print("1. Start Game")
    print("2. Load Game")  # Placeholder for future functionality
    print("3. Options")    # Placeholder for future functionality
    print("4. Exit")
    choice = input("Select an option: ")
    return choice

# Function to handle the start of the game, including character creation
def start_game(game):
    print("Loading backstory...")
    display_backstory()
    print("Character Creation:")
    print("1. Create Custom Character (Coming Soon!)")
    print("2. Load Random Character")
    choice = input("Select an option: ")
    if choice == "1" or choice == "2":
      # Create a random character
      random_character = create_random_character()
      stc(f"Welcome, {random_character.config['name']}!")
    # Placeholder for presenting story options
    stc("Story options are being developed...")

# The main function that ties everything together and runs the game loop
def main(config=None):
    # Initialize game state and modules
    if config is None:
        config = {"modules": [{"name": "test", "description": "Test Module"}]} # Set the config here
    game = setup_game(config)

    # Run setup tests (To be implemented)
    # Run any failsafes or security checks (To be implemented)

    while True:
        choice = main_menu()
        if choice == "1":
            start_game(game)
        elif choice == "4":
            print("Exiting game. Goodbye!")
            break
        else:
            print("Invalid option. Please try again. (Sorry, this is still under development.)")

if __name__ == "__main__":
    main(config)
