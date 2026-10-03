import random
from dataclasses import dataclass
from typing import Set, Tuple


@dataclass(frozen=True)
class Food:
    x: int
    y: int

    @staticmethod
    def spawn(width: int, height: int, occupied: Set[Tuple[int, int]]) -> "Food":
        """
        Generate a new Food instance at a random position within the grid
        defined by width and height that does not overlap any coordinates
        in the occupied set.

        Parameters
        ----------
        width : int
            The width of the game grid (number of columns).
        height : int
            The height of the game grid (number of rows).
        occupied : set[tuple[int, int]]
            Set of coordinates that are currently occupied by the snake
            or other objects; the food will not spawn on these positions.

        Returns
        -------
        Food
            A new Food object with coordinates (x, y).

        Raises
        ------
        ValueError
            If no free position is available.
        """
        if width <= 0 or height <= 0:
            raise ValueError("Grid dimensions must be positive")

        # Build a set of all possible coordinates
        all_positions = {(x, y) for x in range(width) for y in range(height)}
        free_positions = all_positions - occupied

        if not free_positions:
            raise ValueError("No free position available for food")

        x, y = random.choice(list(free_positions))
        return Food(x, y)

    def __str__(self) -> str:
        return f"Food({self.x}, {self.y})"

    def __repr__(self) -> str:
        return f"Food(x={self.x}, y={self.y})"