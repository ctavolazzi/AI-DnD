# module_interface.py

class ModuleInterface:
    def initialize(self, config, game_state):
        raise NotImplementedError

    def update(self, game_state):
        raise NotImplementedError

    def terminate(self, game_state):
        raise NotImplementedError
