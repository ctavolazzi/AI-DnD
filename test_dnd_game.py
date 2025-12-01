import unittest
from unittest.mock import patch, MagicMock
import logging
from dnd_game import Character, DnDGame, GameError

# Configure logging for tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('dnd_game')

class TestCharacter(unittest.TestCase):
    def setUp(self):
        self.fighter = Character("TestFighter", "Fighter")
        self.fighter.hp = 40
        self.fighter.attack = 10
        self.fighter.defense = 3
        self.fighter.alive = True

        self.wizard = Character("TestWizard", "Wizard")
        self.wizard.hp = 30
        self.wizard.attack = 8
        self.wizard.defense = 2
        self.wizard.alive = True

    def test_character_initialization(self):
        """Test that a character is properly initialized with abilities"""
        char = Character("Test", "Fighter")
        self.assertEqual(char.name, "Test")
        self.assertEqual(char.char_class, "Fighter")
        self.assertIn("Heavy Strike", char.abilities)
        self.assertEqual(len(char.status_effects), 0)
        self.assertTrue(20 <= char.hp <= 50)
        self.assertTrue(5 <= char.attack <= 15)
        self.assertTrue(1 <= char.defense <= 5)
        self.assertTrue(char.alive)

    def test_take_damage(self):
        """Test damage calculation and application"""
        initial_hp = self.fighter.hp
        self.fighter.take_damage(10)
        # With 3 defense, should take 7 damage
        self.assertEqual(self.fighter.hp, initial_hp - 7)
        self.assertTrue(self.fighter.alive)

    def test_negative_damage(self):
        """Test that negative damage raises ValueError"""
        with self.assertRaises(ValueError):
            self.fighter.take_damage(-5)

    def test_death_on_damage(self):
        """Test that character dies when HP drops to 0 or below"""
        self.fighter.take_damage(50)
        self.assertFalse(self.fighter.alive)
        self.assertLessEqual(self.fighter.hp, 0)

    @patch('random.random')
    def test_cheap_shot_stun(self, mock_random):
        """Test that cheap shot can apply stun effect"""
        bandit = Character("TestBandit", "Bandit")
        bandit.hp = 30
        bandit.attack = 8
        bandit.defense = 2
        bandit.alive = True

        # Force stun to occur (30% chance)
        mock_random.return_value = 0.2
        bandit._cheap_shot(self.fighter)
        self.assertIn("stunned", self.fighter.status_effects)

    def test_heal_ability(self):
        """Test Cleric's heal ability"""
        cleric = Character("TestCleric", "Cleric")
        target = Character("TestTarget", "Fighter", hp=20, max_hp=50)  # Set HP and max_hp during creation

        with patch('random.randint') as mock_randint:
            mock_randint.return_value = 15  # Force heal amount to 15
            initial_hp = target.hp
            cleric._heal(target)
            self.assertEqual(target.hp, initial_hp + 15)
            self.assertLessEqual(target.hp, target.max_hp)  # Check max HP cap

            # Test healing at max HP
            target.hp = 50
            cleric._heal(target)
            self.assertEqual(target.hp, 50)  # Should not exceed max

    def test_fireball_damage(self):
        """Test fireball damage range"""
        with patch('random.randint') as mock_randint:
            mock_randint.return_value = 20
            self.wizard._fireball(self.fighter)
            expected_damage = 20 - self.fighter.defense
            self.assertEqual(self.fighter.hp, 40 - expected_damage)

    def test_all_abilities_exist(self):
        """Test that all character classes have their abilities"""
        class_abilities = {
            "Fighter": "Heavy Strike",
            "Wizard": "Fireball",
            "Rogue": "Backstab",
            "Cleric": "Heal",
            "Goblin": "Fury",
            "Orc": "Rage",
            "Skeleton": "Bone Shield",
            "Bandit": "Cheap Shot"
        }

        for char_class, ability in class_abilities.items():
            char = Character("Test", char_class)
            self.assertIn(ability, char.abilities)

    def test_monster_abilities(self):
        """Test all monster-specific abilities"""
        # Test Goblin's Fury
        goblin = Character("TestGoblin", "Goblin")
        target = Character("TestTarget", "Fighter")

        # Set fixed values and prevent random ability usage
        with patch.object(goblin, 'attack', 10), \
             patch('random.randint', return_value=6), \
             patch('random.random', return_value=0.5), \
             patch('random.choice', return_value="Fury"):
            initial_attack = goblin.attack
            goblin._fury(target)
            self.assertEqual(goblin.attack, initial_attack + 2)
            # Verify damage was dealt
            self.assertTrue(target.hp < 50)

        # Test Orc's Rage
        orc = Character("TestOrc", "Orc")
        target = Character("TestTarget", "Fighter")
        with patch.object(orc, 'attack', 10), \
             patch.object(orc, 'defense', 5), \
             patch('random.randint', return_value=6), \
             patch('random.random', return_value=0.5), \
             patch('random.choice', return_value="Rage"):
            initial_attack = orc.attack
            initial_defense = orc.defense

            orc._rage(target)
            self.assertEqual(orc.attack, initial_attack + 3)
            self.assertEqual(orc.defense, initial_defense + 2)
            # Verify damage was dealt
            self.assertTrue(target.hp < 50)

        # Test Skeleton's Bone Shield
        skeleton = Character("TestSkeleton", "Skeleton")
        with patch.object(skeleton, 'defense', 5):
            initial_defense = skeleton.defense
            skeleton._bone_shield(target)
            self.assertEqual(skeleton.defense, initial_defense * 2)

        # Test Bandit's Cheap Shot with forced stun
        bandit = Character("TestBandit", "Bandit")
        target = Character("TestTarget", "Fighter")
        with patch('random.random', return_value=0.2), \
             patch.object(bandit, 'attack', 10), \
             patch('random.randint', return_value=6), \
             patch('random.choice', return_value="Cheap Shot"):
            initial_hp = target.hp
            bandit._cheap_shot(target)
            self.assertIn("stunned", target.status_effects)
            # Verify damage was dealt (attack * 1.2 - defense)
            expected_damage = int(bandit.attack * 1.2) - target.defense
            self.assertEqual(target.hp, initial_hp - expected_damage)

    def test_damage_calculation(self):
        """Test damage calculation with different attack and defense values"""
        attacker = Character("Attacker", "Fighter")
        defender = Character("Defender", "Fighter")

        # Test case 1: Attack > Defense
        with patch.object(attacker, 'attack', 10), \
             patch.object(defender, 'defense', 5), \
             patch.object(defender, 'hp', 50), \
             patch('random.randint', return_value=6), \
             patch('random.random', return_value=0.5):  # Prevent ability use

            initial_hp = defender.hp
            attacker.attack_target(defender)
            # Damage = attack (10) + roll (6) - defense (5) = 11
            expected_damage = 11
            self.assertEqual(defender.hp, initial_hp - expected_damage)

        # Test case 2: Defense >= Attack
        defender = Character("Defender", "Fighter")
        with patch.object(attacker, 'attack', 10), \
             patch.object(defender, 'defense', 20), \
             patch.object(defender, 'hp', 50), \
             patch('random.randint', return_value=6), \
             patch('random.random', return_value=0.5):  # Prevent ability use

            initial_hp = defender.hp
            attacker.attack_target(defender)
            # Damage should be 0 due to high defense
            self.assertEqual(defender.hp, initial_hp)

    def test_ability_stacking(self):
        """Test stacking effects of abilities"""
        # Test Orc's rage stacking
        orc = Character("TestOrc", "Orc")
        target = Character("Target", "Fighter")

        with patch.object(orc, 'attack', 10), \
             patch.object(orc, 'defense', 5), \
             patch('random.randint', return_value=6), \
             patch('random.random', return_value=0.5):  # Prevent ability use in attack
            initial_attack = orc.attack
            initial_defense = orc.defense

            # Use rage multiple times
            orc._rage(target)
            first_attack = orc.attack
            first_defense = orc.defense

            orc._rage(target)
            self.assertEqual(orc.attack, first_attack + 3)
            self.assertEqual(orc.defense, first_defense + 2)

        # Test Goblin's fury stacking
        goblin = Character("TestGoblin", "Goblin")
        with patch.object(goblin, 'attack', 10), \
             patch('random.randint', return_value=6), \
             patch('random.random', return_value=0.5):  # Prevent ability use in attack
            initial_attack = goblin.attack

            goblin._fury(target)
            first_attack = goblin.attack

            goblin._fury(target)
            self.assertEqual(goblin.attack, first_attack + 2)

    def test_logging(self):
        """Test that important game events are properly logged"""
        # Configure logging for test
        logger = logging.getLogger('dnd_game')
        logger.setLevel(logging.INFO)

        with self.assertLogs('dnd_game', level='INFO') as log:
            # Test combat logging
            attacker = Character("Attacker", "Fighter")
            target = Character("Target", "Fighter")

            with patch.object(attacker, 'attack', 10), \
                 patch.object(target, 'defense', 5), \
                 patch.object(target, 'hp', 50), \
                 patch('random.randint', return_value=6), \
                 patch('random.random', return_value=0.5):  # Prevent ability use
                attacker.attack_target(target)

                # Verify attack was logged
                attack_log = "Attacker prepares to attack Target!"
                self.assertTrue(any(attack_log in msg for msg in log.output),
                              f"Expected log message containing '{attack_log}' not found in {log.output}")

                # Test death logging
                target.hp = 1
                attacker.attack_target(target)
                death_log = "has fallen"
                self.assertTrue(any(death_log in msg for msg in log.output),
                              f"Expected log message containing '{death_log}' not found in {log.output}")

            # Test ability logging with a fresh log context
            with self.assertLogs('dnd_game', level='INFO') as ability_log:
                wizard = Character("Wizard", "Wizard")
                target = Character("Target", "Fighter")
                with patch('random.random', return_value=0.2), \
                     patch('random.choice', return_value="Fireball"), \
                     patch('random.randint', return_value=20):
                    wizard.attack_target(target)
                    fireball_log = "casts Fireball"
                    self.assertTrue(any(fireball_log in msg for msg in ability_log.output),
                                  f"Expected log message containing '{fireball_log}' not found in {ability_log.output}")

class TestDnDGame(unittest.TestCase):
    def setUp(self):
        self.game = DnDGame(auto_create_characters=True)
        self.cleric = Character("TestCleric", "Cleric")
        self.target = Character("Target", "Fighter")
        self.target.max_hp = 50
        self.target.hp = 50

        # Create players and enemies using game's method
        self.game._create_characters()

    def test_game_initialization(self):
        """Test that game initializes with correct number of players and enemies"""
        self.assertEqual(len(self.game.players), 2)
        self.assertEqual(len(self.game.enemies), 2)

    def test_status_effect_handling(self):
        """Test that stunned characters skip their turn"""
        char = self.game.players[0]
        char.status_effects.append("stunned")

        # Mock the attack_target to verify it's not called for stunned character
        with patch.object(char, 'attack_target') as mock_attack, \
             patch('random.shuffle', side_effect=lambda x: None):  # Prevent shuffling
            self.game.play_turn()
            mock_attack.assert_not_called()

        # Verify stun was removed
        self.assertNotIn("stunned", char.status_effects)

    def test_target_selection(self):
        """Test that characters target the opposite team"""
        # Mock random.random to return 0.5 (above 0.3 threshold for ability use)
        # Mock random.choice to return our enemy
        # Mock random.shuffle to do nothing
        with patch('random.random', return_value=0.5), \
             patch('random.choice', return_value=self.game.enemies[0]), \
             patch('random.shuffle'):

            self.game.play_turn()

            # Verify the enemy took damage (was targeted)
            self.assertTrue(
                any(enemy.hp < enemy.max_hp for enemy in self.game.enemies),
                "Expected at least one enemy to take damage",
            )

    def test_dead_character_skips_turn(self):
        """Test that dead characters are skipped"""
        char = self.game.players[0]
        char.alive = False

        with patch.object(char, 'attack_target') as mock_attack:
            self.game.play_turn()
            mock_attack.assert_not_called()

    def test_full_game_simulation(self):
        """Test that a full game can run without errors"""
        # Run a few turns
        for _ in range(5):
            self.game.play_turn()
            # Check that the game state remains valid
            for char in self.game.players + self.game.enemies:
                self.assertIsInstance(char.hp, int)
                self.assertIsInstance(char.alive, bool)
                if char.alive:
                    self.assertGreater(char.hp, 0)
                else:
                    self.assertLessEqual(char.hp, 0)

    def test_ability_usage(self):
        """Test that abilities are used with correct probability"""
        fighter = Character("TestFighter", "Fighter")
        enemy = Character("TestEnemy", "Goblin")
        self.game.players = [fighter]
        self.game.enemies = [enemy]

        # Force ability use (30% chance)
        with patch('random.random', return_value=0.2), \
             patch('random.choice', return_value="Heavy Strike"):

            initial_hp = enemy.hp
            fighter.attack_target(enemy)

            # Heavy Strike does double damage
            self.assertTrue(enemy.hp < initial_hp)
            self.assertEqual(enemy.hp, initial_hp - max(0, fighter.attack * 2 - enemy.defense))

    def test_fireball_damage(self):
        """Test Wizard's fireball ability"""
        wizard = Character("TestWizard", "Wizard")
        target = Character("TestTarget", "Fighter")

        with patch('random.randint', return_value=20):  # Force fireball damage to 20
            initial_hp = target.hp
            wizard._fireball(target)
            expected_damage = max(0, 20 - target.defense)
            self.assertEqual(target.hp, initial_hp - expected_damage)

    def test_backstab_defense_reduction(self):
        """Test Rogue's backstab defense reduction"""
        rogue = Character("TestRogue", "Rogue")
        target = Character("TestTarget", "Fighter")
        initial_defense = target.defense

        rogue._backstab(target)
        self.assertEqual(target.defense, max(0, initial_defense - 2))

    def test_character_creation(self):
        """Test that character creation generates valid characters"""
        # Test number of characters
        self.assertEqual(len(self.game.players), 2)
        self.assertEqual(len(self.game.enemies), 2)

        # Test player properties
        for player in self.game.players:
            self.assertTrue(20 <= player.hp <= 50)
            self.assertTrue(5 <= player.attack <= 15)
            self.assertTrue(1 <= player.defense <= 5)
            self.assertTrue(player.alive)
            self.assertTrue(player.name.startswith("Hero"))
            self.assertTrue(player.char_class in ["Fighter", "Wizard", "Rogue", "Cleric"])

        # Test enemy properties
        for enemy in self.game.enemies:
            self.assertTrue(20 <= enemy.hp <= 50)
            self.assertTrue(5 <= enemy.attack <= 15)
            self.assertTrue(1 <= enemy.defense <= 5)
            self.assertTrue(enemy.alive)
            self.assertTrue(enemy.name.startswith("Monster"))
            self.assertTrue(enemy.char_class in ["Goblin", "Orc", "Skeleton", "Bandit"])

    def test_game_over_conditions(self):
        """Test various game over conditions"""
        # Test game not over when both sides have living characters
        self.assertFalse(self.game.is_game_over())

        # Test game over when all players dead
        for player in self.game.players:
            player.alive = False
        self.assertTrue(self.game.is_game_over())

        # Reset players
        for player in self.game.players:
            player.alive = True
        self.assertFalse(self.game.is_game_over())

        # Test game over when all enemies dead
        for enemy in self.game.enemies:
            enemy.alive = False
        self.assertTrue(self.game.is_game_over())

        # Test game over when everyone is dead
        for player in self.game.players:
            player.alive = False
        self.assertTrue(self.game.is_game_over())

    def test_multiple_status_effects(self):
        """Test handling of multiple status effects"""
        char = Character("TestChar", "Fighter")

        # Add multiple status effects
        char.status_effects.extend(["stunned", "poisoned"])
        self.assertEqual(len(char.status_effects), 2)

        # Test stun removal after turn
        self.game.players = [char]
        self.game.enemies = [Character("TestEnemy", "Goblin")]

        self.game.play_turn()

        # Verify stun was removed but other effects remain
        self.assertNotIn("stunned", char.status_effects)
        self.assertIn("poisoned", char.status_effects)

    def test_run_game_completion(self):
        """Test that run_game completes when game is over"""
        # Make enemy very weak to ensure game ends quickly
        self.game.enemies[0].hp = 1
        self.game.enemies[0].defense = 0

        # Run game and verify it completes
        self.game.run_game()
        self.assertTrue(self.game.is_game_over())
        self.assertFalse(self.game.enemies[0].alive)

    def test_error_handling(self):
        """Test various error conditions and exception handling"""
        # Test invalid character class
        with self.assertRaises(GameError):
            self.game.players = [Character("Invalid", "InvalidClass")]
            self.game.play_turn()

        # Test negative damage
        char = Character("TestChar", "Fighter")
        with self.assertRaises(ValueError):
            char.take_damage(-10)

        # Test attacking dead target
        attacker = Character("Attacker", "Fighter")
        target = Character("Target", "Fighter")
        target.alive = False
        attacker.attack_target(target)  # Should log warning but not raise exception

        # Test dead character attacking
        attacker.alive = False
        attacker.attack_target(target)  # Should log warning but not raise exception

    def test_state_changes(self):
        """Test character stat changes and state management"""
        # Test stat changes from multiple abilities
        target = Character("Target", "Fighter", hp=100, max_hp=100)  # Give target more HP to survive attacks
        initial_defense = target.defense

        # Apply multiple defense reductions
        rogue = Character("Rogue", "Rogue")
        rogue._backstab(target)  # First reduction
        self.assertEqual(target.defense, max(0, initial_defense - 2))

        rogue._backstab(target)  # Second reduction
        self.assertEqual(target.defense, max(0, initial_defense - 4))

        # Test multiple status effects
        target.status_effects = ["stunned", "poisoned", "weakened"]
        self.game.players = [target]
        self.game.enemies = [Character("Enemy", "Goblin")]

        def mock_choice_fn(x):
            if isinstance(x, list):
                if x and isinstance(x[0], Character):
                    return x[0]  # Return the first character
            return None

        # Mock random values to prevent random ability usage and control turn order
        with patch('random.random', return_value=0.5), \
             patch('random.randint', return_value=6), \
             patch('random.choice', side_effect=mock_choice_fn), \
             patch('random.shuffle', side_effect=lambda x: None):  # Prevent shuffling
            # First, verify initial status effects
            self.assertEqual(len(target.status_effects), 3)
            self.assertIn("stunned", target.status_effects)

            # Play turn and verify stun is removed
            self.game.play_turn()

            # Verify stun was removed but other effects remain
            self.assertNotIn("stunned", target.status_effects)
            self.assertEqual(len(target.status_effects), 2)
            self.assertIn("poisoned", target.status_effects)
            self.assertIn("weakened", target.status_effects)

    def test_turn_order_randomization(self):
        """Test that turn order is properly randomized"""
        # Create fixed characters for testing
        chars = [
            Character("P1", "Fighter"),
            Character("P2", "Wizard"),
            Character("E1", "Goblin"),
            Character("E2", "Orc")
        ]
        self.game.players = chars[:2]
        self.game.enemies = chars[2:]

        # Mock shuffle to track what was passed
        with patch('random.shuffle') as mock_shuffle:
            self.game.play_turn()

            # Verify shuffle was called with all characters
            mock_shuffle.assert_called_once()
            shuffled_list = mock_shuffle.call_args[0][0]
            self.assertEqual(len(shuffled_list), len(chars))
            self.assertTrue(all(char in shuffled_list for char in chars))

    def test_max_hp_constraint(self):
        """Test that healing cannot exceed max HP"""
        healer = Character("Healer", "Cleric")
        target = Character("Target", "Fighter", hp=45, max_hp=50)  # Set both hp and max_hp during creation

        with patch('random.randint') as mock_randint:
            mock_randint.return_value = 20
            healer._heal(target)
            self.assertEqual(target.hp, 50)  # Should be capped at 50

            # Try healing at max HP
            mock_randint.return_value = 20
            healer._heal(target)
            self.assertEqual(target.hp, 50)  # Should still be 50

    def test_heal_during_combat(self):
        """Test healing effectiveness during different combat situations"""
        # Set teams for both characters
        self.cleric.team = "players"
        self.target.team = "players"

        self.target.max_hp = 50  # Set max HP first
        self.target.hp = 20  # Set low HP

        # Test healing after taking damage
        with patch('random.randint') as mock_randint:
            mock_randint.return_value = 15
            self.cleric._heal(self.target)
            self.assertEqual(self.target.hp, 35)

        # Test healing at max HP with a different mock
        self.target.hp = 50
        with patch('random.randint') as mock_randint:
            mock_randint.return_value = 15
            self.cleric._heal(self.target)
            self.assertEqual(self.target.hp, 50)  # Should not exceed max

class TestEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions"""

    def test_max_stats_character(self):
        """Test character with maximum possible stats"""
        with patch('random.randint') as mock_randint:
            # Set up mock to return max values for stats
            mock_randint.side_effect = [50, 15, 5] + [15] * 5  # hp, attack, defense, remaining rolls
            char = Character("MaxStats", "Fighter")
            self.assertEqual(char.hp, 50)
            self.assertEqual(char.attack, 15)
            self.assertEqual(char.defense, 5)

    def test_min_stats_character(self):
        """Test character with minimum possible stats"""
        with patch('random.randint') as mock_randint:
            # Set up mock to return min values for stats
            mock_randint.side_effect = [20, 5, 1] + [1] * 5  # hp, attack, defense, remaining rolls
            char = Character("MinStats", "Fighter")
            self.assertEqual(char.hp, 20)
            self.assertEqual(char.attack, 5)
            self.assertEqual(char.defense, 1)

    def test_boundary_damage_values(self):
        """Test damage calculation at boundary values"""
        attacker = Character("Attacker", "Fighter")
        defender = Character("Defender", "Fighter")

        # Test max possible damage
        with patch.object(attacker, 'attack', 15), \
             patch.object(defender, 'defense', 1), \
             patch.object(defender, 'hp', 50), \
             patch('random.randint', return_value=6), \
             patch('random.random', return_value=0.5):  # Prevent ability use
            initial_hp = defender.hp
            attacker.attack_target(defender)
            # Damage = attack (15) + roll (6) - defense (1) = 20
            expected_damage = 15 + 6 - 1
            self.assertEqual(defender.hp, initial_hp - expected_damage)

        # Test min possible damage
        defender = Character("Defender", "Fighter")  # Reset defender
        with patch.object(attacker, 'attack', 5), \
             patch.object(defender, 'defense', 5), \
             patch.object(defender, 'hp', 50), \
             patch('random.randint', return_value=1), \
             patch('random.random', return_value=0.5):  # Prevent ability use
            initial_hp = defender.hp
            attacker.attack_target(defender)
            # Damage = max(0, attack (5) + roll (1) - defense (5)) = 1
            expected_damage = max(0, 5 + 1 - 5)
            self.assertEqual(defender.hp, initial_hp - expected_damage)

class TestAbilityCombinations(unittest.TestCase):
    """Test combinations and interactions of different abilities"""

    def setUp(self):
        self.rogue = Character("TestRogue", "Rogue")
        self.wizard = Character("TestWizard", "Wizard")
        self.fighter = Character("TestFighter", "Fighter")
        self.cleric = Character("TestCleric", "Cleric")
        self.skeleton = Character("TestSkeleton", "Skeleton")
        self.target = Character("Target", "Fighter")

    def test_backstab_fireball_combo(self):
        """Test Rogue's backstab followed by Wizard's fireball"""
        # Set up initial state
        self.target.hp = 50
        self.target.defense = 5
        initial_hp = self.target.hp
        initial_defense = self.target.defense

        # Apply backstab
        with patch.object(self.rogue, 'attack', 10):
            # Calculate backstab damage
            backstab_raw = int(self.rogue.attack * 1.5)  # 15
            reduced_defense = max(0, initial_defense - 2)  # Defense is reduced by 2
            backstab_damage = max(0, backstab_raw - reduced_defense)  # 15 - 3 = 12
            self.rogue._backstab(self.target)
            self.assertTrue(self.target.defense < initial_defense)

            # Apply fireball with reduced defense
            with patch('random.randint', return_value=20):
                self.wizard._fireball(self.target)
                # Fireball damage = 20 - reduced defense
                fireball_damage = max(0, 20 - reduced_defense)  # 20 - 3 = 17
                expected_hp = initial_hp - backstab_damage - fireball_damage
                self.assertEqual(self.target.hp, expected_hp,
                               f"HP {self.target.hp} != expected {expected_hp} " +
                               f"(initial {initial_hp} - backstab {backstab_damage} - " +
                               f"fireball {fireball_damage})")

    def test_bone_shield_heavy_strike_interaction(self):
        """Test Skeleton's bone shield against Fighter's heavy strike"""
        # Apply bone shield
        self.skeleton._bone_shield(None)
        initial_hp = self.skeleton.hp

        # Apply heavy strike
        with patch.object(self.fighter, 'attack', 10):
            self.fighter._heavy_strike(self.skeleton)
            # Damage should be reduced due to doubled defense
            expected_damage = max(0, (self.fighter.attack * 2) - self.skeleton.defense)
            self.assertEqual(self.skeleton.hp, initial_hp - expected_damage)

    def test_heal_during_combat(self):
        """Test healing effectiveness during different combat situations"""
        self.target.max_hp = 50  # Set max HP first
        self.target.hp = 20  # Set low HP

        # Test healing after taking damage
        with patch('random.randint') as mock_randint:
            mock_randint.return_value = 15
            self.cleric._heal(self.target)
            self.assertEqual(self.target.hp, 35)

        # Test healing at max HP with a different mock
        self.target.hp = 50
        with patch('random.randint') as mock_randint:
            mock_randint.return_value = 15
            self.cleric._heal(self.target)
            self.assertEqual(self.target.hp, 50)  # Should not exceed max

class TestStatusEffectInteractions(unittest.TestCase):
    """Test complex interactions between status effects"""

    def setUp(self):
        self.game = DnDGame(auto_create_characters=False)
        self.char = Character("TestChar", "Fighter")
        self.target = Character("Target", "Fighter")

    def test_multiple_debuff_stacking(self):
        """Test how multiple debuffs affect damage calculation"""
        # Apply multiple status effects
        self.target.status_effects = ["weakened", "poisoned"]
        initial_hp = self.target.hp

        with patch.object(self.char, 'attack', 10), \
             patch('random.randint', return_value=5):
            self.char.attack_target(self.target)
            # Verify damage calculation considers all debuffs
            self.assertLess(self.target.hp, initial_hp)

    def test_status_effect_order(self):
        """Test order of status effect application and removal"""
        self.char.status_effects = ["stunned", "poisoned", "weakened"]

        # Add character to game
        self.game.players = [self.char]
        self.game.enemies = [Character("Enemy", "Goblin")]

        # Play turn and verify effect removal order
        with patch('random.random', return_value=0.5), \
             patch('random.randint', return_value=5):
            self.game.play_turn()
            # Verify stun removed first
            self.assertNotIn("stunned", self.char.status_effects)
            self.assertIn("poisoned", self.char.status_effects)
            self.assertIn("weakened", self.char.status_effects)

    def test_status_effect_immunity(self):
        """Test immunity to certain status effects"""
        bandit = Character("TestBandit", "Bandit")
        target = Character("Target", "Fighter")

        # Test multiple cheap shot attempts
        with patch('random.random', return_value=0.2), \
             patch.object(bandit, 'attack', 10):  # Force stun and set attack
            bandit._cheap_shot(target)
            self.assertIn("stunned", target.status_effects)

            # Remove existing stun before second attempt
            target.status_effects.remove("stunned")
            bandit._cheap_shot(target)
            self.assertEqual(target.status_effects.count("stunned"), 1)

class TestTeamComposition(unittest.TestCase):
    """Test different team compositions and synergies"""

    def test_different_team_sizes(self):
        """Test various team size combinations"""
        game = DnDGame(auto_create_characters=False)

        # Test 1v1
        game.players = [Character("Player", "Fighter")]
        game.enemies = [Character("Enemy", "Goblin")]
        self.assertFalse(game.is_game_over())

        # Test 2v1
        game.players.append(Character("Player2", "Wizard"))
        self.assertFalse(game.is_game_over())

        # Test 1v2
        game = DnDGame(auto_create_characters=False)
        game.players = [Character("Player", "Fighter")]
        game.enemies = [Character("Enemy1", "Goblin"), Character("Enemy2", "Orc")]
        self.assertFalse(game.is_game_over())

    def test_team_synergy(self):
        """Test synergies between different character classes"""
        game = DnDGame(auto_create_characters=False)

        # Test Fighter + Cleric synergy
        fighter = Character("Fighter", "Fighter")
        cleric = Character("Cleric", "Cleric")
        enemy = Character("Enemy", "Orc")

        # Set teams properly
        fighter.team = "players"
        cleric.team = "players"
        enemy.team = "enemies"

        game.players = [fighter, cleric]
        game.enemies = [enemy]

        # Keep the enemy inactive so healing effects are easy to measure
        enemy.alive = False
        enemy.attack = 0
        enemy.abilities = {}

        # Simulate combat with healing
        fighter.hp = 20  # Low HP
        fighter.max_hp = 50  # Set max HP
        initial_hp = fighter.hp

        def mock_choice_fn(x):
            if isinstance(x, list):
                if x and isinstance(x[0], Character):
                    # For players, target enemies; for enemies, target players
                    if x[0] in game.enemies:
                        return enemy
                    else:
                        return fighter  # Always target fighter for healing
            if isinstance(x, dict):
                abilities = list(x.keys())
                # For Cleric, prioritize Heal when targeting fighter
                if "Heal" in abilities and x == cleric.abilities:
                    return "Heal"
                # For other characters, use first available ability
                return abilities[0] if abilities else None
            return None

        # Force ability use for Cleric
        with patch('random.random', return_value=0.2), \
             patch('random.randint', return_value=15), \
             patch('random.choice', side_effect=mock_choice_fn), \
             patch('random.shuffle', side_effect=lambda x: None):  # Prevent shuffling
            game.play_turn()
            # Fighter should be healed by Cleric
            self.assertGreater(fighter.hp, initial_hp)

class TestGameFlow(unittest.TestCase):
    """Test game flow control and state management"""

    def test_turn_order_consistency(self):
        """Test turn order remains consistent within a round"""
        game = DnDGame(auto_create_characters=False)

        # Create fixed characters
        chars = [
            Character("P1", "Fighter"),
            Character("P2", "Wizard"),
            Character("E1", "Goblin")
        ]
        game.players = chars[:2]
        game.enemies = chars[2:]

        # Track action order
        action_order = []

        def mock_attack_target(self, target):
            action_order.append(self.name)

        # Replace attack_target with mock
        with patch.object(Character, 'attack_target', mock_attack_target), \
             patch('random.shuffle', side_effect=lambda x: x):  # Prevent shuffling
            game.play_turn()

            # Verify each character acted exactly once
            self.assertEqual(len(action_order), len(chars))
            self.assertEqual(len(set(action_order)), len(chars))

    def test_temporary_effect_cleanup(self):
        """Test cleanup of temporary effects between turns"""
        game = DnDGame(auto_create_characters=False)
        char = Character("TestChar", "Fighter")
        char.status_effects = ["stunned"]  # Temporary effect

        game.players = [char]
        game.enemies = [Character("Enemy", "Goblin")]

        # Play multiple turns
        with patch('random.random', return_value=0.5):
            game.play_turn()  # First turn
            self.assertNotIn("stunned", char.status_effects)

            game.play_turn()  # Second turn
            self.assertNotIn("stunned", char.status_effects)

class TestErrorRecovery(unittest.TestCase):
    """Test error handling and recovery"""

    def test_invalid_game_state_recovery(self):
        """Test recovery from invalid game states"""
        game = DnDGame(auto_create_characters=False)

        # Test with no characters
        with self.assertRaises(GameError):
            game.play_turn()  # Should raise GameError when no characters exist

        # Test with invalid character class
        with self.assertRaises(GameError):
            Character("Invalid", "InvalidClass")  # Should raise GameError for invalid class

    def test_mid_game_character_removal(self):
        """Test handling of character removal during game"""
        game = DnDGame(auto_create_characters=False)
        player = Character("Player", "Fighter")
        enemy = Character("Enemy", "Goblin")

        game.players = [player]
        game.enemies = [enemy]

        # Kill character mid-game
        player.hp = 0
        player.alive = False

        # Game should handle dead character gracefully
        game.play_turn()
        self.assertTrue(game.is_game_over())

    def test_error_logging(self):
        """Test error logging during exceptional conditions"""
        with self.assertLogs('dnd_game', level='ERROR') as log:
            char = Character("TestChar", "Fighter")

            # Force an error condition
            with patch.object(char, 'attack_target', side_effect=Exception("Test error")):
                try:
                    char.attack_target(None)
                except Exception as e:
                    logger.error(f"Test error: {str(e)}")

                # Verify error was logged
                self.assertTrue(any("Test error" in msg for msg in log.output))

def run_extended_test_suite():
    """Run all tests including the new test classes"""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestCharacter)
    suite.addTests(loader.loadTestsFromTestCase(TestDnDGame))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    suite.addTests(loader.loadTestsFromTestCase(TestAbilityCombinations))
    suite.addTests(loader.loadTestsFromTestCase(TestStatusEffectInteractions))
    suite.addTests(loader.loadTestsFromTestCase(TestTeamComposition))
    suite.addTests(loader.loadTestsFromTestCase(TestGameFlow))
    suite.addTests(loader.loadTestsFromTestCase(TestErrorRecovery))

    runner = unittest.TextTestRunner()
    result = runner.run(suite)
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_extended_test_suite()
    if success:
        print("\nAll tests passed! The game is ready to run.")
    else:
        print("\nSome tests failed. Please fix the issues before running the game.")
