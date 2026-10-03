import curses
import random
import time
from collections import deque
from enum import Enum, auto

# ---------- Constants ----------
WIDTH = 20
HEIGHT = 20
INITIAL_LENGTH = 3
MOVE_DELAY = 0.1  # seconds per move
SNAKE_CHAR = '#'
FOOD_CHAR = '*'
EMPTY_CHAR = ' '

# ---------- Direction Enum ----------
class Direction(Enum):
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()

    def opposite(self):
        return {
            Direction.UP: Direction.DOWN,
            Direction.DOWN: Direction.UP,
            Direction.LEFT: Direction.RIGHT,
            Direction.RIGHT: Direction.LEFT,
        }[self]

# ---------- Snake ----------
class Snake:
    def __init__(self, init_length=INITIAL_LENGTH):
        mid_x = WIDTH // 2
        mid_y = HEIGHT // 2
        self.body = deque(
            [(mid_x - i, mid_y) for i in range(init_length)],
            maxlen=WIDTH * HEIGHT
        )
        self.direction = Direction.RIGHT
        self.grow_pending = 0

    def set_direction(self, new_dir):
        """Change direction unless it's directly opposite."""
        if new_dir != self.direction.opposite():
            self.direction = new_dir

    def move(self):
        head_x, head_y = self.body[0]
        if self.direction == Direction.UP:
            new_head = (head_x, head_y - 1)
        elif self.direction == Direction.DOWN:
            new_head = (head_x, head_y + 1)
        elif self.direction == Direction.LEFT:
            new_head = (head_x - 1, head_y)
        elif self.direction == Direction.RIGHT:
            new_head = (head_x + 1, head_y)
        else:
            new_head = (head_x, head_y)

        # Insert new head
        self.body.appendleft(new_head)

        # Remove tail if not growing
        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            self.body.pop()

    def grow(self, n=1):
        self.grow_pending += n

    def head_position(self):
        return self.body[0]

    def collides_with_self(self):
        head = self.head_position()
        return head in list(self.body)[1:]

# ---------- Food ----------
class Food:
    def __init__(self, snake_body):
        self.position = None
        self.place(snake_body)

    def place(self, snake_body):
        """Place food at a random location not occupied by the snake."""
        empty_cells = [
            (x, y)
            for x in range(WIDTH)
            for y in range(HEIGHT)
            if (x, y) not in snake_body
        ]
        if not empty_cells:
            self.position = None
            return
        self.position = random.choice(empty_cells)

# ---------- Game ----------
class Game:
    def __init__(self, width=WIDTH, height=HEIGHT):
        self.width = width
        self.height = height
        self.snake = Snake()
        self.food = Food(self.snake.body)
        self.score = 0
        self.over = False

    def update(self):
        """Advance the game state by one tick."""
        if self.over:
            return

        self.snake.move()
        head_x, head_y = self.snake.head_position()

        # Check wall collision
        if head_x < 0 or head_x >= self.width or head_y < 0 or head_y >= self.height:
            self.over = True
            return

        # Check self collision
        if self.snake.collides_with_self():
            self.over = True
            return

        # Check food collision
        if self.snake.head_position() == self.food.position:
            self.snake.grow()
            self.score += 1
            self.food.place(self.snake.body)

    def is_over(self):
        return self.over

    def get_state(self):
        """Return a snapshot of the game state for testing or rendering."""
        board = [[EMPTY_CHAR for _ in range(self.width)] for _ in range(self.height)]
        # Place food
        if self.food.position:
            fx, fy = self.food.position
            board[fy][fx] = FOOD_CHAR
        # Place snake
        for idx, (sx, sy) in enumerate(self.snake.body):
            board[sy][sx] = SNAKE_CHAR if idx == 0 else SNAKE_CHAR
        return board

    def set_direction(self, direction):
        self.snake.set_direction(direction)

# ---------- Rendering & Input (curses) ----------
def run_game():
    """Entry point for a console-based snake game using curses."""
    def draw(stdscr):
        curses.curs_set(0)
        stdscr.nodelay(True)
        stdscr.timeout(int(MOVE_DELAY * 1000))
        game = Game()

        key_map = {
            curses.KEY_UP: Direction.UP,
            curses.KEY_DOWN: Direction.DOWN,
            curses.KEY_LEFT: Direction.LEFT,
            curses.KEY_RIGHT: Direction.RIGHT,
        }

        while not game.is_over():
            try:
                key = stdscr.getch()
            except curses.error:
                key = -1

            if key in key_map:
                game.set_direction(key_map[key])

            game.update()
            board = game.get_state()

            stdscr.clear()
            for y in range(game.height):
                line = ''.join(board[y])
                stdscr.addstr(y, 0, line)
            stdscr.addstr(game.height + 1, 0, f"Score: {game.score}")
            stdscr.refresh()

        stdscr.nodelay(False)
        stdscr.addstr(game.height + 3, 0, "Game Over! Press any key to exit.")
        stdscr.getch()

    curses.wrapper(draw)

if __name__ == "__main__":
    run_game()