#!/usr/bin/env python3
import json

# Load game data
with open('examples/web_frontend/data/demo_run.json', 'r') as f:
    data = json.load(f)

html_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI D&D Adventure - Emberpeak Quest</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Courier New', monospace;
            background: linear-gradient(to bottom, #0a0e27 0%, #1a1e3a 100%);
            color: #00ff00;
            padding: 20px;
            line-height: 1.6;
            min-height: 100vh;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: rgba(0, 0, 0, 0.8);
            border: 2px solid #00ff00;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 0 30px rgba(0, 255, 0, 0.3);
        }
        h1 {
            text-align: center;
            color: #00ffff;
            text-shadow: 0 0 10px #00ffff;
            margin-bottom: 20px;
            font-size: 2.5em;
            animation: glow 2s ease-in-out infinite alternate;
        }
        @keyframes glow {
            from { text-shadow: 0 0 5px #00ffff, 0 0 10px #00ffff; }
            to { text-shadow: 0 0 10px #00ffff, 0 0 20px #00ffff, 0 0 30px #00ffff; }
        }
        .quest-box {
            background: rgba(0, 255, 255, 0.1);
            border: 2px solid #00ffff;
            padding: 20px;
            margin: 20px 0;
            border-radius: 10px;
            font-size: 1.2em;
            text-align: center;
        }
        .turn-nav {
            text-align: center;
            margin: 30px 0;
            padding: 20px;
            background: rgba(255, 255, 0, 0.1);
            border: 2px solid #ffff00;
            border-radius: 10px;
        }
        button {
            background: linear-gradient(to bottom, #00ff00, #00cc00);
            color: #000;
            border: 2px solid #00ff00;
            padding: 12px 24px;
            margin: 5px;
            font-family: 'Courier New', monospace;
            font-weight: bold;
            cursor: pointer;
            border-radius: 5px;
            font-size: 16px;
            transition: all 0.3s;
        }
        button:hover {
            background: linear-gradient(to bottom, #00ffff, #00cccc);
            border-color: #00ffff;
            box-shadow: 0 0 15px #00ffff;
            transform: translateY(-2px);
        }
        button:active {
            transform: translateY(0);
        }
        button:disabled {
            background: #555;
            color: #888;
            cursor: not-allowed;
            border-color: #555;
        }
        .characters {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .char-card {
            background: rgba(0, 255, 0, 0.1);
            border: 2px solid #00ff00;
            padding: 20px;
            border-radius: 10px;
            transition: all 0.3s;
        }
        .char-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 5px 20px rgba(0, 255, 0, 0.5);
        }
        .char-card.enemy {
            background: rgba(255, 0, 0, 0.1);
            border-color: #ff0000;
        }
        .char-card.enemy:hover {
            box-shadow: 0 5px 20px rgba(255, 0, 0, 0.5);
        }
        .char-card h4 {
            color: #00ffff;
            margin-bottom: 10px;
            font-size: 1.3em;
        }
        .hp-bar {
            background: #222;
            height: 25px;
            border-radius: 12px;
            overflow: hidden;
            margin: 10px 0;
            border: 2px solid #444;
        }
        .hp-fill {
            height: 100%;
            background: linear-gradient(to right, #00ff00, #00aa00);
            transition: width 0.5s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 13px;
            color: #000;
            font-weight: bold;
        }
        .hp-fill.low {
            background: linear-gradient(to right, #ffaa00, #ff6600);
        }
        .hp-fill.critical {
            background: linear-gradient(to right, #ff0000, #aa0000);
            animation: pulse 1s infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
        }
        .events {
            background: rgba(0, 0, 0, 0.6);
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid #00ff00;
            max-height: 500px;
            overflow-y: auto;
            margin: 20px 0;
        }
        .events::-webkit-scrollbar {
            width: 10px;
        }
        .events::-webkit-scrollbar-track {
            background: #111;
        }
        .events::-webkit-scrollbar-thumb {
            background: #00ff00;
            border-radius: 5px;
        }
        .event-item {
            margin: 10px 0;
            padding: 10px;
            background: rgba(0, 255, 0, 0.05);
            border-radius: 5px;
            border-left: 2px solid #00ff00;
        }
        .status {
            color: #888;
            font-size: 14px;
        }
        .alive { color: #00ff00; font-weight: bold; }
        .dead { color: #ff0000; font-weight: bold; }
        .turn-counter {
            font-size: 28px;
            color: #ffff00;
            margin: 0 20px;
            font-weight: bold;
        }
        h2 {
            color: #ffff00;
            border-bottom: 2px solid #ffff00;
            padding-bottom: 10px;
            margin: 30px 0 15px 0;
            text-shadow: 0 0 5px #ffff00;
        }
        .victory-banner {
            display: none;
            background: linear-gradient(45deg, #00ff00, #00ffff);
            color: #000;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            font-size: 1.5em;
            font-weight: bold;
            margin: 20px 0;
            animation: rainbow 3s infinite;
        }
        @keyframes rainbow {
            0% { filter: hue-rotate(0deg); }
            100% { filter: hue-rotate(360deg); }
        }
        .instructions {
            background: rgba(255, 255, 0, 0.1);
            border: 1px solid #ffff00;
            padding: 15px;
            margin: 20px 0;
            border-radius: 5px;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>⚔️ AI D&D Adventure ⚔️</h1>

        <div class="instructions">
            <strong>🎮 Controls:</strong> Use buttons below or keyboard: ← → (prev/next), Space (auto-play), Home/End (first/last turn)
        </div>

        <div class="quest-box">
            <strong>📜 QUEST:</strong><br>
            {quest_hook}
        </div>

        <div class="turn-nav">
            <button id="prevBtn" onclick="previousTurn()">⏮ Previous</button>
            <span class="turn-counter">Turn <span id="turnNum">0</span> / {max_turn}</span>
            <button id="nextBtn" onclick="nextTurn()">Next ⏭</button>
            <br><br>
            <button onclick="currentTurn = 0; displayTurn()">⏪ First Turn</button>
            <button onclick="playAuto()" id="playBtn">▶️ Auto Play</button>
            <button onclick="currentTurn = gameData.frames.length - 1; displayTurn()">Last Turn ⏩</button>
        </div>

        <div id="victory" class="victory-banner">
            🎉 VICTORY! All enemies defeated! 🎉
        </div>

        <div id="turn-content">
            <h2>⚔️ Party Members</h2>
            <div id="players" class="characters"></div>

            <h2>👹 Enemies</h2>
            <div id="enemies" class="characters"></div>

            <h2>📖 Events This Turn</h2>
            <div id="events" class="events"></div>
        </div>
    </div>

    <script>
        const gameData = {game_data};
        let currentTurn = 0;
        let autoPlayInterval = null;

        function displayTurn() {{
            if (!gameData || !gameData.frames[currentTurn]) return;

            const frame = gameData.frames[currentTurn];

            document.getElementById('turnNum').textContent = currentTurn;
            document.getElementById('prevBtn').disabled = currentTurn === 0;
            document.getElementById('nextBtn').disabled = currentTurn === gameData.frames.length - 1;

            const allEnemiesDead = frame.enemies.every(e => !e.alive);
            document.getElementById('victory').style.display = allEnemiesDead ? 'block' : 'none';

            displayCharacters('players', frame.players, false);
            displayCharacters('enemies', frame.enemies, true);
            displayEvents('events', frame.new_events);
        }}

        function displayCharacters(containerId, characters, isEnemy) {{
            const container = document.getElementById(containerId);
            container.innerHTML = '';

            characters.forEach(char => {{
                const card = document.createElement('div');
                card.className = 'char-card' + (isEnemy ? ' enemy' : '');

                const hpPercent = (char.hp / char.max_hp) * 100;
                let hpClass = '';
                if (hpPercent < 25) hpClass = 'critical';
                else if (hpPercent < 50) hpClass = 'low';

                const status = char.alive ?
                    '<span class="alive">✓ ALIVE</span>' :
                    '<span class="dead">✗ DEFEATED</span>';

                card.innerHTML = `
                    <h4>${{char.name}}</h4>
                    <div class="status">${{char.char_class}} | ${{status}}</div>
                    <div class="hp-bar">
                        <div class="hp-fill ${{hpClass}}" style="width: ${{hpPercent}}%">
                            ${{char.hp}} / ${{char.max_hp}} HP
                        </div>
                    </div>
                `;

                container.appendChild(card);
            }});
        }}

        function displayEvents(containerId, events) {{
            const container = document.getElementById(containerId);
            container.innerHTML = '';

            if (!events || events.length === 0) {{
                container.innerHTML = '<div class="event-item">No events this turn.</div>';
                return;
            }}

            events.forEach(event => {{
                const eventDiv = document.createElement('div');
                eventDiv.className = 'event-item';
                eventDiv.textContent = event;
                container.appendChild(eventDiv);
            }});
        }}

        function nextTurn() {{
            if (currentTurn < gameData.frames.length - 1) {{
                currentTurn++;
                displayTurn();
            }}
        }}

        function previousTurn() {{
            if (currentTurn > 0) {{
                currentTurn--;
                displayTurn();
            }}
        }}

        function playAuto() {{
            const btn = document.getElementById('playBtn');
            if (autoPlayInterval) {{
                clearInterval(autoPlayInterval);
                autoPlayInterval = null;
                btn.textContent = '▶️ Auto Play';
            }} else {{
                btn.textContent = '⏸️ Pause';
                autoPlayInterval = setInterval(() => {{
                    if (currentTurn < gameData.frames.length - 1) {{
                        nextTurn();
                    }} else {{
                        clearInterval(autoPlayInterval);
                        autoPlayInterval = null;
                        btn.textContent = '▶️ Auto Play';
                    }}
                }}, 2000);
            }}
        }}

        document.addEventListener('keydown', (e) => {{
            if (e.key === 'ArrowRight') nextTurn();
            else if (e.key === 'ArrowLeft') previousTurn();
            else if (e.key === 'Home') {{ currentTurn = 0; displayTurn(); }}
            else if (e.key === 'End') {{ currentTurn = gameData.frames.length - 1; displayTurn(); }}
            else if (e.key === ' ') {{ e.preventDefault(); playAuto(); }}
        }});

        displayTurn();
    </script>
</body>
</html>'''

# Fill in the template
html = html_template.replace('{quest_hook}', data['quest_hook'])
html = html.replace('{max_turn}', str(len(data['frames']) - 1))
html = html.replace('{game_data}', json.dumps(data))

# Write the file
with open('dnd-adventure-standalone.html', 'w') as f:
    f.write(html)

print("✅ Created: dnd-adventure-standalone.html")
print("📁 Location: /home/user/AI-DnD/dnd-adventure-standalone.html")
print("\n🎮 Download this file and open it in your browser!")
