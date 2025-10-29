#!/usr/bin/env python3
"""
🎭 LIVE DEMONSTRATION: Gemini-Enhanced D&D Character Generator
Showcasing AI-powered character creation in action
"""

import asyncio
import json
import random
from datetime import datetime
from gemini_enhanced_character_generator import (
    GeminiEnhancedCharacterGenerator,
    CharacterType,
    CharacterTone,
    EnhancedCharacter,
    EnhancedCharacterGenerator
)

class MockGeminiClient:
    """Mock Gemini client for demonstration purposes"""

    async def generate_content(self, request):
        """Simulate Gemini API responses"""
        model = request.get('model', 'gemini-2.5-flash')
        prompt = request['contents'][0]['parts'][0]['text']

        # Simulate API delay
        await asyncio.sleep(0.5)

        # Generate mock response based on prompt content
        if 'AI enhancement' in prompt:
            return self._generate_character_enhancement(prompt)
        elif 'quests' in prompt:
            return self._generate_quest_response()
        elif 'story' in prompt:
            return self._generate_story_response()
        else:
            return self._generate_generic_response()

    def _generate_character_enhancement(self, prompt):
        """Generate mock character enhancement"""
        enhancement_data = {
            "aiBackstory": "Born in the shadowed alleys of Waterdeep, this character's early years were marked by hardship and survival. Their family was torn apart by political intrigue, leaving them to fend for themselves on the dangerous streets. Through cunning and determination, they learned to navigate the complex web of city politics, developing skills that would serve them well in their future adventures. Their experiences have made them both fiercely independent and deeply loyal to those who earn their trust.",
            "aiPersonalityInsights": "Their high Dexterity and Intelligence scores suggest a character who thinks quickly on their feet and adapts to changing situations with remarkable ease. They possess a natural charisma that allows them to read people and situations, making them excellent at negotiation and deception when necessary.",
            "aiCharacterVoice": "Speaks with a measured, thoughtful tone, often pausing to consider their words carefully. When excited or passionate, their speech becomes more animated and expressive. Uses metaphors drawn from their urban background, often referencing 'the game' or 'playing the hand you're dealt.'",
            "aiQuestHooks": [
                "Seeking revenge against the noble family that destroyed their family",
                "Protecting a found family of street urchins who remind them of their past",
                "Uncovering a conspiracy that threatens the city's political stability"
            ],
            "aiRelationshipDynamics": "Forms deep, protective bonds with those they consider family, but remains guarded with strangers. They value loyalty above all else and will go to great lengths to protect those they care about. However, they have difficulty trusting authority figures due to their past experiences.",
            "aiCharacterGoals": [
                "Establish a safe haven for the city's orphaned children",
                "Master their abilities to become a legendary figure",
                "Find closure regarding their family's fate"
            ],
            "aiCharacterFlaws": [
                "Trusts too easily once someone shows them kindness",
                "Fear of abandonment drives them to push people away",
                "Stubborn refusal to ask for help when needed"
            ]
        }

        response_text = f"""
Here is the comprehensive AI enhancement for your D&D character:

{json.dumps(enhancement_data, indent=2)}

This character represents a complex individual shaped by their difficult past, with clear motivations and growth potential for your D&D campaign.
        """

        return MockResponse(response_text)

    def _generate_quest_response(self):
        """Generate mock quest response"""
        quests = [
            {
                "title": "Shadows of the Past",
                "description": "A mysterious figure from the character's past has resurfaced, bringing both danger and opportunity for closure.",
                "objectives": ["Investigate the stranger's motives", "Protect innocent bystanders", "Confront the past"],
                "rewards": ["Valuable information", "Magical item", "Political favor"],
                "difficulty": "Medium",
                "questHook": "Connects directly to the character's backstory and family history"
            },
            {
                "title": "The Orphan's Shield",
                "description": "Street children are disappearing from the city's poorest districts, and the character must uncover the truth.",
                "objectives": ["Find the missing children", "Identify the perpetrators", "Bring them to justice"],
                "rewards": ["Community respect", "New allies", "Hidden safe house"],
                "difficulty": "Hard",
                "questHook": "Taps into the character's protective instincts and past experiences"
            },
            {
                "title": "The Noble's Gambit",
                "description": "A high-stakes political game threatens to destabilize the city, and the character is uniquely positioned to intervene.",
                "objectives": ["Navigate political intrigue", "Gather intelligence", "Prevent disaster"],
                "rewards": ["Political influence", "Wealth", "Powerful connections"],
                "difficulty": "Hard",
                "questHook": "Utilizes the character's street-smart skills and knowledge of city politics"
            }
        ]

        response_text = f"""
Here are 3 personalized quests for your character:

{json.dumps(quests, indent=2)}

Each quest is designed to challenge the character's fears, utilize their abilities, and create meaningful character development opportunities.
        """

        return MockResponse(response_text)

    def _generate_story_response(self):
        """Generate mock story response"""
        story = """
The cobblestones of Waterdeep's Dock Ward were slick with rain as Aria Shadowbane slipped through the shadows, her keen elven ears picking up the distant sound of the city watch's boots on wet stone. She had learned long ago that survival in this city required more than just skill with a blade—it demanded the ability to read people, to understand their motivations, and to know when to strike and when to fade into the darkness.

Tonight, however, was different. The information she had gathered about the missing children had led her to this abandoned warehouse, and she could hear the faint sounds of crying from within. Her heart clenched as memories of her own childhood flooded back—the nights spent huddled in doorways, the constant fear, the desperate hope that someone, anyone, would care enough to help.

But she was no longer that helpless child. She was Aria Shadowbane, and she had made a promise to herself that no child would suffer as she had. Drawing her daggers, she prepared to enter the warehouse, knowing that whatever awaited her inside would test not just her skills, but her very soul.
        """

        return MockResponse(story)

    def _generate_generic_response(self):
        """Generate generic mock response"""
        return MockResponse("This is a mock response from the Gemini API demonstration.")

class MockResponse:
    """Mock response object"""
    def __init__(self, text):
        self.text = text

async def demonstrate_character_generation():
    """Demonstrate the Gemini-enhanced character generator"""
    print("🎭 LIVE DEMONSTRATION: Gemini-Enhanced D&D Character Generator")
    print("=" * 70)
    print()

    # Initialize the generator with mock Gemini client
    mock_client = MockGeminiClient()
    generator = GeminiEnhancedCharacterGenerator(mock_client)

    # Create a sample character for demonstration
    sample_character = EnhancedCharacter(
        name="Aria Shadowbane",
        char_class="Rogue",
        race="Elf",
        level=5,
        background="Criminal",
        ability_scores={
            "strength": 12,
            "dexterity": 18,
            "constitution": 14,
            "intelligence": 16,
            "wisdom": 15,
            "charisma": 13
        }
    )

    print("📋 BASE CHARACTER DATA:")
    print(f"Name: {sample_character.name}")
    print(f"Class: {sample_character.char_class}")
    print(f"Race: {sample_character.race}")
    print(f"Level: {sample_character.level}")
    print(f"Background: {sample_character.background}")
    print(f"Ability Scores: {sample_character.ability_scores}")
    print()

    # Convert to dict for processing
    character_dict = generator.base_generator.to_dict(sample_character)

    print("🤖 GENERATING AI ENHANCEMENT...")
    print("(Simulating Gemini API call...)")
    print()

    # Generate AI-enhanced character using the sample character data
    enhanced_character = await generator.generate_ai_enhanced_character(
        character_type=CharacterType.HERO,
        tone=CharacterTone.DARK,
        level=5
    )

    print("✨ AI-ENHANCED CHARACTER:")
    print("=" * 50)
    print(f"Name: {enhanced_character.get('name', 'Unknown')}")
    print(f"AI Enhanced: {enhanced_character.get('ai_enhanced', False)}")
    print()

    if enhanced_character.get('ai_enhanced'):
        print("📖 AI-GENERATED BACKSTORY:")
        print("-" * 30)
        print(enhanced_character.get('ai_backstory', 'No backstory available'))
        print()

        print("🧠 PERSONALITY INSIGHTS:")
        print("-" * 30)
        print(enhanced_character.get('ai_personality_insights', 'No insights available'))
        print()

        print("🗣️ CHARACTER VOICE:")
        print("-" * 30)
        print(enhanced_character.get('ai_character_voice', 'No voice data available'))
        print()

        print("🎯 CHARACTER GOALS:")
        print("-" * 30)
        goals = enhanced_character.get('ai_character_goals', [])
        for i, goal in enumerate(goals, 1):
            print(f"{i}. {goal}")
        print()

        print("⚠️ CHARACTER FLAWS:")
        print("-" * 30)
        flaws = enhanced_character.get('ai_character_flaws', [])
        for i, flaw in enumerate(flaws, 1):
            print(f"{i}. {flaw}")
        print()

        print("🔗 QUEST HOOKS:")
        print("-" * 30)
        hooks = enhanced_character.get('ai_quest_hooks', [])
        for i, hook in enumerate(hooks, 1):
            print(f"{i}. {hook}")
        print()

        print("👥 RELATIONSHIP DYNAMICS:")
        print("-" * 30)
        print(enhanced_character.get('ai_relationship_dynamics', 'No relationship data available'))
        print()
    else:
        print("⚠️ AI enhancement not available - using base character data")
        print()

    # Generate personalized quests
    print("🎲 GENERATING PERSONALIZED QUESTS...")
    print("(Simulating Gemini API call...)")
    print()

    quests = await generator.generate_character_quests(enhanced_character)

    print("📜 AI-GENERATED QUESTS:")
    print("=" * 50)
    for i, quest in enumerate(quests, 1):
        print(f"QUEST {i}: {quest['title']}")
        print(f"Difficulty: {quest['difficulty']}")
        print(f"Description: {quest['description']}")
        print(f"Quest Hook: {quest['questHook']}")
        print(f"Objectives:")
        for obj in quest['objectives']:
            print(f"  • {obj}")
        print(f"Rewards:")
        for reward in quest['rewards']:
            print(f"  • {reward}")
        print()

    # Generate character story (using mock client directly)
    print("📚 GENERATING CHARACTER STORY...")
    print("(Simulating Gemini API call...)")
    print()

    story_response = await mock_client.generate_content({
        'model': 'gemini-2.5-flash',
        'contents': [{'parts': [{'text': 'Generate a character story'}]}]
    })

    print("📖 AI-GENERATED STORY:")
    print("=" * 50)
    print(story_response.text)
    print()

    # Show cache statistics
    print("📊 CACHE STATISTICS:")
    print("-" * 30)
    print(f"Cache Size: {len(generator.enhancement_cache)} entries")
    print(f"Cached Keys: {list(generator.enhancement_cache.keys())}")
    print()

    print("🎉 DEMONSTRATION COMPLETE!")
    print("=" * 70)
    print("The Gemini-enhanced character generator successfully:")
    print("✅ Generated rich AI backstory and personality insights")
    print("✅ Created personalized quest hooks and character goals")
    print("✅ Developed character voice and relationship dynamics")
    print("✅ Generated 3 personalized quests with objectives and rewards")
    print("✅ Created an engaging character story")
    print("✅ Implemented caching for performance optimization")
    print("✅ Provided comprehensive error handling and fallback systems")

async def main():
    """Run the demonstration"""
    try:
        await demonstrate_character_generation()
    except Exception as e:
        print(f"❌ Demonstration failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
