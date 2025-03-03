#!/usr/bin/env python3
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.layout import Layout
from rich.console import Console
from rich.text import Text
import time

console = Console()

def create_stats_table(turn, total_events):
    """Create a clean stats table"""
    table = Table(box=None)  # Remove table borders for cleaner look
    table.add_column("Stat", style="cyan")
    table.add_column("Value", style="magenta")

    table.add_row("Turn", str(turn))
    table.add_row("Events", str(total_events))
    return table

def create_layout() -> Layout:
    """Create the base layout"""
    layout = Layout()

    # Create the main layout
    layout.split(
        Layout(name="main", ratio=1)
    )

    # Split main into game and stats
    layout["main"].split_column(
        Layout(name="game", ratio=4),
        Layout(name="stats", ratio=1, minimum_size=3)
    )

    return layout

def main():
    # Simulated game events
    game_events = [
        "Hero-1 prepares to attack Monster-1!",
        "Combat Stats: Attacker Hero-1 (Attack=15, HP=34/34) vs Defender Monster-1 (Defense=4, HP=26/26)",
        "Attack Roll: 4 -> Total Damage = 19",
        "Damage Calculation: 19 - 4 = 15; Monster-1 HP: 26 -> 11",
        "Encounter: Mighty blow shatters Giant Ogre!",
        "Monster-2 prepares to attack Hero-2!",
        "Attack Roll: 4 -> Total Damage = 12",
        "Damage Calculation: 12 - 4 = 8; Hero-2 HP: 32 -> 24"
    ]

    turn_count = 0
    total_events = len(game_events)

    # Create and set up the layout
    layout = create_layout()

    # Initial content
    layout["game"].update(
        Panel(
            Text("Game starting...", style="bold white"),
            title="Combat Log",
            border_style="bright_blue",
            padding=(1, 2)
        )
    )

    layout["stats"].update(
        Panel(
            create_stats_table(turn_count, total_events),
            title="Stats",
            border_style="bright_blue",
            padding=(0, 1)
        )
    )

    with Live(layout, refresh_per_second=4, screen=True) as live:
        for event in game_events:
            turn_count += 1

            # Update game panel with new event
            layout["game"].update(
                Panel(
                    Text(event, style="bold yellow"),
                    title="Combat Log",
                    border_style="bright_blue",
                    padding=(1, 2)
                )
            )

            # Update stats panel
            layout["stats"].update(
                Panel(
                    create_stats_table(turn_count, total_events),
                    title="Stats",
                    border_style="bright_blue",
                    padding=(0, 1)
                )
            )

            live.update(layout)
            time.sleep(2)

    console.print("[bold green]Game session complete![/bold green]")

if __name__ == "__main__":
    main()