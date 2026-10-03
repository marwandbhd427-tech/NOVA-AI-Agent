import random
from typing import List, Tuple, Set

Position = Tuple[int, int]
SnakeBody = List[Position]


def _is_position_on_snake(position: Position, snake_body: SnakeBody) -> bool:
    """
    Check whether the given position is occupied by the snake.

    Args:
        position: The (x, y) coordinate to check.
        snake_body: A list of (x, y) tuples representing the snake's body segments.

    Returns:
        True if the position is on the snake, False otherwise.
    """
    return position in snake_body


def _generate_random_position(width: int, height: int) -> Position:
    """
    Generate a random position within the given grid dimensions.

    Args:
        width: The width of the grid (number of columns).
        height: The height of the grid (number of rows).

    Returns:
        A tuple (x, y) representing the random position.
    """
    x = random.randint(0, width - 1)
    y = random.randint(0, height - 1)
    return (x, y)


def get_food_position(
    snake_body: SnakeBody, width: int, height: int, max_attempts: int = 100
) -> Position:
    """
    Return a random position for new food that does not collide with the snake.

    This function will attempt up to ``max_attempts`` times to find a valid position.
    If it cannot find one, it will raise a RuntimeError.

    Args:
        snake_body: The current snake body positions.
        width: Grid width.
        height: Grid height.
        max_attempts: Maximum number of attempts to find a free cell.

    Returns:
        A valid (x, y) position for the food.

    Raises:
        RuntimeError: If no free position is found after ``max_attempts`` attempts.
    """
    for _ in range(max_attempts):
        pos = _generate_random_position(width, height)
        if not _is_position_on_snake(pos, snake_body):
            return pos
    raise RuntimeError("Unable to find a free position for food after many attempts.")


class Food:
    """
    Represents the food item in the Snake game.

    The food has a position on the grid. When the snake consumes the food,
    the game logic should call :meth:`respawn` to place it at a new location.

    Attributes:
        position: Current position of the food on the grid.
        width: Width of the game grid.
        height: Height of the game grid.
    """

    def __init__(self, width: int, height: int, snake_body: SnakeBody):
        """
        Initialize the Food instance and spawn it on the grid.

        Args:
            width: Grid width.
            height: Grid height.
            snake_body: Current snake body positions to avoid when spawning.
        """
        self.width = width
        self.height = height
        self.position: Position = get_food_position(snake_body, width, height)

    def respawn(self, snake_body: SnakeBody) -> None:
        """
        Place the food at a new random position that does not overlap the snake.

        Args:
            snake_body: Current snake body positions to avoid.
        """
        self.position = get_food_position(snake_body, self.width, self.height)

    def __repr__(self) -> str:
        return f"Food(position={self.position}, width={self.width}, height={self.height})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Food):
            return False
        return (
            self.position == other.position
            and self.width == other.width
            and self.height == other.height
        )