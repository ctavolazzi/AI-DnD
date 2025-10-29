#!/usr/bin/env python3
"""
Core Character/Persona Generator Algorithm
A focused, testable character generation system that can be used standalone or as an MCP server
"""

import random
import json
import logging
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, asdict
from enum import Enum
import asyncio
import aiohttp
import ssl

logger = logging.getLogger(__name__)

class CharacterType(Enum):
    """Types of characters that can be generated"""
    HERO = "hero"
    NPC = "npc"
    VILLAIN = "villain"
    COMPANION = "companion"
    MERCHANT = "merchant"
    GUARD = "guard"
    NOBLE = "noble"
    SCHOLAR = "scholar"
    COMMONER = "commoner"

class CharacterTone(Enum):
    """Tone/style of character generation"""
    REALISTIC = "realistic"
    FANTASY = "fantasy"
    SCI_FI = "sci_fi"
    MODERN = "modern"
    HISTORICAL = "historical"
    COMEDY = "comedy"
    DARK = "dark"

@dataclass
class CharacterStats:
    """Core character statistics"""
    strength: int = 10
    dexterity: int = 10
    constitution: int = 10
    intelligence: int = 10
    wisdom: int = 10
    charisma: int = 10

    def get_modifier(self, stat: str) -> int:
        """Get D&D-style ability modifier"""
        value = getattr(self, stat.lower(), 10)
        return (value - 10) // 2

@dataclass
class CharacterAppearance:
    """Character physical appearance"""
    age: int
    gender: str
    height: str
    weight: str
    hair_color: str
    eye_color: str
    skin_tone: str
    distinguishing_features: List[str]
    clothing_style: str
    portrait_url: Optional[str] = None

@dataclass
class CharacterPersonality:
    """Character personality traits"""
    primary_trait: str
    secondary_trait: str
    motivation: str
    fear: str
    secret: str
    quirk: str
    speech_pattern: str
    mannerisms: List[str]

@dataclass
class CharacterBackground:
    """Character background and history"""
    birthplace: str
    family_status: str
    education: str
    occupation: str
    social_class: str
    life_events: List[str]
    relationships: List[str]
    goals: List[str]

@dataclass
class Character:
    """Complete character data structure"""
    # Basic info
    name: str
    character_type: CharacterType
    tone: CharacterTone

    # Core attributes
    stats: CharacterStats
    appearance: CharacterAppearance
    personality: CharacterPersonality
    background: CharacterBackground

    # Game-specific data
    level: int = 1
    hit_points: int = 10
    max_hit_points: int = 10
    skills: List[str] = None
    equipment: List[str] = None
    spells: List[str] = None

    # Metadata
    created_at: str = ""
    tags: List[str] = None

    def __post_init__(self):
        if self.skills is None:
            self.skills = []
        if self.equipment is None:
            self.equipment = []
        if self.spells is None:
            self.spells = []
        if self.tags is None:
            self.tags = []
        if not self.created_at:
            from datetime import datetime
            self.created_at = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert character to dictionary for JSON serialization"""
        return asdict(self)

    def to_json(self) -> str:
        """Convert character to JSON string"""
        return json.dumps(self.to_dict(), indent=2, default=str)

    def get_summary(self) -> str:
        """Get a brief character summary"""
        return f"{self.name} - {self.character_type.value.title()} {self.appearance.age}yo {self.appearance.gender} {self.background.occupation}"

class CharacterGeneratorCore:
    """Core character generation algorithm"""

    def __init__(self):
        self.setup_data()

    def setup_data(self):
        """Initialize character generation data"""
        # Names by culture/region
        self.name_data = {
            "western": {
                "male": ["James", "John", "Robert", "Michael", "William", "David", "Richard", "Charles", "Joseph", "Thomas"],
                "female": ["Mary", "Patricia", "Jennifer", "Linda", "Elizabeth", "Barbara", "Susan", "Jessica", "Sarah", "Karen"],
                "surnames": ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]
            },
            "fantasy": {
                "male": ["Aelar", "Baelor", "Caelum", "Daelin", "Eldrin", "Faelon", "Gaelen", "Haelor", "Iaelin", "Jaelon"],
                "female": ["Aria", "Bria", "Celia", "Daria", "Elia", "Fia", "Gia", "Hia", "Iria", "Jia"],
                "surnames": ["Brightblade", "Stormwind", "Moonwhisper", "Starfall", "Dawnbringer", "Nightshade", "Fireheart", "Iceborn", "Shadowstep", "Lightbringer"]
            },
            "eastern": {
                "male": ["Hiroshi", "Takeshi", "Kenji", "Satoshi", "Yuki", "Akira", "Daiki", "Kenta", "Ryo", "Sota"],
                "female": ["Yuki", "Hana", "Sakura", "Aiko", "Mika", "Nana", "Rina", "Saki", "Yui", "Mai"],
                "surnames": ["Tanaka", "Sato", "Suzuki", "Takahashi", "Watanabe", "Ito", "Yamamoto", "Nakamura", "Kobayashi", "Kato"]
            }
        }

        # Physical appearance data
        self.appearance_data = {
            "hair_colors": ["Black", "Brown", "Blonde", "Red", "Gray", "White", "Auburn", "Chestnut", "Silver", "Gold"],
            "eye_colors": ["Brown", "Blue", "Green", "Hazel", "Gray", "Amber", "Violet", "Black", "Silver", "Gold"],
            "skin_tones": ["Fair", "Light", "Medium", "Olive", "Tan", "Brown", "Dark", "Ebony", "Pale", "Bronze"],
            "heights": ["Very Short", "Short", "Average", "Tall", "Very Tall"],
            "weights": ["Very Thin", "Thin", "Average", "Heavy", "Very Heavy"]
        }

        # Personality traits
        self.personality_data = {
            "primary_traits": ["Bold", "Cautious", "Intelligent", "Charismatic", "Mysterious", "Loyal", "Independent", "Creative", "Practical", "Spiritual"],
            "secondary_traits": ["Humor", "Seriousness", "Optimism", "Pessimism", "Adventure", "Comfort", "Knowledge", "Power", "Peace", "Justice"],
            "motivations": ["Protect others", "Seek knowledge", "Gain power", "Find love", "Avenge wrongs", "Explore the world", "Build something great", "Help the needy", "Discover truth", "Achieve fame"],
            "fears": ["Failure", "Loneliness", "Death", "Betrayal", "Poverty", "Insanity", "Being forgotten", "Hurting others", "Losing control", "The unknown"],
            "quirks": ["Always carries a lucky coin", "Speaks in rhymes", "Collects strange objects", "Never lies", "Always punctual", "Hums while thinking", "Taps fingers when nervous", "Quotes ancient texts", "Always has a plan", "Never gives up"]
        }

        # Background data
        self.background_data = {
            "occupations": ["Warrior", "Scholar", "Merchant", "Artisan", "Noble", "Commoner", "Criminal", "Priest", "Mage", "Explorer"],
            "social_classes": ["Noble", "Merchant", "Artisan", "Commoner", "Outcast", "Slave", "Royal", "Guild Member", "Scholar", "Wanderer"],
            "life_events": ["Lost family", "Found treasure", "Saved someone", "Was betrayed", "Learned magic", "Traveled far", "Fell in love", "Made enemy", "Discovered secret", "Overcame fear"]
        }

        # Skills by character type
        self.skill_data = {
            CharacterType.HERO: ["Combat", "Leadership", "Courage", "Strategy"],
            CharacterType.NPC: ["Local Knowledge", "Gossip", "Trade", "Survival"],
            CharacterType.VILLAIN: ["Deception", "Intimidation", "Strategy", "Power"],
            CharacterType.MERCHANT: ["Haggling", "Appraisal", "Networking", "Travel"],
            CharacterType.GUARD: ["Vigilance", "Combat", "Investigation", "Authority"],
            CharacterType.NOBLE: ["Etiquette", "Politics", "Wealth", "Influence"],
            CharacterType.SCHOLAR: ["Research", "Languages", "History", "Analysis"]
        }

    def generate_name(self, character_type: CharacterType, gender: str, tone: CharacterTone) -> str:
        """Generate appropriate name based on character type and tone"""
        if tone == CharacterTone.FANTASY:
            culture = "fantasy"
        elif tone == CharacterTone.MODERN:
            culture = "western"
        else:
            culture = "western"  # Default

        # Handle non-binary gender by choosing randomly between male/female names
        if gender.lower() == "non-binary":
            gender_key = random.choice(["male", "female"])
        else:
            gender_key = gender.lower()

        first_names = self.name_data[culture][gender_key]
        surnames = self.name_data[culture]["surnames"]

        first_name = random.choice(first_names)
        surname = random.choice(surnames)

        return f"{first_name} {surname}"

    def generate_appearance(self, character_type: CharacterType, tone: CharacterTone) -> CharacterAppearance:
        """Generate character appearance"""
        age = random.randint(18, 80)
        gender = random.choice(["Male", "Female", "Non-binary"])

        # Adjust age based on character type
        if character_type == CharacterType.SCHOLAR:
            age = random.randint(30, 70)
        elif character_type == CharacterType.HERO:
            age = random.randint(20, 40)

        return CharacterAppearance(
            age=age,
            gender=gender,
            height=random.choice(self.appearance_data["heights"]),
            weight=random.choice(self.appearance_data["weights"]),
            hair_color=random.choice(self.appearance_data["hair_colors"]),
            eye_color=random.choice(self.appearance_data["eye_colors"]),
            skin_tone=random.choice(self.appearance_data["skin_tones"]),
            distinguishing_features=random.sample([
                "Scar on face", "Tattoo", "Piercing", "Unusual birthmark",
                "Heterochromia", "Missing finger", "Limp", "Accent", "Stutter", "Perfect posture"
            ], random.randint(1, 3)),
            clothing_style=random.choice([
                "Practical", "Elegant", "Ragged", "Military", "Scholarly",
                "Merchant", "Noble", "Mysterious", "Colorful", "Dark"
            ])
        )

    def generate_personality(self, character_type: CharacterType) -> CharacterPersonality:
        """Generate character personality"""
        return CharacterPersonality(
            primary_trait=random.choice(self.personality_data["primary_traits"]),
            secondary_trait=random.choice(self.personality_data["secondary_traits"]),
            motivation=random.choice(self.personality_data["motivations"]),
            fear=random.choice(self.personality_data["fears"]),
            secret=random.choice([
                "Has a secret family", "Is actually royalty", "Killed someone in self-defense",
                "Has magical powers", "Is being hunted", "Stole something valuable",
                "Is in love with enemy", "Has a terminal illness", "Is from another world",
                "Made a deal with a demon"
            ]),
            quirk=random.choice(self.personality_data["quirks"]),
            speech_pattern=random.choice([
                "Formal", "Casual", "Scholarly", "Rough", "Poetic", "Direct",
                "Cryptic", "Humble", "Arrogant", "Wise"
            ]),
            mannerisms=random.sample([
                "Taps fingers", "Adjusts glasses", "Touches weapon", "Strokes beard",
                "Fidgets", "Stands straight", "Leans forward", "Crosses arms",
                "Nods frequently", "Avoids eye contact"
            ], random.randint(1, 3))
        )

    def generate_background(self, character_type: CharacterType, tone: CharacterTone) -> CharacterBackground:
        """Generate character background"""
        occupation = random.choice(self.background_data["occupations"])
        social_class = random.choice(self.background_data["social_classes"])

        # Adjust based on character type
        if character_type == CharacterType.NOBLE:
            social_class = "Noble"
            occupation = "Noble"
        elif character_type == CharacterType.MERCHANT:
            occupation = "Merchant"
            social_class = "Merchant"
        elif character_type == CharacterType.GUARD:
            occupation = "Guard"
            social_class = "Commoner"

        return CharacterBackground(
            birthplace=random.choice([
                "Small village", "Large city", "Mountain town", "Coastal port",
                "Desert oasis", "Forest settlement", "Capital city", "Border town",
                "Island community", "Underground city"
            ]),
            family_status=random.choice([
                "Orphan", "Single parent", "Large family", "Only child",
                "Adopted", "Estranged", "Close family", "Dysfunctional", "Royal blood", "Unknown"
            ]),
            education=random.choice([
                "Self-taught", "Village school", "City academy", "University",
                "Military training", "Apprenticeship", "Monastery", "Guild school",
                "Private tutor", "Street smarts"
            ]),
            occupation=occupation,
            social_class=social_class,
            life_events=random.sample(self.background_data["life_events"], random.randint(2, 4)),
            relationships=random.sample([
                "Has a mentor", "Lost a loved one", "Has a rival", "Is married",
                "Has children", "Is in love", "Has a best friend", "Is alone",
                "Has enemies", "Has a secret admirer"
            ], random.randint(1, 3)),
            goals=random.sample([
                "Find true love", "Become famous", "Get revenge", "Save the world",
                "Learn everything", "Build an empire", "Find family", "Achieve peace",
                "Discover truth", "Protect others"
            ], random.randint(1, 3))
        )

    def generate_stats(self, character_type: CharacterType) -> CharacterStats:
        """Generate character statistics"""
        # Base stats
        stats = CharacterStats()

        # Adjust based on character type
        if character_type == CharacterType.HERO:
            stats.strength += random.randint(1, 4)
            stats.charisma += random.randint(1, 3)
        elif character_type == CharacterType.SCHOLAR:
            stats.intelligence += random.randint(2, 5)
            stats.wisdom += random.randint(1, 3)
        elif character_type == CharacterType.MERCHANT:
            stats.charisma += random.randint(2, 4)
            stats.intelligence += random.randint(1, 3)
        elif character_type == CharacterType.GUARD:
            stats.strength += random.randint(2, 4)
            stats.constitution += random.randint(1, 3)

        # Add some randomness
        for stat in ['strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma']:
            current_value = getattr(stats, stat)
            adjustment = random.randint(-2, 2)
            new_value = max(3, min(20, current_value + adjustment))
            setattr(stats, stat, new_value)

        return stats

    def generate_character(self,
                          character_type: CharacterType = CharacterType.HERO,
                          tone: CharacterTone = CharacterTone.REALISTIC,
                          level: int = 1) -> Character:
        """Generate a complete character"""

        # Generate basic info
        gender = random.choice(["Male", "Female", "Non-binary"])
        name = self.generate_name(character_type, gender, tone)

        # Generate all components
        appearance = self.generate_appearance(character_type, tone)
        personality = self.generate_personality(character_type)
        background = self.generate_background(character_type, tone)
        stats = self.generate_stats(character_type)

        # Calculate derived stats
        hit_points = 10 + stats.get_modifier('constitution') + (level - 1) * (5 + stats.get_modifier('constitution'))

        # Get skills for character type
        skills = self.skill_data.get(character_type, ["Survival", "Perception"])

        # Generate equipment based on character type and background
        equipment = self._generate_equipment(character_type, background.occupation)

        # Generate spells if applicable
        spells = self._generate_spells(character_type, level)

        return Character(
            name=name,
            character_type=character_type,
            tone=tone,
            stats=stats,
            appearance=appearance,
            personality=personality,
            background=background,
            level=level,
            hit_points=hit_points,
            max_hit_points=hit_points,
            skills=skills,
            equipment=equipment,
            spells=spells,
            tags=[character_type.value, tone.value]
        )

    def _generate_equipment(self, character_type: CharacterType, occupation: str) -> List[str]:
        """Generate starting equipment"""
        equipment = []

        # Basic equipment
        equipment.extend(["Clothes", "Backpack", "Rations", "Water skin"])

        # Type-specific equipment
        if character_type == CharacterType.HERO:
            equipment.extend(["Sword", "Shield", "Armor"])
        elif character_type == CharacterType.MERCHANT:
            equipment.extend(["Merchant's scale", "Trade goods", "Coin purse"])
        elif character_type == CharacterType.GUARD:
            equipment.extend(["Spear", "Chain mail", "Badge of office"])
        elif character_type == CharacterType.SCHOLAR:
            equipment.extend(["Books", "Writing materials", "Magnifying glass"])
        elif character_type == CharacterType.NOBLE:
            equipment.extend(["Fine clothes", "Signet ring", "Jewelry"])

        return equipment

    def _generate_spells(self, character_type: CharacterType, level: int) -> List[str]:
        """Generate starting spells"""
        if character_type not in [CharacterType.SCHOLAR, CharacterType.HERO]:
            return []

        basic_spells = ["Detect Magic", "Light", "Mage Hand", "Prestidigitation"]
        combat_spells = ["Magic Missile", "Fire Bolt", "Healing Word", "Cure Wounds"]

        spells = random.sample(basic_spells, min(2, len(basic_spells)))
        if level > 1:
            spells.extend(random.sample(combat_spells, min(level - 1, len(combat_spells))))

        return spells

class CharacterGeneratorAPI:
    """API integration for enhanced character generation"""

    def __init__(self):
        self.core = CharacterGeneratorCore()
        self.random_user_url = "https://randomuser.me/api/"

    async def get_random_user_data(self, nationality: str = "US") -> Optional[Dict]:
        """Get random user data from API"""
        try:
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE

            connector = aiohttp.TCPConnector(ssl=ssl_context)
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get(self.random_user_url, params={"nat": nationality}) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("results", [{}])[0]
        except Exception as e:
            logger.warning(f"Random User API failed: {e}")
        return None

    async def enhance_character_with_api(self, character: Character) -> Character:
        """Enhance character with real user data"""
        try:
            user_data = await self.get_random_user_data()
            if user_data:
                # Update character with real data
                character.name = f"{user_data['name']['first']} {user_data['name']['last']}"
                character.appearance.portrait_url = user_data['picture']['medium']

                # Add contact info to background
                contact_info = {
                    "email": user_data.get('email', ''),
                    "phone": user_data.get('phone', ''),
                    "location": f"{user_data['location']['city']}, {user_data['location']['state']}"
                }
                character.background.life_events.append(f"Contact: {contact_info}")

        except Exception as e:
            logger.warning(f"Failed to enhance character with API: {e}")

        return character

# Test functions
def test_character_generation():
    """Test the character generation system"""
    print("🧪 Testing Character Generation System")
    print("=" * 50)

    generator = CharacterGeneratorCore()

    # Test different character types
    character_types = [CharacterType.HERO, CharacterType.MERCHANT, CharacterType.SCHOLAR, CharacterType.GUARD]
    tones = [CharacterTone.REALISTIC, CharacterTone.FANTASY]

    for char_type in character_types:
        for tone in tones:
            print(f"\n📝 Generating {char_type.value} ({tone.value})")
            character = generator.generate_character(char_type, tone)
            print(f"   Name: {character.name}")
            print(f"   Summary: {character.get_summary()}")
            print(f"   Stats: STR{character.stats.strength} DEX{character.stats.dexterity} INT{character.stats.intelligence}")
            print(f"   Motivation: {character.personality.motivation}")
            print(f"   Secret: {character.personality.secret}")

async def test_api_enhancement():
    """Test API enhancement"""
    print("\n🌐 Testing API Enhancement")
    print("=" * 50)

    api = CharacterGeneratorAPI()
    generator = CharacterGeneratorCore()

    character = generator.generate_character(CharacterType.HERO, CharacterTone.REALISTIC)
    print(f"Original: {character.name}")

    enhanced = await api.enhance_character_with_api(character)
    print(f"Enhanced: {enhanced.name}")
    if enhanced.appearance.portrait_url:
        print(f"Portrait: {enhanced.appearance.portrait_url}")

if __name__ == "__main__":
    # Run tests
    test_character_generation()
    asyncio.run(test_api_enhancement())
