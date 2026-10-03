#!/usr/bin/env python3
import curses
import random
import time
from collections import deque

# Game configuration constants
BOARD_HEIGHT = 20
BOARD_WIDTH = 40
INITIAL_SNAKE_LENGTH = 5
MOVE_DELAY = 0.1  # seconds between moves
FOOD_CHAR = '*'
SNAKE_CHAR = 'O'
EMPTY_CHAR = ' '

# Directions mapped to key inputs
DIRECTION_KEYS = {
    curses.KEY_UP: (-1, 0),
    curses.KEY_DOWN: (1, 0),
    curses.KEY_LEFT: (0, -1),
    curses.KEY_RIGHT: (0, 1),
}

class SnakeGame:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.height = BOARD_HEIGHT
        self.width = BOARD_WIDTH
        self.score = 0
        self.snake = deque()
        self.direction = (0, 1)  # start moving right
        self.food = None
        self._init_snake()
        self._place_food()
        self._setup_screen()

    def _setup_screen(self):
        curses.curs_set(0)  # Hide cursor
        self.stdscr.nodelay(True)  # Non-blocking input
        self.stdscr.keypad(True)
        self.stdscr.clear()
        self.stdscr.border()
        self._draw_info()

    def _init_snake(self):
        start_y = self.height // 2
        start_x = self.width // 2 - INITIAL_SNAKE_LENGTH // 2
        for i in range(INITIAL_SNAKE_LENGTH):
            self.snake.append((start_y, start_x + i))

    def _place_food(self):
        while True:
            y = random.randint(1, self.height - 2)
            x = random.randint(1, self.width - 2)
            if (y, x) not in self.snake:
                self.food = (y, x)
                break

    def _draw_info(self):
        self.stdscr.addstr(0, 2, f'Score: {self.score}')

    def _draw_board(self):
        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                self.stdscr.addch(y, x, EMPTY_CHAR)
        # Draw food
        fy, fx = self.food
        self.stdscr.addch(fy, fx, FOOD_CHAR)
        # Draw snake
        for y, x in self.snake:
            self.stdscr.addch(y, x, SNAKE_CHAR)
        self.stdscr.refresh()

    def _update_direction(self, key):
        if key in DIRECTION_KEYS:
            new_dir = DIRECTION_KEYS[key]
            # Prevent reverse direction
            if (new_dir[0] != -self.direction[0] or new_dir[1] != -self.direction[1]):
                self.direction = new_dir

    def _move_snake(self):
        head_y, head_x = self.snake[-1]
        dy, dx = self.direction
        new_head = (head_y + dy, head_x + dx)

        # Check collision with walls
        if (new_head[0] <= 0 or new_head[0] >= self.height - 1 or
                new_head[1] <= 0 or new_head[1] >= self.width - 1):
            return False

        # Check collision with self
        if new_head in self.snake:
            return False

        self.snake.append(new_head)

        # Check if food eaten
        if new_head == self.food:
            self.score += 1
            self._place_food()
        else:
            self.snake.popleft()  # remove tail

        return True

    def run(self):
        while True:
            key = self.stdscr.getch()
            if key == ord('q'):
                break
            self._update_direction(key)
            if not self._move_snake():
                break
            self._draw_info()
            self._draw_board()
            time.sleep(MOVE_DELAY)
        self._game_over()

    def _game_over(self):
        self.stdscr.nodelay(False)
        msg = f'Game Over! Final Score: {self.score}. Press any key to exit.'
        self.stdscr.addstr(self.height // 2, (self.width - len(msg)) // 2, msg)
        self.stdscr.refresh()
        self.stdscr.getch()

def main(stdscr):
    game = SnakeGame(stdscr)
    game.run()

if __name__ == '__main__':
    curses.wrapper(main)