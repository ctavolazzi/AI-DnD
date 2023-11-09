# character_state.py

class CharacterState:
    def __init__(self, name, attributes):
        self.name = name
        self.attributes = attributes  # attributes include health, mana, inventory, etc.
        self.position = (0, 0)  # default starting position

    def to_dict(self):
        # Convert the state to a dictionary for easy serialization
        return {
            'name': self.name,
            'attributes': self.attributes,
            'position': self.position
        }

    @classmethod
    def from_dict(cls, data):
        # Create a CharacterState instance from a dictionary
        return cls(data['name'], data['attributes'])
