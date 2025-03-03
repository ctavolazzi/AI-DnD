#!/usr/bin/env python3
"""
Sentinel Test Script

This script demonstrates the Sentinel monitoring system by creating a simple
mock game state with deliberate inconsistencies and running validation on it.
"""

import os
import sys
import logging
import json
from typing import Dict, List, Any

# Set up logging
if not os.path.exists('logs'):
    os.makedirs('logs')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join('logs', 'sentinel_test.log'), mode='w')
    ]
)

logger = logging.getLogger("sentinel.test")

# Import Sentinel components
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sentinel.sentinel import Sentinel
from sentinel.config import SentinelConfig
from sentinel.integration import initialize_sentinel, handle_validation_issues


class MockGameManager:
    """Mock GameManager class for testing Sentinel."""

    def __init__(self):
        """Initialize with mock game data."""
        self.characters = {}
        self.locations = {}
        self.items = {}
        self.quests = {}
        self.facts = {}
        self.entity_relationship_manager = MockRelationshipManager()

    def load_mock_data(self):
        """Load mock data with deliberate inconsistencies."""
        # Load locations
        self.locations = {
            "town_square": {
                "name": "Town Square",
                "description": "The central square of the town.",
                "connections": {
                    "tavern": {"type": "path", "description": "A cobblestone path"},
                    "blacksmith": {"type": "road", "description": "A dirt road"}
                },
                "characters": ["innkeeper", "guard"]  # Inconsistency: innkeeper should be at tavern
            },
            "tavern": {
                "name": "The Drunken Dragon Tavern",
                "description": "A cozy tavern with a roaring fireplace.",
                "connections": {
                    # Inconsistency: Missing bidirectional connection to town_square
                    "inn_rooms": {"type": "stairs", "description": "Wooden stairs leading up"}
                },
                "characters": []  # Inconsistency: Missing innkeeper
            },
            "blacksmith": {
                "name": "Forge & Anvil",
                "description": "A hot, smoky blacksmith shop.",
                "connections": {
                    "town_square": {"type": "road", "description": "A dirt road"}
                },
                "characters": ["blacksmith"]
            },
            "inn_rooms": {
                "name": "Inn Rooms",
                "description": "Cozy rooms for rent above the tavern.",
                "connections": {
                    "tavern": {"type": "stairs", "description": "Wooden stairs leading down"}
                },
                "characters": ["adventurer"]
            },
            "forest": {
                "name": "Dark Forest",
                "description": "A dense, dark forest outside of town.",
                # Inconsistency: No connections (isolated location)
                "characters": []
            }
        }

        # Load characters
        self.characters = {
            "innkeeper": {
                "name": "Galen the Innkeeper",
                "description": "A jolly, rotund man with a big smile.",
                "location": "town_square",  # Inconsistency: Should be at tavern
                "status": "active",
                "inventory": ["tavern_key"],
                "memory": [
                    {"content": "I run the Drunken Dragon Tavern and serve the best ale in town."},
                    {"content": "The blacksmith owes me money for last week's tab."}
                ]
            },
            "blacksmith": {
                "name": "Durgan Ironarm",
                "description": "A muscular dwarf with a singed beard.",
                "location": "blacksmith",
                "status": "active",
                "inventory": ["hammer", "tongs"],
                "memory": [
                    {"content": "I craft the finest weapons in town."},
                    {"content": "I need to pay my tab at the tavern."}
                ]
            },
            "guard": {
                "name": "Sergeant Bryce",
                "description": "A stern-looking town guard with a weathered face.",
                "location": "town_square",
                "status": "active",
                "inventory": ["sword", "whistle"],
                "memory": [
                    {"content": "I patrol the town square and keep the peace."},
                    {"content": "There have been reports of bandits in the forest."}
                ]
            },
            "adventurer": {
                "name": "Lyra the Bold",
                "description": "A young adventurer eager to make a name for herself.",
                "location": "inn_rooms",
                "status": "active",
                "inventory": ["backpack", "map"],
                "memory": [
                    {"content": "I'm staying at the inn while I prepare for my quest."},
                    {"content": "I need to speak with the blacksmith about a new sword."}
                ]
            },
            "merchant": {
                # Inconsistency: Missing location
                "name": "Tomas the Trader",
                "description": "A traveling merchant with exotic goods.",
                "status": "active",
                "inventory": ["silk", "spices", "jewelry"]
            }
        }

        # Load items
        self.items = {
            "tavern_key": {
                "name": "Tavern Key",
                "description": "A large iron key to the Drunken Dragon Tavern."
            },
            "hammer": {
                "name": "Blacksmith's Hammer",
                "description": "A heavy hammer used for metalworking."
            },
            "tongs": {
                "name": "Blacksmith's Tongs",
                "description": "Iron tongs used to hold hot metal."
            },
            "sword": {
                "name": "Guard's Sword",
                "description": "A standard-issue sword of the town guard."
            },
            "whistle": {
                "name": "Guard's Whistle",
                "description": "A loud whistle used to call for backup."
            },
            "backpack": {
                "name": "Adventurer's Backpack",
                "description": "A worn leather backpack with many pockets."
            },
            "map": {
                "name": "Treasure Map",
                "description": "A faded map showing the location of a hidden treasure."
            },
            "silk": {
                "name": "Fine Silk",
                "description": "Luxurious silk from distant lands."
            },
            "spices": {
                "name": "Exotic Spices",
                "description": "Rare and aromatic spices from across the sea."
            },
            "jewelry": {
                "name": "Ornate Jewelry",
                "description": "Finely crafted necklaces and rings."
            },
            "ancient_tome": {
                # Inconsistency: Item not placed anywhere
                "name": "Ancient Tome",
                "description": "A mysterious book written in an unknown language."
            }
        }

        # Load quests
        self.quests = {
            "bandit_hunt": {
                "name": "Hunt the Bandits",
                "description": "Clear out the bandits that have been troubling travelers.",
                "status": "active",
                "prerequisites": [],
                "current_stage": "find_bandits",
                "completed_stages": ["accept_quest"],
                "stages": {
                    "accept_quest": {
                        "description": "Accept the quest from the guard captain.",
                        "dependencies": []
                    },
                    "find_bandits": {
                        "description": "Locate the bandit hideout in the forest.",
                        "dependencies": ["accept_quest"]
                    },
                    "defeat_bandits": {
                        "description": "Defeat the bandits and their leader.",
                        "dependencies": ["find_bandits"]
                    },
                    "report_success": {
                        "description": "Report your success to the guard captain.",
                        "dependencies": ["defeat_bandits"]
                    }
                }
            },
            "blacksmith_delivery": {
                "name": "Special Delivery",
                "description": "Deliver rare metal to the blacksmith.",
                "status": "active",  # Inconsistency: Active without completed prerequisite
                "prerequisites": ["bandit_hunt"],
                "current_stage": "deliver_metal",
                "completed_stages": ["accept_delivery"],
                "stages": {
                    "accept_delivery": {
                        "description": "Accept the delivery job from the merchant.",
                        "dependencies": []
                    },
                    "deliver_metal": {
                        "description": "Deliver the rare metal to the blacksmith.",
                        "dependencies": ["accept_delivery"]
                    },
                    "collect_payment": {
                        "description": "Collect payment from the blacksmith.",
                        "dependencies": ["deliver_metal"]
                    }
                }
            }
        }

        # Load facts
        self.facts = {
            "tavern_history": {
                "name": "Tavern History",
                "description": "The Drunken Dragon Tavern was built 100 years ago.",
                "location": "tavern",
                "keywords": ["tavern", "history", "drunken dragon", "100 years"],
                "hidden": False
            },
            "bandit_leader": {
                "name": "Bandit Leader Identity",
                "description": "The leader of the bandits is the former town guard captain.",
                "revealed_by_quest": "bandit_hunt",
                "keywords": ["bandit", "leader", "guard captain", "former"],
                "hidden": True,
                "known_by_npc": ["guard"]
            }
        }

        # Set up relationships
        self.entity_relationship_manager.add_relationship("innkeeper", "tavern", "owns")
        self.entity_relationship_manager.add_relationship("blacksmith", "hammer", "has_item")
        self.entity_relationship_manager.add_relationship("blacksmith", "tongs", "has_item")
        self.entity_relationship_manager.add_relationship("guard", "sword", "has_item")
        self.entity_relationship_manager.add_relationship("guard", "whistle", "has_item")
        self.entity_relationship_manager.add_relationship("adventurer", "backpack", "has_item")
        self.entity_relationship_manager.add_relationship("adventurer", "map", "has_item")
        self.entity_relationship_manager.add_relationship("merchant", "silk", "has_item")
        self.entity_relationship_manager.add_relationship("merchant", "spices", "has_item")
        self.entity_relationship_manager.add_relationship("merchant", "jewelry", "has_item")

        # Inconsistency: Missing bidirectional relationship
        self.entity_relationship_manager.add_relationship("innkeeper", "blacksmith", "friends_with")
        # Correct bidirectional relationship
        self.entity_relationship_manager.add_relationship("guard", "adventurer", "knows")
        self.entity_relationship_manager.add_relationship("adventurer", "guard", "knows")


class MockRelationshipManager:
    """Mock relationship manager for testing Sentinel."""

    def __init__(self):
        """Initialize with empty relationships."""
        self.relationships = {}

    def add_relationship(self, source: str, target: str, rel_type: str, strength: float = 1.0):
        """Add a relationship between entities."""
        key = f"{source}:{target}:{rel_type}"
        self.relationships[key] = {
            "source": source,
            "target": target,
            "type": rel_type,
            "strength": strength
        }

    def has_relationship(self, source: str, target: str, rel_type: str) -> bool:
        """Check if a relationship exists."""
        key = f"{source}:{target}:{rel_type}"
        return key in self.relationships

    def get_relationship(self, source: str, target: str, rel_type: str) -> Dict:
        """Get a specific relationship."""
        key = f"{source}:{target}:{rel_type}"
        return self.relationships.get(key)

    def get_all_relationships(self) -> List[Dict]:
        """Get all relationships."""
        return list(self.relationships.values())


class MockDungeonMaster:
    """Mock DungeonMaster class for testing Sentinel."""

    def __init__(self, game_manager):
        """Initialize with reference to game manager."""
        self.game_manager = game_manager
        self.current_turn = 0

    def advance_turn(self):
        """Advance the game by one turn."""
        self.current_turn += 1
        logger.info(f"Advanced to turn {self.current_turn}")


def create_test_config() -> SentinelConfig:
    """Create a test configuration for Sentinel."""
    config = SentinelConfig()

    # Set general settings
    config.enabled = True
    config.log_level = "DEBUG"

    # Set validation intervals (in seconds)
    config.validation_intervals = {
        "entity": 1,
        "relationship": 1,
        "world_state": 1,
        "narrative": 1
    }

    # Configure entity validation rules
    config.entity_rules = {
        "required_fields": {
            "character": ["name", "description", "location", "status"],
            "location": ["name", "description", "connections"],
            "item": ["name", "description"],
            "quest": ["name", "description", "status"]
        },
        "valid_statuses": {
            "character": ["active", "inactive", "dead", "missing"],
            "quest": ["inactive", "active", "completed", "failed"]
        }
    }

    # Configure relationship validation rules
    config.relationship_rules = {
        "valid_types": ["knows", "friends_with", "enemies_with", "has_item", "owns", "at_location", "assigned_to"],
        "check_bidirectional": True
    }

    # Configure world state validation rules
    config.world_state_rules = {
        "verify_location_connections": True,
        "verify_location_character_lists": True,
        "check_isolated_locations": True,
        "check_orphaned_entities": True,
        "connections_should_be_bidirectional": True
    }

    # Configure narrative consistency rules
    config.narrative_rules = {
        "check_character_knowledge": True,
        "check_quest_progression": True,
        "check_narrative_continuity": True,
        "significant_relationship_change_threshold": 0.3
    }

    return config


def fix_some_issues(game_manager):
    """Fix some of the issues to demonstrate improvement."""
    logger.info("Fixing some issues manually...")

    # Fix innkeeper location
    game_manager.characters["innkeeper"]["location"] = "tavern"
    game_manager.locations["town_square"]["characters"].remove("innkeeper")
    game_manager.locations["tavern"]["characters"].append("innkeeper")

    # Fix bidirectional connection
    game_manager.locations["tavern"]["connections"]["town_square"] = {
        "type": "path",
        "description": "A cobblestone path"
    }

    # Fix merchant location
    game_manager.characters["merchant"]["location"] = "town_square"
    if "characters" in game_manager.locations["town_square"]:
        game_manager.locations["town_square"]["characters"].append("merchant")

    # Fix quest prerequisite
    game_manager.quests["blacksmith_delivery"]["status"] = "inactive"

    # Add bidirectional relationship
    game_manager.entity_relationship_manager.add_relationship(
        "blacksmith", "innkeeper", "friends_with"
    )

    # Place the ancient tome
    game_manager.entity_relationship_manager.add_relationship(
        "adventurer", "ancient_tome", "has_item"
    )
    game_manager.characters["adventurer"]["inventory"].append("ancient_tome")

    logger.info("Manual fixes applied")


def main():
    """Run the Sentinel test."""
    logger.info("Starting Sentinel test")

    # Create mock game components
    game_manager = MockGameManager()
    game_manager.load_mock_data()
    dungeon_master = MockDungeonMaster(game_manager)

    # Create test configuration
    config = create_test_config()

    # Initialize Sentinel
    sentinel = initialize_sentinel(game_manager, dungeon_master, config)

    # Run initial validation
    logger.info("Running initial validation...")
    issues = sentinel.validate_all()

    # Handle and display issues
    logger.info(f"Found {len(issues)} issues in initial validation")
    handle_validation_issues(issues, game_manager)

    # Save issues to file for review
    with open(os.path.join('logs', 'initial_issues.json'), 'w') as f:
        json.dump(issues, f, indent=2)

    # Fix some issues
    fix_some_issues(game_manager)

    # Run validation again
    logger.info("Running validation after fixes...")
    issues_after_fix = sentinel.validate_all()

    # Handle and display issues
    logger.info(f"Found {len(issues_after_fix)} issues after fixes")
    handle_validation_issues(issues_after_fix, game_manager)

    # Save issues to file for review
    with open(os.path.join('logs', 'issues_after_fix.json'), 'w') as f:
        json.dump(issues_after_fix, f, indent=2)

    # Print summary
    logger.info("Test Summary:")
    logger.info(f"Initial issues: {len(issues)}")
    logger.info(f"Issues after fixes: {len(issues_after_fix)}")
    logger.info(f"Improvement: {len(issues) - len(issues_after_fix)} issues resolved")

    # Calculate issue types
    initial_errors = sum(1 for issue in issues if issue.get("severity") == "error")
    initial_warnings = sum(1 for issue in issues if issue.get("severity") == "warning")
    initial_infos = sum(1 for issue in issues if issue.get("severity") == "info")

    after_errors = sum(1 for issue in issues_after_fix if issue.get("severity") == "error")
    after_warnings = sum(1 for issue in issues_after_fix if issue.get("severity") == "warning")
    after_infos = sum(1 for issue in issues_after_fix if issue.get("severity") == "info")

    logger.info(f"Initial issues by severity: {initial_errors} errors, {initial_warnings} warnings, {initial_infos} infos")
    logger.info(f"After fixes by severity: {after_errors} errors, {after_warnings} warnings, {after_infos} infos")

    logger.info("Sentinel test completed")


if __name__ == "__main__":
    main()