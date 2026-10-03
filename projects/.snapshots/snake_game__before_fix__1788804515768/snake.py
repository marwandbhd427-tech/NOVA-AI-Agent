# snake.py
"""
A pure logic implementation of the classic Snake game suitable for unit testing.
This module contains no external dependencies other than the Python standard library.
"""

from __future__ import annotations
import random
from dataclasses import dataclass, field
from typing import List, Tuple, Set, Optional

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
    # No bounds check here – collisions are handled explicitly by the game logic.


class Direction:
    UP = Position(0, -1)
    DOWN = Position(0, 1)
    LEFT = Position(-1, 0)
    RIGHT = Position(1, 0)

    @classmethod
    def opposite(cls, dir1: Position, dir2: Position) -> bool:
        """Return True if dir1 is the exact opposite of dir2."""
        return dir1.x == -dir2.x and dir1.y == -dir2.y


class Snake:
    def __init__(self, start_pos: Position, length: int = INITIAL_SNAKE_LENGTH):
        self.segments: List[Position] = [start_pos]
        self.direction: Position = Direction.RIGHT
        self