"""
D&D Spell System
Supports spell scrolls, spell learning, and spell casting with mana costs.
"""

import random
from typing import Dict, List, Optional, Any
from enum import Enum


class SpellSchool(Enum):
    """Schools of magic."""
    FIRE = "Fire"
    ICE = "Ice"
    LIGHTNING = "Lightning"
    HOLY = "Holy"
    DARK = "Dark"
    NATURE = "Nature"
    ARCANE = "Arcane"
    ILLUSION = "Illusion"


class SpellType(Enum):
    """Types of spell effects."""
    DAMAGE = "Damage"
    HEAL = "Heal"
    BUFF = "Buff"
    DEBUFF = "Debuff"
    SUMMON = "Summon"
    UTILITY = "Utility"


class Spell:
    """Represents a spell that can be cast."""

    def __init__(
        self,
        spell_id: str,
        name: str,
        school: SpellSchool,
        spell_type: SpellType,
        level: int,
        mana_cost: int,
        description: str,
        damage: tuple = None,  # (min, max) damage
        heal: tuple = None,  # (min, max) healing
        duration: int = 0,  # Turns for buffs/debuffs
        effect: Dict[str, Any] = None,  # Additional effects
        aoe: bool = False,  # Area of effect
        cooldown: int = 0,  # Cooldown in turns
    ):
        self.spell_id = spell_id
        self.name = name
        self.school = school
        self.spell_type = spell_type
        self.level = level
        self.mana_cost = mana_cost
        self.description = description
        self.damage = damage or (0, 0)
        self.heal = heal or (0, 0)
        self.duration = duration
        self.effect = effect or {}
        self.aoe = aoe
        self.cooldown = cooldown

    def cast(self, caster: "Character", target: "Character" = None) -> Dict[str, Any]:
        """
        Cast the spell.

        Returns:
            Dict with result information
        """
        result = {
            "success": False,
            "message": "",
            "damage": 0,
            "heal": 0,
            "effects": []
        }

        # Check if caster has enough mana
        if not hasattr(caster, 'mana') or caster.mana < self.mana_cost:
            result["message"] = f"Not enough mana! Need {self.mana_cost}, have {getattr(caster, 'mana', 0)}"
            return result

        # Consume mana
        caster.mana -= self.mana_cost
        result["success"] = True

        # Apply spell effects
        if self.spell_type == SpellType.DAMAGE and target:
            damage = random.randint(self.damage[0], self.damage[1])
            # Add intelligence modifier for magic users
            if hasattr(caster, 'get_ability_modifier'):
                damage += caster.get_ability_modifier('INT')
            result["damage"] = damage
            if hasattr(target, 'take_damage'):
                target.take_damage(damage)
            result["message"] = f"{caster.name} casts {self.name} dealing {damage} {self.school.value} damage!"

        elif self.spell_type == SpellType.HEAL:
            heal = random.randint(self.heal[0], self.heal[1])
            heal_target = target if target else caster
            if hasattr(heal_target, 'hp'):
                old_hp = heal_target.hp
                heal_target.hp = min(heal_target.max_hp, heal_target.hp + heal)
                actual_heal = heal_target.hp - old_hp
                result["heal"] = actual_heal
                result["message"] = f"{caster.name} casts {self.name} healing {actual_heal} HP!"

        elif self.spell_type == SpellType.BUFF:
            if self.effect and target:
                result["effects"].append(self.effect)
                result["message"] = f"{caster.name} casts {self.name}! {self.description}"

        elif self.spell_type == SpellType.DEBUFF:
            if self.effect and target:
                result["effects"].append(self.effect)
                result["message"] = f"{caster.name} casts {self.name} on {target.name}! {self.description}"

        return result

    def to_dict(self) -> Dict:
        """Convert spell to dictionary."""
        return {
            "spell_id": self.spell_id,
            "name": self.name,
            "school": self.school.value,
            "spell_type": self.spell_type.value,
            "level": self.level,
            "mana_cost": self.mana_cost,
            "description": self.description,
            "damage": self.damage,
            "heal": self.heal,
            "duration": self.duration,
            "aoe": self.aoe,
            "cooldown": self.cooldown
        }


# ============================================================================
# SPELL DEFINITIONS
# ============================================================================

SPELLS = {
    # FIRE SPELLS
    "fireball": Spell(
        spell_id="fireball",
        name="Fireball",
        school=SpellSchool.FIRE,
        spell_type=SpellType.DAMAGE,
        level=3,
        mana_cost=15,
        description="Hurl a ball of fire that explodes on impact",
        damage=(15, 25),
        aoe=True
    ),
    "flame_strike": Spell(
        spell_id="flame_strike",
        name="Flame Strike",
        school=SpellSchool.FIRE,
        spell_type=SpellType.DAMAGE,
        level=1,
        mana_cost=8,
        description="Strike with a blade of flame",
        damage=(8, 12)
    ),
    "meteor": Spell(
        spell_id="meteor",
        name="Meteor",
        school=SpellSchool.FIRE,
        spell_type=SpellType.DAMAGE,
        level=5,
        mana_cost=30,
        description="Call down a meteor from the sky",
        damage=(30, 50),
        aoe=True,
        cooldown=3
    ),

    # ICE SPELLS
    "ice_bolt": Spell(
        spell_id="ice_bolt",
        name="Ice Bolt",
        school=SpellSchool.ICE,
        spell_type=SpellType.DAMAGE,
        level=1,
        mana_cost=6,
        description="Fire a bolt of ice that chills enemies",
        damage=(6, 10),
        effect={"slow": 2}
    ),
    "frost_nova": Spell(
        spell_id="frost_nova",
        name="Frost Nova",
        school=SpellSchool.ICE,
        spell_type=SpellType.DAMAGE,
        level=2,
        mana_cost=12,
        description="Release a wave of frost that freezes nearby enemies",
        damage=(10, 15),
        aoe=True,
        effect={"freeze": 1}
    ),
    "blizzard": Spell(
        spell_id="blizzard",
        name="Blizzard",
        school=SpellSchool.ICE,
        spell_type=SpellType.DAMAGE,
        level=4,
        mana_cost=25,
        description="Summon a blizzard that damages over time",
        damage=(20, 35),
        aoe=True,
        duration=3
    ),

    # LIGHTNING SPELLS
    "lightning_bolt": Spell(
        spell_id="lightning_bolt",
        name="Lightning Bolt",
        school=SpellSchool.LIGHTNING,
        spell_type=SpellType.DAMAGE,
        level=2,
        mana_cost=10,
        description="Strike with a bolt of lightning",
        damage=(12, 18)
    ),
    "chain_lightning": Spell(
        spell_id="chain_lightning",
        name="Chain Lightning",
        school=SpellSchool.LIGHTNING,
        spell_type=SpellType.DAMAGE,
        level=3,
        mana_cost=18,
        description="Lightning that chains between enemies",
        damage=(15, 22),
        aoe=True
    ),
    "thunderstorm": Spell(
        spell_id="thunderstorm",
        name="Thunderstorm",
        school=SpellSchool.LIGHTNING,
        spell_type=SpellType.DAMAGE,
        level=5,
        mana_cost=28,
        description="Summon a thunderstorm that strikes randomly",
        damage=(25, 40),
        aoe=True,
        duration=4
    ),

    # HOLY SPELLS
    "heal": Spell(
        spell_id="heal",
        name="Heal",
        school=SpellSchool.HOLY,
        spell_type=SpellType.HEAL,
        level=1,
        mana_cost=10,
        description="Restore health to yourself or an ally",
        heal=(15, 25)
    ),
    "divine_shield": Spell(
        spell_id="divine_shield",
        name="Divine Shield",
        school=SpellSchool.HOLY,
        spell_type=SpellType.BUFF,
        level=2,
        mana_cost=15,
        description="Grant invulnerability for a short time",
        duration=2,
        effect={"invulnerable": True}
    ),
    "resurrection": Spell(
        spell_id="resurrection",
        name="Resurrection",
        school=SpellSchool.HOLY,
        spell_type=SpellType.HEAL,
        level=5,
        mana_cost=50,
        description="Bring an ally back from death",
        heal=(50, 50),
        cooldown=5
    ),

    # DARK SPELLS
    "shadow_bolt": Spell(
        spell_id="shadow_bolt",
        name="Shadow Bolt",
        school=SpellSchool.DARK,
        spell_type=SpellType.DAMAGE,
        level=1,
        mana_cost=7,
        description="Fire a bolt of dark energy",
        damage=(7, 11)
    ),
    "life_drain": Spell(
        spell_id="life_drain",
        name="Life Drain",
        school=SpellSchool.DARK,
        spell_type=SpellType.DAMAGE,
        level=3,
        mana_cost=16,
        description="Drain life from enemy and heal yourself",
        damage=(12, 18),
        heal=(12, 18)
    ),
    "curse_of_weakness": Spell(
        spell_id="curse_of_weakness",
        name="Curse of Weakness",
        school=SpellSchool.DARK,
        spell_type=SpellType.DEBUFF,
        level=2,
        mana_cost=12,
        description="Reduce enemy attack power",
        duration=3,
        effect={"attack_reduction": 5}
    ),

    # NATURE SPELLS
    "entangle": Spell(
        spell_id="entangle",
        name="Entangle",
        school=SpellSchool.NATURE,
        spell_type=SpellType.DEBUFF,
        level=1,
        mana_cost=8,
        description="Roots hold enemy in place",
        duration=2,
        effect={"rooted": True}
    ),
    "rejuvenation": Spell(
        spell_id="rejuvenation",
        name="Rejuvenation",
        school=SpellSchool.NATURE,
        spell_type=SpellType.HEAL,
        level=2,
        mana_cost=12,
        description="Heal over time",
        heal=(20, 30),
        duration=3
    ),
    "summon_bear": Spell(
        spell_id="summon_bear",
        name="Summon Bear",
        school=SpellSchool.NATURE,
        spell_type=SpellType.SUMMON,
        level=3,
        mana_cost=20,
        description="Summon a bear companion",
        duration=5,
        cooldown=3
    ),

    # ARCANE SPELLS
    "magic_missile": Spell(
        spell_id="magic_missile",
        name="Magic Missile",
        school=SpellSchool.ARCANE,
        spell_type=SpellType.DAMAGE,
        level=1,
        mana_cost=5,
        description="Unerring bolts of magical force",
        damage=(5, 8)
    ),
    "arcane_blast": Spell(
        spell_id="arcane_blast",
        name="Arcane Blast",
        school=SpellSchool.ARCANE,
        spell_type=SpellType.DAMAGE,
        level=2,
        mana_cost=12,
        description="Blast of pure arcane energy",
        damage=(10, 16)
    ),
    "time_stop": Spell(
        spell_id="time_stop",
        name="Time Stop",
        school=SpellSchool.ARCANE,
        spell_type=SpellType.BUFF,
        level=5,
        mana_cost=40,
        description="Freeze time and act freely",
        duration=2,
        effect={"extra_turn": True},
        cooldown=5
    ),
}


class SpellBook:
    """Manages character's known spells and cooldowns."""

    def __init__(self):
        self.known_spells: Dict[str, Spell] = {}
        self.cooldowns: Dict[str, int] = {}  # spell_id: turns_remaining

    def learn_spell(self, spell_id: str) -> bool:
        """Learn a new spell."""
        if spell_id in SPELLS:
            self.known_spells[spell_id] = SPELLS[spell_id]
            return True
        return False

    def forget_spell(self, spell_id: str) -> bool:
        """Forget a spell."""
        if spell_id in self.known_spells:
            del self.known_spells[spell_id]
            if spell_id in self.cooldowns:
                del self.cooldowns[spell_id]
            return True
        return False

    def can_cast(self, spell_id: str, caster: "Character") -> tuple:
        """
        Check if spell can be cast.

        Returns:
            (can_cast: bool, reason: str)
        """
        if spell_id not in self.known_spells:
            return False, "Spell not known"

        spell = self.known_spells[spell_id]

        # Check cooldown
        if spell_id in self.cooldowns and self.cooldowns[spell_id] > 0:
            return False, f"On cooldown ({self.cooldowns[spell_id]} turns remaining)"

        # Check mana
        if not hasattr(caster, 'mana') or caster.mana < spell.mana_cost:
            return False, f"Not enough mana (need {spell.mana_cost}, have {getattr(caster, 'mana', 0)})"

        return True, "Can cast"

    def cast_spell(self, spell_id: str, caster: "Character", target: "Character" = None) -> Dict[str, Any]:
        """Cast a spell from the spellbook."""
        can_cast, reason = self.can_cast(spell_id, caster)
        if not can_cast:
            return {"success": False, "message": reason}

        spell = self.known_spells[spell_id]
        result = spell.cast(caster, target)

        # Apply cooldown if spell was cast successfully
        if result["success"] and spell.cooldown > 0:
            self.cooldowns[spell_id] = spell.cooldown

        return result

    def update_cooldowns(self):
        """Reduce all cooldowns by 1 turn."""
        for spell_id in list(self.cooldowns.keys()):
            self.cooldowns[spell_id] -= 1
            if self.cooldowns[spell_id] <= 0:
                del self.cooldowns[spell_id]

    def to_dict(self) -> Dict:
        """Convert spellbook to dictionary."""
        return {
            "known_spells": list(self.known_spells.keys()),
            "cooldowns": self.cooldowns
        }


def create_spell_scroll(spell_id: str) -> Dict[str, Any]:
    """Create a spell scroll item."""
    if spell_id not in SPELLS:
        return None

    spell = SPELLS[spell_id]
    return {
        "item_id": f"scroll_{spell_id}",
        "name": f"Scroll of {spell.name}",
        "type": "consumable",
        "subtype": "scroll",
        "spell_id": spell_id,
        "description": f"A scroll containing the {spell.name} spell. One-time use.",
        "value": spell.level * 50,
        "rarity": "magic" if spell.level <= 2 else "rare" if spell.level <= 4 else "epic"
    }


def get_class_starting_spells(char_class: str) -> List[str]:
    """Get starting spells for a character class."""
    starting_spells = {
        "Wizard": ["magic_missile", "flame_strike", "ice_bolt"],
        "Cleric": ["heal", "divine_shield"],
        "Rogue": ["shadow_bolt"],
        "Fighter": []  # No spells
    }
    return starting_spells.get(char_class, [])
