"""
Integration example: How to use StatsAdapter with GameManager and PixelInventoryScreen.

This module shows the recommended patterns for:
1. Creating a character with full D&D stats
2. Converting game stats to UI display format
3. Updating UI when character stats change
4. Handling character class and level progression
"""

import pygame
from pygame_mvp.game.systems import Character, Stats, CharacterClass, Item, ItemType
from pygame_mvp.game.stats_adapter import StatsAdapter
from pygame_mvp.ui.pixel_inventory import PixelInventoryScreen


class GameManager:
    """
    Example GameManager that uses StatsAdapter to bridge game and UI.
    """

    def __init__(self, width: int, height: int, surface: pygame.Surface):
        self.width = width
        self.height = height
        self.screen = surface

        # Game state
        self.player: Character = None
        self.stats_adapter: StatsAdapter = None
        self.inventory_screen: PixelInventoryScreen = None

        # UI state
        self.show_inventory = False
        self.is_paused = False

    def create_player(self, name: str, char_class: CharacterClass) -> None:
        """
        Create a new player character with full D&D stats.

        Args:
            name: Character name
            char_class: One of CharacterClass.FIGHTER, .WIZARD, .ROGUE, .CLERIC
        """
        # 1. Create base character
        self.player = Character(name, level=1, max_hp=20)
        self.player.char_class = char_class

        # 2. Set class-specific base stats
        base_stats = self._get_class_base_stats(char_class)
        self.player.base_stats = base_stats

        # 3. Add some starting items
        self._give_starting_equipment(char_class)

        # 4. Create stats adapter
        self.stats_adapter = StatsAdapter(self.player)

    def _get_class_base_stats(self, char_class: CharacterClass) -> Stats:
        """Get starting stats for a character class."""
        class_stats = {
            CharacterClass.FIGHTER: Stats(strength=15, dexterity=10, intelligence=10, constitution=14),
            CharacterClass.WIZARD: Stats(strength=8, dexterity=10, intelligence=15, constitution=10),
            CharacterClass.ROGUE: Stats(strength=10, dexterity=15, intelligence=12, constitution=10),
            CharacterClass.CLERIC: Stats(strength=13, dexterity=10, intelligence=10, constitution=12),
        }
        return class_stats.get(char_class, Stats())

    def _give_starting_equipment(self, char_class: CharacterClass) -> None:
        """Give the player starting gear based on class."""
        starting_gear = {
            CharacterClass.FIGHTER: [
                Item(
                    name="Longsword",
                    item_type=ItemType.WEAPON,
                    value=50,
                    damage_min=1,
                    damage_max=8,
                    stats_bonus=Stats.bonus(strength=1),
                    description="A well-balanced blade"
                ),
                Item(
                    name="Leather Armor",
                    item_type=ItemType.ARMOR,
                    value=30,
                    stats_bonus=Stats.bonus(constitution=1),
                    description="Worn leather protection"
                ),
            ],
            CharacterClass.WIZARD: [
                Item(
                    name="Staff",
                    item_type=ItemType.WEAPON,
                    value=50,
                    stats_bonus=Stats.bonus(intelligence=1),
                    description="Focus for spellcasting"
                ),
                Item(
                    name="Spell Book",
                    item_type=ItemType.ARMOR,
                    value=25,
                    stats_bonus=Stats.bonus(intelligence=2),
                    description="Contains known spells"
                ),
            ],
            CharacterClass.ROGUE: [
                Item(
                    name="Daggers",
                    item_type=ItemType.WEAPON,
                    value=30,
                    damage_min=1,
                    damage_max=4,
                    stats_bonus=Stats.bonus(dexterity=1),
                    description="Quick striking weapons"
                ),
                Item(
                    name="Leather Armor",
                    item_type=ItemType.ARMOR,
                    value=30,
                    stats_bonus=Stats.bonus(dexterity=1),
                    description="Light and flexible"
                ),
            ],
            CharacterClass.CLERIC: [
                Item(
                    name="Mace",
                    item_type=ItemType.WEAPON,
                    value=40,
                    damage_min=1,
                    damage_max=6,
                    stats_bonus=Stats.bonus(),
                    description="Holy striking weapon"
                ),
                Item(
                    name="Holy Symbol",
                    item_type=ItemType.ARMOR,
                    value=25,
                    stats_bonus=Stats.bonus(),
                    description="Focus for divine magic"
                ),
            ],
        }

        if char_class in starting_gear:
            for item in starting_gear[char_class]:
                self.player.inventory.append(item)

    def show_inventory_screen(self) -> None:
        """Display the inventory screen with current character stats."""
        self.show_inventory = True

        # 1. Create inventory screen if needed
        if self.inventory_screen is None:
            self.inventory_screen = PixelInventoryScreen(self.width, self.height)

        # 2. Update with current player data
        self.update_inventory_display()

    def update_inventory_display(self) -> None:
        """
        Sync inventory screen with current character state.

        Call this whenever character stats or inventory changes.
        """
        if self.inventory_screen is None:
            return

        # Get D&D stats from adapter
        d20_stats = self.stats_adapter.get_d20_stats()

        # Update inventory screen
        self.inventory_screen.set_player_name(self.player.name)
        self.inventory_screen.set_player_class(self.player.char_class.value)
        self.inventory_screen.set_player_level(self.player.level)
        self.inventory_screen.set_player_hp(self.player.current_hp, self.player.max_hp)

        # Set D&D stats (STR, DEX, CON, INT, WIS, CHA)
        self.inventory_screen.set_stats({
            "STR": d20_stats.strength,
            "DEX": d20_stats.dexterity,
            "CON": d20_stats.constitution,
            "INT": d20_stats.intelligence,
            "WIS": d20_stats.wisdom,
            "CHA": d20_stats.charisma,
        })

        # Update inventory items
        for idx, item in enumerate(self.player.inventory):
            if idx >= 15:  # Grid capacity
                break
            # In a real implementation, you'd convert item to image
            # For now, just set the name
            self.inventory_screen.add_item_to_grid(idx, item)

        # Update gold/currency
        # self.inventory_screen.set_gold(self.player.gold)

    def level_up(self) -> None:
        """Increase player level and update stats."""
        self.player.level += 1
        self.player.max_hp += 5  # Simple HP increase

        # Refresh adapter to get new proficiency bonus
        self.stats_adapter.update_from_character()

        # Refresh UI
        if self.show_inventory:
            self.update_inventory_display()

    def gain_item(self, item: Item) -> None:
        """Add an item to player inventory and update UI."""
        if len(self.player.inventory) < 15:  # Grid capacity
            self.player.inventory.append(item)

            if self.show_inventory:
                self.update_inventory_display()

    def damage_player(self, amount: int) -> None:
        """Reduce player HP and update UI."""
        self.player.current_hp -= amount

        if self.show_inventory:
            self.update_inventory_display()

    def handle_inventory_input(self, event: pygame.event.Event) -> None:
        """Handle input while inventory is open."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_i:
                # Close inventory
                self.show_inventory = False
            elif event.key == pygame.K_RETURN:
                # Test level up
                print("Leveling up...")
                self.level_up()

    def render_inventory(self, surface: pygame.Surface) -> None:
        """Render the inventory screen overlay."""
        if self.show_inventory and self.inventory_screen:
            self.inventory_screen.render(surface)


# --- EXAMPLE USAGE ---

def example_usage():
    """
    Shows how to use the GameManager with stats adapter.

    This would be called from main.py after initializing pygame.
    """
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Stats Adapter Example")
    clock = pygame.time.Clock()

    # Create game manager
    manager = GameManager(1280, 720, screen)

    # Create player
    manager.create_player("Aragorn", CharacterClass.FIGHTER)

    # Show stats in console
    print("=== Created Character ===")
    print(f"Name: {manager.player.name}")
    print(f"Class: {manager.player.char_class.value}")
    print(f"Level: {manager.player.level}")
    print(f"Base Stats: STR={manager.player.base_stats.strength}, "
          f"DEX={manager.player.base_stats.dexterity}, "
          f"CON={manager.player.base_stats.constitution}, "
          f"INT={manager.player.base_stats.intelligence}")
    print()
    print("=== D&D Stats (with modifiers) ===")
    for line in manager.stats_adapter.get_stat_display_lines():
        print(line)
    print()
    print("=== Starting Inventory ===")
    for item in manager.player.inventory:
        print(f"  - {item.name} ({item.item_type.value})")

    # Show inventory screen
    manager.show_inventory_screen()

    # Main loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if manager.show_inventory:
                manager.handle_inventory_input(event)

        # Render
        screen.fill((20, 20, 30))
        manager.render_inventory(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    example_usage()
