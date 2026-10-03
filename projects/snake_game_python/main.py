from __future__ import annotations
import random
from typing import List, Tuple, Set

Position = Tuple[int, int]
Direction = Tuple[int, int]

UP: Direction = (0, -1)
DOWN: Direction = (0, 1)
LEFT: Direction = (-1, 0)
RIGHT: Direction = (1, 0)

class Snake:
    def __init__(self, start_pos: Position, initial_length: int = 3, direction: Direction = RIGHT) -> None:
        self.positions: List[Position] = [start_pos]
        self.direction = direction
        for _ in range(1, initial_length):
            self.grow()

    def head(self) -> Position:
        return self.positions[0]

    def move(self) -> None:
        new_head = (self.head()[0] + self.direction[0], self.head()[1] + self.direction[1])
        self.positions.insert(0, new_head)
        self.positions.pop()

    def grow(self) -> None:
        tail = self.positions[-1]
        self.positions.append(tail)

    def set_direction(self, direction: Direction) -> None:
        """Set the snake's moving direction."""
        self.direction = direction

    def __repr__(self) -> str:
        return f"Snake(positions={self.positions}, direction={self.direction})"