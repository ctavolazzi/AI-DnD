#!/usr/bin/env python3

from rich.live import Live
from rich.panel import Panel
from rich.console import Console
from rich.layout import Layout
import time
import logging
from dnd_game import DnDGame, GameError
from log_aggregator import LogAggregator

class RichGameDisplay:
    def __init__(self, game: DnDGame):
        self.game = game
        self.console = Console()
        self.turn_count = 0
        self.max_turns = 10

        # Set up logging
        self.logger = logging.getLogger()
        self.logger.handlers.clear()
        self.logger.setLevel(logging.INFO)

        self.aggregator = LogAggregator()
        self.aggregator.setLevel(logging.INFO)
        self.aggregator.setFormatter(logging.Formatter("%(message)s"))
        self.logger.addHandler(self.aggregator)

    def run_game(self):
        """Run the game with live display updates"""
        # Initial game setup
        quest_intro = self.game.narrative_engine.generate_quest(difficulty="medium", theme="epic battle")
        self.console.print(f"Quest: {quest_intro}\n")

        # Create initial panel
        panel = Panel("Game starting...", title="Game Status")

        with Live(panel, refresh_per_second=4) as live:
            while not self.game.is_game_over() and self.turn_count < self.max_turns:
                # Clear previous logs
                self.aggregator.clear()

                # Play a turn
                self.game.play_turn()
                self.turn_count += 1

                # Get the latest game events
                combat_log = self.aggregator.get_logs()
                latest_events = "\n".join(combat_log[-5:]) if combat_log else "No events yet..."

                # Update the display with latest events
                panel = Panel(latest_events, title=f"Turn {self.turn_count}")
                live.update(panel)

                # Add random encounters every 3 turns
                if self.turn_count % 3 == 0:
                    encounter = self.game.narrative_engine.generate_random_encounter(
                        party_level=1,
                        environment=self.game.current_location
                    )
                    self.logger.info(f"Encounter: {encounter}")

                time.sleep(1)  # Pause between turns

        # Game conclusion
        if any(player.alive for player in self.game.players):
            conclusion = "Victory! The party emerges triumphant!"
        else:
            conclusion = "Defeat... The party has fallen."

        self.console.print(f"\nGame Over: {conclusion}")

def main():
    try:
        game = DnDGame(model="mistral")
        display = RichGameDisplay(game)
        display.run_game()
    except KeyboardInterrupt:
        print("\nGame interrupted by user.")
    except GameError as ge:
        print(f"\nGame error: {ge}")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        raise

if __name__ == "__main__":
    main()