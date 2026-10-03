# constants.py

# Screen dimensions
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480

# Grid settings
GRID_SIZE = 20  # Each cell is 20x20 pixels
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Colors (RGB tuples)
COLOR_BACKGROUND = (0, 0, 0)          # Black
COLOR_SNAKE = (0, 255, 0)             # Green
COLOR_FOOD = (255, 0, 0)              # Red
COLOR_TEXT = (255, 255, 255)          # White

# Game settings
INITIAL_SNAKE_LENGTH = 3
SNAKE_SPEED = 10  # Moves per second
FOOD_SPAWN_PROBABILITY = 0.05  # Chance to spawn food each tick

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
DIRECTION_MAP = {
    'UP': UP,
    'DOWN': DOWN,
    'LEFT': LEFT,
    'RIGHT': RIGHT
}

# Scoring
POINTS_PER_FOOD = 10

# Key bindings (Pygame key constants are used in the main game loop)
KEY_UP = 'w'
KEY_DOWN = 's'
KEY_LEFT = 'a'
KEY_RIGHT = 'd'
KEY_QUIT = 'q'

# Miscellaneous
MAX_FRAMES_PER_SECOND = 60
FONT_NAME = 'Arial'
FONT_SIZE = 24

# End of constants.py