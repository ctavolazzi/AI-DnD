#!/usr/bin/env python3
"""
DnD Narrative Theater Server
Orchestrates narrative generation and manages game state for the visual narrative experience.
Port: 5002
"""

import os
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
import random
from datetime import datetime

from dnd_game import DnDGame, Character
from narrative_engine import NarrativeEngine, create_narrative_engine

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for browser access

# Global game state (in-memory for MVP)
game_sessions = {}

class NarrativeSession:
    """Manages a single narrative theater session."""

    def __init__(self, session_id: str, model: str = "gemini"):
        self.session_id = session_id
        self.game = DnDGame(auto_create_characters=True, model=model)

        # Use Gemini by default, Ollama as fallback
        self.narrative_engine = create_narrative_engine(model)

        self.turn_count = 0
        self.scenes = []
        self.character_images = {}  # Cache character images
        self.created_at = datetime.now().isoformat()

        logger.info(f"Created new narrative session: {session_id} with {model} engine")

    def start_adventure(self, theme="epic adventure"):
        """Initialize the adventure with characters and quest."""
        # Generate quest with custom theme if provided
        quest = self.narrative_engine.generate_quest(difficulty="medium", theme=theme)

        # Generate character introductions
        character_data = []
        for player in self.game.players:
            intro = self.narrative_engine.handle_player_action(
                player.name,
                "enters the scene",
                f"A {player.char_class} ready for adventure"
            )

            character_data.append({
                "name": player.name,
                "class": player.char_class,
                "hp": player.hp,
                "max_hp": player.max_hp,
                "attack": player.attack,
                "defense": player.defense,
                "alive": player.alive,
                "intro": intro,
                "abilities": list(player.abilities.keys()) if hasattr(player, 'abilities') else []
            })

        # Create first scene
        first_scene = self.narrative_engine.describe_scene(
            self.game.current_location,
            [c.name for c in self.game.players]
        )

        initial_scene = {
            "scene_id": 0,
            "type": "introduction",
            "narrative": f"{quest}\n\n{first_scene}",
            "location": self.game.current_location,
            "characters": [c.name for c in self.game.players],
            "auto_image": True,
            "image_generated": False,
            "timestamp": datetime.now().isoformat()
        }

        self.scenes.append(initial_scene)

        return {
            "session_id": self.session_id,
            "characters": character_data,
            "quest": quest,
            "first_scene": initial_scene,
            "location": self.game.current_location
        }

    def generate_next_scene(self):
        """Generate the next scene in the narrative."""
        self.turn_count += 1

        # Determine scene type
        scene_type = self._determine_scene_type()

        # Generate scene based on type
        if scene_type == "combat":
            scene_data = self._generate_combat_scene()
        elif scene_type == "exploration":
            scene_data = self._generate_exploration_scene()
        elif scene_type == "choice":
            scene_data = self._generate_choice_scene()
        elif scene_type == "conclusion":
            scene_data = self._generate_conclusion_scene()
        else:
            scene_data = self._generate_exploration_scene()

        # Add to scenes list
        scene_data["scene_id"] = len(self.scenes)
        scene_data["timestamp"] = datetime.now().isoformat()
        self.scenes.append(scene_data)

        # Get current character states
        character_states = self._get_character_states()

        return {
            "scene": scene_data,
            "character_states": character_states,
            "turn_count": self.turn_count,
            "location": self.game.current_location
        }

    def _determine_scene_type(self):
        """Determine what type of scene should come next."""
        # Check if game should end
        if self.turn_count >= 15 or not any(p.alive for p in self.game.players):
            return "conclusion"

        # Combat every 3-4 turns
        if self.turn_count % 4 == 0 and any(e.alive for e in self.game.enemies):
            return "combat"

        # Player choice every 2 turns
        if self.turn_count % 2 == 0:
            return "choice"

        # Default to exploration
        return "exploration"

    def _generate_combat_scene(self):
        """Generate a combat encounter scene."""
        # Ensure we have enemies
        if not any(e.alive for e in self.game.enemies):
            # Create new enemies
            self.game.enemies = [
                Character(f"Enemy {i+1}", random.choice(["Goblin", "Orc", "Skeleton", "Bandit"]))
                for i in range(random.randint(1, 3))
            ]
            for enemy in self.game.enemies:
                enemy.team = "enemies"

        # Generate encounter description
        alive_enemies = [e for e in self.game.enemies if e.alive]
        encounter_desc = self.narrative_engine.generate_random_encounter(
            party_level=1,
            environment=self.game.current_location
        )

        # Process one round of combat
        combat_log = []
        all_combatants = self.game.players + self.game.enemies
        random.shuffle(all_combatants)

        for char in all_combatants:
            if not char.alive:
                continue

            target = self.game._select_attack_target(char)
            if target:
                old_hp = target.hp
                char.attack_target(target)
                damage = old_hp - target.hp

                if damage > 0:
                    action_desc = self.narrative_engine.describe_combat(
                        char.name,
                        target.name,
                        "attacks",
                        damage
                    )
                    combat_log.append(action_desc)

        narrative = f"{encounter_desc}\n\n" + "\n".join(combat_log)

        return {
            "type": "combat",
            "narrative": narrative,
            "location": self.game.current_location,
            "characters": [c.name for c in all_combatants if c.alive],
            "enemies": [e.name for e in alive_enemies],
            "auto_image": True,
            "image_generated": False
        }

    def _generate_exploration_scene(self):
        """Generate an exploration/discovery scene."""
        # Pick a random player
        player = random.choice([p for p in self.game.players if p.alive])

        # Generate exploration action
        actions = [
            "searches for hidden treasures",
            "examines ancient ruins",
            "discovers a mysterious artifact",
            "finds a secret passage",
            "encounters a friendly traveler",
            "notices something unusual"
        ]
        action = random.choice(actions)

        narrative = self.narrative_engine.handle_player_action(
            player.name,
            action,
            f"Exploring {self.game.current_location}"
        )

        return {
            "type": "exploration",
            "narrative": narrative,
            "location": self.game.current_location,
            "characters": [player.name],
            "auto_image": False,
            "image_generated": False
        }

    def _generate_choice_scene(self):
        """Generate a scene with player choices."""
        player = random.choice([p for p in self.game.players if p.alive])

        # Generate choices
        choices = [
            "Press forward into the unknown",
            "Search the area carefully",
            "Rest and prepare for what's ahead",
            "Consult with the party"
        ]

        choice_text = f"\n\nChoices for {player.name}:\n"
        for i, choice in enumerate(choices, 1):
            choice_text += f"{i}. {choice}\n"

        # Auto-select a choice
        selected = random.choice(choices)
        outcome = self.narrative_engine.handle_player_action(
            player.name,
            selected.lower(),
            f"Making a decision in {self.game.current_location}"
        )

        narrative = f"{player.name} must decide what to do next.{choice_text}\n{player.name} chooses: {selected}\n\n{outcome}"

        return {
            "type": "choice",
            "narrative": narrative,
            "location": self.game.current_location,
            "characters": [player.name],
            "auto_image": False,
            "image_generated": False
        }

    def _generate_conclusion_scene(self):
        """Generate the adventure conclusion."""
        # Check victory condition
        players_alive = any(p.alive for p in self.game.players)

        if players_alive:
            conclusion = self.narrative_engine.generate_quest(
                difficulty="easy",
                theme="victorious conclusion"
            )
            narrative = f"Victory! {conclusion}"
        else:
            narrative = "The party has fallen... Their story ends here, but legends will be told of their bravery."

        return {
            "type": "conclusion",
            "narrative": narrative,
            "location": self.game.current_location,
            "characters": [c.name for c in self.game.players],
            "auto_image": True,
            "image_generated": False
        }

    def _get_character_states(self):
        """Get current state of all characters."""
        return [
            {
                "name": p.name,
                "class": p.char_class,
                "hp": p.hp,
                "max_hp": p.max_hp,
                "alive": p.alive,
                "status_effects": p.status_effects if hasattr(p, 'status_effects') else []
            }
            for p in self.game.players
        ]


# =============================================================================
# API ENDPOINTS
# =============================================================================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "DnD Narrative Theater Server",
        "port": 5002,
        "active_sessions": len(game_sessions)
    })


@app.route('/start-adventure', methods=['POST'])
def start_adventure():
    """
    Initialize a new adventure session.

    Request body (optional):
    {
        "session_id": "custom_id",  // Optional custom session ID
        "model": "mistral"          // Optional LLM model
    }

    Returns:
    {
        "session_id": "...",
        "characters": [...],
        "quest": "...",
        "first_scene": {...},
        "location": "..."
    }
    """
    try:
        data = request.json or {}

        # Generate or use provided session ID
        session_id = data.get('session_id', f"session_{datetime.now().strftime('%Y%m%d%H%M%S')}_{random.randint(1000, 9999)}")
        model = data.get('model', 'gemini')  # Default to Gemini
        story_prompt = data.get('story_prompt', 'epic adventure')  # Get custom story theme

        # Create new session
        session = NarrativeSession(session_id, model=model)
        game_sessions[session_id] = session

        # Start the adventure with custom theme
        logger.info(f"Starting adventure with theme: {story_prompt}")
        result = session.start_adventure(theme=story_prompt)

        logger.info(f"Started adventure for session: {session_id}")

        return jsonify({
            "success": True,
            **result
        })

    except Exception as e:
        logger.error(f"Error starting adventure: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/next-scene', methods=['POST'])
def next_scene():
    """
    Generate the next scene in the narrative.

    Request body:
    {
        "session_id": "...",
        "player_action": "..." (optional)
    }

    Returns:
    {
        "scene": {...},
        "character_states": [...],
        "turn_count": 1,
        "location": "...",
        "narrative": "..." (extracted for convenience)
    }
    """
    try:
        data = request.json
        session_id = data.get('session_id')
        player_action = data.get('player_action')

        if not session_id or session_id not in game_sessions:
            return jsonify({
                "success": False,
                "error": "Invalid or missing session_id"
            }), 400

        session = game_sessions[session_id]
        result = session.generate_next_scene()

        logger.info(f"Generated scene {result['scene']['scene_id']} for session: {session_id}")

        return jsonify({
            "success": True,
            "narrative": result['scene']['narrative'],
            **result
        })

    except Exception as e:
        logger.error(f"Error generating next scene: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/generate-chapter', methods=['POST'])
def generate_chapter():
    """
    Generate a story chapter with intelligent scene extraction.
    Story-first approach: Generate text, then extract scenes for images.

    Request body:
    {
        "session_id": "...",
        "player_input": "What the player does/says",
        "story_context": ["previous chapter texts..."] (optional)
    }

    Returns:
    {
        "success": true,
        "chapter": {
            "title": "Chapter title",
            "content": "Full chapter text",
            "number": 1
        },
        "scenes": [
            {
                "description": "Scene description for image generation",
                "position": "start|middle|end",
                "prompt": "Optimized image prompt"
            }
        ],
        "character_states": [...],
        "location": "..."
    }
    """
    try:
        data = request.json
        session_id = data.get('session_id')
        player_input = data.get('player_input', 'continue the adventure')
        story_context = data.get('story_context', [])

        if not session_id or session_id not in game_sessions:
            return jsonify({
                "success": False,
                "error": "Invalid or missing session_id"
            }), 400

        session = game_sessions[session_id]

        # Generate the next scene (this creates the story content)
        result = session.generate_next_scene()
        narrative_text = result['scene']['narrative']

        # Extract key scenes from the narrative for image generation
        scenes = _extract_scenes_for_images(narrative_text, result['scene']['type'])

        # Create chapter data
        chapter = {
            "title": _generate_chapter_title(result['scene']['type'], session.turn_count),
            "content": narrative_text,
            "number": session.turn_count,
            "type": result['scene']['type']
        }

        logger.info(f"Generated chapter {session.turn_count} with {len(scenes)} scenes for session: {session_id}")

        return jsonify({
            "success": True,
            "chapter": chapter,
            "scenes": scenes,
            "character_states": result['character_states'],
            "location": result['location'],
            "turn_count": result['turn_count']
        })

    except Exception as e:
        logger.error(f"Error generating chapter: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


def _extract_scenes_for_images(narrative_text, scene_type):
    """
    Extract key visual scenes from narrative text for image generation.
    Returns list of scene descriptions optimized for image prompts.
    """
    scenes = []

    # Split narrative into sentences
    sentences = [s.strip() for s in narrative_text.split('.') if len(s.strip()) > 20]

    # Strategy: Extract visually descriptive sentences
    visual_keywords = [
        'see', 'sees', 'appear', 'appears', 'stood', 'stands', 'entered', 'enters',
        'emerged', 'emerges', 'raised', 'raises', 'wielding', 'holding', 'wearing',
        'dark', 'bright', 'glowing', 'ancient', 'massive', 'towering', 'surrounded'
    ]

    for i, sentence in enumerate(sentences):
        # Check if sentence contains visual keywords
        if any(keyword in sentence.lower() for keyword in visual_keywords):
            # Determine position in narrative
            if i < len(sentences) * 0.3:
                position = "start"
            elif i > len(sentences) * 0.7:
                position = "end"
            else:
                position = "middle"

            # Create image prompt
            prompt = f"Fantasy D&D scene: {sentence}. {scene_type} scene, detailed, cinematic"

            scenes.append({
                "description": sentence,
                "position": position,
                "prompt": prompt
            })

    # If no visual scenes found, create one from first meaningful sentence
    if not scenes and sentences:
        scenes.append({
            "description": sentences[0],
            "position": "start",
            "prompt": f"Fantasy D&D {scene_type} scene: {sentences[0]}, detailed, cinematic"
        })

    # Limit to 2-3 scenes per chapter to avoid overload
    return scenes[:3]


def _generate_chapter_title(scene_type, turn_count):
    """Generate an appropriate chapter title based on scene type."""
    titles = {
        "introduction": "The Journey Begins",
        "combat": f"Battle #{turn_count}",
        "exploration": f"Discovery in the Unknown",
        "choice": f"A Crossroads",
        "conclusion": "The Final Chapter"
    }
    return titles.get(scene_type, f"Chapter {turn_count}")


@app.route('/generate-scene-image', methods=['POST'])
def generate_scene_image():
    """
    Generate an image for a specific scene.

    Request body:
    {
        "session_id": "...",
        "scene_id": 0,
        "scene_description": "...",
        "scene_type": "character_intro|combat|exploration|..."
    }

    Returns:
    {
        "success": true,
        "image": "base64_image_data",
        "image_type": "sprite|enhanced"
    }
    """
    try:
        import requests

        data = request.json
        session_id = data.get('session_id')
        scene_description = data.get('scene_description', '')
        scene_type = data.get('scene_type', 'exploration')
        format_type = data.get('format', 'square')  # 'landscape' or 'square'
        width = data.get('width', 64)
        height = data.get('height', 64)

        # If no scene description provided, try to get from session
        if not scene_description and session_id and session_id in game_sessions:
            session = game_sessions[session_id]
            # NarrativeSession is an object, not a dict
            if hasattr(session, 'scenes') and session.scenes:
                latest_scene = session.scenes[-1]
                if 'narrative' in latest_scene:
                    scene_description = latest_scene['narrative'][:200]  # First 200 chars
            if not scene_description and hasattr(session, 'game') and hasattr(session.game, 'quest'):
                scene_description = f"fantasy tavern scene, {session.game.quest[:100]}"

        # Fallback description
        if not scene_description:
            scene_description = "epic fantasy adventure scene, medieval tavern, heroes gathering"

        # For MVP, we'll call the existing servers
        # Character intros get pixel art sprites
        if scene_type in ['introduction', 'character_intro']:
            # Call PixelLab for character sprite
            response = requests.post(
                'http://localhost:5001/generate-sprite',
                json={
                    "prompt": scene_description,
                    "width": 128,
                    "height": 128,
                    "no_background": True
                },
                timeout=60
            )

            if response.ok:
                result = response.json()
                return jsonify({
                    "success": True,
                    "image": result.get('image'),
                    "image_type": "sprite"
                })

        # Combat and major scenes get enhanced images
        elif scene_type in ['combat', 'conclusion']:
            # Call Nano Banana for enhanced scene
            response = requests.post(
                'http://localhost:5000/generate-scene',
                json={
                    "description": scene_description,
                    "style": "fantasy",
                    "aspect_ratio": "16:9"
                },
                timeout=60
            )

            if response.ok:
                result = response.json()
                return jsonify({
                    "success": True,
                    "image": result.get('image'),
                    "image_type": "enhanced"
                })

        # Default: Use Nano Banana for landscape scenes
        if format_type == 'landscape':
            response = requests.post(
                'http://localhost:5000/generate',
                json={
                    "prompt": scene_description,
                    "aspect_ratio": "16:9"  # Landscape format
                },
                timeout=60
            )
        else:
            # Square format - use PixelLab
            response = requests.post(
                'http://localhost:5001/generate-sprite',
                json={
                    "prompt": scene_description,
                    "width": width,
                    "height": height,
                    "no_background": True
            },
            timeout=60
        )

        if response.ok:
            result = response.json()
            return jsonify({
                "success": True,
                "image": result.get('image'),
                "image_type": "sprite"
            })

        return jsonify({
            "success": False,
            "error": "Image generation failed"
        }), 500

    except Exception as e:
        logger.error(f"Error generating scene image: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/ai-decision', methods=['POST'])
def ai_decision():
    """
    Generate AI-powered decision analysis for DM choices.

    Request body:
    {
        "session_id": "...",
        "situation": "Current situation description",
        "options": ["Option 1", "Option 2", "Option 3"]
    }

    Returns:
    {
        "success": true,
        "analysis": "...",
        "recommendation": "...",
        "reasoning": "..."
    }
    """
    try:
        data = request.json
        session_id = data.get('session_id')
        situation = data.get('situation')
        options = data.get('options', [])

        if not session_id or session_id not in game_sessions:
            return jsonify({
                "success": False,
                "error": "Invalid or missing session_id"
            }), 400

        if not situation or not options:
            return jsonify({
                "success": False,
                "error": "Missing situation or options"
            }), 400

        session = game_sessions[session_id]
        decision = session.narrative_engine.generate_decision_matrix(situation, options)

        logger.info(f"Generated AI decision for session: {session_id}")

        return jsonify({
            "success": True,
            **decision
        })

    except Exception as e:
        logger.error(f"Error generating AI decision: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/story-branches', methods=['POST'])
def story_branches():
    """
    Generate intelligent story branches based on player choices.

    Request body:
    {
        "session_id": "...",
        "current_situation": "Current story situation",
        "player_choices": ["Choice 1", "Choice 2", "Choice 3"]
    }

    Returns:
    {
        "success": true,
        "branch_analysis": "...",
        "choices": [...],
        "generated_at": timestamp
    }
    """
    try:
        data = request.json
        session_id = data.get('session_id')
        current_situation = data.get('current_situation')
        player_choices = data.get('player_choices', [])

        if not session_id or session_id not in game_sessions:
            return jsonify({
                "success": False,
                "error": "Invalid or missing session_id"
            }), 400

        if not current_situation or not player_choices:
            return jsonify({
                "success": False,
                "error": "Missing current_situation or player_choices"
            }), 400

        session = game_sessions[session_id]
        branches = session.narrative_engine.generate_story_branches(current_situation, player_choices)

        logger.info(f"Generated story branches for session: {session_id}")

        return jsonify({
            "success": True,
            **branches
        })

    except Exception as e:
        logger.error(f"Error generating story branches: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/npc-reaction', methods=['POST'])
def npc_reaction():
    """
    Generate intelligent NPC reactions based on personality and situation.

    Request body:
    {
        "session_id": "...",
        "npc_name": "NPC Name",
        "npc_personality": "Personality traits",
        "player_action": "Action taken by player",
        "context": "Current situation context"
    }

    Returns:
    {
        "success": true,
        "reaction": "...",
        "npc_name": "...",
        "generated_at": timestamp
    }
    """
    try:
        data = request.json
        session_id = data.get('session_id')
        npc_name = data.get('npc_name')
        npc_personality = data.get('npc_personality')
        player_action = data.get('player_action')
        context = data.get('context')

        if not session_id or session_id not in game_sessions:
            return jsonify({
                "success": False,
                "error": "Invalid or missing session_id"
            }), 400

        if not all([npc_name, npc_personality, player_action, context]):
            return jsonify({
                "success": False,
                "error": "Missing required fields: npc_name, npc_personality, player_action, context"
            }), 400

        session = game_sessions[session_id]
        reaction = session.narrative_engine.generate_npc_reaction(
            npc_name, npc_personality, player_action, context
        )

        logger.info(f"Generated NPC reaction for {npc_name} in session: {session_id}")

        return jsonify({
            "success": True,
            **reaction
        })

    except Exception as e:
        logger.error(f"Error generating NPC reaction: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/adapt-narrative', methods=['POST'])
def adapt_narrative():
    """
    Adapt narrative based on campaign progression and player choices.

    Request body:
    {
        "session_id": "...",
        "campaign_history": "Summary of campaign so far",
        "recent_events": "Recent story events"
    }

    Returns:
    {
        "success": true,
        "adaptation_suggestions": "...",
        "generated_at": timestamp
    }
    """
    try:
        data = request.json
        session_id = data.get('session_id')
        campaign_history = data.get('campaign_history')
        recent_events = data.get('recent_events')

        if not session_id or session_id not in game_sessions:
            return jsonify({
                "success": False,
                "error": "Invalid or missing session_id"
            }), 400

        if not campaign_history or not recent_events:
            return jsonify({
                "success": False,
                "error": "Missing campaign_history or recent_events"
            }), 400

        session = game_sessions[session_id]
        adaptation = session.narrative_engine.adapt_narrative(campaign_history, recent_events)

        logger.info(f"Generated narrative adaptation for session: {session_id}")

        return jsonify({
            "success": True,
            **adaptation
        })

    except Exception as e:
        logger.error(f"Error adapting narrative: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/game-state', methods=['GET'])
def get_game_state():
    """
    Get current game state for a session.

    Query params:
    ?session_id=...

    Returns:
    {
        "session_id": "...",
        "turn_count": 1,
        "location": "...",
        "characters": [...],
        "scenes": [...]
    }
    """
    try:
        session_id = request.args.get('session_id')

        if not session_id or session_id not in game_sessions:
            return jsonify({
                "success": False,
                "error": "Invalid or missing session_id"
            }), 400

        session = game_sessions[session_id]

        return jsonify({
            "success": True,
            "session_id": session_id,
            "turn_count": session.turn_count,
            "location": session.game.current_location,
            "characters": session._get_character_states(),
            "scenes": session.scenes,
            "created_at": session.created_at
        })

    except Exception as e:
        logger.error(f"Error getting game state: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/ai/decision-matrix', methods=['POST'])
def generate_decision_matrix():
    """
    Generate AI-powered decision matrix for DM choices.

    Body:
    {
        "session_id": "...",
        "scenario": "Decision scenario description",
        "options": ["option1", "option2", "option3"]
    }

    Returns:
    {
        "success": true,
        "decisions": [
            {
                "option": "option1",
                "reasoning": "AI reasoning",
                "consequences": ["consequence1", "consequence2"],
                "probability_success": 0.8,
                "risk_level": "medium",
                "alignment": "good"
            }
        ]
    }
    """
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        scenario = data.get('scenario')
        options = data.get('options', [])

        if not session_id or session_id not in game_sessions:
            return jsonify({
                "success": False,
                "error": "Invalid or missing session_id"
            }), 400

        if not scenario or not options:
            return jsonify({
                "success": False,
                "error": "Missing scenario or options"
            }), 400

        session = game_sessions[session_id]

        # Check if we have Gemini engine available
        if hasattr(session.narrative_engine, 'generate_decision_matrix'):
            # Create narrative context
            from gemini_narrative_engine import NarrativeContext
            context = NarrativeContext(
                campaign_id=f"campaign_{session_id}",
                session_id=session_id,
                current_scene=session.game.current_location,
                player_actions=[scene.get('narrative', '')[:100] for scene in session.scenes[-3:]],
                npc_states={},
                world_state={"turn_count": session.turn_count},
                campaign_tone="epic",
                difficulty_level="medium"
            )

            decisions = session.narrative_engine.generate_decision_matrix(
                context, scenario, options
            )

            return jsonify({
                "success": True,
                "decisions": [
                    {
                        "option": d.option,
                        "reasoning": d.reasoning,
                        "consequences": d.consequences,
                        "probability_success": d.probability_success,
                        "risk_level": d.risk_level,
                        "alignment": d.alignment
                    }
                    for d in decisions
                ]
            })
        else:
            # Fallback for Ollama engine
            return jsonify({
                "success": True,
                "decisions": [
                    {
                        "option": option,
                        "reasoning": f"Consider the consequences of {option.lower()}",
                        "consequences": ["Unknown consequences"],
                        "probability_success": 0.5,
                        "risk_level": "medium",
                        "alignment": "neutral"
                    }
                    for option in options
                ]
            })

    except Exception as e:
        logger.error(f"Error generating decision matrix: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/ai/story-branches', methods=['POST'])
def analyze_story_branches():
    """
    Analyze potential story branches from player choice.

    Body:
    {
        "session_id": "...",
        "player_choice": "What the player chose to do"
    }

    Returns:
    {
        "success": true,
        "branches": [
            {
                "branch_name": "Branch Name",
                "description": "What happens",
                "immediate_consequences": ["consequence1"],
                "long_term_effects": ["effect1"],
                "character_impact": {"character": "impact"},
                "world_changes": ["change1"]
            }
        ]
    }
    """
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        player_choice = data.get('player_choice')

        if not session_id or session_id not in game_sessions:
            return jsonify({
                "success": False,
                "error": "Invalid or missing session_id"
            }), 400

        if not player_choice:
            return jsonify({
                "success": False,
                "error": "Missing player_choice"
            }), 400

        session = game_sessions[session_id]

        # Check if we have Gemini engine available
        if hasattr(session.narrative_engine, 'analyze_story_branches'):
            # Create narrative context
            from gemini_narrative_engine import NarrativeContext
            context = NarrativeContext(
                campaign_id=f"campaign_{session_id}",
                session_id=session_id,
                current_scene=session.game.current_location,
                player_actions=[scene.get('narrative', '')[:100] for scene in session.scenes[-3:]],
                npc_states={},
                world_state={"turn_count": session.turn_count},
                campaign_tone="epic",
                difficulty_level="medium"
            )

            branches = session.narrative_engine.analyze_story_branches(
                context, player_choice
            )

            return jsonify({
                "success": True,
                "branches": [
                    {
                        "branch_name": b.branch_name,
                        "description": b.description,
                        "immediate_consequences": b.immediate_consequences,
                        "long_term_effects": b.long_term_effects,
                        "character_impact": b.character_impact,
                        "world_changes": b.world_changes
                    }
                    for b in branches
                ]
            })
        else:
            # Fallback for Ollama engine
            return jsonify({
                "success": True,
                "branches": [
                    {
                        "branch_name": "Immediate Path",
                        "description": f"The consequences of {player_choice.lower()} unfold...",
                        "immediate_consequences": ["The situation changes"],
                        "long_term_effects": ["Long-term effects unknown"],
                        "character_impact": {"party": "Characters react to the choice"},
                        "world_changes": ["The world responds to your action"]
                    }
                ]
            })

    except Exception as e:
        logger.error(f"Error analyzing story branches: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/ai/npc-behavior', methods=['POST'])
def generate_npc_behavior():
    """
    Generate dynamic NPC behavior based on personality and situation.

    Body:
    {
        "session_id": "...",
        "npc_name": "NPC Name",
        "npc_personality": "Personality description",
        "situation": "Current situation"
    }

    Returns:
    {
        "success": true,
        "behavior": {
            "npc_name": "NPC Name",
            "personality_traits": ["trait1", "trait2"],
            "current_mood": "mood",
            "reaction": "reaction description",
            "dialogue_suggestions": ["dialogue1", "dialogue2"],
            "action_recommendations": ["action1", "action2"]
        }
    }
    """
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        npc_name = data.get('npc_name')
        npc_personality = data.get('npc_personality')
        situation = data.get('situation')

        if not session_id or session_id not in game_sessions:
            return jsonify({
                "success": False,
                "error": "Invalid or missing session_id"
            }), 400

        if not all([npc_name, npc_personality, situation]):
            return jsonify({
                "success": False,
                "error": "Missing npc_name, npc_personality, or situation"
            }), 400

        session = game_sessions[session_id]

        # Check if we have Gemini engine available
        if hasattr(session.narrative_engine, 'generate_npc_behavior'):
            # Create narrative context
            from gemini_narrative_engine import NarrativeContext
            context = NarrativeContext(
                campaign_id=f"campaign_{session_id}",
                session_id=session_id,
                current_scene=session.game.current_location,
                player_actions=[scene.get('narrative', '')[:100] for scene in session.scenes[-3:]],
                npc_states={},
                world_state={"turn_count": session.turn_count},
                campaign_tone="epic",
                difficulty_level="medium"
            )

            behavior = session.narrative_engine.generate_npc_behavior(
                context, npc_name, npc_personality, situation
            )

            return jsonify({
                "success": True,
                "behavior": {
                    "npc_name": behavior.npc_name,
                    "personality_traits": behavior.personality_traits,
                    "current_mood": behavior.current_mood,
                    "reaction": behavior.reaction,
                    "dialogue_suggestions": behavior.dialogue_suggestions,
                    "action_recommendations": behavior.action_recommendations
                }
            })
        else:
            # Fallback for Ollama engine
            return jsonify({
                "success": True,
                "behavior": {
                    "npc_name": npc_name,
                    "personality_traits": [npc_personality],
                    "current_mood": "neutral",
                    "reaction": f"{npc_name} considers the situation carefully",
                    "dialogue_suggestions": [f"{npc_name} says: 'Interesting...'"],
                    "action_recommendations": [f"{npc_name} waits to see what happens"]
                }
            })

    except Exception as e:
        logger.error(f"Error generating NPC behavior: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/ai/adaptive-story', methods=['POST'])
def generate_adaptive_story():
    """
    Generate adaptive story content based on campaign progression.

    Body:
    {
        "session_id": "...",
        "story_element": "Element to generate story for"
    }

    Returns:
    {
        "success": true,
        "story_content": "Generated story content"
    }
    """
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        story_element = data.get('story_element')

        if not session_id or session_id not in game_sessions:
            return jsonify({
                "success": False,
                "error": "Invalid or missing session_id"
            }), 400

        if not story_element:
            return jsonify({
                "success": False,
                "error": "Missing story_element"
            }), 400

        session = game_sessions[session_id]

        # Check if we have Gemini engine available
        if hasattr(session.narrative_engine, 'generate_adaptive_story'):
            # Create narrative context
            from gemini_narrative_engine import NarrativeContext
            context = NarrativeContext(
                campaign_id=f"campaign_{session_id}",
                session_id=session_id,
                current_scene=session.game.current_location,
                player_actions=[scene.get('narrative', '')[:100] for scene in session.scenes[-3:]],
                npc_states={},
                world_state={"turn_count": session.turn_count},
                campaign_tone="epic",
                difficulty_level="medium"
            )

            story_content = session.narrative_engine.generate_adaptive_story(
                context, story_element
            )

            return jsonify({
                "success": True,
                "story_content": story_content
            })
        else:
            # Fallback for Ollama engine
            story_content = session.narrative_engine.generate_quest(
                difficulty="medium",
                theme=story_element
            )

            return jsonify({
                "success": True,
                "story_content": story_content
            })

    except Exception as e:
        logger.error(f"Error generating adaptive story: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/ai/engine-status', methods=['GET'])
def get_ai_engine_status():
    """
    Get AI engine status and capabilities.

    Returns:
    {
        "success": true,
        "engine_status": {
            "engine_name": "Gemini Narrative Engine",
            "version": "1.0.0",
            "gemini_available": true,
            "capabilities": ["narrative_generation", "decision_matrix", ...]
        }
    }
    """
    try:
        # Check if we have any sessions to get engine status from
        if game_sessions:
            session = next(iter(game_sessions.values()))
            if hasattr(session.narrative_engine, 'get_engine_status'):
                engine_status = session.narrative_engine.get_engine_status()
            else:
                engine_status = {
                    "engine_name": "Ollama Narrative Engine",
                    "version": "1.0.0",
                    "gemini_available": False,
                    "capabilities": ["basic_narrative_generation"],
                    "model": session.narrative_engine.model
                }
        else:
            # No sessions, create a temporary engine to check status
            from narrative_engine import create_narrative_engine
            temp_engine = create_narrative_engine("gemini")
            if hasattr(temp_engine, 'get_engine_status'):
                engine_status = temp_engine.get_engine_status()
            else:
                engine_status = {
                    "engine_name": "Ollama Narrative Engine",
                    "version": "1.0.0",
                    "gemini_available": False,
                    "capabilities": ["basic_narrative_generation"]
                }

        return jsonify({
            "success": True,
            "engine_status": engine_status
        })

    except Exception as e:
        logger.error(f"Error getting engine status: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/save-story', methods=['POST'])
def save_story():
    """
    Save the current story to Obsidian vault.

    Request body:
    {
        "session_id": "...",
        "story_title": "...",
        "chapters": [
            {
                "number": 1,
                "title": "...",
                "content": "..."
            }
        ],
        "vault_path": "ai-dnd-test-vault" (optional)
    }

    Returns:
    {
        "success": true,
        "file_path": "path/to/saved/story.md"
    }
    """
    try:
        from obsidian_logger import ObsidianLogger

        data = request.json
        session_id = data.get('session_id')
        story_title = data.get('story_title', 'Untitled Adventure')
        chapters = data.get('chapters', [])
        vault_path = data.get('vault_path', 'ai-dnd-test-vault')

        if not session_id or session_id not in game_sessions:
            return jsonify({
                "success": False,
                "error": "Invalid or missing session_id"
            }), 400

        # Initialize Obsidian logger
        obs_logger = ObsidianLogger(vault_path)

        # Create story content
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        story_content = f"""# {story_title}

**Session ID:** {session_id}
**Created:** {timestamp}
**Type:** Interactive Story Theater

---

"""

        # Add each chapter
        for chapter in chapters:
            story_content += f"""## Chapter {chapter.get('number', '?')}: {chapter.get('title', 'Untitled')}

{chapter.get('content', '')}

---

"""

        # Save to Obsidian vault
        story_filename = f"{story_title.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        stories_dir = os.path.join(vault_path, "Stories")
        os.makedirs(stories_dir, exist_ok=True)

        file_path = os.path.join(stories_dir, story_filename)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(story_content)

        logger.info(f"Story saved to Obsidian: {file_path}")

        return jsonify({
            "success": True,
            "file_path": file_path,
            "message": f"Story saved successfully to {story_filename}"
        })

    except Exception as e:
        logger.error(f"Error saving story: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


if __name__ == '__main__':
    logger.info("Starting DnD Narrative Theater Server on port 5002...")
    logger.info("Required services:")
    logger.info("  - PixelLab Bridge (port 5001)")
    logger.info("  - Nano Banana (port 5000)")
    logger.info("  - Ollama (for narrative generation)")
    logger.info("  - Gemini API (for enhanced AI features)")

    app.run(host='0.0.0.0', port=5002, debug=True)

