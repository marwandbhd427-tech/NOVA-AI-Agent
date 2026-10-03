import random
from dataclasses import dataclass, field
from typing import List, Tuple, Iterable

@dataclass
class Food:
    """
    Represents a piece of food in the Snake game.

    Attributes:
        x (int): The x-coordinate of the food, aligned to the grid.
        y (int): The y-coordinate of the food, aligned to the grid.
        cell_size (int): The size of a single grid cell in pixels.
        width (int): Width of the food sprite (defaults to cell_size).
        height (int): Height of the food sprite (defaults to cell_size).
    """
    x: int
    y: int
    cell_size: int
    width: int = field(init=False)
    height: int = field(init=False)

    def __post_init__(self) -> None:
        """Align coordinates to the grid and set sprite size."""
        self.x = (self.x // self.cell_size) * self.cell_size
        self.y = (self.y // self.cell_size) * self.cell_size
        self.width = self.cell_size
        self.height = self.cell_size

    def respawn(
        self,
        snake_body: Iterable[Tuple[int, int]],
        grid_width: int,
        grid_height: int,
    ) -> None:
        """
        Place the food at a random position that is not occupied by the snake.

        Args:
            snake_body: Iterable of (x, y) tuples representing snake segments.
            grid_width: Width of the game grid in pixels.
            grid_height: Height of the game grid in pixels.

        Raises:
            RuntimeError: If no free cell is available.
        """
        max_cells_x = grid_width // self.cell_size
        max_cells_y = grid_height // self.cell_size

        # Generate all possible cell positions
        all_cells = [
            (x * self.cell_size, y * self.cell_size)
            for x in range(max_cells_x)
            for y in range(max_cells_y)
        ]

        # Filter out cells occupied by the snake
        free_cells = [cell for cell in all_cells if cell not in snake_body]

        if not free_cells:
            raise RuntimeError("No free space left to spawn food.")

        self.x, self.y = random.choice(free_cells)

    def position(self) -> Tuple[int, int]:
        """Return the current food coordinates as a tuple."""
        return self.x, self.y

    def to_rect(self) -> Tuple[int, int, int, int]:
        """
        Return a rectangle representation of the food suitable for drawing.

        Returns:
            A tuple (x, y, width, height) representing the food rectangle.
        """
        return self.x, self.y, self.width, self.height


# The following block is guarded so that importing this module does not
# start a game window or any side effects.  It only runs when the file
# is executed directly.
if __name__ == "__main__":
    # Minimal demo that does not require Pygame.
    # It shows that the Food class works as expected.
    import os

    # Define a mock snake body occupying the center of a 10x10 grid
    grid_w, grid_h = 200, 200
    cell = 20
    snake = [(grid_w // 2, grid_h // 2)]

    food = Food(0, 0, cell_size=cell)
    try:
        food.respawn(snake_body=snake, grid_width=grid_w, grid_height=grid_h)
        print(f"Food spawned at: {food.position()}")
    except RuntimeError as exc:
        print(f"Could not spawn food: {exc}")

    # Wait for user input before exiting to avoid abrupt termination
    if os.environ.get("PYTEST_CURRENT_TEST") is None:
        input("Press Enter to exit...")