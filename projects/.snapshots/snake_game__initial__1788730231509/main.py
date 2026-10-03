import random
import sys
from dataclasses import dataclass, field
from typing import List, Tuple

# --------------------------------------------------------------------
# Constants
# --------------------------------------------------------------------
BLOCK_SIZE = 20
GRID_WIDTH = 30
GRID_HEIGHT = 20
INITIAL_SNAKE_LENGTH = 3
FOOD_COLOR = (255, 0, 0)
SNAKE_COLOR = (0, 255, 0)
BG_COLOR = (0, 0, 0)
DIRECTIONS = {
    "UP": (0, -1),
    "DOWN": (0, 1),
    "LEFT": (-1, 0),
    "RIGHT": (1, 0),
}
OPPOSITE_DIRECTION = {
    "UP": "DOWN",
    "DOWN": "UP",
    "LEFT": "RIGHT",
    "RIGHT": "LEFT",
}

# --------------------------------------------------------------------
# Data structures
# --------------------------------------------------------------------
@dataclass
class Snake:
    positions: List[Tuple[int, int]] = field(default_factory=list)
    direction: str = "RIGHT"
    grow_pending: int = 0

    def __post_init__(self):
        if not self.positions:
            start_x = GRID_WIDTH // 2
            start_y = GRID_HEIGHT // 2
            self.positions = [(start_x - i, start_y) for i in range(INITIAL_SNAKE_LENGTH)]
            self.direction = "RIGHT"

    def set_direction(self, new_direction: str):
        """Set new direction unless it's directly opposite."""
        if new_direction in DIRECTIONS and OPPOSITE_DIRECTION[new_direction] != self.direction:
            self.direction = new_direction

    def move(self):
        """Move snake in current direction."""
        dx, dy = DIRECTIONS[self.direction]
        head_x, head_y = self.positions[0]
        new_head = (head_x + dx, head_y + dy)

        # Wrap around the grid
        new_head = (new_head[0] % GRID_WIDTH, new_head[1] % GRID_HEIGHT)

        self.positions.insert(0, new_head)
        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            self.positions.pop()

    def grow(self, segments: int = 1):
        """Grow snake by a number of segments."""
        self.grow_pending += segments

    def collides_with_self(self) -> bool:
        """Check if head collides with body."""
        return self.positions[0] in self.positions[1:]

    def collides_with(self, point: Tuple[int, int]) -> bool:
        """Check if head collides with a specific point."""
        return self.positions[0] == point

@dataclass
class Food:
    position: Tuple[int, int] = (0, 0)

    def spawn(self, snake_positions: List[Tuple[int, int]]):
        """Spawn food at a random location not occupied by the snake."""
        available = [
            (x, y)
            for x in range(GRID_WIDTH)
            for y in range(GRID_HEIGHT)
            if (x, y) not in snake_positions
        ]
        if not available:
            # No space left; game will be won
            self.position = None
            return
        self.position = random.choice(available)

@dataclass
class Game:
    snake: Snake = field(default_factory=Snake)
    food: Food = field(default_factory=Food)
    score: int = 0
    game_over: bool = False

    def reset(self):
        self.snake = Snake()
        self.food.spawn(self.snake.positions)
        self.score = 0
        self.game_over = False

    def update(self):
        if self.game_over:
            return

        self.snake.move()

        # Check collision with food
        if self.snake.collides_with(self.food.position):
            self.snake.grow()
            self.score += 1
            self.food.spawn(self.snake.positions)

        # Check collision with self
        if self.snake.collides_with_self():
            self.game_over = True

# --------------------------------------------------------------------
# Main entry point for running the game with pygame
# --------------------------------------------------------------------
def main():
    try:
        import pygame
    except ImportError:
        print("pygame is required to run the game. Install it via pip install pygame.")
        sys.exit(1)

    pygame.init()
    screen = pygame.display.set_mode((GRID_WIDTH * BLOCK_SIZE, GRID_HEIGHT * BLOCK_SIZE))
    pygame.display.set_caption("Snake")
    clock = pygame.time.Clock()

    game = Game()
    game.food.spawn(game.snake.positions)

    direction_keys = {
        pygame.K_UP: "UP",
        pygame.K_DOWN: "DOWN",
        pygame.K_LEFT: "LEFT",
        pygame.K_RIGHT: "RIGHT",
    }

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key in direction_keys:
                    game.snake.set_direction(direction_keys[event.key])

        if not game.game_over:
            game.update()

        # Draw
        screen.fill(BG_COLOR)

        # Draw food
        if game.food.position:
            fx, fy = game.food.position
            pygame.draw.rect(
                screen,
                FOOD_COLOR,
                pygame.Rect(fx * BLOCK_SIZE, fy * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE),
            )

        # Draw snake
        for x, y in game.snake.positions:
            pygame.draw.rect(
                screen,
                SNAKE_COLOR,
                pygame.Rect(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE),
            )

        # Draw score
        font = pygame.font.SysFont(None, 24)
        score_surf = font.render(f"Score: {game.score}", True, (255, 255, 255))
        screen.blit(score_surf, (5, 5))

        if game.game_over:
            over_surf = font.render("Game Over! Press R to Restart", True, (255, 255, 255))
            screen.blit(over_surf, (10, GRID_HEIGHT * BLOCK_SIZE // 2))
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                game.reset()

        pygame.display.flip()
        clock.tick(10)

if __name__ == "__main__":
    main()