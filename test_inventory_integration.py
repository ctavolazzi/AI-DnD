"""Integration tests for Character-Inventory system"""

from dnd_game import Character


def test_inventory_basic_integration():
    """Test that Character has inventory and basic operations work"""
    char = Character("Test", "Fighter")

    assert hasattr(char, 'inventory'), "Character should have inventory"
    assert char.inventory.capacity == 20, "Default capacity should be 20"

    # Add items
    assert char.inventory.add_item('health_potion', 3), "Should add items"
    assert char.inventory.has_item('health_potion', 1), "Should have item"

    print("✅ Basic inventory integration test passed")


def test_inventory_conversion_methods():
    """Test inventory through conversion methods"""
    char = Character("TestHero", "Rogue")
    char.inventory.gold = 200
    char.inventory.add_item('health_potion', 5)
    char.inventory.add_item('mana_potion', 2)

    # Test to_dict
    char_dict = char.to_dict()
    assert "inventory" in char_dict, "to_dict should include inventory"
    assert "items" in char_dict["inventory"], "inventory should have items"
    assert char_dict["inventory"]["gold"] == 200, "Gold should be preserved"

    # Test to_db_dict
    db_dict = char.to_db_dict("char_001", "session_001")
    assert "inventory" in db_dict, "to_db_dict should include inventory"
    assert db_dict["inventory"]["gold"] == 200, "Gold should be in DB format"

    print("✅ Inventory conversion methods test passed")


def test_inventory_persistence_round_trip():
    """Test full round-trip: Character -> DB -> Character"""
    # Create character with inventory
    original = Character("RoundTrip", "Fighter")
    original.inventory.gold = 150
    original.inventory.add_item('health_potion', 3)
    original.inventory.add_item('mana_potion', 2)
    original.inventory.equip('longsword')  # Starting equipment

    original_gold = original.inventory.gold
    original_item_count = len(original.inventory.items)
    original_equipped_count = len(original.inventory.equipped)

    # Convert to DB and back
    db_dict = original.to_db_dict("char_001", "session_001")
    restored = Character.from_db_dict(db_dict)

    # Verify restoration
    assert restored.name == original.name, "Name should match"
    assert restored.inventory.gold == original_gold, f"Gold mismatch: {restored.inventory.gold} != {original_gold}"
    assert len(restored.inventory.items) == original_item_count, f"Item count mismatch: {len(restored.inventory.items)} != {original_item_count}"
    assert len(restored.inventory.equipped) == original_equipped_count, f"Equipped count mismatch: {len(restored.inventory.equipped)} != {original_equipped_count}"

    # Verify specific items
    assert 'health_potion' in restored.inventory.items, "health_potion should be restored"
    assert restored.inventory.items['health_potion'] == 3, "health_potion quantity should match"

    print("✅ Inventory persistence round-trip test passed")


def test_inventory_equipped_restoration():
    """Test equipped items are properly restored"""
    char = Character("EquipTest", "Fighter")
    char.inventory.equip('longsword')
    char.inventory.equip('chainmail')

    equipped_before = char.inventory.equipped.copy()

    # Round-trip
    db_dict = char.to_db_dict("char_001", "session_001")
    restored = Character.from_db_dict(db_dict)

    # Check equipped items restored
    assert len(restored.inventory.equipped) > 0, "Equipped items should be restored"

    # Check specific equipment
    for slot, item_id in equipped_before.items():
        if slot in restored.inventory.equipped:
            assert restored.inventory.equipped[slot] == item_id, f"{slot} should have {item_id}"

    print("✅ Equipped items restoration test passed")


def test_inventory_gold_handling():
    """Test gold handling through conversions"""
    char = Character("GoldTest", "Wizard")
    char.inventory.gold = 500

    # Test to_dict
    char_dict = char.to_dict()
    assert char_dict["inventory"]["gold"] == 500, "Gold in to_dict"

    # Test to_db_dict
    db_dict = char.to_db_dict("char_001", "session_001")
    assert db_dict["inventory"]["gold"] == 500, "Gold in to_db_dict"

    # Test restoration
    restored = Character.from_db_dict(db_dict)
    assert restored.inventory.gold == 500, "Gold should be restored"

    print("✅ Gold handling test passed")


if __name__ == "__main__":
    print("🧪 Testing Character-Inventory Integration\n")

    test_inventory_basic_integration()
    test_inventory_conversion_methods()
    test_inventory_persistence_round_trip()
    test_inventory_equipped_restoration()
    test_inventory_gold_handling()

    print("\n✅ All inventory integration tests passed!")

