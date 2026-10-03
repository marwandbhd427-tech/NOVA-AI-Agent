from dataclasses import dataclass
from typing import Tuple, List, Set
import random

# Simple 2‑D point representation
@dataclass(frozen=True)
class Point:
    x: int
    y: int

# Direction vectors
UP: Tuple[int, int] = (0, -1)
DOWN: Tuple[int, int] = (0, 1)
LEFT: Tuple[int, int] = (-1, 0)
RIGHT: Tuple[int, int] = (1, 0)

# Mapping from key strings (used by the game module) to direction vectors
DIRECTION_MAP = {
    "up": UP,
    "down": DOWN,
    "left": LEFT,
    "right": RIGHT,
}

# Reverse mapping for quick lookup of opposite direction
OPPOSITE_DIRECTION = {
    UP: DOWN,
    DOWN: UP,
    LEFT: RIGHT,
    RIGHT: LEFT,
}


def get_opposite_direction(direction: Tuple[int, int]) -> Tuple[int, int]:
    """
    Return the opposite of a given direction vector.
    """
    return OPPOSITE_DIRECTION[direction]


def move_point(point: Point, direction: Tuple[int, int]) -> Point:
    """
    Return a new Point moved by the given direction vector.
    """
    dx, dy = direction
    return Point(point.x + dx, point.y + dy)


def is_within_bounds(point: Point, board_width: int, board_height: int) -> bool:
    """
    Check if a point lies inside the board boundaries.
    """
    return 0 <= point.x < board_width and 0 <= point.y < board_height


def is_collision(point: Point, snake_body: List[Point]) -> bool:
    """
    Check if a point collides with any part of the snake body.
    """
    return point in snake_body


def place_food(board_width: int, board_height: int, snake_body: List[Point]) -> Point:
    """
    Randomly place food on the board such that it does not overlap with the snake.
    """
    snake_set: Set[Point] = set(snake_body)
    while True:
        new_point = Point(random.randrange(board_width), random.randrange(board_height))
        if new_point not in snake_set:
            return new_point


def load_highscore(file_path: str) -> int:
    """
    Load the highscore from a file. If the file does not exist or is invalid, return 0.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return int(f.read().strip())
    except (FileNotFoundError, ValueError):
        return 0


def save_highscore(file_path: str, score: int) -> None:
    """
    Save the highscore to a file.
    """
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(str(score))