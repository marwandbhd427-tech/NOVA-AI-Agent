import random
from dataclasses import dataclass, field
from typing import List, Tuple, Optional

# --- Constants -------------------------------------------------------------
WIDTH: int = 640            # Window width in pixels
HEIGHT: int = 480           # Window height in pixels
CELL_SIZE: int = 20         # Size of one grid cell in pixels
GRID_WIDTH: int = WIDTH // CELL_SIZE
GRID_HEIGHT: int = HEIGHT // CELL_SIZE
INITIAL_SNAKE_LENGTH: int = 3
FPS: int = 10

# Directions represented as (dx, dy)
UP: Tuple[int, int] = (0, -1)
DOWN: Tuple[int, int] = (0, 1)
LEFT: Tuple[int, int] = (-1, 0)
RIGHT: Tuple[int, int] = (1, 0)

DIRECTION_MAP = {
    pygame.K_UP: UP,
    pygame.K_DOWN: DOWN,
    pygame.K_LEFT: LEFT,
    pygame.K_RIGHT: RIGHT,
}

# --- Helper Functions ------------------------------------------------------
def clamp_position(pos: Tuple[int, int]) -> Tuple[int, int]:
    """Clamp a position to the grid bounds."""
    x, y = pos
    x = max(0, min(GRID_WIDTH - 1, x))
    y = max(0, min(GRID_HEIGHT - 1, y))
    return x, y

# --- Snake Class ------------------------------------------------------------
@dataclass
class Snake:
    body: List[Tuple[int, int]] = field(default_factory=list)
    direction: Tuple[int, int] = RIGHT
    grow_pending: int = 0

    def __post_init__(self):
        # Ensure the snake has at least the initial length
        if not self.body:
            mid_x = GRID_WIDTH // 2
            mid_y = GRID_HEIGHT // 2
            self.body = [(mid_x - i, mid_y) for i in range(INITIAL_SNAKE_LENGTH)]

    def set_direction(self, new_dir: Tuple[int, int]):
        """Set new direction if it's not directly opposite to current."""
        opposite = (-self.direction[0], -self.direction[1])
        if new_dir != opposite:
            self.direction = new_dir

    def move(self):
        """Move snake one step in the current direction."""
        head_x, head_y = self.body[0]
        dx, dy = self.direction
        new_head = clamp_position((head_x + dx, head_y + dy))
        self.body.insert(0, new_head)
        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            self.body.pop()

    def grow(self, amount: int = 1):
        """Schedule the snake to grow by a specified amount."""
        self.grow_pending += amount

    def collision_with_self(self) -> bool:
        """Check if the snake's head collides with its body."""
        return self.body[0] in self.body[1:]

    def collision_with_wall(self) -> bool:
        """Check if the snake's head collides with the wall."""
        head_x, head_y = self.body[0]
        return not (0 <= head_x < GRID_WIDTH and 0 <= head_y < GRID_HEIGHT)

# --- Food Class -------------------------------------------------------------
@dataclass
class Food:
    position: Tuple[int, int] = (0, 0)

    def spawn(self, snake_body: List[Tuple[int, int]]):
        """Spawn food at a random location not occupied by the snake."""
        empty_cells = [
            (x, y)
            for x in range(GRID_WIDTH)
            for y in range(GRID_HEIGHT)
            if (x, y) not in snake_body
        ]
        if not empty_cells:
            self.position = None  # No space left
        else:
            self.position = random.choice(empty_cells)

# --- Game Class -------------------------------------------------------------
@dataclass
class Game:
    snake: Snake = field(default_factory=Snake)
    food: Food = field(default_factory=Food)
    score: int = 0
    running: bool = False

    def start(self):
        """Initialize game state."""
        self.snake = Snake()
        self.food.spawn(self.snake.body)
        self.score = 0
        self.running = True

    def update(self):
        """Update game state for one tick."""
        self.snake.move()
        if self.snake.collision_with_self() or self.snake.collision_with_wall():
            self.running = False
            return
        if self.snake.body[0] == self.food.position:
            self.snake.grow()
            self.score += 1
            self.food.spawn(self.snake.body)

    # The following rendering methods are only used when pygame is available.
    def render(self, screen):
        """Render the game state onto the provided Pygame surface."""
        import pygame
        screen.fill((0, 0, 0))
        # Draw snake
        for segment in self.snake.body:
            rect = pygame.Rect(segment[0] * CELL_SIZE, segment[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, (0, 255, 0), rect)
        # Draw food
        if self.food.position:
            fx, fy = self.food.position
            rect = pygame.Rect(fx * CELL_SIZE, fy * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, (255, 0, 0), rect)
        # Draw score
        font = pygame.font.SysFont(None, 24)
        text = font.render(f"Score: {self.score}", True, (255, 255, 255))
        screen.blit(text, (10, 10))
        pygame.display.flip()

#