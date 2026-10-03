#!/usr/bin/env python3
"""
A minimal console Snake game built with Python's standard library (curses).
This file contains all necessary classes and logic for the game, as well as
an entry point guarded by `if __name__ == "__main__"`.  It is designed to be
imported by unit tests without starting the curses UI.
"""

import curses
import random
import time
from collections import deque
from dataclasses import dataclass
from enum import Enum, auto
from typing import Deque, Iterable, List, Tuple

# --------------------------------------------------------------------------- #
# Constants
# --------------------------------------------------------------------------- #

BOARD_HEIGHT = 20
BOARD_WIDTH = 40
INITIAL_SNAKE_LENGTH = 3
SNAKE_CHAR = "#"
FOOD_CHAR = "*"
EMPTY_CHAR = " "
SCORE_PER_FOOD = 10
GAME_SPEED = 0.1  # seconds per tick


# --------------------------------------------------------------------------- #
# Directions
# --------------------------------------------------------------------------- #

class Direction(Enum):
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()

    @staticmethod
    def opposite(dir1: "Direction", dir2: "Direction") -> bool:
        """Return True if dir1 is the opposite of dir2."""
        opposites = {
            Direction.UP: Direction.DOWN,
            Direction.DOWN: Direction.UP,
            Direction.LEFT: Direction.RIGHT,
            Direction.RIGHT: Direction.LEFT,
        }
        return opposites[dir1] == dir2


# --------------------------------------------------------------------------- #
# Data classes
# --------------------------------------------------------------------------- #

@dataclass(frozen=True)
class Point:
    y: int
    x: int

    def __add__(self, other: Tuple[int, int]) -> "Point":
        return Point(self.y + other[0], self.x + other[1])


# --------------------------------------------------------------------------- #
# Snake implementation
# --------------------------------------------------------------------------- #

class Snake:
    """Represents the snake body and movement logic."""

    _DIR_VECTORS = {
        Direction.UP: (-1, 0),
        Direction.DOWN: (1, 0),
        Direction.LEFT: (0, -1),
        Direction.RIGHT: (0, 1),
    }

    def __init__(self, start_pos: Point, length: int = INITIAL_SNAKE_LENGTH):
        self.body: Deque[Point] = deque()
        self.direction: Direction = Direction.RIGHT
        # Initialize snake body horizontally to the left
        for i in range(length):
            self.body.append(Point(start_pos.y, start_pos.x - i))

    def set_direction(self, new_dir: Direction):
        """Set new direction if it's not directly opposite."""
        if not Direction.opposite(self.direction, new_dir):
            self.direction = new_dir

    def move(self, grow: bool = False) -> Point:
        """
        Move the snake one step in the current direction.
        Returns the new head position.
        If grow is False, the tail is removed; otherwise, the snake grows.
        """
        head = self.body[0]
        vector = self._DIR_VECTORS[self.direction]
        new_head = head + vector
        self.body.appendleft(new_head)
        if not grow:
            self.body.pop()
        return new_head

    def occupies(self, point: Point) -> bool:
        return point in self.body

    def collision_with_self(self) -> bool:
        head = self.body[0]
        return head in list(self.body)[1:]

    def collision_with_wall(self) -> bool:
        head = self.body[0]
        return (
            head.y < 0
            or head.y >= BOARD_HEIGHT
            or head.x < 0
            or head.x >= BOARD_WIDTH
        )


# --------------------------------------------------------------------------- #
# Food implementation
# --------------------------------------------------------------------------- #

class Food:
    """Represents a food item on the board."""

    def __init__(self, snake: Snake):
        self.position: Point = self._generate_position(snake)

    def _generate_position(self, snake: Snake) -> Point:
        """Generate a random position not occupied by the snake."""
        while True:
            y = random.randint(0, BOARD_HEIGHT - 1)
            x = random.randint(0, BOARD_WIDTH - 1)
            pos = Point(y, x)
            if not snake.occupies(pos):
                return pos

    def relocate(self, snake: Snake):
        self.position = self._generate_position(snake)


# --------------------------------------------------------------------------- #
# Game logic
# --------------------------------------------------------------------------- #

class Game:
    """
    Encapsulates the state and logic of a Snake game.
    """

    def __init__(self):
        self.snake = Snake(start_pos=Point(BOARD_HEIGHT // 2, BOARD_WIDTH // 2))
        self.food = Food(self.snake)
        self.score = 0
        self.game_over = False

    def update(self, input_key: int):
        """
        Update the game state based on user input.
        input_key: curses key code (e.g., curses.KEY_UP).
        """
        if input_key == curses.KEY_UP:
            self.snake.set_direction(Direction.UP)
        elif input_key == curses.KEY_DOWN:
            self.snake.set_direction(Direction.DOWN)
        elif input_key == curses.KEY_LEFT:
            self.snake.set_direction(Direction.LEFT)
        elif input_key == curses.KEY_RIGHT:
            self.snake.set_direction(Direction.RIGHT)

        # Determine if snake will grow
        will_grow = self.snake.body[0] + self._dir_vector() == self.food.position

        new_head = self.snake.move(grow=will_grow)

        if will_grow:
            self.score += SCORE_PER_FOOD
            self.food.relocate(self.snake)

        if new_head is None or self.snake.collision_with_self() or self.snake.collision_with_wall():
            self.game_over = True

    def _dir_vector(self) -> Tuple[int, int]:
        return {
            Direction.UP: (-1, 0),
            Direction.DOWN: (1, 0),
            Direction.LEFT: (0, -1),
            Direction.RIGHT: (0, 1),
        }[self.snake.direction]

    def get_board(self) -> List[List[str]]:
        """
        Return a 2D list of characters representing the current board state.
        """
        board = [[EMPTY_CHAR for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]
        # Draw food
        board[self.food.position.y][self.food.position.x] = FOOD_CHAR
        # Draw snake
        for idx, segment in enumerate(self.snake.body):
            board[segment.y][segment.x] = SNAKE_CHAR
        return board

    def render(self, stdscr):
        """Render the current board to the curses window."""
        stdscr.clear()
        board = self.get_board()
        for y, row in enumerate(board):
            stdscr.addstr(y, 0, "".join(row))
        stdscr.addstr(BOARD_HEIGHT + 1, 0, f"Score: {self.score}")
        stdscr.refresh()


# --------------------------------------------------------------------------- #
# Curses UI
# --------------------------------------------------------------------------- #

def main(stdscr):
    # Curses setup
    curses.curs_set(0)  # Hide cursor
    stdscr.nodelay(True)  # Non-blocking input
    stdscr.keypad(True)

    game = Game()

    while not game.game_over:
        input_key = stdscr.getch()
        game.update(input_key)
        game.render(stdscr)
        time.sleep(GAME_SPEED)

    # Game over screen
    stdscr.nodelay(False)
    stdscr.addstr(BOARD_HEIGHT // 2, BOARD_WIDTH // 2 - 5, "GAME OVER")
    stdscr.addstr(BOARD_HEIGHT // 2 +