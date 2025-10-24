"""
Demo of the spell and magic item systems.
Shows off Diablo 2-style equipment and D&D spell casting.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import random
import logging
from dnd_game import Character
from spells import SPELLS, SpellSchool, SpellType
from magic_items import (
    MagicItemGenerator, generate_random_item, ItemRarity,
    GEMS, RUNES, UNIQUE_ITEMS, ALL_SET_ITEMS
)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger()


def print_section(title):
    """Print a formatted section header."""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def print_character_stats(char):
    """Print character stats nicely."""
    print(f"┌─ {char.name} the {char.char_class} ─{'─'*(50-len(char.name)-len(char.char_class))}┐")
    print(f"│ HP: {char.hp}/{char.max_hp:3}  |  Mana: {char.mana}/{char.max_mana:3}  |  " +
          f"Attack: {char.attack:2}  |  Defense: {char.defense:2}  │")
    print(f"│ STR: {char.ability_scores['STR']:2}  DEX: {char.ability_scores['DEX']:2}  " +
          f"CON: {char.ability_scores['CON']:2}  INT: {char.ability_scores['INT']:2}  " +
          f"WIS: {char.ability_scores['WIS']:2}  CHA: {char.ability_scores['CHA']:2}     │")
    print(f"│ Gold: {char.inventory.gold:4}  |  Inventory: {len(char.inventory.items)}/{char.inventory.capacity} items  " +
          f"                          │")
    if char.spellbook.known_spells:
        spells = ', '.join(char.spellbook.known_spells.keys())
        print(f"│ Spells: {spells:<55} │")
    print(f"└{'─'*68}┘")


def demo_spell_system():
    """Demonstrate the spell casting system."""
    print_section("SPELL SYSTEM DEMO")

    # Create a wizard
    wizard = Character("Aldric the Wise", "Wizard", hp=45, max_hp=45, attack=6, defense=4)
    wizard.team = "players"
    print_character_stats(wizard)

    # Create enemies
    orc1 = Character("Grak", "Orc", hp=40, max_hp=40, attack=12, defense=2)
    orc1.team = "enemies"
    orc2 = Character("Morg", "Orc", hp=35, max_hp=35, attack=10, defense=3)
    orc2.team = "enemies"

    print("\n🗡️  Two orcs approach!\n")
    print(f"  {orc1.name}: {orc1.hp}/{orc1.max_hp} HP")
    print(f"  {orc2.name}: {orc2.hp}/{orc2.max_hp} HP")

    # Cast spells
    print("\n⚡ Aldric casts Ice Bolt at Grak!")
    result = wizard.cast_spell("ice_bolt", orc1)
    print(f"  {result['message']}")
    print(f"  Grak HP: {orc1.hp}/{orc1.max_hp}")
    print(f"  Aldric Mana: {wizard.mana}/{wizard.max_mana}")

    print("\n🔥 Aldric casts Flame Strike at Morg!")
    result = wizard.cast_spell("flame_strike", orc2)
    print(f"  {result['message']}")
    print(f"  Morg HP: {orc2.hp}/{orc2.max_hp}")
    print(f"  Aldric Mana: {wizard.mana}/{wizard.max_mana}")

    print("\n💫 Aldric casts Magic Missile at Grak!")
    result = wizard.cast_spell("magic_missile", orc1)
    print(f"  {result['message']}")
    print(f"  Grak HP: {orc1.hp}/{orc1.max_hp}")
    print(f"  Aldric Mana: {wizard.mana}/{wizard.max_mana}")

    # Show spell catalog
    print_section("AVAILABLE SPELLS BY SCHOOL")

    for school in SpellSchool:
        school_spells = [s for s in SPELLS.values() if s.school == school]
        if school_spells:
            print(f"\n{school.value} Spells:")
            for spell in school_spells:
                print(f"  • {spell.name:20} (Lvl {spell.level}) - {spell.mana_cost} mana - {spell.description}")


def demo_magic_items():
    """Demonstrate the magic item system."""
    print_section("MAGIC ITEM SYSTEM DEMO - Diablo 2 Style")

    print("🎲 Rolling for random loot...\n")

    # Generate various items
    items = []
    for i in range(20):
        item = generate_random_item(random.randint(5, 20), random.choice(["longsword", "chainmail", "dagger"]))
        items.append(item)

    # Group by rarity
    by_rarity = {}
    for item in items:
        rarity = item["rarity"]
        if rarity not in by_rarity:
            by_rarity[rarity] = []
        by_rarity[rarity].append(item)

    # Display items by rarity
    for rarity in [ItemRarity.LEGENDARY, ItemRarity.UNIQUE, ItemRarity.SET,
                   ItemRarity.RARE, ItemRarity.MAGIC, ItemRarity.COMMON]:
        if rarity in by_rarity:
            print(f"\n{rarity.display_name.upper()} ITEMS ({rarity.color}):")
            for item in by_rarity[rarity]:
                print(f"  • {item['name']}")
                if item.get('stats'):
                    stats_str = ", ".join([f"+{v} {k.replace('_', ' ').title()}"
                                          for k, v in item['stats'].items()])
                    print(f"    Stats: {stats_str}")
                if item.get('special'):
                    print(f"    Special: {item['special']}")
                if item.get('sockets', 0) > 0:
                    print(f"    Sockets: {item['sockets']}")


def demo_unique_items():
    """Show off unique items."""
    print_section("UNIQUE ITEMS (Legendaries)")

    for unique_id, unique in UNIQUE_ITEMS.items():
        print(f"\n✨ {unique.name} ✨")
        print(f"   Slot: {unique.slot.title()}")
        print(f"   Level Requirement: {unique.level_req}")
        stats_list = [f'+{v} {k.value.replace("_", " ").title()}' for k, v in unique.stats.items()]
        print(f"   Stats: {', '.join(stats_list)}")
        if unique.special:
            print(f"   💎 Special: {unique.special}")


def demo_set_items():
    """Show off set items with bonuses."""
    print_section("SET ITEMS")

    print("📦 Sigon's Complete Steel (Warrior Set)")
    print("   • Sigon's Visor (Helm)")
    print("   • Sigon's Shelter (Armor)")
    print("   • Sigon's Gage (Weapon)")
    print("   Set Bonuses:")
    print("     (2) +10 Defense, +5 Attack")
    print("     (3) +10 Attack, +50 Max HP, +10 Defense")

    print("\n📦 Tancred's Battlegear (Offensive Set)")
    print("   • Tancred's Skull (Helm)")
    print("   • Tancred's Spine (Armor)")
    print("   • Tancred's Hobnails (Boots)")
    print("   Set Bonuses:")
    print("     (2) +5 Damage, +10 Speed")
    print("     (3) +15 Attack, +10% Crit Chance")


def demo_gems_and_runes():
    """Show off gems and runes."""
    print_section("GEMS AND RUNES")

    print("💎 GEMS (Socket into items for bonuses):\n")
    print("Rubies (Fire):")
    print("  • Chipped Ruby    - +5 Fire Res, +1 Damage")
    print("  • Perfect Ruby    - +25 Fire Res, +8 Damage")

    print("\nSapphires (Ice/Mana):")
    print("  • Chipped Sapphire - +5 Ice Res, +10 Max Mana")
    print("  • Perfect Sapphire - +25 Ice Res, +60 Max Mana")

    print("\nDiamonds (All Resistances):")
    print("  • Perfect Diamond  - +12 to All Resistances")

    print("\n\n🔶 RUNES (Combine for Runewords):\n")
    print("Low Runes:")
    print("  • El Rune  (Lvl 1)  - +1 Attack, +1 Defense")
    print("  • Tir Rune (Lvl 3)  - +2 Mana Regen")

    print("\nMid Runes:")
    print("  • Tal Rune (Lvl 7)  - +15 Poison Resistance")
    print("  • Ral Rune (Lvl 8)  - +15 Fire Resistance")

    print("\nHigh Runes:")
    print("  • Ist Rune (Lvl 24) - +40% Magic Find")
    print("  • Ber Rune (Lvl 30) - +20 Damage")
    print("  • Zod Rune (Lvl 33) - +30 Defense")


def demo_magic_combat():
    """Demonstrate combat with magic items."""
    print_section("MAGIC COMBAT DEMO")

    # Create characters
    warrior = Character("Conan", "Fighter", hp=80, max_hp=80, attack=15, defense=8)
    warrior.team = "players"

    wizard = Character("Merlin", "Wizard", hp=50, max_hp=50, attack=8, defense=5)
    wizard.team = "players"

    print("⚔️  THE PARTY:\n")
    print_character_stats(warrior)
    print()
    print_character_stats(wizard)

    # Enemies with magic items
    print("\n\n👹 THE ENEMY:\n")
    boss = Character("Diablo", "Demon", hp=120, max_hp=120, attack=20, defense=10)
    boss.team = "enemies"
    print_character_stats(boss)

    # Simulate combat
    print("\n\n⚔️  COMBAT BEGIN!\n")

    print("Round 1:")
    print("  Merlin casts Fireball!")
    result = wizard.cast_spell("fireball", boss)
    print(f"    {result['message']}")
    print(f"    Diablo HP: {boss.hp}/{boss.max_hp}")

    print("\n  Conan attacks with his magic sword!")
    result = warrior.attack_target(boss)
    print(f"    Conan deals {result['damage_dealt']} damage!")
    print(f"    Diablo HP: {boss.hp}/{boss.max_hp}")

    if boss.alive:
        print("\n  Diablo strikes back at Conan!")
        boss.attack_target(warrior)
        print(f"    Conan HP: {warrior.hp}/{warrior.max_hp}")

    print("\n\nRound 2:")
    print("  Merlin casts Ice Bolt!")
    result = wizard.cast_spell("ice_bolt", boss)
    print(f"    {result['message']}")
    print(f"    Diablo HP: {boss.hp}/{boss.max_hp}")

    print("\n  Conan attacks again!")
    result = warrior.attack_target(boss)
    print(f"    Conan deals {result['damage_dealt']} damage!")
    print(f"    Diablo HP: {boss.hp}/{boss.max_hp}")

    if not boss.alive:
        print("\n\n🎉 VICTORY! Diablo has been defeated!")
        if result.get('loot_collected'):
            print(f"   Loot: {result['loot_collected']}")


def main():
    """Run all demos."""
    print("╔═══════════════════════════════════════════════════════════════════╗")
    print("║                                                                   ║")
    print("║        ⚔️  AI D&D MAGIC SYSTEM DEMONSTRATION  ⚔️                 ║")
    print("║                                                                   ║")
    print("║    Featuring: Spell Casting + Diablo 2-Style Equipment           ║")
    print("║                                                                   ║")
    print("╚═══════════════════════════════════════════════════════════════════╝")

    # Run demos
    demo_spell_system()
    demo_magic_items()
    demo_unique_items()
    demo_set_items()
    demo_gems_and_runes()
    demo_magic_combat()

    print_section("DEMO COMPLETE")
    print("🎮 All systems operational!")
    print("   • 21 unique spells across 7 schools of magic")
    print("   • 40+ affixes for procedurally generated magic items")
    print("   • 5 rarity tiers: Common, Magic, Rare, Set, Unique, Legendary")
    print("   • 20+ gems and runes for socketing")
    print("   • 5 unique legendary items")
    print("   • 2 complete item sets with set bonuses")
    print("\n✨ Your adventure awaits! ✨\n")


if __name__ == "__main__":
    # Set random seed for consistent demo output
    random.seed(12345)
    main()
