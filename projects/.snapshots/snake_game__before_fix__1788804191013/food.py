import random
from typing import List, Tuple


class Food:
    """
    Represents the food item in the Snake game.

    Attributes:
        grid_size (Tuple[int, int]): Width and height of the playing grid.
        position (Tuple[int, int]): Current coordinates of the food on the grid.
    """

    def __init__(self, grid_size: Tuple[int, int], position: Tuple[int, int] | None = None) -> None:
        """
        Initialize the Food object.

        Args:
            grid_size: The width and height of the grid.
            position: Optional starting position. If omitted, a random position is chosen.
        """
        self.grid_size = grid_size
        self.position = position or self._random_position()

    def _random_position(self) -> Tuple[int, int]:
        """
        Generate a random position within the grid boundaries.

        Returns:
            A tuple (x, y) where 0 <= x < width and 0 <= y < height.
        """
        return (
            random.randint(0, self.grid_size[0] - 1),
            random.randint(0, self.grid_size[1] - 1),
        )

    def spawn(self, snake_positions: List[Tuple[int, int]]) -> None:
        """
        Place the food at a new random location that does not overlap the snake.

        The method will keep generating positions until it finds one that is not
        occupied by any part of the snake.

        Args:
            snake_positions: List of (x, y) tuples representing the snake's body.
        """
        while True:
            new_pos = self._random_position()
            if new_pos not in snake_positions:
                self.position = new_pos
                break

    def collides_with(self, pos: Tuple[int, int]) -> bool:
        """
        Check if the given position matches the food's position.

        Args:
            pos: A tuple (x, y) representing a location on the grid.

        Returns:
            True if the position coincides with the food; otherwise False.
        """
        return self.position == pos

    def __repr__(self) -> str:
        return f"Food(position={self.position}, grid_size={self.grid_size})"


if __name__ == "__main__":
    # Demo usage – this block runs only when the module is executed directly.
    grid = (20, 20)
    snake = [(5, 5), (5, 6), (5, 7)]
    food = Food(grid)
    print(f"Initial food: {food}")
    food.spawn(snake)
    print(f"New food after spawn: {food}")
    print(f"Does food collide with snake head? {food.collides_with(snake[0])}")