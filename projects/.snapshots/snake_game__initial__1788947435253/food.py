import random
from typing import Iterable, Tuple, Set, Optional

# Optional constants that may be defined elsewhere.
# If not present, default to a 20x20 grid with 1x1 blocks.
try:
    from constants import BOARD_WIDTH, BOARD_HEIGHT, BLOCK_SIZE
except Exception:
    BOARD_WIDTH = 20
    BOARD_HEIGHT = 20
    BLOCK_SIZE = 1

Position = Tuple[int, int]


class Food:
    """
    Represents a single food item in the Snake game.

    Attributes
    ----------
    board_width : int
        Width of the board in blocks.
    board_height : int
        Height of the board in blocks.
    block_size : int
        Size of one block (default is 1 for grid coordinates).
    position : Optional[Position]
        Current coordinates of the food on the board. ``None`` if not spawned.
    """

    def __init__(
        self,
        board_width: int = BOARD_WIDTH,
        board_height: int = BOARD_HEIGHT,
        block_size: int = BLOCK_SIZE,
    ) -> None:
        self.board_width = board_width
        self.board_height = board_height
        self.block_size = block_size
        self.position: Optional[Position] = None

    def _random_position(self, exclude: Set[Position]) -> Position:
        """
        Generate a random position on the board that is not in ``exclude``.

        Parameters
        ----------
        exclude : Set[Position]
            Set of positions that the food must not occupy (e.g., snake body).

        Returns
        -------
        Position
            A tuple (x, y) representing the food location.
        """
        # Compute all possible positions
        all_positions = [
            (x, y)
            for x in range(self.board_width)
            for y in range(self.board_height)
            if (x, y) not in exclude
        ]
        if not all_positions:
            raise RuntimeError("No available positions to spawn food.")
        return random.choice(all_positions)

    def spawn(self, snake_positions: Iterable[Position]) -> Position:
        """
        Spawn food at a random location not occupied by the snake.

        Parameters
        ----------
        snake_positions : Iterable[Position]
            Iterable of positions occupied by the snake (body and head).

        Returns
        -------
        Position
            The new food position.
        """
        exclude = set(snake_positions)
        self.position = self._random_position(exclude)
        return self.position

    def is_eaten(self, snake_head: Position) -> bool:
        """
        Check if the snake's head is on the food position.

        Parameters
        ----------
        snake_head : Position
            Current coordinates of the snake's head.

        Returns
        -------
        bool
            ``True`` if the food is eaten, ``False`` otherwise.
        """
        if self.position is None:
            return False
        return snake_head == self.position

    def consume(self) -> None:
        """
        Reset the food position to ``None`` after being eaten.
        """
        self.position = None

    def get_position(self) -> Optional[Position]:
        """
        Get the current food position.

        Returns
        -------
        Optional[Position]
            The current position or ``None`` if not spawned.
        """
        return self.position

    def __repr__(self) -> str:
        return f"<Food position={self.position}>"


# The following test functions are not executed automatically; they are
# provided for quick manual verification when running this file directly.
if __name__ == "__main__":
    # Quick sanity check
    food = Food()
    snake_body = {(5, 5), (5, 6), (5, 7)}
    pos = food.spawn(snake_body)
    print("Spawned food at:", pos)
    print("Is eaten (head at (5,5)):", food.is_eaten((5, 5)))
    print("Is eaten (head at", pos, "):", food.is_eaten(pos))
    food.consume()
    print("After consume, position:", food.get_position())