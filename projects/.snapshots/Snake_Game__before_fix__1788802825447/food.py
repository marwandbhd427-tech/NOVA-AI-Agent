import random
from typing import Tuple, Iterable, Set

Position = Tuple[int, int]


class Food:
    """Manages the food item(s) in a Snake game.

    The food is represented by a single coordinate on the board.
    It can be spawned at a random location that does not overlap
    with the snake or any other food, checked for consumption,
    and removed once eaten.
    """

    def __init__(self, board_size: Tuple[int, int]) -> None:
        """
        Parameters
        ----------
        board_size
            A tuple (width, height) defining the playable area.
        """
        self.board_size = board_size
        self.position: Position | None = None

    def spawn(self, occupied: Iterable[Position]) -> Position:
        """
        Place the food on a random position that is not occupied.

        Parameters
        ----------
        occupied
            An iterable of coordinates that are currently occupied
            (e.g., the snake's body segments).

        Returns
        -------
        Position
            The coordinates where the food was placed.

        Raises
        ------
        RuntimeError
            If there is no free space left to spawn food.
        """
        max_x, max_y = self.board_size
        all_positions = {(x, y) for x in range(max_x) for y in range(max_y)}
        available = all_positions - set(occupied)

        if not available:
            raise RuntimeError("No space left to spawn food.")

        self.position = random.choice(list(available))
        return self.position

    def is_eaten(self, pos: Position) -> bool:
        """
        Check whether the given position coincides with the food's position.

        Parameters
        ----------
        pos
            The coordinate to check.

        Returns
        -------
        bool
            ``True`` if the food is at ``pos``; otherwise ``False``.
        """
        return pos == self.position

    def consume(self) -> None:
        """
        Remove the food after it has been eaten.
        """
        self.position = None

    def __repr__(self) -> str:
        return f"<Food position={self.position} board_size={self.board_size}>"


if __name__ == "__main__":
    # Simple manual test when running this file directly.
    board = (10, 10)
    snake_positions = {(1, 1), (1, 2), (1, 3)}
    food = Food(board)
    print("Spawning food...")
    pos = food.spawn(snake_positions)
    print(f"Food spawned at {pos}")
    print(f"Is eaten at {pos}? {food.is_eaten(pos)}")
    food.consume()
    print(f"After consumption: {food}")