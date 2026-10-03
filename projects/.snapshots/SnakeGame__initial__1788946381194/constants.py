# constants.py
# -*- coding: utf-8 -*-

"""
Module: constants
~~~~~~~~~~~~~~~~~

This module defines all constants used across the Snake game.
It is intentionally lightweight so it can be imported by any
module without side effects.  All values are typed and
documented to aid static analysis and readability.

The constants are grouped logically:
  * Display / visual constants
  * Game mechanics constants
  * Direction vectors
  * Key bindings
"""

from __future__ import annotations

from typing import Tuple, Dict

# --------------------------------------------------------------------------- #
# Display / visual constants
# --------------------------------------------------------------------------- #

# Characters used to render the game board
SNAKE_BODY_CHAR: str = "█"
SNAKE_HEAD_CHAR: str = "■"
FOOD_CHAR: str = "●"
EMPTY_SPACE_CHAR: str = " "

# Colors (used only if curses supports them)
# These are indices for curses.init_pair
COLOR_PAIRS: Dict[str, Tuple[int, int]] = {
    "snake": (curses.COLOR_GREEN, curses.COLOR_BLACK),
    "food": (curses.COLOR_RED, curses.COLOR_BLACK),
    "border": (curses.COLOR_WHITE, curses.COLOR_BLACK),
}

# Board dimensions (must be odd to center the snake)
BOARD_HEIGHT: int = 21  # must be >= 5
BOARD_WIDTH: int = 41   # must be >= 5

# Border characters
BORDER_HORIZONTAL: str = "─"
BORDER_VERTICAL: str = "│"
BORDER_TOP_LEFT: str = "┌"
BORDER_TOP_RIGHT: str = "┐"
BORDER_BOTTOM_LEFT: str = "└"
BORDER_BOTTOM_RIGHT: str = "┘"

# --------------------------------------------------------------------------- #
# Game mechanics constants
# --------------------------------------------------------------------------- #

# Initial snake length
INITIAL_SNAKE_LENGTH: int = 3

# Initial speed (milliseconds per move)
INITIAL_SPEED_MS: int = 200

# Speed increase per food eaten (milliseconds reduction)
SPEED_DECREASE_MS: int = 10

# Minimum speed (maximum difficulty)
MIN_SPEED_MS: int = 50

# --------------------------------------------------------------------------- #
# Direction vectors
# --------------------------------------------------------------------------- #

# Directions are represented as (dy, dx) tuples
DIRECTION_UP: Tuple[int, int] = (-1, 0)
DIRECTION_DOWN: Tuple[int, int] = (1, 0)
DIRECTION_LEFT: Tuple[int, int] = (0, -1)
DIRECTION_RIGHT: Tuple[int, int] = (0, 1)

# Mapping from key codes to direction vectors
# These values are intended for use with curses' getch() method
DIRECTION_KEYS: Dict[int, Tuple[int, int]] = {
    curses.KEY_UP: DIRECTION_UP,
    curses.KEY_DOWN: DIRECTION_DOWN,
    curses.KEY_LEFT: DIRECTION_LEFT,
    curses.KEY_RIGHT: DIRECTION_RIGHT,
    # Alternative keys: W/A/S/D
    ord('w'): DIRECTION_UP,
    ord('s'): DIRECTION_DOWN,
    ord('a'): DIRECTION_LEFT,
    ord('d'): DIRECTION_RIGHT,
}

# --------------------------------------------------------------------------- #
# Miscellaneous constants
# --------------------------------------------------------------------------- #

# Score multiplier for each food eaten
SCORE_PER_FOOD: int = 10

# Maximum score before game over (optional)
MAX_SCORE: int | None = None

# --------------------------------------------------------------------------- #
# Helper functions
# --------------------------------------------------------------------------- #

def opposite_direction(dir_a: Tuple[int, int], dir_b: Tuple[int, int]) -> bool:
    """
    Return True if dir_a is the opposite of dir_b.
    Useful for preventing the snake from reversing onto itself.
    """
    return dir_a[0] == -dir_b[0] and dir_a[1] == -dir_b[1]

# End of constants.py