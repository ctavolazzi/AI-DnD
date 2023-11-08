# main.py

import random
from module_loader import ModuleLoader
from game_state import GameState
from character import Character

# Assuming you have the following modules with their configure and update methods
from combat_module import CombatModule
from dialogue_module import DialogueModule
# ... import other game modules ...

def create_random_character():
    # Your character creation logic will go here
    # For now, let's just return a new Character with a random name
    names = ["Ariadne", "Theron", "Kael", "Mira"]
    return Character(random.choice(names))

def load_game_modules(game_state):
    # Instantiate the module loader
    module_loader = ModuleLoader()

    # Configure each game module and load it
    combat_config = {'difficulty': 'normal'}
    dialogue_config = {}  # Add necessary configurations
    # ... other module configurations ...

    # Load and initialize modules with their specific configurations
    module_loader.load_module('combat', CombatModule, combat_config, game_state)
    module_loader.load_module('dialogue', DialogueModule, dialogue_config, game_state)
    # ... load other modules ...

    return module_loader

def main():
    print("Welcome to the DnD Simulator!")

    # Initialize game state
    game_state = GameState()

    # Create a new character with random attributes
    game_state.character = create_random_character()

    # Load and configure game modules
    module_loader = load_game_modules(game_state)

    # Assign the loaded module_loader to the game_state for easy access
    game_state.module_loader = module_loader

    # Start the game loop
    try:
        while not game_state.is_game_over:
            module_loader.update_modules(game_state)
    except KeyboardInterrupt:
        print("\nGame interrupted by user.")
    finally:
        print("Thank you for playing!")
        module_loader.terminate_modules(game_state)

if __name__ == "__main__":
    main()
