# AI-DnD  

## Description  
**AI-DnD** is an **autonomous, AI-driven D&D campaign simulator** that dynamically generates and evolves its own worlds, histories, and characters. This isn’t just a text-based RPG—it’s a **self-running, self-documenting** AI Dungeon Master that **creates, plays, and archives** full campaigns **without human input**.  

### Key Features  
- **Autonomous World-Building** – AI characters make decisions, track history, and generate lore in real time.  
- **Obsidian Integration** – All campaign events, journals, and lore are automatically saved as Markdown files for easy visualization and review.  
- **Sentinel Class** – A monitoring system that ensures narrative and game consistency, acting as a **meta-DM assistant**.  
- **Modular Architecture** – Flexible and expandable, allowing for custom modules and mechanics.  
- **Local-First AI Execution** – Runs offline for privacy and full control, using AI-powered logic to drive campaigns.  

## Table of Contents  
- [Installation](#installation)  
- [Usage](#usage)  
- [Modules](#modules)  
- [Configuration](#configuration)  
- [Contributing](#contributing)  
- [License](#license)  
- [Contact](#contact)  
- [Acknowledgments](#acknowledgments)  

## Installation  
To set up **AI-DnD** on your local machine:  
```bash
git clone https://github.com/ctavolazzi/AI-DnD.git
cd AI-DnD
pip install -r requirements.txt
```

## Obsidian Setup  
AI-DnD is designed to integrate seamlessly with **Obsidian**, allowing it to generate Markdown-based campaign logs, character journals, and world-building documents in real time.  

### Steps to Set Up Obsidian Integration:  
1. **Download and Install Obsidian**  
   - If you haven't already, download Obsidian from [obsidian.md](https://obsidian.md/) and install it.  

2. **Choose or Create an Obsidian Vault**  
   - Open Obsidian and create a new vault (or use an existing one) where AI-DnD will store campaign logs.  

3. **Configure AI-DnD to Save Logs to Obsidian**  
   - In the AI-DnD `config.json` file, set the `obsidian_vault_path` to your chosen Obsidian vault directory.  

4. **Run AI-DnD and Verify Logs**  
   - Start a new AI-driven campaign and check your Obsidian vault.  
   - AI-DnD will generate campaign logs, character journals, and event summaries in **Markdown format**, making them easy to read and edit within Obsidian.  

5. **Navigate the Campaign in Obsidian**  
   - Open the generated Markdown files in Obsidian to explore the AI-generated world, review past events, and track character development over time.  

## Usage
To start AI-DnD:

1. Launch the program from the command line or terminal.
2. Select a pre-made campaign or create your own.
3. Observe the AI-driven adventure unfold.
4. Open Obsidian to view real-time campaign logs.

For additional commands and gameplay mechanics, refer to the user documentation.

### Want a quick peek?
If you just want to see the core combat and logging loop in action without
connecting to Ollama, run the lightweight showcase demo:

```bash
cd examples/simple_demo
python demo_app.py --turns 4
```

The demo swaps in a deterministic narrative engine so you can visualize the
Rich HUD and battle flow immediately.

## Modules  
### Core Components  
- **Character Management** – AI-driven player/NPC attributes, actions, and memory.  
- **Combat System** – Simulated D&D battle mechanics with turn-based AI decision-making.  
- **Dungeon Master AI** – Generates and narrates the world dynamically.  
- **Game State Manager** – Controls the flow of time, events, and interactions.  
- **Sentinel System** – Monitors game consistency and flags discrepancies.  

### Obsidian Integration  
- AI-DnD automatically generates Markdown files to **document campaign history**.  
- Players (or the AI itself) can review and expand on these records in Obsidian.  

## Configuration  
Modify settings in the configuration file to customize:  
- Campaign difficulty  
- AI randomness & decision weight  
- Journal update frequency  
- Obsidian vault path  

## Contributing  
Contributions are welcome! To contribute:  

1. Fork the repository.  
2. Create a new branch for your feature or bug fix.  
3. Submit a pull request with a clear description of changes.  

## License  
This project is licensed under the **MIT License**. See the `LICENSE` file for details.  

## Acknowledgments  
Special thanks to:  
- AI model developers for advancing open-source storytelling.  
- The D&D community for inspiring rich, dynamic worlds.  
- Open-source contributors helping refine AI-DnD.  
