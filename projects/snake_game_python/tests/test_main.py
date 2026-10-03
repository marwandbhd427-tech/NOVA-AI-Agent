import collections
from typing import List, Tuple


class Snake:
    """
    A simple snake representation suitable for a Snake game.

    The snake is represented as a list of (x, y) coordinates, where the first
    element is the head. The snake moves by adding a new head in the current
    direction and removing the tail unless the snake has just eaten food.

    Attributes
    ----------
    segments : collections.deque[Tuple[int, int]]
        Ordered list of segment positions, head first.
    direction : Tuple[int, int]
        Current movement direction as a unit vector (dx, dy).
    pending_growth : int
        Number of segments to grow before the tail is trimmed.
    """

    def __init__(
        self,
        start_pos: Tuple[int, int] = (5, 5),
        direction: Tuple[int, int] = (0, 1),
        initial_length: int = 3,
    ) -> None:
        """
        Parameters
        ----------
        start_pos : Tuple[int, int]
            Starting position of the snake's head.
        direction : Tuple[int, int]
            Initial movement direction. Must be one of (1,0), (-1,0), (0,1), (0,-1).
        initial_length : int
            Initial length of the snake (including head).
        """
        self.segments = collections.deque([start_pos] * initial_length)
        self.direction = direction
        self.pending_growth = 0

    def set_direction(self, new_direction: Tuple[int, int]) -> None:
        """
        Change the snake's movement direction.

        The new direction cannot be directly opposite to the current one,
        which would cause the snake to collide with itself.

        Parameters
        ----------
        new_direction : Tuple[int, int]
            Desired direction vector.
        """
        opposite = (-self.direction[0], -self.direction[1])
        if new_direction != opposite:
            self.direction = new_direction

    def move(self) -> None:
        """
        Move the snake one step in the current direction.
        """
        new_head = (
            self.segments[0][0] + self.direction[0],
            self.segments[0][1] + self.direction[1],
        )
        self.segments.appendleft(new_head)

        if self.pending_growth > 0:
            self.pending_growth -= 1
        else:
            self.segments.pop()

    def grow(self, amount: int = 1) -> None:
        """
        Increase the snake's length by the specified amount.

        The growth is applied on subsequent moves.

        Parameters
        ----------
        amount : int
            Number of segments to grow.
        """
        self.pending_growth += amount

    def get_positions(self) -> List[Tuple[int, int]]:
        """
        Return a list of all segment positions, head first.
        """
        return list(self.segments)

    def check_self_collision(self) -> bool:
        """
        Check if the snake's head collides with its body.

        Returns
        -------
        bool
            True if the head's position matches any other segment.
        """
        head = self.segments[0]
        return head in list(self.segments)[1:]

    def __len__(self) -> int:
        """
        Return the current length of the snake.
        """
        return len(self.segments) + self.pending_growth

    def __repr__(self) -> str:
        return f"Snake(head={self.segments[0]}, length={len(self)})"