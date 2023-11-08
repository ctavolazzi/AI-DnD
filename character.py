# character.py

class Character:
    def __init__(self, name):
        self.name = name
        # ... other character attributes

    def engage_combat(self, combat_module, enemy):
        combat_module.start_combat(self, enemy)
