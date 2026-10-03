import curses
import random
import time

# Game configuration
WINDOW_WIDTH = 40
WINDOW_HEIGHT = 20
SNAKE_CHAR = "█"
FOOD_CHAR = "🍎"
SPEED = 0.1  # seconds per move
INITIAL_SNAKE_LENGTH = 3

# Directions mapped to key codes
DIRECTIONS = {
    curses.KEY_UP: (0, -1),
    curses.KEY_DOWN: (0, 1),
    curses.KEY_LEFT: (-1, 0),
    curses.KEY_RIGHT: (1, 0),
}

class Snake:
    """Represents the snake as a list of (x, y) tuples."""
    def __init__(self, init_pos):
        self.body = [init_pos]
        self.direction = DIRECTIONS[curses.KEY_RIGHT]

    def set_direction(self, key):
        if key in DIRECTIONS:
            new_dir = DIRECTIONS[key]
            # Prevent the snake from reversing onto itself
            if (new_dir[0] != -self.direction[0] or new_dir[1] != -self.direction[1]):
                self.direction = new_dir

    def move(self, grow=False):
        head_x, head_y = self.body[0]
        delta_x, delta_y = self.direction
        new_head = (head_x + delta_x, head_y + delta_y)
        self.body.insert(0, new_head)
        if not grow:
            self.body.pop()

    def head(self):
        return self.body[0]

    def collides_with_self(self):
        return self.head() in self.body[1:]

class Food:
    """Handles food placement."""
    def __init__(self, snake_body, max_x, max_y):
        self.position = None
        self.max_x = max_x
        self.max_y = max_y
        self.snake_body = snake_body
        self.spawn()

    def spawn(self):
        while True:
            x = random.randint(1, self.max_x - 2)
            y = random.randint(1, self.max_y - 2)
            if (x, y) not in self.snake_body:
                self.position = (x, y)
                break

class Game:
    """Main game logic."""
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.max_y, self.max_x = stdscr.getmaxyx()
        self.max_x = min(self.max_x, WINDOW_WIDTH + 2)
        self.max_y = min(self.max_y, WINDOW_HEIGHT + 2)
        init_x = self.max_x // 2
        init_y = self.max_y // 2
        self.snake = Snake((init_x, init_y))
        self.food = Food(self.snake.body, self.max_x, self.max_y)
        self.score = 0
        self.game_over = False
        self.speed_multiplier = 1.0  # Added for store feature

    def draw_borders(self):
        for x in range(self.max_x):
            self.stdscr.addch(0, x, curses.ACS_HLINE)
            self.stdscr.addch(self.max_y - 1, x, curses.ACS_HLINE)
        for y in range(self.max_y):
            self.stdscr.addch(y, 0, curses.ACS_VLINE)
            self.stdscr.addch(y, self.max_x - 1, curses.ACS_VLINE)
        self.stdscr.addch(0, 0, curses.ACS_ULCORNER)
        self.stdscr.addch(0, self.max_x - 1, curses.ACS_URCORNER)
        self.stdscr.addch(self.max_y - 1, 0, curses.ACS_LLCORNER)
        self.stdscr.addch(self.max_y - 1, self.max_x - 1, curses.ACS_LRCORNER)

    def draw(self):
        self.stdscr.clear()
        self.draw_borders()
        # Draw food
        fx, fy = self.food.position
        self.stdscr.addch(fy, fx, FOOD_CHAR)
        # Draw snake
        for idx, (x, y) in enumerate(self.snake.body):
            char = SNAKE_CHAR
            self.stdscr.addch(y, x, char)
        # Draw score
        score_text = f"Score: {self.score}"
        self.stdscr.addstr(0, 2, score_text)
        self.stdscr.refresh()

    def increase_snake_length(self, n):
        """Increase snake length by n segments."""
        if self.snake.body:
            last = self.snake.body[-1]
            for _ in range(n):
                self.snake.body.append(last)

    def open_store(self):
        """Display a simple store interface."""
        self.stdscr.nodelay(False)
        self.stdscr.clear()
        self.stdscr.addstr(5, 5, "Store")
        current_speed = SPEED / self.speed_multiplier
        self.stdscr.addstr(7, 5, f"1. Speed up (cost 5)   Current speed: {current_speed:.2f}")
        self.stdscr.addstr(8, 5, "2. Grow snake (cost 3)")
        self.stdscr.addstr(10, 5, "Press 1, 2 or q to exit.")
        self.stdscr.refresh()
        while True:
            c = self.stdscr.getch()
            if c == ord('1'):
                if self.score >= 5:
                    self.score -= 5
                    self.speed_multiplier *= 1.5
                    self.stdscr.addstr(12, 5, f"Speed increased! New speed: {SPEED / self.speed_multiplier:.2f} ")
                else:
                    self.stdscr.addstr(12, 5, "Not enough points.                    ")
                self.stdscr.refresh()
                time.sleep(1)
                break
            elif c == ord('2'):
                if self.score >= 3:
                    self.score -= 3
                    self.increase_snake_length(1)
                    self.stdscr.addstr(12, 5, "Snake grew!                            ")