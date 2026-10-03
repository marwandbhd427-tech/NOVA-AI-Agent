import random
from dataclasses import dataclass, field
from typing import List, Tuple, Set

# ----------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------
BLOCK_SIZE: int = 20          # Size of one block in pixels (used only for GUI)
GRID_WIDTH: int = 20          # Number of blocks horizontally
GRID_HEIGHT: int = 20         # Number of blocks vertically

# Directions represented as (dx, dy)
UP: Tuple[int, int] = (0, -1)
DOWN: Tuple[int, int] = (0, 1)
LEFT: Tuple[int, int] = (-1, 0)
RIGHT: Tuple[int, int] = (1, 0)
DIRECTIONS = {UP, DOWN, LEFT, RIGHT}


# ----------------------------------------------------------------------
# Utility functions
# ----------------------------------------------------------------------
def random_position(exclude: Set[Tuple[int, int]]) -> Tuple[int, int]:
    """Return a random grid position not in `exclude`."""
    while True:
        pos = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
        if pos not in exclude:
            return pos


# ----------------------------------------------------------------------
# Core game entities
# ----------------------------------------------------------------------
@dataclass
class Snake:
    """Represents the snake."""
    body: List[Tuple[int, int]] = field(default_factory=lambda: [(GRID_WIDTH // 2, GRID_HEIGHT // 2)])
    direction: Tuple[int, int] = RIGHT
    grow_pending: bool = False

    def set_direction(self, new_dir: Tuple[int, int]) -> None:
        """Change direction if it's not directly opposite to current."""
        if (new_dir[0] == -self.direction[0] and new_dir[1] == -self.direction[1]) or new_dir not in DIRECTIONS:
            return
        self.direction = new_dir

    def move(self) -> None:
        """Move snake one step in current direction."""
        head_x, head_y = self.body[0]
        dx, dy = self.direction
        new_head = ((head_x + dx) % GRID_WIDTH, (head_y + dy) % GRID_HEIGHT)
        self.body.insert(0, new_head)
        if self.grow_pending:
            self.grow_pending = False
        else:
            self.body.pop()

    def grow(self) -> None:
        """Mark that the snake should grow on next move."""
        self.grow_pending = True

    def collides_with_self(self) -> bool:
        """Check if head collides with body."""
        return self.body[0] in self.body[1:]

    def collides_with_wall(self) -> bool:
        """In this implementation, the snake wraps around the grid, so this always returns False."""
        return False


@dataclass
class Food:
    """Represents the food."""
    position: Tuple[int, int] = field(default_factory=lambda: (0, 0))

    def spawn(self, occupied: Set[Tuple[int, int]]) -> None:
        """Spawn food at a random position not occupied by the snake."""
        self.position = random_position(occupied)


# ----------------------------------------------------------------------
# Game logic
# ----------------------------------------------------------------------
@dataclass
class Game:
    """Encapsulates the game state."""
    snake: Snake = field(default_factory=Snake)
    food: Food = field(default_factory=Food)
    score: int = 0
    game_over: bool = False

    def __post_init__(self) -> None:
        """Spawn the first food."""
        self.food.spawn(set(self.snake.body))

    def update(self) -> None:
        """Advance the game by one step."""
        if self.game_over:
            return
        self.snake.move()
        if self.snake.collides_with_self():
            self.game_over = True
            return
        if self.snake.body[0] == self.food.position:
            self.snake.grow()
            self.score += 1
            self.food.spawn(set(self.snake.body))

    def change_direction(self, new_dir: Tuple[int, int]) -> None:
        """Change snake direction."""
        self.snake.set_direction(new_dir)

    def reset(self) -> None:
        """Reset the game to initial state."""
        self.snake = Snake()
        self.food = Food()
        self.score = 0
        self.game_over = False
        self.food.spawn(set(self.snake.body))


# ----------------------------------------------------------------------
# GUI entry point (optional)
# ----------------------------------------------------------------------
def _run_gui() -> None:
    """Simple pygame-based GUI. Import only if pygame is available."""
    try:
        import pygame
    except ImportError:
        print("pygame not installed; GUI cannot be started.")
        return

    pygame.init()
    screen = pygame.display.set_mode((GRID_WIDTH * BLOCK_SIZE, GRID_HEIGHT * BLOCK_SIZE))
    clock = pygame.time.Clock()
    game = Game()

    direction_map = {
        pygame.K_UP: UP,
        pygame.K_DOWN: DOWN,
        pygame.K_LEFT: LEFT,
        pygame.K_RIGHT: RIGHT,
    }

    while not game.game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.game_over = True
            elif event.type == pygame.KEYDOWN:
                if event.key in direction_map:
                    game.change_direction(direction_map[event.key])

        game.update()

        screen.fill((0, 0, 0))
        # Draw food
        fx, fy = game.food.position
        pygame.draw.rect(screen, (255, 0, 0), (fx * BLOCK_SIZE, fy * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
        # Draw snake
        for sx, sy in game.snake.body:
            pygame.draw.rect(screen, (0, 255, 0), (sx * BLOCK_SIZE, sy * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))

        pygame.display.flip()
        clock.tick(10)

    pygame.quit()
    print(f"Game over! Score: {game.score}")


# ----------------------------------------------------------------------
# Main guard
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Start GUI only if pygame is available; otherwise, run a simple text demo.
    try:
        _run_gui()
    except Exception as exc: