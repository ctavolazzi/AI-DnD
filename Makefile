.PHONY: reset run setup clean archive structure play-game

# Default target - complete workflow to play the game
play-game: setup
	@echo "Setting up project environment..."
	@echo "Killing any running game processes..."
	@pkill -f "python3 run_game.py" || true
	@pkill -f "python3 main.py" || true
	@echo "Running game with fresh reset..."
	@python3 main.py --reset

# Setup the project environment
setup:
	@echo "Setting up project environment..."
	@mkdir -p templates
	@mkdir -p ai-dnd-test-vault/Runs/Archived
	@mkdir -p ai-dnd-test-vault/Dashboard

# Reset and run a new game
reset:
	@echo "Killing any running game processes..."
	@pkill -f "python3 run_game.py" || true
	@pkill -f "python3 main.py" || true
	@echo "Resetting vault to blank slate..."
	@python3 main.py --reset --no-run

# Just run the game without resetting
run:
	@echo "Running the game without resetting..."
	@python3 main.py

# Run the game with reset
run-reset:
	@echo "Running the game with reset flag..."
	@python3 main.py --reset

# Run the game with specific number of turns
run-turns:
	@echo "Running the game with custom turns..."
	@python3 main.py --turns $(turns)

# Rebuild the vault structure without running the game
structure:
	@echo "Rebuilding vault structure..."
	@python3 main.py --reset --no-run

# Clean up generated files
clean:
	@echo "Cleaning up generated files..."
	@rm -rf ai-dnd-test-vault

# Archive the current run
archive:
	@echo "Archiving the current run..."
	@python3 -c "from reset_game import archive_current_vault, update_runs_readme; archive = archive_current_vault(); update_runs_readme(archive)"

# Help message
help:
	@echo "Available commands:"
	@echo "  make play-game   - Complete workflow: setup, reset vault, and run game (default)"
	@echo "  make setup       - Set up project environment"
	@echo "  make reset       - Reset vault to blank slate (no Current-Run.md created)"
	@echo "  make run         - Run the game without resetting"
	@echo "  make run-reset   - Run the game with reset flag"
	@echo "  make run-turns turns=N - Run the game with N turns"
	@echo "  make structure   - Rebuild vault structure without running the game (same as reset)"
	@echo "  make clean       - Clean up generated files"
	@echo "  make archive     - Archive the current run"
	@echo "  make help        - Show this help message"