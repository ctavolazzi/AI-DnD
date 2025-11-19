import random
import logging
import sys
from typing import List, Dict, Any, Optional
from narrative_engine import NarrativeEngine
from items import Inventory, get_loot_from_enemy
from spells import SpellBook, get_class_starting_spells
from backend.app.core.providers import (
    TimeProvider,
    RealTimeProvider,
    LogProvider,
    FileLogProvider,
)

# Get logger without adding handlers (main.py will configure logging)
logger = logging.getLogger("dnd_game")

class GameError(Exception):
    """Custom exception for game-related errors."""
    pass

class Character:
    def __init__(
        self,
        name: str,
        char_class: str,
        hp: int = None,
        max_hp: int = None,
        attack: int = None,
        defense: int = None,
        log_provider: Optional[LogProvider] = None,
        character_id: Optional[str] = None,
    ):
        self.name = name
        self.char_class = char_class
        self.team = None
        self.log_provider = log_provider
        self.id: Optional[str] = character_id

        # Validate character class
        valid_classes = ["Fighter", "Wizard", "Rogue", "Cleric", "Goblin", "Orc", "Skeleton", "Bandit"]
        if char_class not in valid_classes:
            raise GameError(f"Invalid character class: {char_class}")

        # Generate random values if not provided
        if max_hp is None:
            max_hp = random.randint(20, 50)
        if hp is None:
            hp = max_hp
        if attack is None:
            attack = random.randint(5, 15)
        if defense is None:
            defense = random.randint(1, 5)

        self.hp = hp
        self.max_hp = max_hp
        self.attack = attack
        self.defense = defense
        self.alive = True
        self.status_effects: List[str] = []

        # Initialize D&D ability scores based on class
        self.ability_scores = self._generate_ability_scores(char_class)

        # Initialize mana system
        self.max_mana = 50 + (self.get_ability_modifier('INT') * 10)
        self.mana = self.max_mana

        # Initialize inventory system
        self.inventory = Inventory(capacity=20)

        # Initialize spellbook
        self.spellbook = SpellBook()

        # Give starting equipment and spells based on class
        self._give_starting_equipment(char_class)
        self._learn_starting_spells(char_class)

        # Initialize proficiency bonus (starts at +2)
        self.proficiency_bonus = 2

        # Initialize skill proficiencies based on class
        self.skill_proficiencies = self._get_class_proficiencies(char_class)

        # Initialize abilities
        self.abilities = {}
        if char_class == "Fighter":
            self.abilities["Heavy Strike"] = self._heavy_strike
        elif char_class == "Wizard":
            self.abilities["Fireball"] = self._fireball
        elif char_class == "Rogue":
            self.abilities["Backstab"] = self._backstab
            self.abilities["Cheap Shot"] = self._cheap_shot
        elif char_class == "Cleric":
            self.abilities["Heal"] = self._heal
        elif char_class == "Skeleton":
            self.abilities["Bone Shield"] = self._bone_shield
        elif char_class == "Bandit":
            self.abilities["Cheap Shot"] = self._cheap_shot
        elif char_class == "Orc":
            self.abilities["Rage"] = self._rage
        elif char_class == "Goblin":
            self.abilities["Fury"] = self._fury

    def _log(
        self,
        message: str,
        *,
        level: str = "INFO",
        metadata: Optional[Dict[str, Any]] = None,
        exc_info: Optional[BaseException] = None,
    ) -> None:
        """Send character-scoped log messages through the active provider."""
        details = {"character": self.name}
        if metadata:
            details.update(metadata)

        if self.log_provider:
            self.log_provider.log(getattr(logging, level.upper(), logging.INFO), message, extra=details)
            return

        log_fn = getattr(logger, level.lower(), logger.info)
        if exc_info:
            log_fn(message, exc_info=exc_info)
        else:
            log_fn(message)

    def _generate_ability_scores(self, char_class: str) -> dict:
        """Generate D&D ability scores based on class."""
        if char_class == "Fighter":
            return {"STR": 16, "DEX": 12, "CON": 14, "INT": 10, "WIS": 12, "CHA": 10}
        elif char_class == "Wizard":
            return {"STR": 8, "DEX": 12, "CON": 12, "INT": 16, "WIS": 14, "CHA": 10}
        elif char_class == "Rogue":
            return {"STR": 10, "DEX": 16, "CON": 12, "INT": 12, "WIS": 12, "CHA": 14}
        elif char_class == "Cleric":
            return {"STR": 12, "DEX": 10, "CON": 14, "INT": 10, "WIS": 16, "CHA": 12}
        else:  # Monsters
            return {"STR": 12, "DEX": 12, "CON": 12, "INT": 10, "WIS": 10, "CHA": 10}

    def _get_class_proficiencies(self, char_class: str) -> List[str]:
        """Get skill proficiencies based on class."""
        proficiencies = {
            "Fighter": ["Athletics", "Intimidation"],
            "Wizard": ["Arcana", "Investigation"],
            "Rogue": ["Stealth", "Sleight of Hand", "Perception"],
            "Cleric": ["Medicine", "Insight"],
        }
        return proficiencies.get(char_class, ["Perception"])

    def _give_starting_equipment(self, char_class: str) -> None:
        """Give starting equipment based on class."""
        # Starting gold (use add_item with "gold_coin")
        self.inventory.add_item("gold_coin", random.randint(10, 50))

        # Class-specific starting gear
        if char_class == "Fighter":
            self.inventory.add_item("longsword", 1)
            self.inventory.add_item("shield", 1)
            self.inventory.add_item("chainmail", 1)
            self.inventory.equip("longsword")
            self.inventory.equip("chainmail")
        elif char_class == "Wizard":
            self.inventory.add_item("quarterstaff", 1)
            self.inventory.add_item("spellbook", 1)
            self.inventory.add_item("health_potion", 2)
            self.inventory.add_item("mana_potion", 3)
        elif char_class == "Rogue":
            self.inventory.add_item("dagger", 2)
            self.inventory.add_item("lockpicks", 1)
            self.inventory.add_item("leather_armor", 1)
            self.inventory.equip("dagger")
            self.inventory.equip("leather_armor")
        elif char_class == "Cleric":
            self.inventory.add_item("mace", 1)
            self.inventory.add_item("holy_symbol", 1)
            self.inventory.add_item("health_potion", 3)
            self.inventory.add_item("mana_potion", 2)
            self.inventory.equip("mace")
        else:
            # Monsters/enemies get basic items
            self.inventory.add_item("rusty_dagger", 1)
            self.inventory.add_item("gold_coin", random.randint(1, 10))

    def _learn_starting_spells(self, char_class: str) -> None:
        """Learn starting spells based on class."""
        starting_spells = get_class_starting_spells(char_class)
        for spell_id in starting_spells:
            self.spellbook.learn_spell(spell_id)
            self._log(f"{self.name} learned spell: {spell_id}")

    def get_ability_modifier(self, ability: str) -> int:
        """Calculate D&D ability modifier from ability score."""
        score = self.ability_scores.get(ability, 10)
        return (score - 10) // 2

    @staticmethod
    def roll_d20(advantage: bool = False, disadvantage: bool = False) -> int:
        """Roll a d20 with optional advantage/disadvantage."""
        roll1 = random.randint(1, 20)

        if advantage and not disadvantage:
            roll2 = random.randint(1, 20)
            result = max(roll1, roll2)
            # Logging not static, need instance context or global log
            # self._log(f"Rolling with advantage: {roll1}, {roll2} -> {result}")
            return result
        elif disadvantage and not advantage:
            roll2 = random.randint(1, 20)
            result = min(roll1, roll2)
            # self._log(f"Rolling with disadvantage: {roll1}, {roll2} -> {result}")
            return result
        else:
            # self._log(f"Rolling d20: {roll1}")
            return roll1

    def ability_check(self, ability: str, dc: int, skill: str = None,
                     advantage: bool = False, disadvantage: bool = False) -> dict:
        """
        Make an ability check against a DC.

        Args:
            ability: The ability to check (STR, DEX, CON, INT, WIS, CHA)
            dc: Difficulty Class to beat
            skill: Optional skill for proficiency bonus
            advantage: Whether to roll with advantage
            disadvantage: Whether to roll with disadvantage

        Returns:
            Dict with roll, modifier, total, success, and description
        """
        roll = self.roll_d20(advantage, disadvantage)
        modifier = self.get_ability_modifier(ability)

        # Add proficiency if skilled
        if skill and skill in self.skill_proficiencies:
            modifier += self.proficiency_bonus
            proficient = True
        else:
            proficient = False

        total = roll + modifier
        success = total >= dc

        result = {
            "character": self.name,
            "ability": ability,
            "skill": skill,
            "roll": roll,
            "modifier": modifier,
            "total": total,
            "dc": dc,
            "success": success,
            "proficient": proficient,
            "natural_20": roll == 20,
            "natural_1": roll == 1
        }

        # Log the check
        proficiency_str = f" ({skill}, proficient)" if proficient else f" ({skill})" if skill else ""
        self._log(f"{self.name} {ability} check{proficiency_str}: {roll} + {modifier} = {total} vs DC {dc} -> {'SUCCESS' if success else 'FAILURE'}")

        if roll == 20:
            self._log("NATURAL 20! Critical success!")
        elif roll == 1:
            self._log("NATURAL 1! Critical failure!")

        return result

    def cast_spell(self, spell_id: str, target: "Character" = None) -> Dict[str, Any]:
        """
        Cast a spell from spellbook.

        Args:
            spell_id: ID of spell to cast
            target: Optional target character

        Returns:
            Dict with result of spell cast
        """
        return self.spellbook.cast_spell(spell_id, self, target)

    def regenerate_mana(self, amount: int = None) -> None:
        """Regenerate mana (default: 10% of max per turn)."""
        if amount is None:
            amount = max(5, int(self.max_mana * 0.1))
        self.mana = min(self.max_mana, self.mana + amount)
        self._log(f"{self.name} regenerated {amount} mana ({self.mana}/{self.max_mana})", level="DEBUG")

    def take_damage(self, damage: int) -> dict:
        """
        Apply damage to character and return loot if character dies.

        Returns:
            Dict with 'died' bool and 'loot' dict of item_id: quantity
        """
        if damage < 0:
            raise ValueError("Damage cannot be negative.")

        old_hp = self.hp
        self._log("Damage Calculation:")
        self._log(f"- Incoming Damage: {damage}")
        self._log(f"- Target Defense: {self.defense}")
        actual_damage = max(0, damage - self.defense)
        self._log(f"- Final Damage: {damage} - {self.defense} = {actual_damage}")
        self.hp = max(0, old_hp - actual_damage)

        if actual_damage > 0:
            self._log(f"Result: {self.name} takes {actual_damage} damage! (HP: {old_hp} -> {self.hp})")

        result = {"died": False, "loot": {}}

        if self.hp <= 0:
            self.alive = False
            self._log(f"Critical Event: {self.name} has fallen!")

            # Generate loot if this is an enemy
            if self.team == "enemies":
                loot = get_loot_from_enemy(self.char_class)
                result["died"] = True
                result["loot"] = loot
                self._log(f"Loot dropped: {loot}")

        return result

    def _heavy_strike(self, target: "Character") -> dict:
        self._log(f"{self.name} performs Heavy Strike on {target.name}!")
        damage = self.attack * 2
        return target.take_damage(damage)

    def _fireball(self, target: "Character") -> dict:
        self._log(f"{self.name} casts Fireball on {target.name}!")
        damage = random.randint(15, 20)
        return target.take_damage(damage)

    def _backstab(self, target: "Character") -> dict:
        original_defense = target.defense
        target.defense = max(0, target.defense - 2)
        self._log(f"{self.name} performs Backstab on {target.name}, reducing defense from {original_defense} to {target.defense}")
        damage = int(self.attack * 1.5)
        return target.take_damage(damage)

    def _cheap_shot(self, target: "Character") -> dict:
        if random.random() < 0.3 and "stunned" not in target.status_effects:
            target.status_effects.append("stunned")
            self._log(f"{target.name} is stunned by {self.name}!")
        self._log(f"{self.name} performs Cheap Shot on {target.name}!")
        damage = int(self.attack * 1.2)
        return target.take_damage(damage)

    def _heal(self, target: "Character") -> None:
        if not target.alive:
            return
        old_hp = target.hp
        heal_amount = random.randint(1, 20)  # Use full range for random healing
        target.hp = min(target.max_hp, old_hp + heal_amount)
        actual_heal = target.hp - old_hp
        if actual_heal > 0:
            self._log(f"{self.name} heals {target.name} for {actual_heal} HP (from {old_hp} to {target.hp})")

    def _bone_shield(self, target: "Character") -> dict:
        self.defense *= 2
        self._log(f"{self.name} uses Bone Shield to double defense to {self.defense}!")
        return {"died": False, "loot": {}}

    def _rage(self, target: "Character") -> dict:
        self.attack += 3
        self.defense += 2
        self._log(f"{self.name} uses Rage! Attack +3, Defense +2")
        # Deal damage after increasing stats
        damage = int(self.attack * 1.5)  # Deal 150% damage like Backstab
        return target.take_damage(damage)

    def _fury(self, target: "Character") -> dict:
        self.attack += 2
        damage = self.attack - target.defense
        result1 = target.take_damage(damage)
        result2 = target.take_damage(damage)
        self._log(f"{self.name} uses Fury for a double attack on {target.name}!")
        # Return the second result as it includes death/loot if applicable
        return result2 if result2["died"] else result1

    def attack_target(self, target: "Character") -> dict:
        """
        Attack a target and collect loot if they die.

        Returns:
            Dict with combat result including any loot collected
        """
        result = {"damage_dealt": 0, "loot_collected": {}}

        if not self.alive or not target.alive:
            return result

        # Heal ally if possible
        if "Heal" in self.abilities and self.team == target.team and target.hp < target.max_hp:
            self._heal(target)
            return result

        # Attack enemy
        if self.team is None or target.team is None or self.team != target.team:
            if self.abilities and random.random() < 0.3:
                ability = next(iter(self.abilities.values()))
                damage_result = ability(target)

                # Collect loot if target died from ability
                if damage_result.get("died") and damage_result.get("loot"):
                    for item_id, quantity in damage_result["loot"].items():
                        if self.inventory.add_item(item_id, quantity):
                            if item_id == "gold_coin":
                                self._log(f"{self.name} collected {quantity} gold!")
                            else:
                                self._log(f"{self.name} collected {quantity}x {item_id}")
                        else:
                            self._log(f"{self.name}'s inventory is full! Couldn't collect {item_id}")
                    result["loot_collected"] = damage_result["loot"]

                return result

            # Normal attack
            self._log(f"\n{self.name} prepares to attack {target.name}!")
            self._log("Combat Stats:")
            self._log(f"- Attacker ({self.name}): Attack = {self.attack}, HP = {self.hp}/{self.max_hp}")
            self._log(f"- Defender ({target.name}): Defense = {target.defense}, HP = {target.hp}/{target.max_hp}")

            roll = random.randint(1, 6)
            damage = self.attack + roll
            self._log(f"Attack Roll: {roll}")
            self._log(f"Total Damage = {self.attack} (base) + {roll} (roll) = {damage}")

            damage_result = target.take_damage(damage)
            result["damage_dealt"] = damage

            # Collect loot if target died
            if damage_result["died"] and damage_result["loot"]:
                for item_id, quantity in damage_result["loot"].items():
                    if self.inventory.add_item(item_id, quantity):
                        if item_id == "gold_coin":
                            self._log(f"{self.name} collected {quantity} gold!")
                        else:
                            self._log(f"{self.name} collected {quantity}x {item_id}")
                    else:
                        self._log(f"{self.name}'s inventory is full! Couldn't collect {item_id}")
                result["loot_collected"] = damage_result["loot"]

        return result

    def clear_temporary_effects(self) -> None:
        if "stunned" in self.status_effects:
            self.status_effects.remove("stunned")

    # ========== Conversion Methods for Backend Integration ==========

    def to_dict(self) -> Dict[str, Any]:
        """Convert Character to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "name": self.name,
            "char_class": self.char_class,
            "team": self.team,
            "hp": self.hp,
            "max_hp": self.max_hp,
            "mana": self.mana,
            "max_mana": self.max_mana,
            "attack": self.attack,
            "defense": self.defense,
            "ability_scores": self.ability_scores,
            "alive": self.alive,
            "status_effects": self.status_effects,
            "inventory": self.inventory.to_dict() if hasattr(self.inventory, 'to_dict') else {
                "items": self.inventory.items if hasattr(self.inventory, 'items') else {},
                "equipped": self.inventory.equipped if hasattr(self.inventory, 'equipped') else {},
                "capacity": self.inventory.capacity if hasattr(self.inventory, 'capacity') else 20
            },
            "spells": list(self.spellbook.spells.keys()) if hasattr(self.spellbook, 'spells') else [],
            "proficiency_bonus": self.proficiency_bonus,
            "skill_proficiencies": self.skill_proficiencies,
            "abilities": list(self.abilities.keys()) if self.abilities else []
        }

    def to_db_dict(self, char_id: str, session_id: str) -> Dict[str, Any]:
        """Convert Character to dictionary compatible with backend Character (SQLAlchemy) model"""
        inventory_dict = self.inventory.to_dict() if hasattr(self.inventory, 'to_dict') else {
            "items": self.inventory.items if hasattr(self.inventory, 'items') else {},
            "equipped": self.inventory.equipped if hasattr(self.inventory, 'equipped') else {},
            "capacity": self.inventory.capacity if hasattr(self.inventory, 'capacity') else 20
        }

        spells_list = list(self.spellbook.spells.keys()) if hasattr(self.spellbook, 'spells') else []

        return {
            "id": char_id,
            "session_id": session_id,
            "name": self.name,
            "char_class": self.char_class,
            "team": self.team or "players",
            "hp": self.hp,
            "max_hp": self.max_hp,
            "mana": self.mana,
            "max_mana": self.max_mana,
            "attack": self.attack,
            "defense": self.defense,
            "ability_scores": self.ability_scores,
            "alive": self.alive,
            "current_location_id": None,  # Can be set from context
            "status_effects": self.status_effects,
            "inventory": inventory_dict,
            "spells": spells_list,
            "proficiency_bonus": self.proficiency_bonus,
            "skill_proficiencies": self.skill_proficiencies,
            "bio": None  # Can be set if available
        }

    @classmethod
    def from_db_dict(cls, data: Dict[str, Any], log_provider: Optional[LogProvider] = None) -> 'Character':
        """Create Character instance from backend Character model dictionary"""
        char = cls(
            name=data["name"],
            char_class=data["char_class"],
            hp=data.get("hp", data.get("max_hp", 30)),
            max_hp=data.get("max_hp", 30),
            attack=data.get("attack", 10),
            defense=data.get("defense", 5),
            log_provider=log_provider,
            character_id=data.get("id")
        )

        # Set additional fields
        char.team = data.get("team")
        char.mana = data.get("mana", 0)
        char.max_mana = data.get("max_mana", 0)
        char.ability_scores = data.get("ability_scores", {})
        char.alive = data.get("alive", True)
        char.status_effects = data.get("status_effects", [])
        char.proficiency_bonus = data.get("proficiency_bonus", 2)
        char.skill_proficiencies = data.get("skill_proficiencies", [])

        # Restore inventory if provided
        if "inventory" in data and data["inventory"]:
            inv_data = data["inventory"]
            if isinstance(inv_data, dict):
                # Restore gold first (if present)
                if "gold" in inv_data:
                    char.inventory.gold = inv_data["gold"]

                # First add items
                # Handle two formats: {item_id: quantity} or {item_id: {"quantity": qty, "name": "..."}}
                if "items" in inv_data and isinstance(inv_data["items"], dict):
                    for item_id, item_data in inv_data["items"].items():
                        if isinstance(item_data, dict):
                            # Rich format: {"quantity": 5, "name": "Health Potion"}
                            quantity = item_data.get("quantity", 1)
                        else:
                            # Simple format: item_id -> quantity (int)
                            quantity = item_data
                        char.inventory.add_item(item_id, quantity)
                # Then equip items (must exist in inventory first)
                # equipped can be: {slot: item_id} or {slot: {"item_id": "...", "name": "..."}}
                if "equipped" in inv_data and isinstance(inv_data["equipped"], dict):
                    for slot, item_ref in inv_data["equipped"].items():
                        # Handle two formats: string item_id or dict with item_id
                        if isinstance(item_ref, dict):
                            item_id = item_ref.get("item_id")
                        elif isinstance(item_ref, str):
                            item_id = item_ref
                        else:
                            continue

                        # Ensure item exists and equip it
                        if item_id and isinstance(item_id, str):
                            try:
                                if hasattr(char.inventory, 'has_item') and char.inventory.has_item(item_id, 1):
                                    char.inventory.equip(item_id)
                            except (AttributeError, TypeError):
                                # If equip fails, skip - item might not be compatible
                                pass

        # Restore spells if provided
        if "spells" in data and data["spells"]:
            for spell_id in data["spells"]:
                char.spellbook.learn_spell(spell_id)

        return char

    def to_pydantic(self) -> Dict[str, Any]:
        """Convert Character to dictionary compatible with session_service CharacterModel"""
        from session_service.schemas import CharacterModel
        return {
            "name": self.name,
            "char_class": self.char_class,
            "hp": self.hp,
            "max_hp": self.max_hp,
            "alive": self.alive
        }

    # ========== Validation Methods ==========

    def validate(self) -> List[str]:
        """
        Validate character state and return list of issues found.

        Returns:
            List of issue descriptions (empty if valid)
        """
        issues = []

        # HP validation
        if self.hp < 0:
            issues.append(f"Invalid: HP is negative ({self.hp})")
        if self.hp > self.max_hp:
            issues.append(f"Invalid: HP ({self.hp}) exceeds max_hp ({self.max_hp})")
        if self.max_hp <= 0:
            issues.append(f"Invalid: max_hp must be positive ({self.max_hp})")

        # Mana validation
        if self.mana < 0:
            issues.append(f"Invalid: Mana is negative ({self.mana})")
        if self.mana > self.max_mana:
            issues.append(f"Invalid: Mana ({self.mana}) exceeds max_mana ({self.max_mana})")

        # Alive consistency
        if self.hp <= 0 and self.alive:
            issues.append(f"Inconsistent: HP is 0 or negative but alive=True")
        if self.hp > 0 and not self.alive:
            issues.append(f"Inconsistent: HP is positive but alive=False")

        # Attack/Defense validation
        if self.attack < 0:
            issues.append(f"Invalid: Attack is negative ({self.attack})")
        if self.defense < 0:
            issues.append(f"Invalid: Defense is negative ({self.defense})")

        # Ability scores validation
        if self.ability_scores:
            for ability, value in self.ability_scores.items():
                if not isinstance(value, int) or value < 1 or value > 30:
                    issues.append(f"Invalid: {ability} ability score out of range ({value})")

        return issues

    def fix_validation_issues(self) -> List[str]:
        """
        Automatically fix common validation issues.

        Returns:
            List of fixes applied
        """
        fixes = []

        # Fix HP issues
        if self.hp < 0:
            self.hp = 0
            fixes.append("Fixed: Set negative HP to 0")
        if self.hp > self.max_hp:
            self.hp = self.max_hp
            fixes.append(f"Fixed: Reduced HP from {self.hp} to max_hp ({self.max_hp})")

        # Fix mana issues
        if self.mana < 0:
            self.mana = 0
            fixes.append("Fixed: Set negative mana to 0")
        if self.mana > self.max_mana:
            self.mana = self.max_mana
            fixes.append(f"Fixed: Reduced mana to max_mana ({self.max_mana})")

        # Fix alive consistency
        if self.hp <= 0 and self.alive:
            self.alive = False
            fixes.append("Fixed: Set alive=False when HP <= 0")
        if self.hp > 0 and not self.alive:
            self.alive = True
            fixes.append("Fixed: Set alive=True when HP > 0")

        # Fix negative stats
        if self.attack < 0:
            self.attack = 0
            fixes.append("Fixed: Set negative attack to 0")
        if self.defense < 0:
            self.defense = 0
            fixes.append("Fixed: Set negative defense to 0")

        return fixes

class DnDGame:
    def __init__(
        self,
        auto_create_characters: bool = True,
        model: str = "mistral",
        time_provider: Optional[TimeProvider] = None,
        log_provider: Optional[LogProvider] = None
    ):
        self.time_provider: TimeProvider = time_provider or RealTimeProvider()
        self.log_provider: LogProvider = log_provider or FileLogProvider(logger=logger)
        self._log("Initializing DnDGame")
        self.players: List[Character] = []
        self.enemies: List[Character] = []
        self.narrative_engine = NarrativeEngine(model)
        self.current_location = "Starting Tavern"
        self.current_quest = None
        self.scene_counter = 0
        if auto_create_characters:
            self._create_characters(generate_intros=False)  # Don't generate intros during init
        self.turn_delay = 0.0

    def _log(
        self,
        message: str,
        *,
        level: str = "INFO",
        metadata: Optional[Dict[str, Any]] = None,
        exc_info: Optional[BaseException] = None
    ) -> None:
        """Route log output through the injected provider."""
        details = {"component": "DnDGame"}
        if metadata:
            details.update(metadata)

        if self.log_provider:
            self.log_provider.log(getattr(logging, level.upper(), logging.INFO), message, extra=details)
            return

        log_fn = getattr(logger, level.lower(), logger.info)
        if exc_info:
            log_fn(message, exc_info=exc_info)
        else:
            log_fn(message)

    def _pause(self) -> None:
        """Throttle output pacing based on the injected time provider."""
        if self.turn_delay > 0:
            self.time_provider.sleep(self.turn_delay)

    def generate_character_introductions(self):
        """Generate narrative introductions for each character.
        Should be called after session setup is complete."""
        intros = []
        for character in self.players:
            intro = self.narrative_engine.handle_player_action(
                character.name,
                "enters the tavern",
                f"A new {character.char_class} joining the adventure"
            )
            self._log(intro, metadata={"character": character.name})
            intros.append(intro)
        return intros

    def _create_characters(self, generate_intros: bool = False) -> None:
        try:
            self.players = [
                Character(
                    f"Hero {i+1}",
                    random.choice(["Fighter", "Wizard", "Rogue", "Cleric"]),
                    log_provider=self.log_provider
                )
                for i in range(2)
            ]
            for player in self.players:
                player.team = "players"

            self.enemies = [
                Character(
                    f"Monster {i+1}",
                    random.choice(["Goblin", "Orc", "Skeleton", "Bandit"]),
                    log_provider=self.log_provider
                )
                for i in range(2)
            ]
            for enemy in self.enemies:
                enemy.team = "enemies"

            # Optionally generate narrative introductions
            if generate_intros:
                self.generate_character_introductions()

        except Exception as e:
            self._log("Error creating characters", level="ERROR", exc_info=e)
            raise GameError(f"Failed to create characters: {str(e)}")

    def play_turn(self) -> None:
        if not self.players or not self.enemies:
            raise GameError("Cannot play turn with no characters")

        self.scene_counter += 1
        all_characters = self.players + self.enemies
        random.shuffle(all_characters)

        # Describe the scene at the start of each turn
        scene_description = self.narrative_engine.describe_scene(
            self.current_location,
            [char.name for char in all_characters if char.alive]
        )
        self._log(scene_description)

        for char in all_characters:
            if not char.alive:
                continue

            if "stunned" in char.status_effects:
                status_desc = self.narrative_engine.describe_combat(
                    char.name,
                    "themselves",
                    "struggles with the stun effect"
                )
                self._log(status_desc)
                char.status_effects.remove("stunned")
                self._pause()
                continue

            try:
                if "Heal" in char.abilities:
                    heal_target = self._select_heal_target(char)
                    if heal_target:
                        old_hp = heal_target.hp
                        char.attack_target(heal_target)
                        heal_amount = heal_target.hp - old_hp
                        if heal_amount > 0:
                            heal_desc = self.narrative_engine.describe_combat(
                                char.name,
                                heal_target.name,
                                "casts a healing spell on"
                            )
                            self._log(heal_desc)
                        continue

                attack_target = self._select_attack_target(char)
                if attack_target:
                    old_hp = attack_target.hp
                    char.attack_target(attack_target)
                    damage_dealt = old_hp - attack_target.hp
                    if damage_dealt > 0:
                        combat_desc = self.narrative_engine.describe_combat(
                            char.name,
                            attack_target.name,
                            "attacks",
                            damage_dealt
                        )
                        self._log(combat_desc)

            except Exception as e:
                self._log(f"Error during {char.name}'s turn: {e}", level="ERROR", metadata={"character": char.name}, exc_info=e)
            finally:
                self._pause()

    def _select_heal_target(self, char: Character) -> Character:
        valid_targets = [p for p in self.players if p.alive and p.hp < p.max_hp] if char.team == "players" else [e for e in self.enemies if e.alive and e.hp < e.max_hp]
        if not valid_targets:
            return None
        # Sort by HP ratio to heal most damaged first
        valid_targets.sort(key=lambda x: x.hp / x.max_hp)
        return valid_targets[0]

    def _select_attack_target(self, char: Character) -> Character:
        # Get valid targets from the opposite team
        valid_targets = [e for e in self.enemies if e.alive] if char in self.players else [p for p in self.players if p.alive]
        if not valid_targets:
            return None
        # Sort by HP to target weakest first
        valid_targets.sort(key=lambda x: x.hp)
        return valid_targets[0]

    def is_game_over(self) -> bool:
        return not any(char.alive for char in self.players) or not any(char.alive for char in self.enemies)

    def generate_player_action(self, player: Character) -> str:
        """Generate a narrative action for a player character.

        Args:
            player: The character to generate an action for

        Returns:
            A narrative description of the character's action
        """
        actions = [
            "searches the area for hidden treasures",
            "consults with the party about the next move",
            "shares a story of past adventures",
            "prepares equipment for the upcoming challenge",
            "observes the surroundings with a keen eye",
            "takes a moment to rest and recover"
        ]
        action = random.choice(actions)
        return self.narrative_engine.handle_player_action(
            player.name,
            action,
            f"{player.char_class} taking initiative"
        )

    def run_game(self) -> None:
        # Generate initial quest
        self.current_quest = self.narrative_engine.generate_quest()
        self._log("\nYour Quest:")
        self._log(self.current_quest)

        turn_count = 0
        while not self.is_game_over() and turn_count < 100:
            # Generate random encounter every 3 turns
            if turn_count % 3 == 0:
                encounter = self.narrative_engine.generate_random_encounter(
                    party_level=1,
                    environment=self.current_location
                )
                self._log("\nNew Encounter!")
                self._log(encounter)

            self.play_turn()
            self._pause()
            turn_count += 1

        if any(char.alive for char in self.players):
            victory_desc = self.narrative_engine.handle_player_action(
                "The party",
                "emerges victorious",
                "Final battle concluded"
            )
            self._log(victory_desc)
        else:
            defeat_desc = self.narrative_engine.handle_player_action(
                "The party",
                "has fallen",
                "Final battle concluded"
            )
            self._log(defeat_desc)

if __name__ == "__main__":
    try:
        game = DnDGame()
        game.run_game()
    except GameError as ge:
        logger.error(f"Game terminated due to an error: {ge}")
    except Exception as e:
        logger.exception(f"Unhandled exception: {e}")
