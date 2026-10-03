import curses
import random
import time

# Game configuration constants
BOARD_HEIGHT = 20
BOARD_WIDTH = 40
SNAKE_CHAR = "#"
FOOD_CHAR = "*"
EMPTY_CHAR = " "
BORDER_CHAR = "+"

# Direction vectors
UP = (-1, 0)
DOWN = (1, 0)
LEFT = (0, -1)
RIGHT = (0, 1)
DIRECTION_MAP = {
    curses.KEY_UP: UP,
    curses.KEY_DOWN: DOWN,
    curses.KEY_LEFT: LEFT,
    curses.KEY_RIGHT: RIGHT,
}

class Snake:
    """Represents the snake in the game."""
    def __init__(self, init_pos, init_length=3, init_direction=RIGHT):
        self.body = [init_pos]
        self.direction = init_direction
        self.growing = False
        # Initialize body with initial length
        for _ in range(1, init_length):
            y, x = self.body[-1]
            dy, dx = (-self.direction[0], -self.direction[1])
            self.body.append((y + dy, x + dx))

    def set_direction(self, new_direction):
        """Change direction if it's not directly opposite."""
        if (new_direction[0] + self.direction[0] != 0 or
                new_direction[1] + self.direction[1] != 0):
            self.direction = new_direction

    def move(self):
        """Move the snake forward by one step."""
        head_y, head_x = self.body[0]
        dy, dx = self.direction
        new_head = (head_y + dy, head_x + dx)
        self.body.insert(0, new_head)
        if not self.growing:
            self.body.pop()
        else:
            self.growing = False

    def grow(self):
        """Set the snake to grow on the next move."""
        self.growing = True

    def head(self):
        return self.body[0]

    def collides_with_self(self):
        return self.head() in self.body[1:]

    def collides_with_wall(self):
        y, x = self.head()
        return y <= 0 or y >= BOARD_HEIGHT - 1 or x <= 0 or x >= BOARD_WIDTH - 1

class Food:
    """Represents the food item."""
    def __init__(self):
        self.position = None

    def spawn(self, snake):
        """Place food at a random position not occupied by the snake."""
        while True:
            y = random.randint(1, BOARD_HEIGHT - 2)
            x = random.randint(1, BOARD_WIDTH - 2)
            if (y, x) not in snake.body:
                self.position = (y, x)
                break

class Game:
    """Main game logic."""
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.snake = Snake(init_pos=(BOARD_HEIGHT // 2, BOARD_WIDTH // 2))
        self.food = Food()
        self.food.spawn(self.snake)
        self.score = 0
        self.stdscr.nodelay(True)
        self.stdscr.keypad(True)
        curses.curs_set(0)

    def draw_borders(self):
        for y in range(BOARD_HEIGHT):
            for x in range(BOARD_WIDTH):
                if y == 0 or y == BOARD_HEIGHT - 1 or x == 0 or x == BOARD_WIDTH - 1:
                    self.stdscr.addch(y, x, BORDER_CHAR)
                else:
                    self.stdscr.addch(y, x, EMPTY_CHAR)

    def draw(self):
        self.draw_borders()
        # Draw food
        fy, fx = self.food.position
        self.stdscr.addch(fy, fx, FOOD_CHAR)
        # Draw snake
        for y, x in self.snake.body:
            self.stdscr.addch(y, x, SNAKE_CHAR)
        # Draw score
        score_text = f"Score: {self.score}"
        self.stdscr.addstr(0, 2, score_text)
        self.stdscr.refresh()

    def process_input(self):
        try:
            key = self.stdscr.getch()
        except:
            key = -1
        if key in DIRECTION_MAP:
            self.snake.set_direction(DIRECTION_MAP[key])
        elif key in (ord('q'), ord('Q')):
            raise KeyboardInterrupt

    def update(self):
        self.snake.move()
        if self.snake.head() == self.food.position:
            self.snake.grow()
            self.score += 1
            self.food.spawn(self.snake)
        if self.snake.collides_with_self() or self.snake.collides_with_wall():
            raise RuntimeError("Game Over")

    def run(self):
        try:
            while True:
                self.process_input()
                self.update()
                self.draw()
                time.sleep(0.1)
        except (KeyboardInterrupt, RuntimeError):
            self.stdscr.nodelay(False)
            self.stdscr.clear()
            msg = f"Game Over! Final Score: {self.score}. Press any key to exit."
            self.stdscr.addstr(BOARD_HEIGHT // 2, (BOARD_WIDTH - len(msg)) // 2, msg)
            self.stdscr.refresh()
            self.stdscr.getch()

def main(stdscr):
    game = Game(stdscr)
    game.run()

if __name__ == "__main__":
    curses.wrapper(main)