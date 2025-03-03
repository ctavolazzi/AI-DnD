#!/usr/bin/env python3
from rich.live import Live
from rich.panel import Panel
from rich.console import Console
import time

console = Console()

def main():
    # Simulated game events for the HUD
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

    # Use Live to update a panel as our HUD
    with Live(Panel("Game starting...", title="Game Status"), refresh_per_second=4, screen=True) as live:
        for event in game_events:
            # Update the panel with the latest event
            live.update(Panel(event, title="Game Status"))
            time.sleep(2)  # Wait between updates

    console.print("Game readout finished.")

if __name__ == "__main__":
    main()