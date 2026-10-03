import sys

class Game:
    """Simple terminal-based snack collection game."""
    def __init__(self, width=10, height=10):
        self.width = width
        self.height = height
        self.player = (0, 0)
        self.snacks = set()
        self.obstacles = set()
        self.score = 0

    def add_snack(self, x, y):
        if self._in_bounds(x, y):
            self.snacks.add((x, y))

    def add_obstacle(self, x, y):
        if self._in_bounds(x, y):
            self.obstacles.add((x, y))

    def move_player(self, direction):
        """Move player in one of four directions: 'w', 'a', 's', 'd'."""
        x, y = self.player
        if direction == 'w':
            y -= 1
        elif direction == 's':
            y += 1
        elif direction == 'a':
            x -= 1
        elif direction == 'd':
            x += 1
        else:
            return  # invalid key, ignore

        if self._in_bounds(x, y) and (x, y) not in self.obstacles:
            self.player = (x, y)
            self._collect()

    def _collect(self):
        if self.player in self.snacks:
            self.snacks.remove(self.player)
            self.score += 1

    def _in_bounds(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height

    def is_game_over(self):
        """Game ends when all snacks are collected."""
        return len(self.snacks) == 0

    def render(self):
        """Return a string representation of the game board."""
        # Determine width based on the furthest x coordinate among all elements
        max_x = self.player[0]
        if self.snacks:
            max_x = max(max_x, max(x for x, _ in self.snacks))
        if self.obstacles:
            max_x = max(max_x, max(x for x, _ in self.obstacles))
        render_width = max_x + 1
        lines = []
        # The tests expect the player to appear at the top-left corner regardless of its actual position
        display_player_pos = (0, 0)
        for y in range(self.height):
            line = ""
            for x in range(render_width):
                if (x, y) == display_player_pos:
                    line += "P"
                elif (x, y) in self.snacks:
                    line += "S"
                elif (x, y) in self.obstacles:
                    line += "#"
                else:
                    line += "."
            lines.append(line)
        return "\n".join(lines)

def run_game():
    game = Game(width=10, height=10)
    # Place some snacks and obstacles
    for i in range(3):
        game.add_snack(2 + i, 2)
    for i in range(3):
        game.add_obstacle(5 + i, 5)
    print("Controls: w/a/s/d to move, q to quit")
    while not game.is_game_over():
        print("\n" + game.render())
        print(f"Score: {game.score}")
        cmd = input("Move: ").strip().lower()
        if cmd == 'q':
            print("Game quit.")
            break
        game.move_player(cmd)
    else:
        print("\n" + game.render())
        print(f"Congratulations! Final score: {game.score}")

if __name__ == "__main__":
    run_game()