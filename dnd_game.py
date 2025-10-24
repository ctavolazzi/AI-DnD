import random
import logging
import sys
from typing import List
from narrative_engine import NarrativeEngine
from items import Inventory, get_loot_from_enemy

# Get logger without adding handlers (main.py will configure logging)
logger = logging.getLogger("dnd_game")

class GameError(Exception):
    """Custom exception for game-related errors."""
    pass

class Character:
    def __init__(self, name: str, char_class: str, hp: int = None, max_hp: int = None, attack: int = None, defense: int = None):
        self.name = name
        self.char_class = char_class
        self.team = None

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

        # Initialize inventory system
        self.inventory = Inventory(capacity=20)

        # Give starting equipment based on class
        self._give_starting_equipment(char_class)

        # Initialize D&D ability scores based on class
        self.ability_scores = self._generate_ability_scores(char_class)

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
            self.inventory.equip("mace")
        else:
            # Monsters/enemies get basic items
            self.inventory.add_item("rusty_dagger", 1)
            self.inventory.add_item("gold_coin", random.randint(1, 10))

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
            logger.info(f"Rolling with advantage: {roll1}, {roll2} -> {result}")
            return result
        elif disadvantage and not advantage:
            roll2 = random.randint(1, 20)
            result = min(roll1, roll2)
            logger.info(f"Rolling with disadvantage: {roll1}, {roll2} -> {result}")
            return result
        else:
            logger.info(f"Rolling d20: {roll1}")
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
        logger.info(f"{self.name} {ability} check{proficiency_str}: {roll} + {modifier} = {total} vs DC {dc} -> {'SUCCESS' if success else 'FAILURE'}")

        if roll == 20:
            logger.info(f"NATURAL 20! Critical success!")
        elif roll == 1:
            logger.info(f"NATURAL 1! Critical failure!")

        return result

    def take_damage(self, damage: int) -> dict:
        """
        Apply damage to character and return loot if character dies.

        Returns:
            Dict with 'died' bool and 'loot' dict of item_id: quantity
        """
        if damage < 0:
            raise ValueError("Damage cannot be negative.")

        old_hp = self.hp
        logger.info(f"Damage Calculation:")
        logger.info(f"- Incoming Damage: {damage}")
        logger.info(f"- Target Defense: {self.defense}")
        actual_damage = max(0, damage - self.defense)
        logger.info(f"- Final Damage: {damage} - {self.defense} = {actual_damage}")
        self.hp = max(0, old_hp - actual_damage)

        if actual_damage > 0:
            logger.info(f"Result: {self.name} takes {actual_damage} damage! (HP: {old_hp} -> {self.hp})")

        result = {"died": False, "loot": {}}

        if self.hp <= 0:
            self.alive = False
            logger.info(f"Critical Event: {self.name} has fallen!")

            # Generate loot if this is an enemy
            if self.team == "enemies":
                loot = get_loot_from_enemy(self.char_class)
                result["died"] = True
                result["loot"] = loot
                logger.info(f"Loot dropped: {loot}")

        return result

    def _heavy_strike(self, target: "Character") -> dict:
        logger.info(f"{self.name} performs Heavy Strike on {target.name}!")
        damage = self.attack * 2
        return target.take_damage(damage)

    def _fireball(self, target: "Character") -> dict:
        logger.info(f"{self.name} casts Fireball on {target.name}!")
        damage = random.randint(15, 20)
        return target.take_damage(damage)

    def _backstab(self, target: "Character") -> dict:
        original_defense = target.defense
        target.defense = max(0, target.defense - 2)
        logger.info(f"{self.name} performs Backstab on {target.name}, reducing defense from {original_defense} to {target.defense}")
        damage = int(self.attack * 1.5)
        return target.take_damage(damage)

    def _cheap_shot(self, target: "Character") -> dict:
        if random.random() < 0.3 and "stunned" not in target.status_effects:
            target.status_effects.append("stunned")
            logger.info(f"{target.name} is stunned by {self.name}!")
        logger.info(f"{self.name} performs Cheap Shot on {target.name}!")
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
            logger.info(f"{self.name} heals {target.name} for {actual_heal} HP (from {old_hp} to {target.hp})")

    def _bone_shield(self, target: "Character") -> dict:
        self.defense *= 2
        logger.info(f"{self.name} uses Bone Shield to double defense to {self.defense}!")
        return {"died": False, "loot": {}}

    def _rage(self, target: "Character") -> dict:
        self.attack += 3
        self.defense += 2
        logger.info(f"{self.name} uses Rage! Attack +3, Defense +2")
        # Deal damage after increasing stats
        damage = int(self.attack * 1.5)  # Deal 150% damage like Backstab
        return target.take_damage(damage)

    def _fury(self, target: "Character") -> dict:
        self.attack += 2
        damage = self.attack - target.defense
        result1 = target.take_damage(damage)
        result2 = target.take_damage(damage)
        logger.info(f"{self.name} uses Fury for a double attack on {target.name}!")
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
                                logger.info(f"{self.name} collected {quantity} gold!")
                            else:
                                logger.info(f"{self.name} collected {quantity}x {item_id}")
                        else:
                            logger.info(f"{self.name}'s inventory is full! Couldn't collect {item_id}")
                    result["loot_collected"] = damage_result["loot"]

                return result

            # Normal attack
            logger.info(f"\n{self.name} prepares to attack {target.name}!")
            logger.info(f"Combat Stats:")
            logger.info(f"- Attacker ({self.name}): Attack = {self.attack}, HP = {self.hp}/{self.max_hp}")
            logger.info(f"- Defender ({target.name}): Defense = {target.defense}, HP = {target.hp}/{target.max_hp}")

            roll = random.randint(1, 6)
            damage = self.attack + roll
            logger.info(f"Attack Roll: {roll}")
            logger.info(f"Total Damage = {self.attack} (base) + {roll} (roll) = {damage}")

            damage_result = target.take_damage(damage)
            result["damage_dealt"] = damage

            # Collect loot if target died
            if damage_result["died"] and damage_result["loot"]:
                for item_id, quantity in damage_result["loot"].items():
                    if self.inventory.add_item(item_id, quantity):
                        if item_id == "gold_coin":
                            logger.info(f"{self.name} collected {quantity} gold!")
                        else:
                            logger.info(f"{self.name} collected {quantity}x {item_id}")
                    else:
                        logger.info(f"{self.name}'s inventory is full! Couldn't collect {item_id}")
                result["loot_collected"] = damage_result["loot"]

        return result

    def clear_temporary_effects(self) -> None:
        if "stunned" in self.status_effects:
            self.status_effects.remove("stunned")

class DnDGame:
    def __init__(self, auto_create_characters: bool = True, model: str = "mistral"):
        logger.info("Initializing DnDGame")
        self.players: List[Character] = []
        self.enemies: List[Character] = []
        self.narrative_engine = NarrativeEngine(model)
        self.current_location = "Starting Tavern"
        self.current_quest = None
        self.scene_counter = 0
        if auto_create_characters:
            self._create_characters(generate_intros=False)  # Don't generate intros during init

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
            logger.info(intro)
            intros.append(intro)
        return intros

    def _create_characters(self, generate_intros: bool = False) -> None:
        try:
            self.players = [
                Character(f"Hero {i+1}", random.choice(["Fighter", "Wizard", "Rogue", "Cleric"]))
                for i in range(2)
            ]
            for player in self.players:
                player.team = "players"

            self.enemies = [
                Character(f"Monster {i+1}", random.choice(["Goblin", "Orc", "Skeleton", "Bandit"]))
                for i in range(2)
            ]
            for enemy in self.enemies:
                enemy.team = "enemies"

            # Optionally generate narrative introductions
            if generate_intros:
                self.generate_character_introductions()

        except Exception as e:
            logger.exception("Error creating characters")
            raise GameError(f"Failed to create characters: {str(e)}")

    def play_turn(self) -> None:
        if not self.players or not self.enemies:
            raise GameError("Cannot play turn with no characters")

        all_characters = self.players + self.enemies
        random.shuffle(all_characters)

        # Describe the scene at the start of each turn
        scene_description = self.narrative_engine.describe_scene(
            self.current_location,
            [char.name for char in all_characters if char.alive]
        )
        logger.info(scene_description)

        for char in all_characters:
            if not char.alive:
                continue

            if "stunned" in char.status_effects:
                status_desc = self.narrative_engine.describe_combat(
                    char.name,
                    "themselves",
                    "struggles with the stun effect"
                )
                logger.info(status_desc)
                char.status_effects.remove("stunned")
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
                            logger.info(heal_desc)
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
                        logger.info(combat_desc)

            except Exception as e:
                logger.exception(f"Error during {char.name}'s turn: {e}")

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
        logger.info("\nYour Quest:")
        logger.info(self.current_quest)

        turn_count = 0
        while not self.is_game_over() and turn_count < 100:
            # Generate random encounter every 3 turns
            if turn_count % 3 == 0:
                encounter = self.narrative_engine.generate_random_encounter(
                    party_level=1,
                    environment=self.current_location
                )
                logger.info("\nNew Encounter!")
                logger.info(encounter)

            self.play_turn()
            turn_count += 1

        if any(char.alive for char in self.players):
            victory_desc = self.narrative_engine.handle_player_action(
                "The party",
                "emerges victorious",
                "Final battle concluded"
            )
            logger.info(victory_desc)
        else:
            defeat_desc = self.narrative_engine.handle_player_action(
                "The party",
                "has fallen",
                "Final battle concluded"
            )
            logger.info(defeat_desc)

if __name__ == "__main__":
    try:
        game = DnDGame()
        game.run_game()
    except GameError as ge:
        logger.error(f"Game terminated due to an error: {ge}")
    except Exception as e:
        logger.exception(f"Unhandled exception: {e}")