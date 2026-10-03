import random
from typing import Tuple, List, Optional

# Optional import of pygame. It may not be available in test environments.
try:
    import pygame  # type: ignore
except Exception:  # pragma: no cover
    pygame = None  # type: ignore

# Import the Snake class defined in snake.py
from snake import Snake


# Direction constants
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
DIRECTION_MAP = {
    pygame.K_UP: UP,
    pygame.K_DOWN: DOWN,
    pygame.K_LEFT: LEFT,
    pygame.K_RIGHT: RIGHT,
}


class Game:
    """
    Core game logic for a Snake game. The rendering and event handling
    are optional and only performed when pygame is available.
    """

    def __init__(
        self,
        width: int = 640,
        height: int = 480,
        block_size: int = 20,
        speed: int = 10,
        seed: Optional[int] = None,
    ) -> None:
        self.width =