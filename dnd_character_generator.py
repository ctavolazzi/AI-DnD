"""
D&D Character Generator with Random User API Integration
Enhances character creation with realistic names, backgrounds, and profiles
"""

import random
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from random_user_api import RandomUserAPI, RandomUser, APIError

logger = logging.getLogger(__name__)

@dataclass
class DnDCharacter:
    """Enhanced D&D character with Random User data"""
    name: str
    char_class: str
    race: str
    background: str
    level: int
    hp: int
    max_hp: int
    mana: int
    max_mana: int
    attack: int
    defense: int
    ability_scores: Dict[str, int]
    skills: List[str]
    equipment: List[str]
    spells: List[str]
    bio: str
    location: str
    profile_picture_url: str
    contact_info: Dict[str, str]

    def __str__(self):
        return f"{self.name} - Level {self.level} {self.race} {self.char_class}"

class DnDCharacterGenerator:
    """Enhanced character generator using Random User API"""

    def __init__(self):
        self.api = RandomUserAPI()
        self.races = [
            "Human", "Elf", "Dwarf", "Halfling", "Gnome", "Half-Orc",
            "Half-Elf", "Tiefling", "Dragonborn", "Aasimar"
        ]
        self.classes = [
            "Fighter", "Wizard", "Rogue", "Cleric", "Paladin", "Ranger",
            "Barbarian", "Bard", "Sorcerer", "Warlock", "Monk", "Druid"
        ]
        self.backgrounds = [
            "Acolyte", "Criminal", "Folk Hero", "Noble", "Sage", "Soldier",
            "Charlatan", "Entertainer", "Guild Artisan", "Hermit", "Outlander",
            "Sailor", "Hermit", "Knight", "Merchant", "Pirate", "Scholar"
        ]

        # Fantasy-appropriate nationalities for different races
        self.race_nationalities = {
            "Human": ["US", "GB", "FR", "DE", "ES", "IT"],
            "Elf": ["GB", "FR", "DE", "NO", "NL"],
            "Dwarf": ["DE", "NO", "NL", "GB"],
            "Halfling": ["GB", "IE", "US"],
            "Gnome": ["DE", "NL", "CH"],
            "Half-Orc": ["DE", "NO", "US"],
            "Half-Elf": ["US", "GB", "FR"],
            "Tiefling": ["IT", "ES", "FR"],
            "Dragonborn": ["US", "GB", "DE"],
            "Aasimar": ["US", "GB", "FR"]
        }

    def generate_character(self,
                          char_class: Optional[str] = None,
                          race: Optional[str] = None,
                          level: int = 1,
                          background: Optional[str] = None,
                          use_api: bool = True) -> DnDCharacter:
        """
        Generate a complete D&D character with Random User API data

        Args:
            char_class: Character class (random if None)
            race: Character race (random if None)
            level: Character level (default 1)
            background: Character background (random if None)
            use_api: Whether to use Random User API for name/bio

        Returns:
            Complete DnDCharacter object
        """
        # Select random values if not provided
        if not char_class:
            char_class = random.choice(self.classes)
        if not race:
            race = random.choice(self.races)
        if not background:
            background = random.choice(self.backgrounds)

        # Get Random User data if API is enabled
        if use_api:
            try:
                nationality = random.choice(self.race_nationalities.get(race, ["US", "GB"]))
                random_user = self.api.get_dnd_npc("villager", nationality)
                name = random_user.full_name
                bio = self._generate_bio(random_user, char_class, race, background)
                location = random_user.location_string
                profile_picture_url = random_user.profile_picture_url
                contact_info = {
                    "email": random_user.email,
                    "phone": random_user.phone,
                    "cell": random_user.cell
                }
            except APIError as e:
                logger.warning(f"API failed, using fallback: {e}")
                name, bio, location, profile_picture_url, contact_info = self._fallback_character_data(char_class, race)
        else:
            name, bio, location, profile_picture_url, contact_info = self._fallback_character_data(char_class, race)

        # Generate character stats
        ability_scores = self._generate_ability_scores(char_class, race)
        hp, max_hp = self._calculate_hp(char_class, level, ability_scores)
        mana, max_mana = self._calculate_mana(char_class, level, ability_scores)
        attack, defense = self._calculate_combat_stats(char_class, level, ability_scores)

        # Generate character features
        skills = self._get_class_skills(char_class)
        equipment = self._get_starting_equipment(char_class, background)
        spells = self._get_starting_spells(char_class, level)

        return DnDCharacter(
            name=name,
            char_class=char_class,
            race=race,
            background=background,
            level=level,
            hp=hp,
            max_hp=max_hp,
            mana=mana,
            max_mana=max_mana,
            attack=attack,
            defense=defense,
            ability_scores=ability_scores,
            skills=skills,
            equipment=equipment,
            spells=spells,
            bio=bio,
            location=location,
            profile_picture_url=profile_picture_url,
            contact_info=contact_info
        )

    def generate_npc(self,
                   npc_type: str = "villager",
                   level: int = 1) -> DnDCharacter:
        """
        Generate an NPC with appropriate class and background

        Args:
            npc_type: Type of NPC ("villager", "merchant", "guard", "noble", "scholar")
            level: NPC level

        Returns:
            DnDCharacter object for NPC
        """
        npc_configs = {
            "villager": {"class": "Commoner", "background": "Folk Hero"},
            "merchant": {"class": "Rogue", "background": "Guild Artisan"},
            "guard": {"class": "Fighter", "background": "Soldier"},
            "noble": {"class": "Paladin", "background": "Noble"},
            "scholar": {"class": "Wizard", "background": "Sage"},
            "priest": {"class": "Cleric", "background": "Acolyte"},
            "bard": {"class": "Bard", "background": "Entertainer"},
            "ranger": {"class": "Ranger", "background": "Outlander"}
        }

        config = npc_configs.get(npc_type, npc_configs["villager"])

        return self.generate_character(
            char_class=config["class"],
            background=config["background"],
            level=level
        )

    def generate_party(self,
                      size: int = 4,
                      level: int = 1,
                      balanced: bool = True) -> List[DnDCharacter]:
        """
        Generate a balanced party of characters

        Args:
            size: Number of characters in party
            level: Character level
            balanced: Whether to ensure balanced party composition

        Returns:
            List of DnDCharacter objects
        """
        party = []

        if balanced and size >= 4:
            # Ensure balanced party with core roles
            core_classes = ["Fighter", "Wizard", "Rogue", "Cleric"]
            for i, char_class in enumerate(core_classes[:size]):
                party.append(self.generate_character(char_class=char_class, level=level))

            # Fill remaining slots with random classes
            remaining = size - len(party)
            for _ in range(remaining):
                party.append(self.generate_character(level=level))
        else:
            # Generate random party
            for _ in range(size):
                party.append(self.generate_character(level=level))

        return party

    def _generate_bio(self, random_user: RandomUser, char_class: str, race: str, background: str) -> str:
        """Generate character biography using Random User data"""
        age = random_user.age
        location = random_user.location_string

        bio_templates = [
            f"{random_user.full_name} is a {age}-year-old {race} {char_class} from {location}. "
            f"Born into a {background.lower()} background, they have traveled far from their homeland "
            f"seeking adventure and purpose.",

            f"A {race} {char_class} with a {background.lower()} background, {random_user.full_name} "
            f"hails from {location}. At {age} years old, they bring wisdom and experience to any party "
            f"they join.",

            f"From the distant lands of {location} comes {random_user.full_name}, a {race} {char_class} "
            f"who once worked as a {background.lower()}. Now {age} years old, they seek new challenges "
            f"and adventures."
        ]

        return random.choice(bio_templates)

    def _fallback_character_data(self, char_class: str, race: str) -> Tuple[str, str, str, str, Dict]:
        """Fallback character data when API is unavailable"""
        fallback_names = {
            "Fighter": ["Marcus Steel", "Thorin Ironfist", "Aria Blade"],
            "Wizard": ["Eldrin Mystic", "Luna Starweaver", "Gandalf"],
            "Rogue": ["Shadow", "Raven", "Whisper"],
            "Cleric": ["Divine Light", "Healer", "Blessed One"]
        }

        name = random.choice(fallback_names.get(char_class, ["Adventurer"]))
        bio = f"A {race} {char_class} seeking adventure and glory."
        location = "Unknown Lands"
        profile_picture_url = ""
        contact_info = {
            "email": f"{name.replace(' ', '').lower()}@adventure.example.com",
            "sending_stone": "Rune-link unavailable"
        }

        return name, bio, location, profile_picture_url, contact_info

    def _generate_ability_scores(self, char_class: str, race: str) -> Dict[str, int]:
        """Generate ability scores based on class and race"""
        # Base ability scores (4d6 drop lowest)
        scores = []
        for _ in range(6):
            rolls = [random.randint(1, 6) for _ in range(4)]
            rolls.sort(reverse=True)
            scores.append(sum(rolls[:3]))

        scores.sort(reverse=True)

        # Assign scores based on class priority
        class_priorities = {
            "Fighter": ["STR", "CON", "DEX", "WIS", "INT", "CHA"],
            "Wizard": ["INT", "CON", "DEX", "WIS", "STR", "CHA"],
            "Rogue": ["DEX", "INT", "CON", "WIS", "STR", "CHA"],
            "Cleric": ["WIS", "CON", "STR", "DEX", "INT", "CHA"],
            "Paladin": ["STR", "CHA", "CON", "WIS", "DEX", "INT"],
            "Ranger": ["DEX", "WIS", "CON", "STR", "INT", "CHA"],
            "Barbarian": ["STR", "CON", "DEX", "WIS", "INT", "CHA"],
            "Bard": ["CHA", "DEX", "CON", "WIS", "INT", "STR"],
            "Sorcerer": ["CHA", "CON", "DEX", "WIS", "INT", "STR"],
            "Warlock": ["CHA", "CON", "DEX", "WIS", "INT", "STR"],
            "Monk": ["DEX", "WIS", "CON", "STR", "INT", "CHA"],
            "Druid": ["WIS", "CON", "DEX", "STR", "INT", "CHA"],
            "Commoner": ["CON", "STR", "DEX", "WIS", "INT", "CHA"]
        }

        priorities = class_priorities.get(char_class, ["STR", "DEX", "CON", "WIS", "INT", "CHA"])

        ability_scores = {}
        for i, ability in enumerate(priorities):
            ability_scores[ability] = scores[i]

        # Apply race bonuses
        race_bonuses = {
            "Human": {"STR": 1, "DEX": 1, "CON": 1, "INT": 1, "WIS": 1, "CHA": 1},
            "Elf": {"DEX": 2, "INT": 1},
            "Dwarf": {"CON": 2, "STR": 1},
            "Halfling": {"DEX": 2, "CHA": 1},
            "Gnome": {"INT": 2, "CON": 1},
            "Half-Orc": {"STR": 2, "CON": 1},
            "Half-Elf": {"CHA": 2, "STR": 1, "DEX": 1},
            "Tiefling": {"CHA": 2, "INT": 1},
            "Dragonborn": {"STR": 2, "CHA": 1},
            "Aasimar": {"CHA": 2, "WIS": 1}
        }

        bonuses = race_bonuses.get(race, {})
        for ability, bonus in bonuses.items():
            ability_scores[ability] += bonus

        return ability_scores

    def _calculate_hp(self, char_class: str, level: int, ability_scores: Dict[str, int]) -> Tuple[int, int]:
        """Calculate hit points based on class and level"""
        con_mod = (ability_scores["CON"] - 10) // 2

        hit_dice = {
            "Fighter": 10, "Paladin": 10, "Ranger": 10, "Barbarian": 12,
            "Wizard": 6, "Sorcerer": 6, "Warlock": 8,
            "Rogue": 8, "Monk": 8, "Bard": 8,
            "Cleric": 8, "Druid": 8,
            "Commoner": 4
        }

        dice_size = hit_dice.get(char_class, 8)
        max_hp = dice_size + con_mod + (level - 1) * (dice_size // 2 + 1 + con_mod)
        hp = max_hp

        return hp, max_hp

    def _calculate_mana(self, char_class: str, level: int, ability_scores: Dict[str, int]) -> Tuple[int, int]:
        """Calculate mana/spell points based on class and level"""
        if char_class in ["Wizard", "Sorcerer", "Warlock", "Bard", "Cleric", "Druid", "Paladin", "Ranger"]:
            # Spellcasting classes
            if char_class in ["Wizard", "Sorcerer", "Warlock"]:
                ability_mod = (ability_scores["CHA"] - 10) // 2 if char_class == "Sorcerer" or char_class == "Warlock" else (ability_scores["INT"] - 10) // 2
            else:
                ability_mod = (ability_scores["WIS"] - 10) // 2

            max_mana = level * 4 + ability_mod * level
            mana = max_mana
        else:
            # Non-spellcasting classes
            max_mana = 0
            mana = 0

        return mana, max_mana

    def _calculate_combat_stats(self, char_class: str, level: int, ability_scores: Dict[str, int]) -> Tuple[int, int]:
        """Calculate attack and defense bonuses"""
        if char_class in ["Fighter", "Paladin", "Ranger", "Barbarian"]:
            attack_mod = (ability_scores["STR"] - 10) // 2
        elif char_class in ["Rogue", "Monk"]:
            attack_mod = (ability_scores["DEX"] - 10) // 2
        else:
            attack_mod = (ability_scores["STR"] - 10) // 2

        attack = attack_mod + level
        defense = 10 + (ability_scores["DEX"] - 10) // 2 + level // 2

        return attack, defense

    def _get_class_skills(self, char_class: str) -> List[str]:
        """Get class-specific skills"""
        class_skills = {
            "Fighter": ["Athletics", "Intimidation", "Survival"],
            "Wizard": ["Arcana", "History", "Investigation"],
            "Rogue": ["Stealth", "Sleight of Hand", "Perception"],
            "Cleric": ["Religion", "Medicine", "Insight"],
            "Paladin": ["Athletics", "Intimidation", "Religion"],
            "Ranger": ["Animal Handling", "Survival", "Perception"],
            "Barbarian": ["Athletics", "Intimidation", "Survival"],
            "Bard": ["Performance", "Persuasion", "Deception"],
            "Sorcerer": ["Arcana", "Intimidation", "Persuasion"],
            "Warlock": ["Arcana", "Deception", "Intimidation"],
            "Monk": ["Acrobatics", "Athletics", "Stealth"],
            "Druid": ["Animal Handling", "Nature", "Survival"],
            "Commoner": ["Animal Handling", "Survival"]
        }

        return class_skills.get(char_class, ["Athletics", "Perception"])

    def _get_starting_equipment(self, char_class: str, background: str) -> List[str]:
        """Get starting equipment based on class and background"""
        class_equipment = {
            "Fighter": ["Longsword", "Shield", "Chain Mail", "Handaxe"],
            "Wizard": ["Quarterstaff", "Dagger", "Component Pouch", "Scholar's Pack"],
            "Rogue": ["Rapier", "Shortbow", "Leather Armor", "Thieves' Tools"],
            "Cleric": ["Mace", "Shield", "Chain Mail", "Holy Symbol"],
            "Paladin": ["Longsword", "Shield", "Chain Mail", "Holy Symbol"],
            "Ranger": ["Longbow", "Longsword", "Leather Armor", "Dungeoneer's Pack"],
            "Barbarian": ["Greataxe", "Handaxe", "Leather Armor", "Explorer's Pack"],
            "Bard": ["Rapier", "Lute", "Leather Armor", "Entertainer's Pack"],
            "Sorcerer": ["Quarterstaff", "Dagger", "Component Pouch", "Explorer's Pack"],
            "Warlock": ["Quarterstaff", "Dagger", "Leather Armor", "Scholar's Pack"],
            "Monk": ["Shortsword", "Dart", "Explorer's Pack"],
            "Druid": ["Scimitar", "Shield", "Leather Armor", "Druidic Focus"],
            "Commoner": ["Club", "Simple Clothes", "Backpack"]
        }

        equipment = class_equipment.get(char_class, ["Club", "Simple Clothes"])

        # Add background equipment
        background_equipment = {
            "Acolyte": ["Holy Symbol", "Prayer Book"],
            "Criminal": ["Thieves' Tools", "Crowbar"],
            "Folk Hero": ["Artisan's Tools", "Shovel"],
            "Noble": ["Signet Ring", "Fine Clothes"],
            "Sage": ["Ink", "Quill", "Parchment"],
            "Soldier": ["Insignia of Rank", "Playing Cards"]
        }

        equipment.extend(background_equipment.get(background, []))

        return equipment

    def _get_starting_spells(self, char_class: str, level: int) -> List[str]:
        """Get starting spells based on class and level"""
        if level < 1:
            return []

        class_spells = {
            "Wizard": ["Magic Missile", "Detect Magic", "Mage Hand", "Prestidigitation"],
            "Cleric": ["Cure Wounds", "Bless", "Guidance", "Sacred Flame"],
            "Bard": ["Vicious Mockery", "Healing Word", "Charm Person", "Disguise Self"],
            "Sorcerer": ["Fire Bolt", "Mage Hand", "Prestidigitation", "Shield"],
            "Warlock": ["Eldritch Blast", "Mage Hand", "Prestidigitation", "Hex"],
            "Druid": ["Produce Flame", "Guidance", "Druidcraft", "Cure Wounds"],
            "Paladin": ["Cure Wounds", "Bless", "Divine Favor"],
            "Ranger": ["Cure Wounds", "Hunter's Mark", "Goodberry"]
        }

        spells = class_spells.get(char_class, [])

        # Limit spells based on level
        if level == 1:
            spells = spells[:2]  # Only 2 spells at level 1

        return spells

# Convenience functions
def create_random_character(level: int = 1) -> DnDCharacter:
    """Create a random D&D character"""
    generator = DnDCharacterGenerator()
    return generator.generate_character(level=level)

def create_npc(npc_type: str = "villager", level: int = 1) -> DnDCharacter:
    """Create a random NPC"""
    generator = DnDCharacterGenerator()
    return generator.generate_npc(npc_type, level)

def create_party(size: int = 4, level: int = 1) -> List[DnDCharacter]:
    """Create a balanced party"""
    generator = DnDCharacterGenerator()
    return generator.generate_party(size, level)

if __name__ == "__main__":
    # Test the character generator
    generator = DnDCharacterGenerator()

    print("Testing D&D Character Generator with Random User API...")

    try:
        # Test single character
        character = generator.generate_character()
        print(f"\nGenerated Character: {character}")
        print(f"Bio: {character.bio}")
        print(f"Location: {character.location}")
        print(f"Profile Picture: {character.profile_picture_url}")
        print(f"Ability Scores: {character.ability_scores}")
        print(f"Equipment: {character.equipment}")

        # Test NPC
        npc = generator.generate_npc("merchant")
        print(f"\nGenerated NPC: {npc}")
        print(f"NPC Bio: {npc.bio}")

        # Test party
        party = generator.generate_party(4)
        print(f"\nGenerated Party:")
        for i, member in enumerate(party, 1):
            print(f"{i}. {member}")

    except APIError as e:
        print(f"API Error: {e}")
        print("Testing with fallback data...")
        character = generator.generate_character(use_api=False)
        print(f"Fallback Character: {character}")
    except Exception as e:
        print(f"Unexpected error: {e}")
