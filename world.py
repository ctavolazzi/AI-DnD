class ConnectionManager:
    def __init__(self, world):
        self.world = world

    def setup_connections(self, location_name):
        location = self.world.locations[location_name]
        location.connections = {
            "north": self.get_connected_location(location_name, "north"),
            "south": self.get_connected_location(location_name, "south"),
            "east": self.get_connected_location(location_name, "east"),
            "west": self.get_connected_location(location_name, "west")
        }

    def get_connected_location(self, location_name, direction):
        # We get the name of the connected location, if it exists
        target_location_name = self.world.locations[location_name].connections.get(direction)
        # Then, we return the Location object corresponding to the name, or None if it doesn't exist
        return self.world.locations.get(target_location_name)

class Location:
    def __init__(self, name, description, connections):
        self.name = name
        self.description = description
        self.connections = connections  # This will be a dictionary of direction: location_name pairs

    def describe(self):
        print(self.description)

class World:
    def __init__(self, config):
        # We convert location dictionaries to Location instances here
        self.locations = {
            location_dict['name']: Location(
                name=location_dict['name'],
                description=location_dict['description'],
                connections=location_dict['connections']
            ) for location_dict in config["locations"]
        }
        self.connection_manager = ConnectionManager(self)
        self.load_world()

    def load_world(self):
        # Here we ensure connections are set up as Location instances
        for location_name in self.locations:
            self.connection_manager.setup_connections(location_name)

    def get_location(self, position):
        # Assuming 'position' is the name of the location
        return self.locations.get(position, Location("Unknown", "Endless void surrounds you.", {}))