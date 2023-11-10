# main_menu.py
class MainMenu:
    def __init__(self, game):
        self.game = game

    def display(self):
        print("Welcome to the DnD Game!")
        print("1. Start Game")
        print("2. Load Game")
        print("3. Save Game")
        print("4. Options")
        print("5. Exit")
        choice = input("Select an option: ")
        return choice

    def handle_selection(self, selection):
        menu_options = {
            "1": self.game.start,
            "2": self.game.load,
            "3": self.game.save,
            "4": self.game.options,
            "5": self.game.exit
        }
        action = menu_options.get(selection, lambda: print("Invalid option, please try again."))
        action()
