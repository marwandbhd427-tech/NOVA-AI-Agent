# snake.py
"""
A pure logic implementation of the classic Snake game suitable for unit testing.
This module contains no external dependencies other than the Python standard library.
"""

from __future__ import annotations
import random
from dataclasses import dataclass, field
from typing import List, Tuple, Set

# --------------------------------------------------------------------------- #
# Configuration constants
# --------------------------------------------------------------------------- #
GRID_WIDTH = 20
GRID_HEIGHT = 20
INITIAL_SNAKE_LENGTH = 3
MAX_TURNS_WITHOUT_EATING = 100  # to prevent infinite loops in tests


@dataclass(frozen=True)
class Position:
    x: int
    y: int

    def __post_init__(self):
        if not (0 <= self.x < GRID_WIDTH) or not (0 <= self.y < GRID_HEIGHT):
            raise ValueError(f"Position {self} out of bounds")


class Direction:
    UP = Position(0, -1)
    DOWN = Position(0, 1)
    LEFT = Position(-1, 0)
    RIGHT = Position(1, 0)

    @classmethod
    def opposite(cls, dir1: Position, dir2: Position) -> bool:
        return dir1.x == -dir2.x and dir1.y == -dir2.y


class Snake:
    def __init__(self, start_pos: Position, length: int = INITIAL_SNAKE_LENGTH):
        self.segments: List[Position] = [start_pos]
        self.direction: Position = Direction.RIGHT
        self.grow_pending = 0
        # Initialize the body
        for _ in range(1, length):
            self._move_head(False)

    def set_direction(self, new_dir: Position):
        if not Direction.opposite(new_dir, self.direction):
            self.direction = new_dir

    def _move_head(self, grow: bool):
        head = self.segments[0]
        new_head = Position(head.x + self.direction.x, head.y + self.direction.y)
        self.segments.insert(0, new_head)
        if not grow:
            self.segments.pop()

    def move(self):
        if self.grow_pending > 0:
            self._move_head(True)
            self.grow_pending -= 1
        else:
            self._move_head(False)

    def grow(self):
        self.grow_pending += 1

    def head(self) -> Position:
        return self.segments[0]

    def body_set(self) -> Set[Position]:
        return set(self.segments[1:])

    def collides_with_self(self) -> bool:
        return self.head() in self.body_set()

    def collides_with_wall(self) -> bool:
        head = self.head()
        return not (0 <= head.x < GRID_WIDTH and 0 <= head.y < GRID_HEIGHT)


class Food:
    def __init__(self, snake: Snake):
        self.position: Position = self._spawn(snake)

    def _spawn(self, snake: Snake) -> Position:
        occupied = set(snake.segments)
        attempts = 0
        while True:
            attempts += 1
            if attempts > 1000:
                raise RuntimeError("Unable to spawn food; grid might be full.")
            pos = Position(random.randint(0, GRID_WIDTH - 1),
                           random.randint(0, GRID_HEIGHT - 1))
            if pos not in occupied:
                return pos


class Game:
    """
    Pure logic game state. No rendering or event loop.
    """
    def __init__(self):
        start = Position(GRID_WIDTH // 2, GRID_HEIGHT // 2)
        self.snake = Snake(start)
        self.food = Food(self.snake)
        self.score = 0
        self.turns_since_last_eat = 0
        self.game_over = False

    def update(self, input_dir: Position | None = None):
        if self.game_over:
            return

        if input_dir:
            self.snake.set_direction(input_dir)

        self.snake.move()

        # Check collisions
        if self.snake.collides_with_wall() or self.snake.collides_with_self():
            self.game_over = True
            return

        # Check food consumption
        if self.snake.head() == self.food.position:
            self.snake.grow()
            self.score += 1
            self.turns_since_last_eat = 0
            self.food = Food(self.snake)
        else:
            self.turns_since_last_eat += 1
            if self.turns_since_last_eat > MAX_TURNS_WITHOUT_EATING:
                self.game_over = True

    def is_over(self) -> bool:
        return self.game_over

    def get_state(self) -> Tuple[List[Position], Position, int, bool]:
        """
        Return a tuple containing:
        - list of snake segments (head first)
        - food position
        - score
        - game_over flag
        """
        return (self.snake.segments, self.food.position, self.score, self.game_over)


# --------------------------------------------------------------------------- #
# Optional console-based demo (guarded)
# --------------------------------------------------------------------------- #
def _demo():
    """
    Simple console demo that runs the game logic without a GUI.
    Press 'w', 'a', 's', 'd' to change direction, 'q' to quit.
    """
    import sys
    import tty
    import termios

    game = Game()
    directions = {
        'w': Direction.UP,
        's': Direction.DOWN,
        'a': Direction.LEFT,
        'd': Direction.RIGHT
    }

    def get_key():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

    print("Snake demo (console). Use WASD to move, q to quit.")
    while not game.is_over():
        key = get_key()
        if key == 'q':
            break
        if key in directions:
            game.update(directions[key])
        else:
            game.update()
        # Render simple grid
        grid = [[' ' for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        for seg in game.snake.segments:
            grid[seg.y][seg.x] = 'O'
        head = game.snake.head()
        grid[head.y][head.x] = 'X'
        fx, fy = game.food.position.x, game.food.position.y
        grid[fy][fx] = '*'
        print("\033[H\033[J", end='')  # clear screen
        for row in grid:
            print(''.join(row))
        print(f"Score: {game.score}")
    print("Game over! Final score:", game.score)

if __name__ == "__main__":
    # Guarded demo: only run if executed directly
    _demo()