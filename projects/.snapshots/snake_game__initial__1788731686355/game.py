import random
import time
import sys
from dataclasses import dataclass, field
from typing import List, Tuple, Set, Optional

# --- Constants -------------------------------------------------------------
GRID_WIDTH = 20
GRID_HEIGHT = 20
INITIAL_SNAKE_LENGTH = 3
MOVE_DELAY = 0.1  # seconds between moves in the demo loop
DIRECTIONS = {
    "UP": (0, -1),
    "DOWN": (0, 1),
    "LEFT": (-1, 0),
    "RIGHT": (1, 0),
}
OPPOSITE_DIRECTION = {
    "UP": "DOWN",
    "DOWN": "UP",
    "LEFT": "RIGHT",
    "RIGHT": "LEFT",
}

# --- Data Structures -------------------------------------------------------
@dataclass(frozen=True)
class Position:
    x: int
    y: int

    def move(self, dx: int, dy: int) -> "Position":
        return Position((self.x + dx) % GRID_WIDTH, (self.y + dy) % GRID_HEIGHT)

@dataclass
class Snake:
    body: List[Position] = field(default_factory=list)
    direction: str = "RIGHT"

    def __post_init__(self):
        if not self.body:
            # start in the middle
            mid_x = GRID_WIDTH // 2
            mid_y = GRID_HEIGHT // 2
            self.body = [Position(mid_x - i, mid_y) for i in range(INITIAL_SNAKE_LENGTH)]

    def head(self) -> Position:
        return self.body[0]

    def move(self, grow: bool = False) -> None:
        dx, dy = DIRECTIONS[self.direction]
        new_head = self.head().move(dx, dy)
        self.body.insert(0, new_head)
        if not grow:
            self.body.pop()

    def set_direction(self, new_dir: str) -> None:
        if new_dir in DIRECTIONS and new_dir != OPPOSITE_DIRECTION[self.direction]:
            self.direction = new_dir

    def occupies(self, pos: Position) -> bool:
        return pos in self.body

    def collision_with_self(self) -> bool:
        return self.head() in self.body[1:]

@dataclass
class Food:
    position: Position

    @staticmethod
    def spawn(snake: Snake, occupied: Set[Position]) -> "Food":
        while True:
            pos = Position(random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
            if pos not in occupied:
                return Food(pos)

# --- Game Logic -------------------------------------------------------------
class Game:
    def __init__(self):
        self.snake = Snake()
        self.food = Food.spawn(self.snake, set(self.snake.body))
        self.score = 0
        self.is_over = False

    def step(self) -> None:
        if self.is_over:
            return
        next_head = self.snake.head().move(*DIRECTIONS[self.snake.direction])
        # Check wall collision (with wrap-around this is always false)
        # Check self collision
        if next_head in self.snake.body:
            self.is_over = True
            return
        # Check food
        if next_head == self.food.position:
            self.snake.move(grow=True)
            self.score += 1
            occupied = set(self.snake.body)
            self.food = Food.spawn(self.snake, occupied)
        else:
            self.snake.move(grow=False)

    def change_direction(self, new_dir: str) -> None:
        self.snake.set_direction(new_dir)

    def get_state(self) -> Tuple[List[Position], Position, int, bool]:
        return (self.snake.body, self.food.position, self.score, self.is_over)

# --- Demo Loop (guarded) ----------------------------------------------------
if __name__ == "__main__":
    # Simple console demo using arrow keys via curses
    try:
        import curses
    except ImportError:
        print("Curses module is not available on this platform.")
        sys.exit(1)

    def main(stdscr):
        curses.curs_set(0)
        stdscr.nodelay(True)
        stdscr.timeout(100)

        game = Game()
        key_map = {
            curses.KEY_UP: "UP",
            curses.KEY_DOWN: "DOWN",
            curses.KEY_LEFT: "LEFT",
            curses.KEY_RIGHT: "RIGHT",
        }

        while not game.is_over:
            try:
                key = stdscr.getch()
            except KeyboardInterrupt:
                break
            if key in key_map:
                game.change_direction(key_map[key])

            game.step()
            stdscr.clear()
            # Draw grid
            for y in range(GRID_HEIGHT):
                for x in range(GRID_WIDTH):
                    char = "."
                    pos = Position(x, y)
                    if pos == game.food.position:
                        char = "F"
                    elif pos == game.snake.head():
                        char = "H"
                    elif pos in game.snake.body[1:]:
                        char = "S"
                    stdscr.addch(y, x, char)
            stdscr.addstr(GRID_HEIGHT + 1, 0, f"Score: {game.score}")
            stdscr.refresh()
            time.sleep(MOVE_DELAY)

        stdscr.addstr(GRID_HEIGHT // 2, GRID_WIDTH // 2 - 5, "GAME OVER")
        stdscr.refresh()
        time.sleep(2)

    curses.wrapper(main)