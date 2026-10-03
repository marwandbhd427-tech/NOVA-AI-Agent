import random
from dataclasses import dataclass, field
from typing import List, Tuple

# ---------- Constants ----------
CELL_SIZE = 20
GRID_WIDTH = 30   # number of cells horizontally
GRID_HEIGHT = 20  # number of cells vertically
WINDOW_WIDTH = GRID_WIDTH * CELL_SIZE
WINDOW_HEIGHT = GRID_HEIGHT * CELL_SIZE
FPS = 10

# Directions as (dx, dy)
UP: Tuple[int, int] = (0, -1)
DOWN: Tuple[int, int] = (0, 1)
LEFT: Tuple[int, int] = (-1, 0)
RIGHT: Tuple[int, int] = (1, 0)

# ---------- Data Classes ----------
@dataclass
class Snake:
    body: List[Tuple[int, int]] = field(default_factory=lambda: [(GRID_WIDTH // 2, GRID_HEIGHT // 2)])
    direction: Tuple[int, int] = RIGHT
    grow_pending: int = 0

    def turn(self, new_direction: Tuple[int, int]) -> None:
        """Change direction unless it's directly opposite to current."""
        opposite = (-self.direction[0], -self.direction[1])
        if new_direction != opposite:
            self.direction = new_direction

    def move(self) -> None:
        """Move snake one step in current direction."""
        head_x, head_y = self.body[0]
        dx, dy = self.direction
        new_head = ((head_x + dx) % GRID_WIDTH, (head_y + dy) % GRID_HEIGHT)

        # Insert new head
        self.body.insert(0, new_head)

        # Remove tail unless growing
        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            self.body.pop()

    def grow(self, amount: int = 1) -> None:
        """Set the snake to grow by a given amount."""
        self.grow_pending += amount

    def head(self) -> Tuple[int, int]:
        return self.body[0]

    def collides_with_self(self) -> bool:
        return self.head() in self.body[1:]

@dataclass
class Food:
    position: Tuple[int, int] = (0, 0)

    def spawn(self, snake_body: List[Tuple[int, int]]) -> None:
        """Place food on a random cell not occupied by the snake."""
        empty_cells = [(x, y) for x in range(GRID_WIDTH) for y in range(GRID_HEIGHT)
                       if (x, y) not in snake_body]
        if not empty_cells:
            # No space left; keep current position
            return
        self.position = random.choice(empty_cells)

# ---------- Game