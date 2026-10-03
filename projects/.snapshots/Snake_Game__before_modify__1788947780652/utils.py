import random
from typing import Iterable, Tuple, Optional

Point = Tuple[int, int]

def get_random_position(
    grid_width: int,
    grid_height: int,
    cell_size: int,
    exclude_positions: Optional[Iterable[Point]] = None,
) -> Point:
    """
    Return a random position (top-left corner) aligned to the grid.

    Parameters
    ----------
    grid_width : int
        Width of the game area in pixels.
    grid_height : int
        Height of the game area in pixels.
    cell_size : int
        Size of one grid cell in pixels.
    exclude_positions : Iterable[Point], optional
        Positions that must not be chosen (e.g., snake body).

    Returns
    -------
    Point
        A tuple (x, y) representing the chosen position.
    """
    if cell_size <= 0:
        raise ValueError("cell_size must be positive")
    if grid_width <= 0 or grid_height <= 0:
        raise ValueError("grid dimensions must be positive")

    cols = grid_width // cell_size
    rows = grid_height // cell_size

    all_positions = [
        (col * cell_size, row * cell_size)
        for col in range(cols)
        for row in range(rows)
    ]

    if exclude_positions:
        excluded_set = set(exclude_positions)
        available = [p for p in all_positions if p not in excluded_set]
    else:
        available = all_positions

    if not available:
        raise RuntimeError("No available positions left to place the object.")

    return random.choice(available)


def is_position_valid(
    position: Point,
    grid_width: int,
    grid_height: int,
    cell_size: int,
) -> bool:
    """
    Check if a position is within the grid and aligned to cell_size.

    Parameters
    ----------
    position : Point
        The (x, y) position to validate.
    grid_width : int
        Width of the game area in pixels.
    grid_height : int
        Height of the game area in pixels.
    cell_size : int
        Size of one grid cell in pixels.

    Returns
    -------
    bool
        True if position is valid, False otherwise.
    """
    x, y = position
    return (
        0 <= x < grid_width
        and 0 <= y < grid_height
        and x % cell_size == 0
        and y % cell_size == 0
    )


def clamp_position(
    position: Point,
    grid_width: int,
    grid_height: int,
    cell_size: int,
) -> Point:
    """
    Clamp a position to the nearest valid grid coordinate within bounds.

    Parameters
    ----------
    position : Point
        The (x, y) position to clamp.
    grid_width : int
        Width of the game area in pixels.
    grid_height : int
        Height of the game area in pixels.
    cell_size : int
        Size of one grid cell in pixels.

    Returns
    -------
    Point
        The clamped position.
    """
    x, y = position
    x = max(0, min(x, grid_width - cell_size))
    y = max(0, min(y, grid_height - cell_size))
    return (x - x % cell_size, y - y % cell_size)


def random_color() -> Tuple[int, int, int]:
    """
    Generate a random RGB color.

    Returns
    -------
    Tuple[int, int, int]
        A tuple representing an RGB color.
    """
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))