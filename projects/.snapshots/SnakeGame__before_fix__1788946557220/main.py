import random
import time
from collections import deque
from typing import Deque, Tuple

# ---------- Constants ----------
BOARD_WIDTH = 40
BOARD_HEIGHT = 20
SNAKE_CHAR = "O"
FOOD_CHAR = "*"
EMPTY_CHAR = " "
SPEED = 0.1  # seconds per frame

# Direction vectors
UP = (-1, 0)
DOWN = (1, 0)
LEFT = (0, -1)
RIGHT = (0, 1)

# ---------- Core Classes ----------

class Snake:
    def __init__(self, init_pos: Tuple[int, int]):
        self.body: Deque[Tuple[int, int]] = deque([init_pos])
        self.direction: Tuple[int, int] = RIGHT
        self.grow_next: bool = False

    def set_direction(self, new_dir: Tuple[int, int]):
        # Prevent reversing onto itself
        if (self.direction[0] + new_dir[0], self.direction[1] + new_dir[1]) != (0, 0):
            self.direction = new_dir

    def move(self):
        head_y, head_x = self.body[0]
        delta_y, delta_x = self.direction
        new_head = (head_y + delta_y, head_x + delta_x)
        self.body.appendleft(new_head)
        if not self.grow_next:
            self.body.pop()
        else:
            self.grow_next = False

    def grow(self):
        self.grow_next = True

    def collides_with_self(self) -> bool:
        head = self.body[0]
        return head in list(self.body)[1:]

    def collides_with_wall(self, width: int, height: int) -> bool:
        y, x = self.body[0]
        return not (0 <= y < height and 0 <= x < width)

class Food:
    def __init__(self, width: int, height: int, snake: Snake):
        self.width = width
        self.height = height
        self.snake = snake
        self.position = self._spawn()

    def _spawn(self) -> Tuple[int, int]:
        while True:
            pos = (random.randint(0, self.height - 1), random.randint(0, self.width - 1))
            if pos not in self.snake.body:
                return pos

    def respawn(self):
        self.position = self._spawn()

class Game:
    def __init__(self, width: int = BOARD_WIDTH, height: int = BOARD_HEIGHT):
        self.width = width
        self.height = height
        init_pos = (height // 2, width // 4)
        self.snake = Snake(init_pos)
        self.food = Food(width, height, self.snake)
        self.score = 0
        self.game_over = False

    def update(self):
        if self.game_over:
            return
        self.snake.move()
        # Check collisions
        if self.snake.collides_with_wall(self.width, self.height) or self.snake.collides_with_self():
            self.game_over = True
            return
        # Check food
        if self.snake.body[0] == self.food.position:
            self.snake.grow()
            self.score += 1
            self.food.respawn()

    def get_state(self):
        return {
            "snake": list(self.snake.body),
            "food": self.food.position,
            "score": self.score,
            "game_over": self.game_over,
        }

# ---------- Rendering and Input ----------

def render(stdscr, game: Game):
    stdscr.clear()
    # Draw borders
    for y in range(game.height + 2):
        for x in range(game.width + 2):
            if y == 0 or y == game.height + 1 or x == 0 or x == game.width + 1:
                stdscr.addch(y, x, "#")
    # Draw food
    food_y, food_x = game.food.position
    stdscr.addch(food_y + 1, food_x + 1, FOOD_CHAR)
    # Draw snake
    for y, x in game.snake.body:
        stdscr.addch(y + 1, x + 1, SNAKE_CHAR)
    # Draw score
    stdscr.addstr(game.height + 3, 0, f"Score: {game.score}")
    stdscr.refresh()

def main(stdscr):
    import curses  # Import here to avoid issues on platforms without curses
    # Curses setup
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.keypad(True)

    # Direction mapping using curses keys
    DIRECTION_MAP = {
        curses.KEY_UP: UP,
        curses.KEY_DOWN: DOWN,
        curses.KEY_LEFT: LEFT,
        curses.KEY_RIGHT: RIGHT,
    }

    game = Game()

    while True:
        try:
            key = stdscr.getch()
        except curses.error:
            key = -1

        if key == ord("q"):
            break
        if key in DIRECTION_MAP:
            game.snake.set_direction(DIRECTION_MAP[key])

        game.update()
        render(stdscr, game)

        if game.game_over:
            stdscr.addstr(game.height // 2, game.width // 2 - 5, "GAME OVER")
            stdscr.addstr(game.height // 2 + 1, game.width // 2 - 10, f"Final Score: {game.score}")
            stdscr.nodelay(False)
            stdscr.getch()
            break

        time.sleep(SPEED)

if __name__ == "__main__":
    import curses
    curses.wrapper(main)