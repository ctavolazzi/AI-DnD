AI-DnD

Description

AI-DnD is an autonomous, AI-driven D&D campaign simulator that dynamically generates and evolves its own worlds, histories, and characters. This isn’t just a text-based RPG—it’s a self-running, self-documenting AI Dungeon Master that creates, plays, and archives full campaigns without human input.

Key Features
	•	Autonomous World-Building – AI characters make decisions, track history, and generate lore in real time.
	•	Obsidian Integration – All campaign events, journals, and lore are automatically saved as Markdown files for easy visualization and review.
	•	Sentinel Class – A monitoring system that ensures narrative and game consistency, acting as a meta-DM assistant.
	•	Modular Architecture – Flexible and expandable, allowing for custom modules and mechanics.
	•	Local-First AI Execution – Runs offline for privacy and full control, using AI-powered logic to drive campaigns.

Table of Contents
	•	Installation
	•	Usage
	•	Modules
	•	Configuration
	•	Contributing
	•	License
	•	Contact
	•	Acknowledgments

Installation

To set up AI-DnD on your local machine:

git clone https://github.com/ctavolazzi/AI-DnD.git
cd AI-DnD
pip install -r requirements.txt

Obsidian Setup
	1.	Download Obsidian (if you haven’t already).
	2.	Configure AI-DnD to save logs to your desired Obsidian vault.
	3.	Open Obsidian and navigate the campaign as it unfolds.

Usage

Run the AI-driven D&D campaign simulator:

python main.py

	•	Choose a pre-made campaign or create your own.
	•	Watch the AI play out adventures, keep journals, and make decisions.
	•	Open Obsidian to see the real-time campaign log unfold.

Modules

Core Components
	•	character.py – AI-driven player/NPC management, including attributes, actions, and memory.
	•	combat_module.py – Handles D&D battle mechanics.
	•	dungeon_master.py – The AI DM that generates and narrates the world.
	•	game_manager.py – Oversees overall game progression and state.
	•	sentinel.py – Monitors game consistency, flagging discrepancies and ensuring smooth AI interactions.

Obsidian Integration
	•	AI-DnD automatically generates Markdown files to document campaign history.
	•	Players (or the AI itself) can review and expand on these records in Obsidian.

Configuration

Modify settings in config.json to adjust:
	•	Campaign difficulty
	•	AI randomness & decision weight
	•	Journal update frequency
	•	Obsidian vault path

Contributing

Want to contribute? Fork the repo and submit a pull request!

License

MIT License

Contact
	•	GitHub: @ctavolazzi
	•	Project Updates: Coming soon

Acknowledgments

Shoutout to AI model devs, open-source contributors, and tabletop RPG enthusiasts who inspired this project.