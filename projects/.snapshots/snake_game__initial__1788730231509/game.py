import random
import sys
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Tuple, Optional

# -------------------- Constants -------------------- #
DEFAULT_WIDTH = 20
DEFAULT_HEIGHT = 10
DEFAULT_SNAKE_START = [(10, 5), (9, 5), (8, 5)]  # Head at index 0

# -------------------- Enums -------------------- #
class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

    def opposite(self) -> "Direction":
        """Return the opposite direction."""
        mapping = {Direction.UP: Direction.DOWN,
                   Direction.DOWN: Direction.UP,
                   Direction.LEFT: Direction.RIGHT,
                   Direction.RIGHT: Direction.LEFT}
        return mapping[self]

# -------------------- Data Classes -------------------- #
@dataclass
class Snake:
    body: List[Tuple[int, int]] = field(default_factory=lambda: DEFAULT_SNAKE_START.copy())
    direction: Direction = Direction.RIGHT
    grow_pending: int = 0

    def set_direction(self, new_dir: Direction) -> None:
        """Change direction unless it's directly opposite."""
        if new_dir != self.direction.opposite():
            self.direction = new_dir

    def move(self) -> None:
        """Advance snake by one step."""
        dx, dy = self.direction.value
        new_head = (self.body[0][0] + dx, self.body[0][1] + dy)
        self.body.insert(0, new_head)
        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            self.body.pop()

    def grow(self, segments: int = 1) -> None:
        """Increase length after eating food."""
        self.grow_pending += segments

    def head(self) -> Tuple[int, int]:
        return self.body[0]

    def collides_with_self(self) -> bool:
        return self.head() in self.body[1:]

@dataclass
class Food:
    position: Tuple[int, int]

    @staticmethod
    def spawn(width: int, height: int, occupied: List[Tuple[int, int]]) -> "Food":
        """Generate food not on occupied cells."""
        while True:
            pos = (random.randint(0, width - 1), random.randint(0, height - 1))
            if pos not in occupied:
                return Food(position=pos)

# -------------------- Game Class -------------------- #
@dataclass
class Game:
    width: int = DEFAULT_WIDTH
    height: int = DEFAULT_HEIGHT
    snake: Snake = field(default_factory=Snake)
    food: Food = field(init=False)
    score: int = 0
    alive: bool = True

    def __post_init__(self) -> None:
        self.spawn_food()

    def spawn_food(self) -> None:
        self.food = Food.spawn(self.width, self.height, self.snake.body)

    def step(self) -> None:
        """Advance game state by one tick."""
        if not self.alive:
            return
        self.snake.move()
        if self.check_collision():
            self.alive = False
            return
        if self.snake.head() == self.food.position:
            self.snake.grow()
            self.score += 1
            self.spawn_food()

    def check_collision(self) -> bool:
        """Return True if snake collides with wall or itself."""
        x, y = self.snake.head()
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return True
        if self.snake.collides_with_self():
            return True
        return False

    def set_direction(self, dir_key: str) -> None:
        """Convenience method to set direction via key input."""
        mapping = {
            "w": Direction.UP,
            "s": Direction.DOWN,
            "a": Direction.LEFT,
            "d": Direction.RIGHT,
        }
        if dir_key in mapping:
            self.snake.set_direction(mapping[dir_key])

    def render(self) -> List[str]:
        """Return a list of strings representing the grid for testing."""
        grid = [[" " for _ in range(self.width)] for _ in range(self.height)]
        # Draw food
        fx, fy = self.food.position
        grid[fy][fx] = "*"
        # Draw snake
        for idx, (x, y) in enumerate(self.snake.body):
            if 0 <= x < self.width and 0 <= y < self.height:
                grid[y][x] = "O" if idx == 0 else "o"
        return ["".join(row) for row in grid]

# -------------------- Optional CLI -------------------- #
def _curses_main(stdscr):
    import curses
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(150)

    game = Game()
    key_mapping = {curses.KEY_UP: "w", curses.KEY_DOWN: "s",
                   curses.KEY_LEFT: "a", curses.KEY_RIGHT: "d"}

    while True:
        stdscr.clear()
        for y, row in enumerate(game.render()):
            stdscr.addstr(y, 0, row)
        stdscr.addstr(game.height + 1, 0, f"Score: {game.score}")
        stdscr.refresh()

        if not game.alive:
            stdscr.addstr(game.height // 2, game.width // 2 - 5, "GAME OVER")
            stdscr.nodelay(False)
            stdscr.getch()
            break

        try:
            key = stdscr.getch()
        except Exception:
            key = -1
        if key in key_mapping:
            game.set_direction(key_mapping[key])

        game.step()

if __name__ == "__main__":
    try:
        import curses
        curses.wrapper(_curses_main)
    except Exception as e:
        print("Curses not available or error occurred:", e, file=sys.stderr)
        print("You can import the Game class in your own environment to test logic.", file=sys.stderr)