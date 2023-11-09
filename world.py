# world.py

class Location:
    def __init__(self, description, connections):
        self.description = description
        self.connections = connections  # Dictionary of direction: Location pairs

class World:
    def __init__(self):
        self.locations = {}
        self.load_world()

    def load_world(self):
        # Define the village location first
        village_location = Location(
            "You are in a quiet village surrounded by rolling hills.",
            {}  # Start with an empty connections dictionary
        )

        # Define the forest location
        forest_location = Location(
            "You are in a dark, dense forest. The trees obscure the sky.",
            {"south": "village"}  # The forest connects south back to the village
        )

        # Add the locations to the locations dictionary
        self.locations = {
            "village": village_location,
            "forest": forest_location
        }

        # Now that both locations are created, connect them
        self.locations["village"].connections["north"] = "forest"

    def get_location(self, position):
        # Assuming 'position' is a key to access 'locations'
        return self.locations.get(position, Location("Endless void surrounds you.", {}))
