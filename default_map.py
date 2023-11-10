class Default_Map:
    def __init__(self, size):
        self.size = size
        self.grid = [['?' for _ in range(size)] for _ in range(size)]
        self.explored_positions = set()

    def mark_as_explored(self, position):
        x, y = position
        self.explored_positions.add(position)
        self.grid[y][x] = '.'

    def display(self, player_position):
        for y in range(self.size):
            for x in range(self.size):
                if (x, y) == player_position:
                    print('X', end='')
                elif (x, y) in self.explored_positions:
                    print('.', end='')
                else:
                    print('?', end='')
            print()  # Newline after each row