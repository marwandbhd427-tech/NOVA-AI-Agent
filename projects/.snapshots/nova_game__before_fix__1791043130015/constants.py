import curses
import random
from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Tuple, Set

# ──────────────────────────────────────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────────────────────────────────────
SCREEN_HEIGHT = 20
SCREEN_WIDTH = 40
CELL_CHAR = "■"
FOOD_CHAR = "●"
EMPTY_CHAR = " "
SNAKE_CHAR = "█"
SNAKE_HEAD_CHAR = "▓"
SCORE_POS = (0, 0)
DELAY = 0.1  # seconds per move

# ──────────────────────────────────────────────────────────────────────────────
# Direction enumeration
# ──────────────────────────────────────────────────────────────────────────────
class Direction(Enum):
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()

    @property
    def delta(self) -> Tuple[int, int]:
        return {
            Direction.UP: (-1, 0),
            Direction.DOWN: (1, 0),
            Direction.LEFT: (0, -1),
            Direction.RIGHT: (0, 1),
        }[self]

# ──────────────────────────────────────────────────────────────────────────────
# Data classes
# ──────────────────────────────────────────────────────────────────────────────
@dataclass(frozen=True)
class Position:
    y: int
    x: int

# ──────────────────────────────────────────────────────────────────────────────
# Snake class
# ──────────────────────────────────────────────────────────────────────────────
class Snake:
    def __init__(self, init_pos: Position, length: int = 3):
        self.body: List[Position] = [init_pos]
        self.direction: Direction = Direction.RIGHT
        for _ in range(1, length):
            self.body.append(
                Position(self.body[-1].y, self.body[-1].x - 1)
            )
        self.grow_pending: int = 0

    def set_direction(self, new_dir: Direction):
        # Prevent reverse direction
        opposite = {
            Direction.UP: Direction.DOWN,
            Direction.DOWN: Direction.UP,
            Direction.LEFT: Direction.RIGHT,
            Direction.RIGHT: Direction.LEFT,
        }
        if new_dir != opposite[self.direction]:
            self.direction = new_dir

    def head(self) -> Position:
        return self.body[0]

    def move(self):
        dy, dx = self.direction.delta
        new_head = Position(self.head().y + dy, self.head().x + dx)
        self.body.insert(0, new_head)
        if self.grow_pending:
            self.grow_pending -= 1
        else:
            self.body.pop()

    def grow(self, n: int = 1):
        self.grow_pending += n

    def collides_with_self(self) -> bool:
        return self.head() in self.body[1:]

    def collides_with_wall(self, max_y: int, max_x: int) -> bool:
        return not (0 <= self.head().y < max_y and 0 <= self.head().x < max_x)

# ──────────────────────────────────────────────────────────────────────────────
# Food class
# ──────────────────────────────────────────────────────────────────────────────
class Food:
    def __init__(self, max_y: int, max_x: int, occupied: Set[Position]):
        self.max_y = max_y
        self.max_x = max_x
        self.position = self.spawn(occupied)

    def spawn(self, occupied: Set[Position]) -> Position:
        available = [
            Position(y, x)
            for y in range(self.max_y)
            for x in range(self.max_x)
            if Position(y, x) not in occupied
        ]
        if not available:
            raise RuntimeError("No space to spawn food.")
        return random.choice(available)

# ──────────────────────────────────────────────────────────────────────────────
# Game class
# ──────────────────────────────────────────────────────────────────────────────
class Game:
    def __init__(self, height: int = SCREEN_HEIGHT, width: int = SCREEN_WIDTH):
        self.height = height
        self.width = width
        init_pos = Position(height // 2, width // 2)
        self.snake = Snake(init_pos)
        self.food = Food(height, width, set(self.snake.body))
        self.score = 0
        self.game_over = False

    def step(self):
        if self.game_over:
            return
        self.snake.move()
        if self.snake.collides_with_wall(self.height, self.width) or self.snake.collides_with_self():
            self.game_over = True
            return
        if self.snake.head() == self.food.position:
            self.snake.grow()
            self.score += 1
            self.food = Food(self.height, self.width, set(self.snake.body))

    def get_state(self):
        """Return a 2D list of characters representing the current board."""
        board = [[EMPTY_CHAR for _ in range(self.width)] for _ in range(self.height)]
        for pos in self.snake.body[1:]:
            board[pos.y][pos.x] = SNAKE_CHAR
        head = self.snake.head()
        board[head.y][head.x] = SNAKE_HEAD_CHAR
        board[self.food.position.y][self.food.position.x] = FOOD_CHAR
        return board

    def render(self, stdscr):
        stdscr.clear()
        board = self.get_state()
        for y, row in enumerate(board):
            stdscr.addstr(y, 0, "".join(row))
        stdscr.addstr(SCORE_POS[0], SCORE_POS[1], f"Score: {self.score}")
        if self.game_over:
            stdscr.addstr(self.height // 2, self.width // 2 - 5, "GAME OVER")
        stdscr.refresh()

    def handle_input(self, key):
        mapping = {
            curses.KEY_UP: Direction.UP,
            curses.KEY_DOWN: Direction.DOWN,
            curses.KEY_LEFT: Direction.LEFT,
            curses.KEY_RIGHT: Direction.RIGHT,
        }
        if key in mapping:
            self.snake.set_direction(mapping[key])

# ──────────────────────────────────────────────────────────────────────────────
# Main loop guarded
# ──────────────────────────────────────────────────────────────────────────────
def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(int(DELAY * 1000))
    game = Game()
    while True:
        key = stdscr.getch()
        if key == ord("q"):
            break
        if key != -1:
            game.handle_input(key)
        game.step()
        game.render(stdscr)
        if game.game_over:
            stdscr.nodelay(False)
            stdscr.getch()
            break

if __name__ == "__main__":
    curses.wrapper(main)