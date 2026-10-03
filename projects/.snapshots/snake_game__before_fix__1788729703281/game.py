import random
import sys
import time
from dataclasses import dataclass, field
from typing import Deque, List, Tuple, Optional, Set

# Basic configuration constants
GRID_WIDTH = 20
GRID_HEIGHT = 15
INITIAL_SNAKE_LENGTH = 3
FOOD_SYMBOL = "🍎"
SNAKE_SYMBOL = "🟩"
EMPTY_SYMBOL = " "
DIRECTION_DELTAS = {
    "UP": (0, -1),
    "DOWN": (0, 1),
    "LEFT": (-1, 0),
    "RIGHT": (1, 0),
}

@dataclass
class SnakeGame:
    width: int = GRID_WIDTH
    height: int = GRID_HEIGHT
    snake: Deque[Tuple[int, int]] = field(default_factory=deque)
    direction: str = "RIGHT"
    food: Optional[Tuple[int, int]] = None
    score: int = 0
    game_over: bool = False

    def __post_init__(self):
        self.reset()

    def reset(self):
        """Reset the game to the initial state."""
        self.snake.clear()
        mid_x = self.width // 2
        mid_y = self.height // 2
        for i in range(INITIAL_SNAKE_LENGTH):
            self.snake.append((mid_x - i, mid_y))
        self.direction = "RIGHT"
        self.score = 0
        self.game_over = False
        self.spawn_food()

    def spawn_food(self):
        """Place food on a random empty cell."""
        all_cells = {(x, y) for x in range(self.width) for y in range(self.height)}
        occupied = set(self.snake)
        available = list(all_cells - occupied)
        if not available:
            # No space left: player wins
            self.food = None
            return
        self.food = random.choice(available)

    def set_direction(self, new_dir: str):
        """Change the snake's moving direction, disallow 180° turns."""
        opposite = {"UP": "DOWN", "DOWN": "UP", "LEFT": "RIGHT", "RIGHT": "LEFT"}
        if new_dir in DIRECTION_DELTAS and new_dir != opposite[self.direction]:
            self.direction = new_dir

    def move(self):
        """Move the snake one step in the current direction."""
        if self.game_over:
            return
        dx, dy = DIRECTION_DELTAS[self.direction]
        head_x, head_y = self.snake[0]
        new_head = (head_x + dx, head_y + dy)

        # Check wall collision
        if not (0 <= new_head[0] < self.width and 0 <= new_head[1] < self.height):
            self.game_over = True
            return

        # Check self collision
        if new_head in self.snake:
            self.game_over = True
            return

        # Add new head
        self.snake.appendleft(new_head)

        # Check food consumption
        if self.food and new_head == self.food:
            self.score += 1
            self.spawn_food()
        else:
            # Remove tail
            self.snake.pop()

    def get_grid(self) -> List[List[str]]:
        """Return a 2D list representing the current grid for rendering."""
        grid = [[EMPTY_SYMBOL for _ in range(self.width)] for _ in range(self.height)]
        for x, y in self.snake:
            grid[y][x] = SNAKE_SYMBOL
        if self.food:
            fx, fy = self.food
            grid[fy][fx] = FOOD_SYMBOL
        return grid

    def render(self):
        """Print the current grid to the console."""
        grid = self.get_grid()
        lines = ["+" + "-" * self.width + "+"]
        for row in grid:
            lines.append("|" + "".join(row) + "|")
        lines.append("+" + "-" * self.width + "+")
        lines.append(f"Score: {self.score}")
        print("\n".join(lines))

# Only run the interactive demo when executed directly
if __name__ == "__main__":
    try:
        import curses
    except ImportError:
        print("Curses library is required to run the interactive demo.")
        sys.exit(1)

    def main(stdscr):
        curses.curs_set(0)
        stdscr.nodelay(True)
        stdscr.timeout(150)

        game = SnakeGame()

        key_map = {
            curses.KEY_UP: "UP",
            curses.KEY_DOWN: "DOWN",
            curses.KEY_LEFT: "LEFT",
            curses.KEY_RIGHT: "RIGHT",
        }

        while not game.game_over:
            try:
                key = stdscr.getch()
            except Exception:
                key = -1

            if key in key_map:
                game.set_direction(key_map[key])

            game.move()

            stdscr.clear()
            grid = game.get_grid()
            for y, row in enumerate(grid):
                stdscr.addstr(y, 0, "".join(row))
            stdscr.addstr(game.height + 1, 0, f"Score: {game.score}")
            stdscr.refresh()
            time.sleep(0.1)

        stdscr.clear()
        stdscr.addstr(0, 0, "Game Over! Press any key to exit.")
        stdscr.refresh()
        stdscr.nodelay(False)
        stdscr.getch()

    curses.wrapper(main)