import curses
import random
import time
from dataclasses import dataclass, field
from typing import List, Tuple, Optional

# ---------- constants ----------
WIDTH = 40
HEIGHT = 20
INITIAL_SNAKE_LENGTH = 5
SPEED = 0.1  # seconds per tick
DIRECTIONS = {
    curses.KEY_UP: (0, -1),
    curses.KEY_DOWN: (0, 1),
    curses.KEY_LEFT: (-1, 0),
    curses.KEY_RIGHT: (1, 0),
}
OPPOSITE_DIRECTIONS = {
    curses.KEY_UP: curses.KEY_DOWN,
    curses.KEY_DOWN: curses.KEY_UP,
    curses.KEY_LEFT: curses.KEY_RIGHT,
    curses.KEY_RIGHT: curses.KEY_LEFT,
}


# ---------- data structures ----------
@dataclass
class Snake:
    body: List[Tuple[int, int]] = field(default_factory=list)
    direction: int = curses.KEY_RIGHT
    grow_pending: int = 0

    def __post_init__(self):
        if not self.body:
            # Initialize snake in the center
            cx, cy = WIDTH // 2, HEIGHT // 2
            self.body = [(cx - i, cy) for i in range(INITIAL_SNAKE_LENGTH)]
            self.direction = curses.KEY_RIGHT

    def set_direction(self, new_dir: int):
        if new_dir in DIRECTIONS and OPPOSITE_DIRECTIONS[new_dir] != self.direction:
            self.direction = new_dir

    def move(self):
        dx, dy = DIRECTIONS[self.direction]
        head_x, head_y = self.body[0]
        new_head = ((head_x + dx) % WIDTH, (head_y + dy) % HEIGHT)
        self.body.insert(0, new_head)
        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            self.body.pop()

    def grow(self, n: int = 1):
        self.grow_pending += n

    def collides_with_self(self) -> bool:
        return self.body[0] in self.body[1:]


@dataclass
class Food:
    position: Tuple[int, int] = field(default_factory=lambda: (0, 0))

    def spawn(self, snake: Snake):
        while True:
            pos = (random.randint(0, WIDTH - 1), random.randint(0, HEIGHT - 1))
            if pos not in snake.body:
                self.position = pos
                break


@dataclass
class Game:
    snake: Snake = field(default_factory=Snake)
    food: Food = field(default_factory=Food)
    score: int = 0
    running: bool = True

    def __post_init__(self):
        self.food.spawn(self.snake)

    def update(self):
        self.snake.move()
        if self.snake.body[0] == self.food.position:
            self.snake.grow()
            self.score += 1
            self.food.spawn(self.snake)

        if self.snake.collides_with_self():
            self.running = False

    def handle_input(self, key: int):
        if key == ord('q'):
            self.running = False
        else:
            self.snake.set_direction(key)

    def render(self, stdscr):
        stdscr.clear()
        # Draw borders
        for x in range(WIDTH + 2):
            stdscr.addch(0, x, '#')
            stdscr.addch(HEIGHT + 1, x, '#')
        for y in range(1, HEIGHT + 1):
            stdscr.addch(y, 0, '#')
            stdscr.addch(y, WIDTH + 1, '#')

        # Draw food
        fx, fy = self.food.position
        stdscr.addch(fy + 1, fx + 1, '*')

        # Draw snake
        for i, (x, y) in enumerate(self.snake.body):
            ch = 'O' if i == 0 else 'o'
            stdscr.addch(y + 1, x + 1, ch)

        # Draw score
        stdscr.addstr(HEIGHT + 3, 0, f'Score: {self.score}  (Press q to quit)')
        stdscr.refresh()


def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(0)
    game = Game()

    while game.running:
        key = stdscr.getch()
        if key != -1:
            game.handle_input(key)

        game.update()
        game.render(stdscr)
        time.sleep(SPEED)

    # Game over
    stdscr.nodelay(False)
    stdscr.addstr(HEIGHT // 2, WIDTH // 2 - 5, 'Game Over')
    stdscr.addstr(HEIGHT // 2 + 1, WIDTH // 2 - 7, f'Final Score: {game.score}')
    stdscr.addstr(HEIGHT // 2 + 3, WIDTH // 2 - 12, 'Press any key to exit.')
    stdscr.refresh()
    stdscr.getch()


if __name__ == "__main__":
    curses.wrapper(main)