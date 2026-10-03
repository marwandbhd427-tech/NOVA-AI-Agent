from __future__ import annotations

import random
from typing import Iterable, Tuple, Set


class Food:
    """
    Represents a food item on the snake board.

    Attributes
    ----------
    board_size : Tuple[int, int]
        Width and height of the board (columns, rows).
    position : Tuple[int, int]
        Current coordinates of the food.
    """

    def __init__(self, board_size: Tuple[int, int], snake_positions: Iterable[Tuple[int, int]]) -> None:
        """
        Create a new food instance.

        Parameters
        ----------
        board_size : Tuple[int, int]
            The dimensions of the board as (width, height).
        snake_positions : Iterable[Tuple[int, int]]
            Iterable of coordinates occupied by the snake.
        """
        self.board_size = board_size
        self.position = self._generate_position(set(snake_positions))

    def _generate_position(self, occupied: Set[Tuple[int, int]]) -> Tuple[int, int]:
        """
        Generate a random position that is not occupied by the snake.

        Parameters
        ----------
        occupied : Set[Tuple[int, int]]
            Set of coordinates that are already occupied.

        Returns
        -------
        Tuple[int, int]
            A new position for the food.
        """
        width, height = self.board_size
        while True:
            pos = (random.randint(0, width - 1), random.randint(0, height - 1))
            if pos not in occupied:
                return pos

    def respawn(self, snake_positions: Iterable[Tuple[int, int]]) -> None:
        """
        Move the food to a new random position, avoiding the snake.

        Parameters
        ----------
        snake_positions : Iterable[Tuple[int, int]]
            Iterable of coordinates occupied by the snake.
        """
        self.position = self._generate_position(set(snake_positions))

    def is_eaten_by(self, snake_head: Tuple[int, int]) -> bool:
        """
        Check if the food has been eaten by the snake.

        Parameters
        ----------
        snake_head : Tuple[int, int]
            The coordinates of the snake's head.

        Returns
        -------
        bool
            True if the snake's head is on the food, False otherwise.
        """
        return self.position == snake_head

    def __repr__(self) -> str:
        return f"Food(position={self.position}, board_size={self.board_size})"

# Guard against accidental GUI startup when this module is executed directly.
if __name__ == "__main__":
    # Simple demonstration that does not open a window.
    board = (20, 20)
    snake = {(5, 5), (5, 6), (5, 7)}
    food = Food(board, snake)
    print(f"Initial food position: {food.position}")
    # Simulate eating
    food.respawn(snake)
    print(f"New food position after respawn: {food.position}")