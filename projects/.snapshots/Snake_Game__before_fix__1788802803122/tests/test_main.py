import os
import random
import sys
import time
import threading
from collections import deque

# ------------------------------------------------------------------
# Constants
# ------------------------------------------------------------------
BOARD_WIDTH = 20
BOARD_HEIGHT = 10
SNAKE_CHAR = "O"
FOOD_CHAR = "*"
EMPTY_CHAR = " "
INITIAL_SNAKE_LENGTH = 3
MOVE_DELAY = 0.2  # seconds between moves

# Directions: (dy, dx)
DIR_UP = (-1, 0)
DIR_DOWN = (1, 0)
DIR_LEFT = (0, -1)
DIR_RIGHT = (0, 1)
DIRECTION_MAP = {
    "w": DIR_UP,
    "s": DIR_DOWN,
    "a": DIR_LEFT,
    "d": DIR_RIGHT,
}

# ------------------------------------------------------------------
# Snake class
# ------------------------------------------------------------------
class Snake:
    def __init__(self, init_pos, init_dir=DIR_RIGHT):
        self.body = deque([init_pos])
        self.direction = init_dir
        self.grow_pending = 0

    def set_direction(self, new_dir):
        # Prevent reversing
        opp = (-self.direction[0], -self.direction[1])
        if new_dir != opp:
            self.direction = new_dir

    def move(self):
        head_y, head_x = self.body[0]
        dy, dx = self.direction
        new_head = (head_y + dy, head_x + dx)
        self.body.appendleft(new_head)
        if self.grow_pending:
            self.grow_pending -= 1
        else:
            self.body.pop()

    def grow(self):
        self.grow_pending += 1

    def collides_with_self(self):
        head = self.body[0]
        return head in list(self.body)[1:]

    def collides_with_wall(self):
        head_y, head_x = self.body[0]
        return not (0 <= head_y < BOARD_HEIGHT and 0 <= head_x < BOARD_WIDTH)

    def get_positions(self):
        return list(self.body)

# ------------------------------------------------------------------
# Food class
# ------------------------------------------------------------------
class Food:
    def __init__(self, snake_positions):
        self.position = self._spawn(snake_positions)

    def _spawn(self, snake_positions):
        available = [
            (y, x)
            for y in range(BOARD_HEIGHT)
            for x in range(BOARD_WIDTH)
            if (y, x) not in snake_positions
        ]
        if not available:
            return None
        return random.choice(available)

    def respawn(self, snake_positions):
        self.position = self._spawn(snake_positions)

# ------------------------------------------------------------------
# Game class
# ------------------------------------------------------------------
class Game:
    def __init__(self, width=BOARD_WIDTH, height=BOARD_HEIGHT):
        self.width = width
        self.height = height
        init_pos = (height // 2, width // 2)
        self.snake = Snake(init_pos)
        for _ in range(INITIAL_SNAKE_LENGTH - 1):
            self.snake.move()
        self.food = Food(self.snake.get_positions())
        self.score = 0
        self.running = True
        self.lock = threading.Lock()

    def update(self):
        with self.lock:
            self.snake.move()
            if self.snake.collides_with_wall() or self.snake.collides_with_self():
                self.running = False
                return
            if self.snake.body[0] == self.food.position:
                self.snake.grow()
                self.score += 1
                self.food.respawn(self.snake.get_positions())

    def render(self):
        board = [[EMPTY_CHAR for _ in range(self.width)] for _ in range(self.height)]
        for y, x in self.snake.get_positions():
            board[y][x] = SNAKE_CHAR
        if self.food.position:
            fy, fx = self.food.position
            board[fy][fx] = FOOD_CHAR
        lines = ["".join(row) for row in board]
        return "\n".join(lines)

    def change_direction(self, key):
        if key in DIRECTION_MAP:
            self.snake.set_direction(DIRECTION_MAP[key])

    def get_score(self):
        return self.score

# ------------------------------------------------------------------
# Input handling (non-blocking)
# ------------------------------------------------------------------
class KeyListener(threading.Thread):
    def __init__(self, game):
        super().__init__(daemon=True)
        self.game = game
        self._running = True
        if os.name == "nt":
            import msvcrt
            self.get_key = msvcrt.getch
            self.kbhit = msvcrt.kbhit
        else:
            import sys
            import tty
            import termios
            import select

            def _getch():
                fd = sys.stdin.fileno()
                old_settings = termios.tcgetattr(fd)
                try:
                    tty.setraw(fd)
                    [i, o, e] = select.select([sys.stdin], [], [], 0)
                    if i:
                        ch = sys.stdin.read(1)
                    else:
                        ch = None
                finally:
                    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                return ch

            self.get_key = _getch
            self.kbhit = lambda: True  # always true, we block inside get_key

    def run(self):
        while self._running:
            if os.name == "nt":
                if self.kbhit():
                    ch = self.get_key().decode("utf-8").lower()
                    if ch in DIRECTION_MAP:
                        self.game.change_direction(ch)
            else:
                ch = self.get_key()
                if ch and ch.lower() in DIRECTION_MAP:
                    self.game.change_direction(ch.lower())
            time.sleep(0.01)

    def stop(self):
        self._running = False

# ------------------------------------------------------------------
# Main loop
# ------------------------------------------------------------------
def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def main():
    game = Game()
    listener = KeyListener(game)
    listener.start()
    try:
        while game.running:
            clear_screen()
            print(f"Score: {game.get_score()}")
            print(game.render())
            game.update()
            time.sleep(MOVE_DELAY)
        clear_screen()
        print(f"Game Over! Final Score: {game.get_score()}")
    finally:
        listener.stop()

if __name__ == "__main__":
    main()