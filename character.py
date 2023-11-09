# character.py
"""
The Character class is one of the backbones of the program.
It represents a character in the game - any character.
Some things you might not expect to be character are. This is due to the intentional limitations of the class system.
"""

class Character:
  DEFAULT_CONFIG = {
    "id": "default_id",
    "name": "Default Character",
  }

  def __init__(self, config=None):
    self.config = {**self.DEFAULT_CONFIG, **(config or {})}
    if self.config["id"] is None:
      raise ValueError("Character must have an ID")
    if self.config["name"] is None:
      raise ValueError("Character must have a Name")

  def __str__(self):
    return self.config["name"]

# Test the Character module
if __name__ == "__main__":
  print("Testing Character module")
  test_character = Character()
  print(test_character)
  print("Character module tests passed")