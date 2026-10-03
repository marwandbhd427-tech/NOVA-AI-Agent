import random
import curses
import time
from dataclasses import dataclass, field
from typing import List, Tuple, Set

# Game constants
WIDTH: int = 40
HEIGHT: int = 20
INITIAL_SNAKE_LENGTH: int = 3
SNAKE_CHAR: str = "O"
FOOD_CHAR: str = "*"
EMPTY_CHAR: str = " "
SLEEP_TIME: float = 0.1  # seconds per frame

# Directions: (dy, dx)
UP: Tuple[int, int] = (-1, 0)
DOWN: Tuple[int, int] = (1, 0)
LEFT: Tuple[int, int] = (0, -1)
RIGHT: Tuple[int, int] = (0, 1)
DIRECTION_KEYS = {
    curses.KEY_UP: UP,
    curses.KEY_DOWN: DOWN,
    curses.KEY_LEFT: LEFT,
    curses.KEY_RIGHT: RIGHT,
    ord('w'): UP,
    ord('s'): DOWN,
    ord('a'): LEFT,
    ord('d'): RIGHT,
}

@dataclass
class Snake:
    body: List[Tuple[int, int]] = field(default_factory=list)
    direction: Tuple[int, int] = DOWN
    grow_pending: int = 0

    def __post_init__(self):
        if not self.body:
            # Initialize snake in the center
            mid_y, mid_x = HEIGHT // 2, WIDTH // 2
            self.body = [(mid_y, mid_x - i) for i in range(INITIAL_SNAKE_LENGTH)]
            self.direction = RIGHT

    def set_direction(self, new_dir: Tuple[int, int]):
        # Prevent reversing
        if (new_dir[0] == -self.direction[0] and new_dir[1] == -self.direction[1]):
            return
        self.direction = new_dir

    def head(self) -> Tuple[int, int]:
        return self.body[0]

    def move(self):
        new_head = (self.head()[0] + self.direction[0], self.head()[1] + self.direction[1])
        self.body.insert(0, new_head)
        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            self.body.pop()

    def grow(self, segments: int = 1):
        self.grow_pending += segments

    def collides_with_self(self) -> bool:
        return self.head() in self.body[1:]

    def collides_with_wall(self) -> bool:
        y, x = self.head()
        return y <= 0 or y >= HEIGHT - 1 or x <= 0 or x >= WIDTH - 1

@dataclass
class Food:
    position: Tuple[int, int] = (0, 0)

    def spawn(self, snake_body: Set[Tuple[int, int]]):
        while True:
            y = random.randint(1, HEIGHT - 2)
            x = random.randint(1, WIDTH - 2)
            if (y, x) not in snake_body:
                self.position = (y, x)
                break

class Game:
    def __init__(self):
        self.snake = Snake()
        self.food = Food()
        self.food.spawn(set(self.snake.body))
        self.score = 0
        self.game_over = False

    def update(self):
        if self.game_over:
            return
        self.snake.move()
        if self.snake.collides_with_wall() or self.snake.collides_with_self():
            self.game_over = True
            return
        if self.snake.head() == self.food.position:
            self.snake.grow()
            self.score += 1
            self.food.spawn(set(self.snake.body))

    def render(self, stdscr):
        stdscr.clear()
        # Draw borders
        for x in range(WIDTH):
            stdscr.addch(0, x, "#")
            stdscr.addch(HEIGHT - 1, x, "#")
        for y in range(HEIGHT):
            stdscr.addch(y, 0, "#")
            stdscr.addch(y, WIDTH - 1, "#")
        # Draw food
        fy, fx = self.food.position
        stdscr.addch(fy, fx, FOOD_CHAR)
        # Draw snake
        for i, (y, x) in enumerate(self.snake.body):
            stdscr.addch(y, x, SNAKE_CHAR if i == 0 else "o")
        # Draw score
        stdscr.addstr(HEIGHT, 0, f"Score: {self.score}  ")
        stdscr.refresh()

    def handle_input(self, key):
        if key in DIRECTION_KEYS:
            self.snake.set_direction(DIRECTION_KEYS[key])

    def run(self):
        curses.wrapper(self._curses_loop)

    def _curses_loop(self, stdscr):
        # Setup
        stdscr.nodelay(True)
        stdscr.keypad(True)
        curses.curs_set(0)
        while not self.game_over:
            key = stdscr.getch()
            if key != -1:
                self.handle_input(key)
            self.update()
            self.render(stdscr)
            time.sleep(SLEEP_TIME)
        # Game over screen
        stdscr.nodelay(False)
        stdscr.addstr(HEIGHT // 2, WIDTH // 2 - 5, "GAME OVER")
        stdscr.addstr(HEIGHT // 2 + 1, WIDTH // 2 - 7, f"Final Score: {self.score}")
        stdscr.addstr(HEIGHT // 2 + 3, WIDTH // 2 - 12, "Press any key to exit")
        stdscr.getch()

if __name__ == "__main__":
    game = Game()
    game.run()