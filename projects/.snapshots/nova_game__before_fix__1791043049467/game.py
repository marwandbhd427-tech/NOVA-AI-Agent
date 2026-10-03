import curses
import random
import time
from dataclasses import dataclass, field
from typing import List, Tuple

# Game configuration constants
GRID_WIDTH = 40
GRID_HEIGHT = 20
INITIAL_SNAKE_LENGTH = 3
SNAKE_CHAR = "O"
FOOD_CHAR = "*"
DELAY = 0.1  # seconds per frame

@dataclass
class Snake:
    body: List[Tuple[int, int]] = field(default_factory=list)
    direction: Tuple[int, int] = (0, 1)  # start moving right

    def __post_init__(self):
        if not self.body:
            # initialize snake in the middle
            mid_x = GRID_HEIGHT // 2
            mid_y = GRID_WIDTH // 2
            self.body = [(mid_x, mid_y - i) for i in range(INITIAL_SNAKE_LENGTH)]

    def move(self, grow: bool = False):
        """Move snake in current direction. If grow is True, tail is not removed."""
        head_x, head_y = self.body[0]
        delta_x, delta_y = self.direction
        new_head = (head_x + delta_x, head_y + delta_y)
        self.body.insert(0, new_head)
        if not grow:
            self.body.pop()

    def change_direction(self, new_dir: Tuple[int, int]):
        """Change direction unless it's directly opposite."""
        opposite = (-self.direction[0], -self.direction[1])
        if new_dir != opposite:
            self.direction = new_dir

    def collides_with_self(self) -> bool:
        return self.body[0] in self.body[1:]

    def collides_with_wall(self) -> bool:
        head_x, head_y = self.body[0]
        return not (0 <= head_x < GRID_HEIGHT and 0 <= head_y < GRID_WIDTH)

@dataclass
class Food:
    position: Tuple[int, int] = (0, 0)

    def spawn(self, snake_body: List[Tuple[int, int]]):
        """Place food at random position not occupied by snake."""
        while True:
            pos = (random.randint(0, GRID_HEIGHT - 1), random.randint(0, GRID_WIDTH - 1))
            if pos not in snake_body:
                self.position = pos
                break

class Game:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.snake = Snake()
        self.food = Food()
        self.food.spawn(self.snake.body)
        self.score = 0
        self.game_over = False

    def process_input(self):
        key = self.stdscr.getch()
        if key == curses.KEY_UP:
            self.snake.change_direction((-1, 0))
        elif key == curses.KEY_DOWN:
            self.snake.change_direction((1, 0))
        elif key == curses.KEY_LEFT:
            self.snake.change_direction((0, -1))
        elif key == curses.KEY_RIGHT:
            self.snake.change_direction((0, 1))
        elif key in (ord('q'), ord('Q')):
            self.game_over = True

    def update(self):
        self.snake.move()
        if self.snake.collides_with_wall() or self.snake.collides_with_self():
            self.game_over = True
            return
        if self.snake.body[0] == self.food.position:
            self.score += 1
            self.snake.move(grow=True)  # grow on same move
            self.food.spawn(self.snake.body)

    def render(self):
        self.stdscr.clear()
        # Draw borders
        for y in range(GRID_WIDTH + 2):
            self.stdscr.addch(0, y, '#')
            self.stdscr.addch(GRID_HEIGHT + 1, y, '#')
        for x in range(GRID_HEIGHT + 2):
            self.stdscr.addch(x, 0, '#')
            self.stdscr.addch(x, GRID_WIDTH + 1, '#')
        # Draw food
        fx, fy = self.food.position
        self.stdscr.addch(fx + 1, fy + 1, FOOD_CHAR)
        # Draw snake
        for i, (x, y) in enumerate(self.snake.body):
            ch = SNAKE_CHAR if i == 0 else SNAKE_CHAR.lower()
            self.stdscr.addch(x + 1, y + 1, ch)
        # Draw score
        self.stdscr.addstr(GRID_HEIGHT + 3, 0, f"Score: {self.score}  Press 'q' to quit.")
        self.stdscr.refresh()

    def run(self):
        while not self.game_over:
            self.process_input()
            self.update()
            self.render()
            time.sleep(DELAY)
        # Game over message
        self.stdscr.clear()
        self.stdscr.addstr(GRID_HEIGHT // 2, GRID_WIDTH // 2 - 5, "GAME OVER")
        self.stdscr.addstr(GRID_HEIGHT // 2 + 1, GRID_WIDTH // 2 - 7, f"Final Score: {self.score}")
        self.stdscr.addstr(GRID_HEIGHT // 2 + 3, GRID_WIDTH // 2 - 12, "Press any key to exit.")
        self.stdscr.refresh()
        self.stdscr.getch()

def main(stdscr):
    # Curses setup
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.keypad(True)
    game = Game(stdscr)
    game.run()

if __name__ == "__main__":
    curses.wrapper(main)