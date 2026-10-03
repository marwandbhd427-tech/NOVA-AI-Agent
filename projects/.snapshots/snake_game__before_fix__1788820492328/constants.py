# constants.py
"""
Constants and configuration values for the Snake game.

This module defines screen dimensions, block size, grid size, colors,
game settings, and direction vectors. It contains no executable logic,
ensuring that importing it has no side effects and can be safely used
in unit tests or by the main game loop.
"""

# Screen dimensions (pixels)
SCREEN_WIDTH: int = 640
SCREEN_HEIGHT: int = 480

# Size of each snake segment and food item (pixels)
BLOCK_SIZE: int = 20

# Grid dimensions derived from screen size and block size
GRID_WIDTH: int = SCREEN_WIDTH // BLOCK_SIZE
GRID_HEIGHT: int = SCREEN_HEIGHT // BLOCK_SIZE

# Color definitions (RGB tuples)
COLOR_BG: tuple[int, int, int] = (0, 0, 0)          # Background
COLOR_SNAKE: tuple[int, int, int] = (0, 255, 0)    # Snake body
COLOR_FOOD: tuple[int, int, int] = (255, 0, 0)     # Food
COLOR_TEXT: tuple[int, int, int] = (255, 255, 255) # Text

# Game settings
FPS: int = 10                                 # Frames per second
INITIAL_SNAKE_LENGTH: int = 3                 # Starting length of the snake

# Direction vectors (dx, dy) used for movement
UP: tuple[int, int] = (0, -1)
DOWN: tuple[int, int] = (0, 1)
LEFT: tuple[int, int] = (-1, 0)
RIGHT: tuple[int, int] = (1, 0)

# Mapping of string keys to direction vectors (useful for input handling)
KEY_DIRECTION_MAP: dict[str, tuple[int, int]] = {
    "up": UP,
    "down": DOWN,
    "left": LEFT,
    "right": RIGHT,
}

# Optional: font settings for rendering text
FONT_NAME: str = "Arial"
FONT_SIZE: int = 24

# End of constants.py