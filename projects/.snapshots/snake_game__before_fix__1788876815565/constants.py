# constants.py
"""
Module containing global constants for the Snake game.
These constants are used throughout the project to keep the code
clean, maintainable, and easily configurable.
"""

# Screen dimensions (pixels)
SCREEN_WIDTH: int = 640
SCREEN_HEIGHT: int = 480

# Size of one grid cell (pixels)
CELL_SIZE: int = 20

# Derived grid dimensions (cells)
GRID_WIDTH: int = SCREEN_WIDTH // CELL_SIZE
GRID_HEIGHT: int = SCREEN_HEIGHT // CELL_SIZE

# Color definitions (RGB tuples)
WHITE: tuple[int, int, int] = (255, 255, 255)
BLACK: tuple[int, int, int] = (0, 0, 0)
RED:   tuple[int, int, int] = (255,   0,   0)
GREEN: tuple[int, int, int] = (0,   255,   0)
BLUE:  tuple[int, int, int] = (0,     0, 255)

# Direction vectors
UP: tuple[int, int] = (0, -1)
DOWN: tuple[int, int] = (0, 1)
LEFT: tuple[int, int] = (-1, 0)
RIGHT: tuple[int, int] = (1, 0)

# Movement speed (ticks per second)
TICKS_PER_SECOND: int = 10

# Initial snake configuration
INITIAL_SNAKE_LENGTH: int = 3
INITIAL_SNAKE_COLOR: tuple[int, int, int] = GREEN

# Food configuration
FOOD_COLOR: tuple[int, int, int] = RED
FOOD_SCORE_VALUE: int = 1

# Game state limits
MAX_SCORE: int = 9999
MAX_SNAKE_LENGTH: int = GRID_WIDTH * GRID_HEIGHT

# Miscellaneous
FPS: int = 60  # Frames per second for rendering loop
WINDOW_TITLE: str = "Snake Game"

# Utility dictionary for quick lookup of opposite directions
OPPOSITE_DIRECTION = {
    UP: DOWN,
    DOWN: UP,
    LEFT: RIGHT,
    RIGHT: LEFT,
}