import os
import random
import sys
import time
import threading

# Cross‑platform key handling
try:
    import msvcrt  # Windows
except ImportError:
    import tty
    import termios
    import select

# Game constants
WIDTH = 40
HEIGHT = 20
SNAKE_CHAR = "O"
FOOD_CHAR = "*"
EMPTY_CHAR = " "
INITIAL_SNAKE_LENGTH = 3
TICK_RATE = 0.1  # seconds per move

# Directions
UP = (-1, 0)
DOWN = (1, 0)
LEFT = (0, -1)
RIGHT = (0, 1)
DIRECTION_MAP = {
    "w": UP,
    "s": DOWN,
    "a": LEFT,
    "d": RIGHT,
    "k": UP,
    "j": DOWN,
    "h": LEFT,
    "l": RIGHT,
    "\x1b[A": UP,   # ANSI escape codes for arrow keys
    "\x1b[B": DOWN,
    "\x1b[D": LEFT,
    "\x1b[C": RIGHT,
}

class Snake:
    def __init__(self, start_pos, length=INITIAL_SNAKE_LENGTH):
        self.body = [start_pos]
        self.direction = RIGHT
        self.grow = False
        # Initialize body
        for _ in range(1, length):
            self.body.append((self.body[-1][0] - self.direction[0],
                              self.body[-1][1] - self.direction[1]))

    def set_direction(self, new_direction):
        # Prevent reversing
        opposite = (-self.direction[0], -self.direction[1])
        if new_direction != opposite:
            self.direction = new_direction

    def move(self):
        head = self.body[0]
        new_head = ((head[0] + self.direction[0]) % HEIGHT,
                    (head[1] + self.direction[1]) % WIDTH)
        self.body.insert(0, new_head)
        if self.grow:
            self.grow = False
        else:
            self.body.pop()

    def grow_snake(self):
        self.grow = True

    def collision(self):
        head = self.body[0]
        return head in self.body[1:]

class Food:
    def __init__(self, snake_body):
        self.position = self.random_position(snake_body)

    def random_position(self, snake_body):
        while True:
            pos = (random.randint(0, HEIGHT - 1), random.randint(0, WIDTH - 1))
            if pos not in snake_body:
                return pos

class Game:
    def __init__(self):
        self.snake = Snake(start_pos=(HEIGHT // 2, WIDTH // 2))
        self.food = Food(self.snake.body)
        self.score = 0
        self.game_over = False
        self.input_thread = threading.Thread(target=self.input_listener, daemon=True)
        self.input_queue = []
        self.input_thread.start()

    def input_listener(self):
        while not self.game_over:
            key = self.get_key()
            if key:
                self.input_queue.append(key)

    def get_key(self):
        if os.name == "nt":
            if msvcrt.kbhit():
                ch = msvcrt.getch()
                if ch in {b'\x00', b'\xe0'}:  # special keys
                    ch = msvcrt.getch()
                    return None
                try:
                    return ch.decode()
                except UnicodeDecodeError:
                    return None
        else:
            dr, _, _ = select.select([sys.stdin], [], [], 0)
            if dr:
                old_settings = termios.tcgetattr(sys.stdin)
                try:
                    tty.setcbreak(sys.stdin.fileno())
                    ch = sys.stdin.read(1)
                    if ch == '\x1b':  # escape sequence
                        ch += sys.stdin.read(2)
                    return ch
                finally:
                    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
        return None

    def process_input(self):
        if not self.input_queue:
            return
        key = self.input_queue.pop(0)
        direction = DIRECTION_MAP.get(key)
        if direction:
            self.snake.set_direction(direction)

    def update(self):
        self.snake.move()
        if self.snake.collision():
            self.game_over = True
            return
        if self.snake.body[0] == self.food.position:
            self.snake.grow_snake()
            self.score += 1
            self.food = Food(self.snake.body)

    def render(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        board = [[EMPTY_CHAR for _ in range(WIDTH)] for _ in range(HEIGHT)]
        for y, x in self.snake.body:
            board[y][x] = SNAKE_CHAR
        fy, fx = self.food.position
        board[fy][fx] = FOOD_CHAR