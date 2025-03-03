import random
import logging
import sys
from typing import List
from narrative_engine import NarrativeEngine

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

    def take_damage(self, damage: int) -> None:
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

        if self.hp <= 0:
            self.alive = False
            logger.info(f"Critical Event: {self.name} has fallen!")

    def _heavy_strike(self, target: "Character") -> None:
        logger.info(f"{self.name} performs Heavy Strike on {target.name}!")
        damage = self.attack * 2
        target.take_damage(damage)

    def _fireball(self, target: "Character") -> None:
        logger.info(f"{self.name} casts Fireball on {target.name}!")
        damage = random.randint(15, 20)
        target.take_damage(damage)

    def _backstab(self, target: "Character") -> None:
        original_defense = target.defense
        target.defense = max(0, target.defense - 2)
        logger.info(f"{self.name} performs Backstab on {target.name}, reducing defense from {original_defense} to {target.defense}")
        damage = int(self.attack * 1.5)
        target.take_damage(damage)

    def _cheap_shot(self, target: "Character") -> None:
        if random.random() < 0.3 and "stunned" not in target.status_effects:
            target.status_effects.append("stunned")
            logger.info(f"{target.name} is stunned by {self.name}!")
        logger.info(f"{self.name} performs Cheap Shot on {target.name}!")
        damage = int(self.attack * 1.2)
        target.take_damage(damage)

    def _heal(self, target: "Character") -> None:
        if not target.alive:
            return
        old_hp = target.hp
        heal_amount = random.randint(1, 20)  # Use full range for random healing
        target.hp = min(target.max_hp, old_hp + heal_amount)
        actual_heal = target.hp - old_hp
        if actual_heal > 0:
            logger.info(f"{self.name} heals {target.name} for {actual_heal} HP (from {old_hp} to {target.hp})")

    def _bone_shield(self, target: "Character") -> None:
        self.defense *= 2
        logger.info(f"{self.name} uses Bone Shield to double defense to {self.defense}!")

    def _rage(self, target: "Character") -> None:
        self.attack += 3
        self.defense += 2
        logger.info(f"{self.name} uses Rage! Attack +3, Defense +2")
        # Deal damage after increasing stats
        damage = int(self.attack * 1.5)  # Deal 150% damage like Backstab
        target.take_damage(damage)

    def _fury(self, target: "Character") -> None:
        self.attack += 2
        damage = self.attack - target.defense
        target.take_damage(damage)
        target.take_damage(damage)
        logger.info(f"{self.name} uses Fury for a double attack on {target.name}!")

    def attack_target(self, target: "Character") -> None:
        if not self.alive or not target.alive:
            return

        # Heal ally if possible
        if "Heal" in self.abilities and self.team == target.team and target.hp < target.max_hp:
            self._heal(target)
            return

        # Attack enemy
        if self.team is None or target.team is None or self.team != target.team:
            if self.abilities and random.random() < 0.3:
                ability = next(iter(self.abilities.values()))
                ability(target)
                return

            # Normal attack
            logger.info(f"\n{self.name} prepares to attack {target.name}!")
            logger.info(f"Combat Stats:")
            logger.info(f"- Attacker ({self.name}): Attack = {self.attack}, HP = {self.hp}/{self.max_hp}")
            logger.info(f"- Defender ({target.name}): Defense = {target.defense}, HP = {target.hp}/{target.max_hp}")

            roll = random.randint(1, 6)
            damage = self.attack + roll
            logger.info(f"Attack Roll: {roll}")
            logger.info(f"Total Damage = {self.attack} (base) + {roll} (roll) = {damage}")

            target.take_damage(damage)

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
                Character(f"Hero-{i+1}", random.choice(["Fighter", "Wizard", "Rogue", "Cleric"]))
                for i in range(2)
            ]
            for player in self.players:
                player.team = "players"

            self.enemies = [
                Character(f"Monster-{i+1}", random.choice(["Goblin", "Orc", "Skeleton", "Bandit"]))
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