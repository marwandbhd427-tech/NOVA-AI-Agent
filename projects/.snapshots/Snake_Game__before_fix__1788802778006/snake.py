import random
import sys
from dataclasses import dataclass, field
from typing import List, Tuple, Set

# ----------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------
WIDTH: int = 20   # board width (number of columns)
HEIGHT: int = 10  # board height (number of rows)

# Directions represented as (dy, dx)
UP: Tuple[int, int] = (-1, 0)
DOWN: Tuple[int, int] = (1, 0)
LEFT: Tuple[int, int] = (0, -1)
RIGHT: Tuple[int, int] = (0, 1)
OPPOSITE: dict = {UP: DOWN, DOWN: UP, LEFT: RIGHT, RIGHT: LEFT}


# ----------------------------------------------------------------------
# Snake
# ----------------------------------------------------------------------
@dataclass
class Snake:
    """Represents the snake: its body segments, direction, and growth status."""
    body: List[Tuple[int, int]] = field(default_factory=list)
    direction: Tuple[int, int] = RIGHT
    grow_pending: int = 0  # number of segments to grow

    def __post_init__(self):
        if not self.body:
            # start with a 3‑segment snake in the center
            mid_y, mid_x = HEIGHT // 2, WIDTH // 2
            self.body = [
                (mid_y, mid_x - 1),
                (mid_y, mid_x),
                (mid_y, mid_x + 1)
            ]

    def turn(self, new_direction: Tuple[int, int]) -> None:
        """Change direction unless it's directly opposite."""
        if new_direction != OPPOSITE[self.direction]:
            self.direction = new_direction

    def move(self) -> Tuple[int, int]:
        """Advance the snake one step; return the new head position."""
        head_y, head_x = self.body[0]
        dy, dx = self.direction
        new_head = (head_y + dy, head_x + dx)
        self.body.insert(0, new_head)

        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            self.body.pop()  # remove tail

        return new_head

    def grow(self, segments: int = 1) -> None:
        """Increase the snake's length by the given number of segments."""
        self.grow_pending += segments

    def collides_with_self(self) -> bool:
        """Return True if the head collides with the body."""
        head = self.body[0]
        return head in self.body[1:]

    def collides_with_wall(self) -> bool:
        """Return True if the head is outside the board boundaries."""
        head_y, head_x = self.body[0]
        return not (0 <= head_y < HEIGHT and 0 <= head_x < WIDTH)


# ----------------------------------------------------------------------
# Food
# ----------------------------------------------------------------------
@dataclass
class Food:
    """Represents a food item on the board."""
    position: Tuple[int, int] = (-1, -1)

    def spawn(self, occupied: Set[Tuple[int, int]]) -> None:
        """Place food at a random location not occupied by the snake."""
        empty_spaces = [
            (y, x)
            for y in range(HEIGHT)
            for x in range(WIDTH)
            if (y, x) not in occupied
        ]
        if not empty_spaces:
            # No space left; keep the food off the board
            self.position = (-1, -1)
            return
        self.position = random.choice(empty_spaces)


# ----------------------------------------------------------------------
# Game
# ----------------------------------------------------------------------
@dataclass
class Game:
    """Game state: board, snake, food, score, and game over flag."""
    snake: Snake = field(default_factory=Snake)
    food: Food = field(default_factory=Food)
    score: int = 0
    game_over: bool = False

    def __post_init__(self):
        # Spawn first food
        self.food.spawn(set(self.snake.body))

    def update(self) -> None:
        """Advance the game one tick."""
        if self.game_over:
            return

        # Move snake
        new_head = self.snake.move()

        # Check collisions
        if self.snake.collides_with_wall() or self.snake.collides_with_self():
            self.game_over = True
            return

        # Check food consumption
        if new_head == self.food.position:
            self.score += 1
            self.snake.grow()
            self.food.spawn(set(self.snake.body))

    def render(self) -> List[str]:
        """Return a list of strings representing the current board state."""
        board = [[' ' for _ in range(WIDTH)] for _ in range(HEIGHT)]

        # Draw food
        fy, fx = self.food.position
        if 0 <= fy < HEIGHT and 0 <= fx < WIDTH:
            board[fy][fx] = '*'

        # Draw snake
        for idx, (y, x) in enumerate(self.snake.body):
            if 0 <= y < HEIGHT and 0 <= x < WIDTH:
                board[y][x] = 'O' if idx == 0 else 'o'

        # Convert to strings
        return [''.join(row) for row in board]


# ----------------------------------------------------------------------
# Console entry point (optional)
# ----------------------------------------------------------------------
def _run_console():
    """Run a simple console based game using curses if available."""
    try:
        import curses
    except ImportError:
        print("Curses module is not available.")
        return

    def main(stdscr):
        curses.curs_set(0)
        stdscr.nodelay(True)
        stdscr.timeout(100)

        game = Game()
        key_map = {
            curses.KEY_UP: UP,
            curses.KEY_DOWN: DOWN,
            curses.KEY_LEFT: LEFT,
            curses.KEY_RIGHT: RIGHT,
            ord('w'): UP,
            ord('s'): DOWN,
            ord('a'): LEFT,
            ord('d'): RIGHT,
        }

        while not game.game_over:
            try:
                key = stdscr.getch()
                if key in key_map:
                    game.snake.turn(key_map[key])
                elif key == ord('q'):
                    break

                game.update()

                stdscr.clear()
                for y, line in enumerate(game.render()):
                    stdscr.addstr(y, 0, line)
                stdscr.addstr(HEIGHT + 1, 0, f"Score: {game.score}")
                stdscr.refresh()
            except KeyboardInterrupt:
                break

        stdscr.nodelay(False)
        stdscr.addstr(HEIGHT + 3, 0, "Game Over! Press any key to exit.")
        stdscr.getch()

    curses.wrapper(main)


if __name__ == "__main__" and sys.argv[0].endswith("snake.py"):
    _run_console()