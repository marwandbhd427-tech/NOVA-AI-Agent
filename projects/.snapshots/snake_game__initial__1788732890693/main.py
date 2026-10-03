import random
import sys
from dataclasses import dataclass, field
from typing import List, Tuple, Optional

# Attempt to import pygame, but allow the module to be used without it for logic testing
try:
    import pygame
except ImportError:  # pragma: no cover
    pygame = None

# --------------------------- Constants ------------------------------------
SCREEN_WIDTH: int = 640
SCREEN_HEIGHT: int = 480
GRID_SIZE: int = 20
GRID_WIDTH: int = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT: int = SCREEN_HEIGHT // GRID_SIZE
FPS: int = 10

# --------------------------- Data Classes ----------------------------------
@dataclass
class Snake:
    """Represents the snake."""
    segments: List[Tuple[int, int]] = field(default_factory=list)
    direction: Tuple[int, int] = (1, 0)  # start moving right
    grow_pending: int = 0

    def __post_init__(self):
        if not self.segments:
            mid_x = GRID_WIDTH // 2
            mid_y = GRID_HEIGHT // 2
            self.segments = [(mid_x, mid_y), (mid_x - 1, mid_y), (mid_x - 2, mid_y)]

    def set_direction(self, new_dir: Tuple[int, int]) -> None:
        """Change direction if it's not directly opposite."""
        opposite = (-self.direction[0], -self.direction[1])
        if new_dir != opposite:
            self.direction = new_dir

    def move(self) -> None:
        """Move snake forward by one grid cell."""
        new_head = (self.segments[0][0] + self.direction[0],
                    self.segments[0][1] + self.direction[1])
        self.segments.insert(0, new_head)
        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            self.segments.pop()

    def grow(self, amount: int = 1) -> None:
        """Grow snake by specified amount."""
        self.grow_pending += amount

    def collides_with_self(self) -> bool:
        """Check if head collides with body."""
        return self.segments[0] in self.segments[1:]

    def collides_with_wall(self) -> bool:
        """Check if head collides with walls."""
        x, y = self.segments[0]
        return not (0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT)

@dataclass
class Food:
    """Represents a food item."""
    position: Tuple[int, int] = (0, 0)

    def spawn(self, snake_segments: List[Tuple[int, int]]) -> None:
        """Spawn food at a random position not occupied by the snake."""
        available = [(x, y) for x in range(GRID_WIDTH)
                     for y in range(GRID_HEIGHT)
                     if (x, y) not in snake_segments]
        if not available:
            raise RuntimeError("No space to spawn food.")
        self.position = random.choice(available)

@dataclass
class Game:
    """Game logic and state."""
    snake: Snake = field(default_factory=Snake)
    food: Food = field(default_factory=Food)
    score: int = 0
    over: bool = False
    _clock: Optional[object] = None  # pygame.time.Clock or None

    def __post_init__(self):
        self.food.spawn(self.snake.segments)

    def update(self) -> None:
        """Update game state: move snake, handle collisions."""
        if self.over:
            return
        self.snake.move()

        # Check wall collision
        if self.snake.collides_with_wall():
            self.over = True
            return

        # Check self collision
        if self.snake.collides_with_self():
            self.over = True
            return

        # Check food collision
        if self.snake.segments[0] == self.food.position:
            self.snake.grow()
            self.score += 1