import curses
import random
import time
from dataclasses import dataclass, field
from typing import List, Tuple, Set

# ---------- Constants ----------
WINDOW_HEIGHT = 20
WINDOW_WIDTH = 40
INITIAL_SNAKE_LENGTH = 3
SNAKE_CHAR = "O"
FOOD_CHAR = "*"
EMPTY_CHAR = " "
SLEEP_TIME = 0.1  # Seconds between moves

# ---------- Data Structures ----------
@dataclass
class Snake:
    body: List[Tuple[int, int]] = field(default_factory=list)
    direction: Tuple[int, int] = (0, 1)  # Initially moving right

    def __post_init__(self):
        if not self.body:
            # Start in the middle of the window
            mid_y = WINDOW_HEIGHT // 2
            mid_x = WINDOW_WIDTH // 2
            self.body = [(mid_y, mid_x - i) for i in range(INITIAL_SNAKE_LENGTH)]

    def move(self, grow: bool = False):
        head_y, head_x = self.body[0]
        dir_y, dir_x = self.direction
        new_head = (head_y + dir_y, head_x + dir_x)

        # Insert new head
        self.body.insert(0, new_head)

        if not grow:
            # Remove tail
            self.body.pop()

    def set_direction(self, new_dir: Tuple[int, int]):
        # Prevent reverse
        if (new_dir[0] == -self.direction[0] and new_dir[1] == -self.direction[1]):
            return
        self.direction = new_dir

    def collides_with_self(self) -> bool:
        return self.body[0] in self.body[1:]

    def collides_with_wall(self) -> bool:
        head_y, head_x = self.body[0]
        return not (0 <= head_y < WINDOW_HEIGHT and 0 <= head_x < WINDOW_WIDTH)

@dataclass
class Food:
    position: Tuple[int, int] = (0, 0)

    def spawn(self, occupied: Set[Tuple[int, int]]):
        while True:
            pos = (random.randint(0, WINDOW_HEIGHT - 1), random.randint(0, WINDOW_WIDTH - 1))
            if pos not in occupied:
                self.position = pos
                break

@dataclass
class Game:
    snake: Snake = field(default_factory=Snake)
    food: Food = field(default_factory=Food)
    score: int = 0
    running: bool = True

    def __post_init__(self):
        self.food.spawn(set(self.snake.body))

    def update(self):
        # Check collisions before moving
        if self.snake.collides_with_wall() or self.snake.collides_with_self():
            self.running = False
            return

        # Check if food eaten
        grow = False
        if self.snake.body[0] == self.food.position:
            self.score += 1
            grow = True
            self.food.spawn(set(self.snake.body))

        self.snake.move(grow=grow)

    def handle_input(self, key):
        if key == curses.KEY_UP:
            self.snake.set_direction((-1, 0))
        elif key == curses.KEY_DOWN:
            self.snake.set_direction((1, 0))
        elif key == curses.KEY_LEFT:
            self.snake.set_direction((0, -1))
        elif key == curses.KEY_RIGHT:
            self.snake.set_direction((0, 1))
        elif key == ord('q') or key == ord('Q'):
            self.running = False

    def render(self, stdscr):
        stdscr.clear()
        # Draw borders
        for y in range(WINDOW_HEIGHT):
            for x in range(WINDOW_WIDTH):
                char = EMPTY_CHAR
                if (y, x) == self.food.position:
                    char = FOOD_CHAR
                elif (y, x) in self.snake.body:
                    char = SNAKE_CHAR
                stdscr.addch(y, x, char)
        # Draw score
        stdscr.addstr(WINDOW_HEIGHT, 0, f"Score: {self.score}  Press 'q' to quit.")
        stdscr.refresh()

def main(stdscr):
    # Setup curses
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.keypad(True)

    game = Game()

    while game.running:
        start_time = time.time()

        # Input
        try:
            key = stdscr.getch()
            if key != -1:
                game.handle_input(key)
        except Exception:
            pass

        # Update
        game.update()

        # Render
        game.render(stdscr)

        # Timing
        elapsed = time.time() - start_time
        if elapsed < SLEEP_TIME:
            time.sleep(SLEEP_TIME - elapsed)

    # Game over
    stdscr.nodelay(False)
    stdscr.clear()
    stdscr.addstr(WINDOW_HEIGHT // 2, WINDOW_WIDTH // 2 - 5, "Game Over!")
    stdscr.addstr(WINDOW_HEIGHT // 2 + 1, WINDOW_WIDTH // 2 - 7, f"Final Score: {game.score}")
    stdscr.addstr(WINDOW_HEIGHT // 2 + 3, WINDOW_WIDTH // 2 - 12, "Press any key to exit.")
    stdscr.refresh()
    stdscr.getch()

if __name__ == "__main__":
    curses.wrapper(main)