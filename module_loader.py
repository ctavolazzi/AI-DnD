# module_loader.py

class ModuleLoader:
    def __init__(self, config):
        self.modules = config["modules"]

    def load_module(self, module_name, config=None):
        module_class = __import__(module_name)
        module = module_class.initialize(config)
        self.modules[module_name] = module

    def update_modules(self, game_state):
        for module in self.modules.values():
            module.update(game_state)

    def terminate_modules(self, game_state):
        for module in self.modules.values():
            module.terminate(game_state)

    def load_all(self):
        for module_name, module_config in self.modules.items():
            self.load_module(module_name, module_config)
        return self.modules
