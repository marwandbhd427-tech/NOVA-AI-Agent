import random
from typing import Iterable, Tuple, Set, Optional

# Attempt to import board dimensions from constants module.
# If unavailable, provide default values for testing purposes.
try:
    from constants import BOARD_WIDTH, BOARD_HEIGHT
except Exception:
    BOARD_WIDTH: int = 20
    BOARD_HEIGHT: int = 20


class Food:
    """
    Represents the food item in a Snake game.

    Attributes
    ----------
    board_width : int
        Width of the game board in grid cells.
    board_height : int
        Height of the game board in grid cells.
    position : Tuple[int, int] | None
        Current grid coordinates of the food. ``None`` if the food
        has not been spawned yet.
    """

    def __init__(
        self,
        board_width: int = BOARD_WIDTH,
        board_height: int = BOARD_HEIGHT,
        snake_positions: Optional[Set[Tuple[int, int]]] = None,
    ) -> None:
        """
        Initialise a Food instance and spawn it on the board.

        Parameters
        ----------
        board_width : int, optional
            Width of the board. Defaults to ``BOARD_WIDTH`` from constants
            or ``20`` if not defined.
        board_height : int, optional
            Height of the board. Defaults to ``BOARD_HEIGHT`` from constants
            or ``20`` if not defined.
        snake_positions : set of (int, int), optional
            Set of grid coordinates currently occupied by the snake.
            The food will spawn in a free cell.
        """
        self.board_width = board_width
        self.board_height = board_height
        self.position: Optional[Tuple[int, int]] = None
        self.spawn(snake_positions or set())

    def spawn(self, snake_positions: Iterable[Tuple[int, int]]) -> None:
        """
        Place the food at a random position that is not occupied by the snake.

        Parameters
        ----------
        snake_positions : iterable of (int, int)
            Grid coordinates occupied by the snake. The food will not spawn
            on any of these cells.

        Raises
        ------
        RuntimeError
            If there is no free space left on the board.
        """
        occupied = set(snake_positions)
        free_positions = [
            (x, y)
            for x in range(self.board_width)
            for y in range(self.board_height)
            if (x, y) not in occupied
        ]

        if not free_positions:
            raise RuntimeError("No available positions to spawn food.")

        self.position = random.choice(free_positions)

    def is_eaten(self, position: Tuple[int, int]) -> bool:
        """
        Check whether the food has been eaten at the given position.

        Parameters
        ----------
        position : (int, int)
            The grid coordinates to check.

        Returns
        -------
        bool
            ``True`` if the food occupies the given position, otherwise ``False``.
        """
        return self.position == position

    def __repr__(self) -> str:
        return f"<Food position={self.position!r}>"


if __name__ == "__main__":
    # Guarded entry point for manual testing; does not start a game loop.
    print("Food module loaded. Food instance can be created in a game context.")