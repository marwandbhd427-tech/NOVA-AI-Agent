import random
from dataclasses import dataclass, field
from typing import List, Tuple, Optional

# Basic constants – kept inside the file so tests can import without external dependencies
GRID_SIZE = 20          # Size of one grid cell in pixels (used only by the optional GUI)
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 400
INITIAL_SNAKE_LENGTH = 3
SNAKE_COLOR = (0, 255, 0)
FOOD_COLOR = (255, 0, 0)
BACKGROUND_COLOR = (0, 0, 0)
FPS = 10

# Type alias for clarity
Position = Tuple[int, int]


@dataclass
class Snake:
    """Represents the snake."""
    segments: List[Position] = field(default_factory=list)
    direction: Position = (1, 0)  # Initially moving right
    grow_pending: int = 0

    def __post_init__(self):
        if not self.segments:
            # Create an initial snake in the middle of the grid
            mid_x = WINDOW_WIDTH // (2 * GRID_SIZE)
            mid_y = WINDOW_HEIGHT // (2 * GRID_SIZE)
            self.segments = [(mid_x - i, mid_y) for i in range(INITIAL_SNAKE_LENGTH)]

    def set_direction(self, new_dir: Position):
        """Change direction if not directly opposite."""
        opposite = (-self.direction[0], -self.direction[1])
        if new_dir != opposite:
            self.direction = new_dir

    def move(self):
        """Move the snake by adding a new head in the current direction."""
        head_x, head_y = self.segments[0]
        dir_x, dir_y = self.direction
        new_head = (head_x + dir_x, head_y + dir_y)
        self.segments.insert(0, new_head)
        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            self.segments.pop()  # Remove tail

    def grow(self, amount: int = 1):
        """Increase the length of the snake by the specified amount."""
        self.grow_pending += amount

    def collides_with_self(self) -> bool:
        """Check if the snake collides with itself."""
        return self.segments[0] in self.segments[1:]

    def collides_with_wall(self) -> bool:
        """Check if the snake collides with the game boundaries."""
        head_x, head_y = self.segments[0]
        max_x = WINDOW_WIDTH // GRID_SIZE - 1
        max_y = WINDOW_HEIGHT // GRID_SIZE - 1
        return not (0 <= head_x <= max_x and 0 <= head_y <= max_y)


@dataclass
class Food:
    """Represents a food item."""
    position: Position

    @staticmethod
    def spawn(snake_segments: List[Position]) -> 'Food':
        """Generate food at a random location not occupied by the snake."""
        max_x = WINDOW_WIDTH // GRID_SIZE
        max_y = WINDOW_HEIGHT // GRID_SIZE
        while True:
            pos = (random.randint(0, max_x - 1), random.randint(0, max_y - 1))
            if pos not in snake_segments:
                return Food(pos)


@dataclass
class GameState:
    """Encapsulates the overall game state."""
    snake: Snake = field(default_factory=Snake)
    food: Food = field(init=False)
    score: int = 0
    game_over: bool = False

    def __post_init__(self):
        self.food = Food.spawn(self.snake.segments)

    def update(self):
        """Advance the game by one tick."""
        if self.game_over:
            return

        self.snake.move()

        # Check for collisions
        if self.snake.collides_with_wall() or self.snake.collides_with_self():
            self.game_over = True
            return

        # Check for food consumption
        if self.snake.segments[0] == self.food.position:
            self.snake.grow()
            self.score += 1
            self.food = Food.spawn(self.snake.segments)

    def reset(self):
        """Reset the game to its initial state."""
        self.snake = Snake()
        self.score = 0
        self.game_over = False
        self.food = Food.spawn(self.snake.segments)


# Optional minimal GUI using pygame – guarded so that importing this module does not require pygame
def _run_gui():
    try:
        import pygame
    except ImportError:
        print("Pygame is not installed. The game can only be run in console mode.")
        return

    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()
    pygame.display.set_caption("Snake")

    state = GameState()

    direction_keys = {
        pygame.K_UP: (0, -1),
        pygame.K_DOWN: (0, 1),
        pygame.K_LEFT: (-1, 0),
        pygame.K_RIGHT: (1, 0),
    }

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                if event.key in direction_keys:
                    state.snake.set_direction(direction_keys[event.key])
                elif event.key == pygame.K_r and state.game_over:
                    state.reset()

        if not state.game_over:
            state.update()

        screen.fill(BACKGROUND_COLOR)

        # Draw food
        fx, fy = state.food.position
        pygame.draw.rect(
            screen,
            FOOD_COLOR,
            pygame.Rect(fx * GRID_SIZE, fy * GRID_SIZE, GRID_SIZE, GRID_SIZE),
        )

        # Draw snake
        for sx, sy in state.snake.segments:
            pygame.draw.rect(
                screen,
                SNAKE_COLOR,
                pygame.Rect(sx * GRID_SIZE, sy * GRID_SIZE, GRID_SIZE, GRID_SIZE),
            )

        # Draw score
        font = pygame.font.SysFont(None, 36)
        score_surf = font.render(f"Score: {state.score}", True, (255, 255, 255))
        screen.blit(score_surf, (10, 10))

        if state.game_over:
            over_surf = font.render("Game Over! Press R to restart.", True, (255, 0, 0))
            screen.blit(over_surf, (WINDOW_WIDTH // 4, WINDOW_HEIGHT // 2))

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    _run_gui()