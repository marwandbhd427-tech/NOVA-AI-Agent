import random
from typing import List, Tuple, Optional

# Try to import board size constants; fall back to defaults if unavailable.
try:
    from constants import BOARD_WIDTH, BOARD_HEIGHT
except Exception:
    BOARD_WIDTH: int = 20
    BOARD_HEIGHT: int = 20


class Food:
    """
    Represents a food item in a Snake game.

    Attributes
    ----------
    board_width : int
        Width of the playing board in cells.
    board_height : int
        Height of the playing board in cells.
    position : Tuple[int, int] | None
        Current coordinates of the food. ``None`` means the food has not
        been spawned yet.
    """

    def __init__(self, board_width: int = BOARD_WIDTH, board_height: int = BOARD_HEIGHT) -> None:
        self.board_width = board_width
        self.board_height = board_height
        self.position: Optional[Tuple[int, int]] = None

    def spawn(self, snake_positions: List[Tuple[int, int]]) -> None:
        """
        Place the food on a random cell that is not occupied by the snake.

        Parameters
        ----------
        snake_positions : List[Tuple[int, int]]
            List of coordinates occupied by the snake body segments.

        Raises
        ------
        RuntimeError
            If there are no free cells left to spawn food.
        """
        # Generate all possible positions on the board.
        all_positions = [(x, y) for x in range(self.board_width) for y in range(self.board_height)]
        # Exclude positions occupied by the snake.
        free_positions = [pos for pos in all_positions if pos not in snake_positions]

        if not free_positions:
            raise RuntimeError("No free cells available to spawn food.")

        self.position = random.choice(free_positions)

    def get_position(self) -> Tuple[int, int]:
        """
        Return the current position of the food.

        Returns
        -------
        Tuple[int, int]
            The (x, y) coordinates of the food.

        Raises
        ------
        ValueError
            If the food has not been spawned yet.
        """
        if self.position is None:
            raise ValueError("Food has not been spawned yet.")
        return self.position

    def __repr__(self) -> str:
        return f"Food(position={self.position})"


# The following block is only executed when the module is run directly.
# It serves as a minimal demonstration and does not start a game loop or GUI.
if __name__ == "__main__":
    # Simple demo: spawn food avoiding a mock snake.
    demo_snake = [(5, 5), (5, 6), (5, 7)]
    food = Food()
    food.spawn(demo_snake)
    print(f"Demo: spawned food at {food.get_position()}")