from dnd_game import DnDGame
import logging

# Configure logging to display all messages
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'  # Simplified format for better readability
)

def main():
    print("Welcome to the Narrative D&D Game!")
    print("===================================")

    # Create game instance with Mistral model
    game = DnDGame(model="mistral")

    # Run the game
    try:
        game.run_game()
    except KeyboardInterrupt:
        print("\nGame ended by user.")
    except Exception as e:
        print(f"\nGame ended due to error: {e}")

if __name__ == "__main__":
    main()