"""
Enhanced D&D Character Generator
Implements comprehensive character generation system based on reference specifications
REF-103 through REF-108: Personality, Background, Statistics, Equipment, Skills, Spells
"""

import random
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)

class CharacterType(Enum):
    """Character types as specified in REF-100.1"""
    HERO = "hero"
    NPC = "npc"
    VILLAIN = "villain"
    MERCHANT = "merchant"
    GUARD = "guard"
    NOBLE = "noble"
    SCHOLAR = "scholar"

class CharacterTone(Enum):
    """Character tones as specified in REF-100.1"""
    REALISTIC = "realistic"
    FANTASY = "fantasy"
    COMEDY = "comedy"
    DRAMATIC = "dramatic"

@dataclass
class PersonalityTraits:
    """Personality traits as specified in REF-103.1"""
    primary_trait: str
    secondary_trait: str
    motivation: str
    fear: str
    quirk: str
    speech_pattern: str

@dataclass
class CharacterBackground:
    """Character background as specified in REF-104.1"""
    occupation: str
    social_class: str
    life_events: List[str]
    hometown: str
    family_status: str

@dataclass
class CharacterStats:
    """Character statistics as specified in REF-105.1"""
    strength: int
    dexterity: int
    constitution: int
    intelligence: int
    wisdom: int
    charisma: int

@dataclass
class CharacterEquipment:
    """Character equipment as specified in REF-106.1"""
    base_equipment: List[str]
    type_specific_equipment: List[str]
    weapons: List[str]
    armor: List[str]
    tools: List[str]

@dataclass
class CharacterSkills:
    """Character skills as specified in REF-107.1"""
    combat_skills: List[str]
    social_skills: List[str]
    knowledge_skills: List[str]
    utility_skills: List[str]

@dataclass
class CharacterSpells:
    """Character spells as specified in REF-108.1"""
    basic_spells: List[str]
    combat_spells: List[str]
    utility_spells: List[str]
    spell_level: int

@dataclass
class EnhancedCharacter:
    """Enhanced D&D character with comprehensive attributes"""
    name: str
    character_type: CharacterType
    tone: CharacterTone
    level: int
    race: str
    char_class: str

    # Core attributes
    personality: PersonalityTraits
    background: CharacterBackground
    stats: CharacterStats
    equipment: CharacterEquipment
    skills: CharacterSkills
    spells: CharacterSpells

    # Additional attributes
    appearance: Dict[str, str] = field(default_factory=dict)
    bio: str = ""
    portrait_url: str = ""

class EnhancedCharacterGenerator:
    """Enhanced character generator implementing REF-103 through REF-108"""

    def __init__(self):
        # REF-103.1: Personality Trait Databases
        self.personality_data = {
            "primary_traits": ["Bold", "Cautious", "Intelligent", "Charismatic", "Mysterious",
                              "Loyal", "Independent", "Creative", "Practical", "Spiritual"],
            "secondary_traits": ["Humor", "Seriousness", "Optimism", "Pessimism", "Adventure",
                                "Comfort", "Knowledge", "Power", "Peace", "Justice"],
            "motivations": ["Protect others", "Seek knowledge", "Gain power", "Find love",
                           "Avenge wrongs", "Explore the world", "Build something great",
                           "Help the needy", "Discover truth", "Achieve fame"],
            "fears": ["Failure", "Loneliness", "Death", "Betrayal", "Poverty", "Insanity",
                     "Being forgotten", "Hurting others", "Losing control", "The unknown"],
            "quirks": ["Always carries a lucky coin", "Speaks in rhymes", "Collects strange objects",
                      "Never lies", "Always punctual", "Hums while thinking", "Taps fingers when nervous",
                      "Quotes ancient texts", "Always has a plan", "Never gives up"]
        }

        # REF-103.2: Speech Pattern Classification
        self.speech_patterns = [
            "Formal", "Casual", "Scholarly", "Rough", "Poetic",
            "Direct", "Cryptic", "Humble", "Arrogant", "Wise"
        ]

        # REF-104.1: Background Data Structures
        self.background_data = {
            "occupations": ["Warrior", "Scholar", "Merchant", "Artisan", "Noble",
                           "Commoner", "Criminal", "Priest", "Mage", "Explorer"],
            "social_classes": ["Noble", "Merchant", "Artisan", "Commoner", "Outcast",
                              "Slave", "Royal", "Guild Member", "Scholar", "Wanderer"],
            "life_events": ["Lost family", "Found treasure", "Saved someone", "Was betrayed",
                           "Learned magic", "Traveled far", "Fell in love", "Made enemy",
                           "Discovered secret", "Overcame fear"]
        }

        # REF-106.1: Base Equipment List
        self.base_equipment = ["Clothes", "Backpack", "Rations", "Water skin"]

        # REF-106.2: Type-Specific Equipment Mapping
        self.equipment_by_type = {
            CharacterType.HERO: ["Sword", "Shield", "Armor"],
            CharacterType.MERCHANT: ["Merchant's scale", "Trade goods", "Coin purse"],
            CharacterType.GUARD: ["Spear", "Chain mail", "Badge of office"],
            CharacterType.SCHOLAR: ["Books", "Writing materials", "Magnifying glass"],
            CharacterType.NOBLE: ["Fine clothes", "Signet ring", "Jewelry"]
        }

        # REF-107.1: Skills by Character Type
        self.skill_data = {
            CharacterType.HERO: ["Combat", "Leadership", "Courage", "Strategy"],
            CharacterType.NPC: ["Local Knowledge", "Gossip", "Trade", "Survival"],
            CharacterType.VILLAIN: ["Deception", "Intimidation", "Strategy", "Power"],
            CharacterType.MERCHANT: ["Haggling", "Appraisal", "Networking", "Travel"],
            CharacterType.GUARD: ["Vigilance", "Combat", "Investigation", "Authority"],
            CharacterType.NOBLE: ["Etiquette", "Politics", "Wealth", "Influence"],
            CharacterType.SCHOLAR: ["Research", "Languages", "History", "Analysis"]
        }

        # REF-108.1: Spell Lists by Level
        self.spell_lists = {
            "basic": ["Detect Magic", "Light", "Mage Hand", "Prestidigitation"],
            "combat": ["Magic Missile", "Fire Bolt", "Healing Word", "Cure Wounds"],
            "utility": ["Identify", "Mage Armor", "Shield", "Feather Fall"]
        }

        # Basic character data
        self.races = [
            "Human", "Elf", "Dwarf", "Halfling", "Gnome", "Half-Orc",
            "Half-Elf", "Tiefling", "Dragonborn", "Aasimar"
        ]
        self.classes = [
            "Fighter", "Wizard", "Rogue", "Cleric", "Paladin", "Ranger",
            "Bard", "Barbarian", "Monk", "Warlock", "Sorcerer", "Druid"
        ]

    def generate_personality(self) -> PersonalityTraits:
        """Generate personality traits as specified in REF-103"""
        return PersonalityTraits(
            primary_trait=random.choice(self.personality_data["primary_traits"]),
            secondary_trait=random.choice(self.personality_data["secondary_traits"]),
            motivation=random.choice(self.personality_data["motivations"]),
            fear=random.choice(self.personality_data["fears"]),
            quirk=random.choice(self.personality_data["quirks"]),
            speech_pattern=random.choice(self.speech_patterns)
        )

    def generate_background(self, character_type: CharacterType) -> CharacterBackground:
        """Generate character background as specified in REF-104"""
        # REF-104.2: Character Type Background Mapping
        type_mappings = {
            CharacterType.NOBLE: {"occupation": "Noble", "social_class": "Noble"},
            CharacterType.MERCHANT: {"occupation": "Merchant", "social_class": "Merchant"},
            CharacterType.GUARD: {"occupation": "Guard", "social_class": "Commoner"},
            CharacterType.SCHOLAR: {"occupation": "Scholar", "social_class": "Scholar"}
        }

        mapping = type_mappings.get(character_type, {})
        occupation = mapping.get("occupation", random.choice(self.background_data["occupations"]))
        social_class = mapping.get("social_class", random.choice(self.background_data["social_classes"]))

        return CharacterBackground(
            occupation=occupation,
            social_class=social_class,
            life_events=random.sample(self.background_data["life_events"], random.randint(1, 3)),
            hometown=f"{random.choice(['North', 'South', 'East', 'West'])} {random.choice(['Village', 'Town', 'City', 'Keep'])}",
            family_status=random.choice(["Orphaned", "Large family", "Only child", "Adopted", "Royal blood"])
        )

    def generate_stats(self, character_type: CharacterType, level: int = 1) -> CharacterStats:
        """Generate character statistics as specified in REF-105"""
        # REF-105.1: Base Stat Calculation
        stats = CharacterStats(
            strength=10, dexterity=10, constitution=10,
            intelligence=10, wisdom=10, charisma=10
        )

        # REF-105.2: Character Type Stat Modifiers
        modifiers = {
            CharacterType.HERO: {"strength": +4, "charisma": +3},
            CharacterType.SCHOLAR: {"intelligence": +5, "wisdom": +3},
            CharacterType.MERCHANT: {"charisma": +4, "intelligence": +3},
            CharacterType.GUARD: {"strength": +4, "constitution": +3}
        }

        type_mods = modifiers.get(character_type, {})
        for stat, bonus in type_mods.items():
            current_value = getattr(stats, stat)
            setattr(stats, stat, current_value + bonus)

        # REF-105.3: Random Stat Variation
        for stat in ['strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma']:
            current_value = getattr(stats, stat)
            adjustment = random.randint(-2, 2)
            new_value = max(3, min(20, current_value + adjustment))
            setattr(stats, stat, new_value)

        return stats

    def generate_equipment(self, character_type: CharacterType) -> CharacterEquipment:
        """Generate character equipment as specified in REF-106"""
        type_equipment = self.equipment_by_type.get(character_type, [])

        return CharacterEquipment(
            base_equipment=self.base_equipment.copy(),
            type_specific_equipment=type_equipment.copy(),
            weapons=random.sample(["Sword", "Bow", "Staff", "Dagger", "Mace"], random.randint(1, 2)),
            armor=random.sample(["Leather", "Chain mail", "Plate", "Robes"], 1),
            tools=random.sample(["Lockpicks", "Healer's kit", "Thieves' tools", "Alchemist's supplies"], random.randint(0, 2))
        )

    def generate_skills(self, character_type: CharacterType) -> CharacterSkills:
        """Generate character skills as specified in REF-107"""
        type_skills = self.skill_data.get(character_type, ["General Knowledge", "Survival"])

        return CharacterSkills(
            combat_skills=random.sample(["Swordsmanship", "Archery", "Unarmed Combat", "Tactics"], random.randint(1, 2)),
            social_skills=random.sample(["Persuasion", "Intimidation", "Deception", "Insight"], random.randint(1, 2)),
            knowledge_skills=type_skills.copy(),
            utility_skills=random.sample(["Stealth", "Perception", "Investigation", "Athletics"], random.randint(1, 2))
        )

    def generate_spells(self, character_type: CharacterType, level: int = 1) -> CharacterSpells:
        """Generate character spells as specified in REF-108"""
        if character_type not in [CharacterType.SCHOLAR, CharacterType.HERO]:
            return CharacterSpells([], [], [], 0)

        # REF-108.2: Spell Selection Algorithm
        spells = random.sample(self.spell_lists["basic"], min(2, len(self.spell_lists["basic"])))
        combat_spells = []
        utility_spells = []

        if level > 1:
            combat_spells = random.sample(self.spell_lists["combat"], min(level - 1, len(self.spell_lists["combat"])))
            utility_spells = random.sample(self.spell_lists["utility"], min(level - 1, len(self.spell_lists["utility"])))

        return CharacterSpells(
            basic_spells=spells,
            combat_spells=combat_spells,
            utility_spells=utility_spells,
            spell_level=level
        )

    def generate_character(self, character_type: CharacterType = None, tone: CharacterTone = None, level: int = 1) -> EnhancedCharacter:
        """Generate a complete enhanced character"""
        if character_type is None:
            character_type = random.choice(list(CharacterType))
        if tone is None:
            tone = random.choice(list(CharacterTone))

        return EnhancedCharacter(
            name=f"{random.choice(['Aria', 'Borin', 'Celia', 'Dain', 'Elena', 'Finn', 'Gwen', 'Haldor', 'Iris', 'Jax'])} {random.choice(['Stormwind', 'Ironforge', 'Silverleaf', 'Goldheart', 'Shadowbane', 'Brightblade', 'Darkwood', 'Lightbringer'])}",
            character_type=character_type,
            tone=tone,
            level=level,
            race=random.choice(self.races),
            char_class=random.choice(self.classes),
            personality=self.generate_personality(),
            background=self.generate_background(character_type),
            stats=self.generate_stats(character_type, level),
            equipment=self.generate_equipment(character_type),
            skills=self.generate_skills(character_type),
            spells=self.generate_spells(character_type, level),
            appearance={
                "age": random.randint(18, 80),
                "height": f"{random.randint(4, 7)}'{random.randint(0, 11)}\"",
                "weight": f"{random.randint(100, 300)} lbs",
                "hair_color": random.choice(["Black", "Brown", "Blonde", "Red", "Gray", "White"]),
                "eye_color": random.choice(["Brown", "Blue", "Green", "Hazel", "Gray", "Amber"]),
                "distinguishing_features": random.choice(["Scar", "Tattoo", "Piercing", "Birthmark", "Missing finger", "Limp"])
            },
            bio=f"A {character_type.value} {tone.value} character with a {self.generate_personality().primary_trait.lower()} personality."
        )

    def generate_multiple_characters(self, count: int, character_type: CharacterType = None) -> List[EnhancedCharacter]:
        """Generate multiple characters for party creation"""
        characters = []
        for _ in range(count):
            characters.append(self.generate_character(character_type))
        return characters

    def to_dict(self, character: EnhancedCharacter) -> Dict:
        """Convert character to dictionary for serialization"""
        return {
            "name": character.name,
            "character_type": character.character_type.value,
            "tone": character.tone.value,
            "level": character.level,
            "race": character.race,
            "char_class": character.char_class,
            "personality": {
                "primary_trait": character.personality.primary_trait,
                "secondary_trait": character.personality.secondary_trait,
                "motivation": character.personality.motivation,
                "fear": character.personality.fear,
                "quirk": character.personality.quirk,
                "speech_pattern": character.personality.speech_pattern
            },
            "background": {
                "occupation": character.background.occupation,
                "social_class": character.background.social_class,
                "life_events": character.background.life_events,
                "hometown": character.background.hometown,
                "family_status": character.background.family_status
            },
            "stats": {
                "strength": character.stats.strength,
                "dexterity": character.stats.dexterity,
                "constitution": character.stats.constitution,
                "intelligence": character.stats.intelligence,
                "wisdom": character.stats.wisdom,
                "charisma": character.stats.charisma
            },
            "equipment": {
                "base_equipment": character.equipment.base_equipment,
                "type_specific_equipment": character.equipment.type_specific_equipment,
                "weapons": character.equipment.weapons,
                "armor": character.equipment.armor,
                "tools": character.equipment.tools
            },
            "skills": {
                "combat_skills": character.skills.combat_skills,
                "social_skills": character.skills.social_skills,
                "knowledge_skills": character.skills.knowledge_skills,
                "utility_skills": character.skills.utility_skills
            },
            "spells": {
                "basic_spells": character.spells.basic_spells,
                "combat_spells": character.spells.combat_spells,
                "utility_spells": character.spells.utility_spells,
                "spell_level": character.spells.spell_level
            },
            "appearance": character.appearance,
            "bio": character.bio,
            "portrait_url": character.portrait_url
        }

# Convenience functions for easy integration
def generate_hero(level: int = 1) -> EnhancedCharacter:
    """Generate a hero character"""
    generator = EnhancedCharacterGenerator()
    return generator.generate_character(CharacterType.HERO, CharacterTone.FANTASY, level)

def generate_npc(character_type: CharacterType = None) -> EnhancedCharacter:
    """Generate an NPC character"""
    generator = EnhancedCharacterGenerator()
    if character_type is None:
        character_type = random.choice([CharacterType.MERCHANT, CharacterType.GUARD, CharacterType.SCHOLAR])
    return generator.generate_character(character_type, CharacterTone.REALISTIC)

def generate_party(size: int = 4) -> List[EnhancedCharacter]:
    """Generate a balanced party of characters"""
    generator = EnhancedCharacterGenerator()
    return generator.generate_multiple_characters(size, CharacterType.HERO)

if __name__ == "__main__":
    # Test the enhanced character generator
    generator = EnhancedCharacterGenerator()

    print("=== Enhanced D&D Character Generator Test ===")

    # Generate a hero
    hero = generate_hero(5)
    print(f"\nHero: {hero.name}")
    print(f"Type: {hero.character_type.value} | Level: {hero.level}")
    print(f"Personality: {hero.personality.primary_trait} {hero.personality.secondary_trait}")
    print(f"Motivation: {hero.personality.motivation}")
    print(f"Background: {hero.background.occupation} from {hero.background.hometown}")
    print(f"Stats: STR:{hero.stats.strength} DEX:{hero.stats.dexterity} CON:{hero.stats.constitution}")

    # Generate an NPC
    npc = generate_npc(CharacterType.MERCHANT)
    print(f"\nNPC: {npc.name}")
    print(f"Type: {npc.character_type.value}")
    print(f"Equipment: {', '.join(npc.equipment.type_specific_equipment)}")
    print(f"Skills: {', '.join(npc.skills.knowledge_skills)}")

    # Generate a party
    party = generate_party(3)
    print(f"\nParty ({len(party)} members):")
    for i, member in enumerate(party, 1):
        print(f"  {i}. {member.name} - Level {member.level} {member.race} {member.char_class}")
