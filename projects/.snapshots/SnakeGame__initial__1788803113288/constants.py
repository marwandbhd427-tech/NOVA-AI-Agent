import curses
import random
import time

# =========================
# Configuration constants
# =========================
WINDOW_HEIGHT = 20
WINDOW_WIDTH = 60
INITIAL_SNAKE_LENGTH = 3
SNAKE_CHAR = "O"
FOOD_CHAR = "*"
SPEED = 0.1  # seconds per move

# =========================
# Helper classes
# =========================
class Snake:
    def __init__(self, start_y, start_x, length=INITIAL_SNAKE_LENGTH):
        self.body = [(start_y, start_x - i) for i in range(length)]
        self.direction = (0, 1)  # moving right
        self.grow_pending = 0

    def set_direction(self, new_dir):
        # Prevent reversing
        opposite = (-self.direction[0], -self.direction[1])
        if new_dir != opposite:
            self.direction = new_dir

    def move(self):
        head_y, head_x = self.body[0]
        delta_y, delta_x = self.direction
        new_head = (head_y + delta_y, head_x + delta_x)
        self.body.insert(0, new_head)
        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            self.body.pop()

    def grow(self):
        self.grow_pending += 1

    def collides_with_self(self):
        return self.body[0] in self.body[1:]

    def collides_with_wall(self, height, width):
        y, x = self.body[0]
        return y <= 0 or y >= height - 1 or x <= 0 or x >= width - 1


class Food:
    def __init__(self, height, width, snake_body):
        self.position = self.spawn(height, width, snake_body)

    def spawn(self, height, width, snake_body):
        while True:
            y = random.randint(1, height - 2)
            x = random.randint(1, width - 2)
            if (y, x) not in snake_body:
                return (y, x)


class Game:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.height, self.width = stdscr.getmaxyx()
        # Ensure window is large enough
        if self.height < WINDOW_HEIGHT or self.width < WINDOW_WIDTH:
            raise ValueError("Terminal window too small for the game.")
        self.stdscr.nodelay(True)
        self.stdscr.keypad(True)
        curses.curs_set(0)
        self.snake = Snake(self.height // 2, self.width // 2)
        self.food = Food(self.height, self.width, self.snake.body)
        self.score = 0
        self.game_over = False

    def process_input(self):
        try:
            key = self.stdscr.getch()
        except Exception:
            key = -1
        if key == curses.KEY_UP:
            self.snake.set_direction((-1, 0))
        elif key == curses.KEY_DOWN:
            self.snake.set_direction((1, 0))
        elif key == curses.KEY_LEFT:
            self.snake.set_direction((0, -1))
        elif key == curses.KEY_RIGHT:
            self.snake.set_direction((0, 1))
        elif key in (ord('q'), ord('Q')):
            self.game_over = True

    def update(self):
        self.snake.move()
        if self.snake.collides_with_self() or self.snake.collides_with_wall(self.height, self.width):
            self.game_over = True
            return
        if self.snake.body[0] == self.food.position:
            self.snake.grow()
            self.score += 1
            self.food = Food(self.height, self.width, self.snake.body)

    def render(self):
        self.stdscr.clear()
        # Draw borders
        for x in range(self.width):
            self.stdscr.addch(0, x, '#')
            self.stdscr.addch(self.height - 1, x, '#')
        for y in range(self.height):
            self.stdscr.addch(y, 0, '#')
            self.stdscr.addch(y, self.width - 1, '#')
        # Draw food
        fy, fx = self.food.position
        self.stdscr.addch(fy, fx, FOOD_CHAR)
        # Draw snake
        for idx, (y, x) in enumerate(self.snake.body):
            ch = SNAKE_CHAR
            self.stdscr.addch(y, x, ch)
        # Draw score
        score_text = f"Score: {self.score}"
        self.stdscr.addstr(0, 2, score_text)
        self.stdscr.refresh()

    def run(self):
        while not self.game_over:
            self.process_input()
            self.update()
            self.render()
            time.sleep(SPEED)
        # Game over message
        self.stdscr.nodelay(False)
        msg = f"Game Over! Final Score: {self.score}. Press any key to exit."
        self.stdscr.addstr(self.height // 2, (self.width - len(msg)) // 2, msg)
        self.stdscr.getch()


def main(stdscr):
    try:
        game = Game(stdscr)
        game.run()
    except Exception as e:
        stdscr.clear()
        stdscr.addstr(0, 0, f"Error: {e}")
        stdscr.refresh()
        stdscr.getch()


if __name__ == "__main__":
    curses.wrapper(main)