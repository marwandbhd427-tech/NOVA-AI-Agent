import random
from typing import List, Tuple, Optional

# ----------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------
BLOCK_SIZE: int = 20
GRID_WIDTH: int = 30  # number of blocks horizontally
GRID_HEIGHT: int = 20  # number of blocks vertically
SCREEN_WIDTH: int = GRID_WIDTH * BLOCK_SIZE
SCREEN_HEIGHT: int = GRID_HEIGHT * BLOCK_SIZE
FPS: int = 10

# Directions represented as (dx, dy)
UP: Tuple[int, int] = (0, -1)
DOWN: Tuple[int, int] = (0, 1)
LEFT: Tuple[int, int] = (-1, 0)
RIGHT: Tuple[int, int] = (1, 0)

# ----------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------
def get_random_food_position(snake_positions: List[Tuple[int, int]]) -> Tuple[int, int]:
    """
    Return a random position within the grid that is not occupied by the snake.
    """
    available_positions = [
        (x, y)
        for x in range(GRID_WIDTH)
        for y in range(GRID_HEIGHT)
        if (x, y) not in snake_positions
    ]
    if not available_positions:
        raise RuntimeError("No available positions for food.")
    return random.choice(available_positions)

# ----------------------------------------------------------------------
# Snake class
# ----------------------------------------------------------------------
class Snake:
    """
    Represents the snake. The snake is a list of positions (x, y) where
    the head is the first element.
    """
    def __init__(self, init_position: Tuple[int, int], init_direction: Tuple[int, int] = RIGHT):
        self.positions: List[Tuple[int, int]] = [init_position]
        self.direction: Tuple[int, int] = init_direction
        self.growing: bool = False

    def set_direction(self, new_direction: Tuple[int, int]) -> None:
        """
        Change direction unless it's directly opposite to current direction.
        """
        opposite = (-self.direction[0], -self.direction[1])
        if new_direction != opposite:
            self.direction = new_direction

    def move(self) -> None:
        """
        Move the snake one step in the current direction.
        """
        head_x, head_y = self.positions[0]
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)
        self.positions.insert(0, new_head)
        if not self.growing:
            self.positions.pop()
        else:
            self.growing = False

    def grow(self) -> None:
        """
        Grow the snake by setting a flag; the tail will not be removed on next move.
        """
        self.growing = True

    def collides_with_self(self) -> bool:
        """
        Check if the snake's head collides with its body.
        """
        head = self.positions[0]
        return head in self.positions[1:]

    def collides_with_wall(self) -> bool:
        """
        Check if the snake's head collides with the boundaries of the grid.
        """
        head_x, head_y = self.positions[0]
        return not (0 <= head_x < GRID_WIDTH and 0 <= head_y < GRID_HEIGHT)

# ----------------------------------------------------------------------
# Food class
# ----------------------------------------------------------------------
class Food:
    """
    Represents the food item in the game.
    """
    def __init__(self, snake: Snake):
        self.position: Tuple[int, int] = get_random_food_position(snake.positions)

    def respawn(self, snake: Snake) -> None:
        self.position = get_random_food_position(snake.positions)

# ----------------------------------------------------------------------
# Game class (only used when running the script)
# ----------------------------------------------------------------------
class Game:
    """
    Handles the game loop and rendering using pygame.
    This class is only instantiated when the script is run directly.
    """
    def __init__(self):
        import pygame  # Imported lazily to avoid dependency during tests
        self.pygame = pygame
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Snake")
        self.clock = pygame.time.Clock()
        self.snake = Snake(init_position=(GRID_WIDTH // 2, GRID_HEIGHT // 2))
        self.food = Food(self.snake)
        self.score: int = 0
        self.font = pygame.font.SysFont(None, 36)

    def draw_grid(self) -> None:
        for x in range(0, SCREEN_WIDTH, BLOCK_SIZE):
            self.pygame.draw.line(self.screen, (40, 40, 40), (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, BLOCK_SIZE):
            self.pygame.draw.line(self