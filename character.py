import json

class Character:
    DEFAULT_CONFIG = {
        "id": "default_id",
        "name": "Default Character",
        "race": "Human",
        "character_class": "Warrior",
        "strength": 10,
        "dexterity": 10,
        "constitution": 10,
        "intelligence": 10,
        "wisdom": 10,
        "charisma": 10,
    }

    def __init__(self, config=None):
        self.config = {**self.DEFAULT_CONFIG, **(config or {})}
        if self.config["id"] is None:
            raise ValueError("Character must have an ID")
        if self.config["name"] is None:
            raise ValueError("Character must have a Name")
        # Validate other attributes as needed
        self.state = {
          "hp": 10,
          "mp": 10,
          "xp": 0,
          "level": 1,
          "inventory": [{"id": "journal", "entries": []}, {"gold": 0,}],
          "body": {"head": [], "torso": [], "left_hand": [], "right_hand": [], "belt": [], "legs": [], "feet": []},
          "spells": [],
          "status_effects": [],
          "position": (0, 0),
          "current_map": None,
        }

    def __str__(self):
        return f"{self.config['name']} the {self.config['race']} {self.config['character_class']}"

    # Add methods to update individual attributes if needed

    def set_race(self, race):
        if race not in ['Human', 'Elf', 'Dwarf', 'Orc']:  # Add all valid races
            raise ValueError("Invalid race chosen.")
        self.config['race'] = race

    def set_character_class(self, character_class):
        if character_class not in ['Warrior', 'Mage', 'Rogue']:  # Add all valid classes
            raise ValueError("Invalid class chosen.")
        self.config['character_class'] = character_class

    def set_attribute(self, attribute, value):
        if attribute in ['strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma']:
            if not (1 <= value <= 20):  # Assuming DnD-like attribute range
                raise ValueError(f"{attribute} must be between 1 and 20.")
            self.config[attribute] = value
        else:
            raise ValueError(f"{attribute} is not a valid character attribute.")

    def save(self, file_path):
        with open(file_path, 'w') as file:
            json.dump(self.config, file)

    @classmethod
    def load(cls, file_path):
        with open(file_path, 'r') as file:
            config = json.load(file)
        return cls(config)

    def move(self, direction):
        # Check if the direction is valid in the current location
        current_location = self.state['current_map'].get_location(self.state['position'])
        if direction in current_location.connections:
            new_position_key = current_location.connections[direction]
            new_position = self.state['current_map'].get_location(new_position_key)
            self.state['position'] = new_position_key
            print(f"You move {direction} to {new_position.description}.")
        else:
            print("You can't go that way.")

    def to_dict(self):
        return {
            "config": self.config,
            "state": self.state,
            # Include any other necessary data
        }

    @classmethod
    def from_dict(cls, data):
        character = cls(data['config'])
        character.state = data['state']
        return character