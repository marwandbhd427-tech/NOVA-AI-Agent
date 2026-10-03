import random
from typing import Tuple, Set

class Food:
    """Represents the food item in a Snake game.

    The food is placed on a rectangular grid.  The grid size is
    provided when the Food instance is created.  The position is
    stored as a tuple of (row, col).  The food can be relocated
    to a random free cell that is not occupied by the snake.
    """

    def __init__(self, grid_rows: int, grid_cols: int, snake_positions: Set[Tuple[int, int]] = None):
        """
        Parameters
        ----------
        grid_rows : int
            Number of rows in the game grid.
        grid_cols : int
            Number of columns in the game grid.
        snake_positions : set[tuple[int, int]], optional
            Set of grid cells currently occupied by the snake.  The
            initial food position will avoid these cells if provided.
        """
        self.grid_rows = grid_rows
        self.grid_cols = grid_cols
        self.position = None
        self.spawn(snake_positions or set())

    def spawn(self, snake_positions: Set[Tuple[int, int]]):
        """Place the food at a random position that is not occupied by the snake.

        Parameters
        ----------
        snake_positions : set[tuple[int, int]]
            Set of coordinates occupied by the snake.
        """
        free_cells = [
            (r, c)
            for r in range(self.grid_rows)
            for c in range(self.grid_cols)
            if (r, c) not in snake_positions
        ]
        if not free_cells:
            # No free cell left; the snake occupies the entire grid.
            raise RuntimeError("No free cells available to spawn food.")
        self.position = random.choice(free_cells)

    def __repr__(self) -> str:
        return f"<Food pos={self.position}>"

# Guarded entry point for manual testing
if __name__ == "__main__":
    # Demo: create a 10x20 grid with a snake occupying some cells
    snake_cells = {(5, 5), (5, 6), (5, 7)}
    food = Food(grid_rows=10, grid_cols=20, snake_positions=snake_cells)
    print(f"Initial food position: {food.position}")
    # Simulate eating the food and spawning a new one
    snake_cells.add(food.position)
    food.spawn(snake_cells)
    print(f"New food position after eating: {food.position}")