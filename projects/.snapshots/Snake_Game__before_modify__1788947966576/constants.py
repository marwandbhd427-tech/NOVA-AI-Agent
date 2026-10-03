# constants.py

# Game screen dimensions
SCREEN_WIDTH: int = 600
SCREEN_HEIGHT: int = 600

# Size of each snake segment / food block (pixels)
BLOCK_SIZE: int = 20

# Frames per second (controls game speed)
FPS: int = 10

# Color definitions (RGB tuples)
WHITE: tuple[int, int, int] = (255, 255, 255)
BLACK: tuple[int, int, int] = (0, 0, 0)
RED:   tuple[int, int, int] = (255, 0, 0)
GREEN: tuple[int, int, int] = (0, 255, 0)
BLUE:  tuple[int, int, int] = (0, 0, 255)

# Directions as (dx, dy) offsets
UP: tuple[int, int] = (0, -1)
DOWN: tuple[int, int] = (0, 1)
LEFT: tuple[int, int] = (-1, 0)
RIGHT: tuple[int, int] = (1, 0)

# Mapping of key codes to directions (used in the main game loop)
# The actual key codes should be imported from pygame.locals in the game module
# Example mapping:
# KEY_DIRECTION_MAP = {
#     pygame.K_UP: UP,
#     pygame.K_DOWN: DOWN,
#     pygame.K_LEFT: LEFT,
#     pygame.K_RIGHT: RIGHT,
# }

# Default starting snake length
STARTING_LENGTH: int = 3

# Maximum number of food items that can appear simultaneously
MAX_FOOD: int = 1

# Collision detection threshold (distance in blocks)
COLLISION_THRESHOLD: int = 0

# Score multiplier for each food eaten
SCORE_PER_FOOD: int = 10

# Optional: define a simple enumeration for game states
class GameState:
    RUNNING = "running"
    PAUSED = "paused"
    GAME_OVER = "game_over"
    MENU = "menu"

# End of constants.py