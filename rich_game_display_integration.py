#!/usr/bin/env python3
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.layout import Layout
from rich.console import Console
from rich.text import Text
from rich.style import Style
import time
import logging
from dnd_game import DnDGame, GameError
from log_aggregator import LogAggregator

console = Console()

class RichGameDisplay:
    def __init__(self):
        self.turn_count = 0
        self.max_turns = 10
        self.combat_log = []
        self.game = None

        # Configure logging for the HUD (clear any existing handlers)
        self.logger = logging.getLogger()
        self.logger.handlers.clear()
        self.logger.setLevel(logging.INFO)

        # Set up our LogAggregator to capture game events
        self.aggregator = LogAggregator()
        self.aggregator.setLevel(logging.INFO)
        self.aggregator.setFormatter(logging.Formatter("%(message)s"))
        self.logger.addHandler(self.aggregator)

    def create_stats_table(self) -> Table:
        """Create a stats table showing game stats."""
        table = Table(box=None, show_header=False, padding=(0, 2))

        # Add columns with consistent styling
        table.add_column("Stat", style="bright_blue")
        table.add_column("Value", style="bright_white")

        # Add game stats
        table.add_row(
            Text("Turn", style="bright_blue"),
            Text(str(self.turn_count), style="bright_yellow")
        )
        table.add_row(
            Text("Max Turns", style="bright_blue"),
            Text(str(self.max_turns), style="bright_yellow")
        )

        # Add player stats if game is initialized
        if self.game:
            for player in self.game.players:
                if player.alive:
                    name = Text(player.name, style="bright_green")
                    hp = Text(
                        f"HP: {player.hp}/{player.max_hp}",
                        style="bright_white"
                    )
                    table.add_row(name, hp)

            # Add enemy stats if any
            for enemy in self.game.enemies:
                if enemy.alive:
                    name = Text(enemy.name, style="bright_red")
                    hp = Text(
                        f"HP: {enemy.hp}/{enemy.max_hp}",
                        style="bright_white"
                    )
                    table.add_row(name, hp)

        return table

    def update_combat_log(self, new_event: str = None):
        """Update the combat log with a new event."""
        if new_event:
            self.combat_log.append(new_event)
        # Keep only the last 10 events
        self.combat_log = self.combat_log[-10:]

    def create_layout(self) -> Layout:
        """Create the base layout."""
        layout = Layout()
        layout.split_column(
            Layout(name="game", ratio=4),
            Layout(name="stats", ratio=1, minimum_size=5)
        )
        return layout

    def render_combat_log(self) -> Panel:
        """Render the combat log panel."""
        # Get the latest logs and add them to our history
        current_logs = self.aggregator.get_logs()
        if current_logs:
            for log in current_logs:
                self.update_combat_log(log)

        # Join logs with proper styling
        log_content = Text()
        if self.combat_log:
            for line in self.combat_log:
                log_content.append(line + "\n", style="bright_white")
        else:
            log_content.append("Waiting for game events...\n", style="bright_yellow")

        return Panel(
            log_content,
            title=Text("GAME STATUS", style="bold bright_red"),
            border_style="bright_blue"
        )

    def update_display(self, live: Live):
        """Update the live display."""
        layout = self.create_layout()

        # Update game panel
        layout["game"].update(self.render_combat_log())

        # Update stats panel
        stats_panel = Panel(
            self.create_stats_table(),
            title=Text("GAME STATS", style="bold bright_cyan"),
            border_style="bright_blue"
        )
        layout["stats"].update(stats_panel)

        live.update(layout)

    def initialize_game(self, live: Live):
        """Initialize the game while showing progress."""
        def show_step(message: str, style: str = "bright_cyan"):
            text = Text("► ", style=style) + Text(message, style=style)
            self.update_combat_log(str(text))
            self.update_display(live)
            time.sleep(1)

        # Initialize game with visual feedback
        show_step("Initializing game system...")

        show_step("Creating game instance...")
        self.game = DnDGame(model="mistral")

        show_step("Loading narrative engine...")

        show_step("Generating quest...")
        quest_intro = self.game.narrative_engine.generate_quest(difficulty="medium", theme="epic battle")
        self.update_combat_log(str(Text("QUEST: ", style="bright_green") + Text(quest_intro, style="bright_white")))
        self.update_display(live)
        time.sleep(2)

        show_step("Preparing combat system...")

        show_step("Game initialization complete!", "bright_green")
        show_step("Starting game...", "bright_yellow")

    def run_game(self):
        """Run the game with live display updates."""
        try:
            layout = self.create_layout()
            with Live(layout, refresh_per_second=4, screen=True) as live:
                self.initialize_game(live)

                while not self.game.is_game_over() and self.turn_count < self.max_turns:
                    self.aggregator.clear()
                    self.game.play_turn()
                    self.turn_count += 1
                    self.update_display(live)

                    if self.turn_count % 3 == 0:
                        encounter = self.game.narrative_engine.generate_random_encounter(
                            party_level=1,
                            environment=self.game.current_location
                        )
                        self.logger.info(Text(f"Encounter: {encounter}", style="bright_red bold"))

                    time.sleep(1)

                # Game conclusion
                conclusion = (
                    Text("The party emerges victorious!", style="bright_green bold")
                    if any(player.alive for player in self.game.players)
                    else Text("The party has fallen...", style="bright_red bold")
                )
                self.update_combat_log(Text("Game Over: ", style="bright_yellow bold") + conclusion)
                self.update_display(live)
                time.sleep(2)

        except Exception as e:
            console.print(Text(f"Error during game: {str(e)}", style="bright_red bold"))
            raise

def main():
    try:
        display = RichGameDisplay()
        display.run_game()
    except KeyboardInterrupt:
        console.print(Text("\nGame interrupted by user.", style="bright_red bold"))
    except GameError as ge:
        console.print(Text(f"\nGame error: {ge}", style="bright_red bold"))
    except Exception as e:
        console.print(Text(f"\nUnexpected error: {e}", style="bright_red bold"))
        raise

if __name__ == "__main__":
    main()