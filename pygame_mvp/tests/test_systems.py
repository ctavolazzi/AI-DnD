"""
Unit tests for pygame_mvp.game.systems (pytest style).
"""

import types

import pytest

from pygame_mvp.game.systems import (
    CLASS_BASE_STATS,
    Character,
    CharacterClass,
    CombatSystem,
    Item,
    ItemType,
    Player,
    Stats,
    create_enemy,
)


def test_stats_defaults():
    """Stats() defaults to average human (10 each)."""
    s = Stats()
    assert (s.strength, s.dexterity, s.intelligence, s.constitution) == (10, 10, 10, 10)


def test_stats_zero():
    """Stats.zero() creates all-zero stats for bonuses."""
    s = Stats.zero()
    assert (s.strength, s.dexterity, s.intelligence, s.constitution) == (0, 0, 0, 0)


def test_stats_bonus():
    """Stats.bonus() creates stats with only specified bonuses."""
    s = Stats.bonus(strength=5, dexterity=3)
    assert (s.strength, s.dexterity, s.intelligence, s.constitution) == (5, 3, 0, 0)


def test_stats_addition():
    a = Stats(5, 6, 7, 8)
    b = Stats(1, 2, 3, 4)
    c = a + b
    assert (c.strength, c.dexterity, c.intelligence, c.constitution) == (6, 8, 10, 12)


def test_character_hp_clamping():
    c = Character("Tester", max_hp=10)
    c.current_hp = 50
    assert c.current_hp == 10
    c.current_hp = -5
    assert c.current_hp == 0
    c.max_hp = 5
    assert c.max_hp == 5
    assert c.current_hp == 0


def test_character_defaults_use_average_stats():
    c = Character("Tester")
    assert (c.base_stats.strength, c.base_stats.dexterity, c.base_stats.intelligence, c.base_stats.constitution) == (10, 10, 10, 10)


@pytest.mark.parametrize(
    "char_class",
    [CharacterClass.FIGHTER, CharacterClass.WIZARD, CharacterClass.ROGUE, CharacterClass.CLERIC],
)
def test_player_baselines(char_class):
    player = Player("Hero", char_class)
    cfg = CLASS_BASE_STATS[char_class]
    assert player.base_stats == cfg["stats"]
    assert player.max_hp == cfg["hp"]
    assert player.current_hp == player.max_hp


def test_equipment_influences_total_stats():
    c = Character("Tester")
    bonus = Stats(2, 3, 4, 5)
    sword = Item("Sword", ItemType.WEAPON, value=10, stats_bonus=bonus)
    c.equip(sword)
    total = c.total_stats
    assert total.strength == c.base_stats.strength + bonus.strength
    assert total.dexterity == c.base_stats.dexterity + bonus.dexterity
    assert total.intelligence == c.base_stats.intelligence + bonus.intelligence
    assert total.constitution == c.base_stats.constitution + bonus.constitution


def test_combat_attack_deterministic(monkeypatch):
    attacker = Character("Attacker")
    defender = Character("Defender")
    attacker.base_stats = Stats(strength=12, dexterity=0, intelligence=0, constitution=0)
    sword = Item("Sword", ItemType.WEAPON, value=0, damage_min=2, damage_max=2)
    attacker.equip(sword)
    defender.current_hp = 20

    seq = iter([1, 2, 100])  # hit roll (success), damage roll (2), crit roll (no crit)

    def fake_randint(a, b):
        try:
            return next(seq)
        except StopIteration:
            return a

    monkeypatch.setattr("pygame_mvp.game.systems.random.randint", fake_randint)

    outcome = CombatSystem.calculate_attack(attacker, defender)
    assert outcome["hit"] is True
    assert outcome["crit"] is False
    expected_damage = 2 + attacker.total_stats.strength // 3
    assert outcome["damage"] == expected_damage
    assert defender.current_hp == 20 - expected_damage


def test_combat_unarmed(monkeypatch):
    attacker = Character("Attacker")
    defender = Character("Defender")
    attacker.base_stats = Stats(strength=9, dexterity=0, intelligence=0, constitution=0)
    defender.current_hp = 10

    seq = iter([1, 100])  # hit, no crit

    def fake_randint(a, b):
        try:
            return next(seq)
        except StopIteration:
            return a

    monkeypatch.setattr("pygame_mvp.game.systems.random.randint", fake_randint)

    outcome = CombatSystem.calculate_attack(attacker, defender)
    assert outcome["hit"] is True
    expected_damage = 1 + attacker.total_stats.strength // 3
    assert outcome["damage"] == expected_damage
    assert defender.current_hp == 10 - expected_damage


def test_create_enemy_helper():
    enemy = create_enemy("Goblin", base_hp=15)
    assert enemy.name == "Goblin"
    assert enemy.current_hp == 15
    assert enemy.max_hp == 15
