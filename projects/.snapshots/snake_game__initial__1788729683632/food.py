import random
from typing import Tuple, Sequence

# The constants module should define the grid dimensions and cell size.
# For the purpose of this file, we import them. If they are not defined,
# fallback values are used to keep the module self‑contained for testing.
try:
    from constants import GRID_WIDTH, GRID_HEIGHT, CELL_SIZE
except ImportError:
    GRID_WIDTH = 20   # number of cells horizontally
    GRID_HEIGHT = 20  # number of cells vertically
    CELL_SIZE = 20    # pixel size of each cell (unused in logic)

Position = Tuple[int, int]


class Food:
    """
    Represents a food item on the snake game board.

    The food is always located on the grid defined by GRID_WIDTH and
    GRID_HEIGHT. It can be respawned at a random location that does not
    overlap with the snake's body.

    Attributes
    ----------
    position : Position
        Current grid coordinates of the food.
    """

    def __init__(self, snake_body: Sequence[Position] | None = None) -> None:
        """
        Create a new Food instance and place it on the board.

        Parameters
        ----------
        snake_body : Sequence[Position] | None
            The current positions occupied by the snake. The food will
            not be spawned on any of these cells. If ``None`` is
            supplied, the food will be placed at a random location.
        """
        self.position: Position = (0, 0)
        self.spawn(snake_body)

    def spawn(self, snake_body: Sequence[Position] | None = None) -> None:
        """
        Place the food at a random location that is not occupied by the snake.

        Parameters
        ----------
        snake_body : Sequence[Position] | None
            The current positions occupied by the snake. The food will
            not be spawned on any of these cells. If ``None`` is
            supplied, the food will be placed at a random location.
        """
        occupied = set(snake_body) if snake_body else set()
        free_cells = [
            (x, y)
            for x in range(GRID_WIDTH)
            for y in range(GRID_HEIGHT)
            if (x, y) not in occupied
        ]

        if not free_cells:
            raise RuntimeError("No free cells available to spawn food.")

        self.position = random.choice(free_cells)

    def get_position(self) -> Position:
        """
        Return the current position of the food.

        Returns
        -------
        Position
            The (x, y) coordinates of the food on the grid.
        """
        return self.position

    def __repr__(self) -> str:
        return f"Food(position={self.position})"


# Guarded entry point for manual testing or debugging.
if __name__ == "__main__":
    # Example usage: spawn food avoiding a dummy snake body.
    dummy_snake = [(5, 5), (5, 6), (5, 7)]
    food = Food(dummy_snake)
    print(f"Spawned food at {food.get_position()}")
    # Respawn after "eating" the food.
    food.spawn(dummy_snake)
    print(f"Respawned food at {food.get_position()}")