import random
from dataclasses import dataclass
from typing import List, Tuple

# Safely import curses; it may not be available in all environments (e.g., Windows)
try:
    import curses
except Exception:
    curses = None

# ---------- Constants ----------
WIDTH = 40
HEIGHT = 20
INITIAL_SNAKE_LENGTH = 3
SNAKE_CHAR = "O"
FOOD_CHAR = "*"
EMPTY_CHAR = " "
SCORE_POS = (0, 2)

# ---------- Data Structures ----------
@dataclass(frozen=True)
class Point:
    y: int
    x: int

class Snake:
    def __init__(self, start: Point, length: int = INITIAL_SNAKE_LENGTH):
        self.segments: List[Point] = [Point(start.y, start.x - i) for i in range(length)]
        self.direction: Point = Point(0, 1)  # moving right initially
        self.grow_pending: int = 0

    def set_direction(self, new_dir: Point):
        # Prevent reversing by comparing the actual y and x components
        if (self.direction.y, self.direction.x) == (-new_dir.y, -new_dir.x):
            return
        self.direction = new_dir

    def move(self):
        head = self.segments[0]
        new_head = Point(head.y + self.direction.y, head.x + self.direction.x)
        self.segments.insert(0, new_head)
        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            self.segments.pop()

    def grow(self, amount: int = 1):
        self.grow_pending += amount

    def head(self) -> Point:
        return self.segments[0]

    def collides_with_self(self) -> bool:
        return self.head() in self.segments[1:]

    def collides_with(self, point: Point) -> bool:
        return point in self.segments

class Food:
    def __init__(self, snake: Snake):
        self.position: Point = self._spawn(snake)

    def _spawn(self, snake: Snake) -> Point:
        """Generate a random position for the food that does not collide with the snake."""
        while True:
            y = random.randint(0, HEIGHT - 1)
            x = random.randint(0, WIDTH - 1)
            pos = Point(y, x)
            if pos not in snake.segments:
                return pos