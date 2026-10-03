import curses
import random
import time
from dataclasses import dataclass, field
from typing import List, Tuple, Set, Optional

# ---------- Constants ----------
WIDTH = 40
HEIGHT = 20
SNAKE_CHAR = "O"
FOOD_CHAR = "*"
EMPTY_CHAR = " "
INITIAL_SNAKE_LENGTH = 3
MOVE_DELAY = 0.1  # seconds per move

# ---------- Data Models ----------
@dataclass
class Point:
    x: int
    y: int

    def __add__(self, other: "Point") -> "Point":
        return Point(self.x + other.x, self.y + other.y)

    def __hash__(self) -> int:
        return hash((self.x, self.y))

@dataclass
class Snake:
    body: List[Point] = field(default_factory=list)
    direction: Point = field(default_factory=lambda: Point(1, 0))  # moving right

    def __post_init__(self):
        # Initialize snake in the center
        center = Point(WIDTH // 2, HEIGHT // 2)
        self.body = [center + Point(-i, 0) for i in range(INITIAL_SNAKE_LENGTH)]

    def move(self, grow: bool = False) -> bool:
        """Move snake in current direction. Return False if collision occurs."""
        new_head = self.body[0] + self.direction
        # Check wall collision
        if not (0 <= new_head.x < WIDTH and 0 <= new_head.y < HEIGHT):
            return False
        # Check self collision
        if new_head in self.body:
            return False
        # Move
        self.body.insert(0, new_head)
        if not grow:
            self.body.pop()
        return True

    def set_direction(self, new_dir: Point):
        # Prevent reverse
        if (self.direction.x + new_dir.x, self.direction.y + new_dir.y) != (0, 0):
            self.direction = new_dir

@dataclass
class Food:
    position: Point

    @staticmethod
    def spawn(snake_body: Set[Point]) -> "Food":
        """Spawn food at random location not occupied by snake."""
        while True:
            pos = Point(random.randint(0, WIDTH - 1), random.randint(0, HEIGHT - 1))
            if pos not in snake_body:
                return Food(pos)

# ---------- Game Logic ----------
class Game:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.snake = Snake()
        self.food = Food.spawn(set(self.snake.body))
        self.score = 0
        self.game_over = False

    def handle_input(self):
        key = self.stdscr.getch()
        if key == curses.KEY_UP:
            self.snake.set_direction(Point(0, -1))
        elif key == curses.KEY_DOWN:
            self.snake.set_direction(Point(0, 1))
        elif key == curses.KEY_LEFT:
            self.snake.set_direction(Point(-1, 0))
        elif key == curses.KEY_RIGHT:
            self.snake.set_direction(Point(1, 0))

    def update(self):
        if not self.snake.move():
            self.game_over = True
            return
        # Check food consumption
        if self.snake.body[0] == self.food.position:
            self.score += 1
            # Grow snake on next move
            self.snake.move(grow=True)
            self.food = Food.spawn(set(self.snake.body))

    def draw(self):
        self.stdscr.clear()
        # Draw borders
        for x in range(WIDTH):
            self.stdscr.addch(0, x, "#")
            self.stdscr.addch(HEIGHT - 1, x, "#")
        for y in range(HEIGHT):
            self.stdscr.addch(y, 0, "#")
            self.stdscr.addch(y, WIDTH - 1, "#")
        # Draw food
        self.stdscr.addch(self.food.position.y, self.food.position.x, FOOD_CHAR)
        # Draw snake
        for idx, segment in enumerate(self.snake.body):
            ch = SNAKE_CHAR
            self.stdscr.addch(segment.y, segment.x, ch)
        # Draw score
        self.stdscr.addstr(HEIGHT, 0, f"Score: {self.score} ")
        self.stdscr.refresh()

    def run(self):
        self.stdscr.nodelay(True)
        self.stdscr.timeout(int(MOVE_DELAY * 1000))
        while not self.game_over:
            self.handle_input()
            self.update()
            self.draw()
            time.sleep(MOVE_DELAY)
        # Game over screen
        self.stdscr.nodelay(False)
        self.stdscr.addstr(HEIGHT // 2, WIDTH // 2 - 5, "GAME OVER")
        self.stdscr.addstr(HEIGHT // 2 + 1, WIDTH // 2 - 7, f"Final Score: {self.score}")
        self.stdscr.addstr(HEIGHT // 2 + 3, WIDTH // 2 - 12, "Press any key to exit.")
        self.stdscr.refresh()
        self.stdscr.getch()

# ---------- Entry Point ----------
def main(stdscr):
    curses.curs_set(0)
    game = Game(stdscr)
    game.run()

if __name__ == "__main__":
    curses.wrapper(main)