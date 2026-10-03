# constants.py

"""
Game constants for the Snake game.
These values are used throughout the project to keep configuration
in one place and make it easy to adjust the game's behaviour.
"""

from __future__ import annotations

# Screen configuration
SCREEN_WIDTH: int = 640          # Width of the game window in pixels
SCREEN_HEIGHT: int = 480         # Height of the game window in pixels
BLOCK_SIZE: int = 20             # Size of one square block (snake segment, food)

# Derived constants
GRID_WIDTH: int = SCREEN_WIDTH // BLOCK_SIZE
GRID_HEIGHT: int = SCREEN_HEIGHT // BLOCK_SIZE

# Game timing
FPS: int = 10                    # Frames per second (controls snake speed)
INITIAL_SPEED: int = FPS         # Starting speed
SPEED_INCREMENT: int = 1         # Speed increase per food eaten

# Colors (RGB tuples)
COLOR_BG: tuple[int, int, int] = (0, 0, 0)              # Background
COLOR_SNAKE: tuple[int, int, int] = (0, 255, 0)         # Snake body
COLOR_HEAD: tuple[int, int, int] = (0, 200, 0)          # Snake head
COLOR_FOOD: tuple[int, int, int] = (255, 0, 0)          # Food
COLOR_TEXT: tuple[int, int, int] = (255, 255, 255)      # Text

# Font settings
FONT_NAME: str = "Arial"
FONT_SIZE: int = 24

# Directions
UP: tuple[int, int] = (0, -1)
DOWN: tuple[int, int] = (0, 1)
LEFT: tuple[int, int] = (-1, 0)
RIGHT: tuple[int, int] = (1, 0)

# Key mappings (for pygame)
# These keys are used in the main game loop to change direction
KEY_UP: int = 273          # pygame.K_UP
KEY_DOWN: int = 274        # pygame.K_DOWN
KEY_LEFT: int = 276        # pygame.K_LEFT
KEY_RIGHT: int = 275       # pygame.K_RIGHT

# Game limits
MAX_SNAKE_LENGTH: int = GRID_WIDTH * GRID_HEIGHT - 1

# Scoring
POINTS_PER_FOOD: int = 10

# Miscellaneous
WINDOW_TITLE: str = "Snake Game"

# End of constants.py