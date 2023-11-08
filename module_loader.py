# module_loader.py

class ModuleLoader:
    def __init__(self):
        self.modules = {}

    def load_module(self, module_name, config, game_state):
        module_class = __import__(module_name)
        module = module_class.initialize(config, game_state)
        self.modules[module_name] = module

    def update_modules(self, game_state):
        for module in self.modules.values():
            module.update(game_state)

    def terminate_modules(self, game_state):
        for module in self.modules.values():
            module.terminate(game_state)
