import random
import sys
from dataclasses import dataclass, field
from typing import List, Tuple, Optional

# Constants for the game (used by other modules if needed)
CELL_SIZE = 20
GRID_WIDTH = 20
GRID_HEIGHT = 20
INITIAL_SNAKE_LENGTH = 3
SNAKE_HEAD_COLOR = (0, 255, 0)
SNAKE_BODY_COLOR = (0, 200, 0)
FOOD_COLOR = (255, 0, 0)
BACKGROUND_COLOR = (0, 0, 0)

# Direction vectors
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
DIRECTION_MAP = {
    "UP": UP,
    "DOWN": DOWN,
    "LEFT": LEFT,
    "RIGHT": RIGHT,
}


@dataclass
class Snake:
    """Represents the snake in the game."""

    body: List[Tuple[int, int]] = field(default_factory=list)
    direction: Tuple[int, int] = field(default=RIGHT)
    pending_growth: int = 0

    def __post_init__(self):
        if not self.body:
            # Initialize snake in the middle of the grid
            mid_x = GRID_WIDTH // 2
            mid_y = GRID_HEIGHT // 2
            self.body = [(mid_x - i, mid_y) for i in range(INITIAL_SNAKE_LENGTH)]

    def set_direction(self, new_direction: Tuple[int, int]):
        """Set new direction if it is not directly opposite."""
        opposite = (-self.direction[0], -self.direction[1])
        if new_direction != opposite:
            self.direction = new_direction

    def move(self):
        """Move the snake by adding a new head in the current direction."""
        new_head = (
            self.body[0][0] + self.direction[0],
            self.body[0][1] + self.direction[1],
        )
        self.body.insert(0, new_head)
        if self.pending_growth > 0:
            self.pending_growth -= 1
        else:
            self.body.pop()  # Remove tail

    def grow(self, amount: int = 1):
        """Increase the snake's length by the specified amount."""
        self.pending_growth += amount

    def collides_with_self(self) -> bool:
        """Check if the snake's head collides with its body."""
        head = self.body[0]
        return head in self.body[1:]

    def collides_with_wall(self) -> bool:
        """Check if the snake's head collides with the game boundaries."""
        head_x, head_y = self.body[0]
        return not (0 <= head_x < GRID_WIDTH and 0 <= head_y < GRID_HEIGHT)


@dataclass
class Food:
    """Represents food in the game."""

    position: Tuple[int, int] = field(default_factory=lambda: (0, 0))

    def spawn(self, occupied_positions: List[Tuple[int, int]]):
        """Spawn food at a random unoccupied position."""
        available = [
            (x, y)
            for x in range(GRID_WIDTH)
            for y in range(GRID_HEIGHT)
            if (x, y) not in occupied_positions
        ]
        if not available:
            raise RuntimeError("No space left to spawn food.")
        self.position = random.choice(available)


@dataclass
class Game:
    """Main game logic."""

    snake: Snake = field(default_factory=Snake)
    food: Food = field(default_factory=Food)
    score: int = 0
    game_over: bool = False

    def __post_init__(self):
        self.food.spawn(self.snake.body)

    def update(self):
        """Update the game state: move snake, check collisions, handle food."""
        if self.game_over:
            return

        self.snake.move()

        if self.snake.collides_with_wall() or self.snake.collides_with_self():
            self.game_over = True
            return

        if self.snake.body[0] == self.food.position:
            self.snake.grow()
            self.score += 1
            self.food.spawn(self.snake.body)

    def reset(self):
        """Reset the game to its initial state."""
        self.snake = Snake()
        self.food = Food()
        self.score = 0
        self.game_over = False
        self.food.spawn(self.snake.body)


# The following section is optional and only executed when running the module directly.
# It uses pygame to create a graphical interface. Tests that import this module
# will not execute this block, ensuring no GUI windows or event loops are started.

try:
    import pygame  # type: ignore
except ImportError:  # pragma: no cover
    pygame = None  # type: ignore

if pygame:

    def run_pygame():
        pygame.init()
        screen = pygame.display.set_mode(
            (GRID_WIDTH * CELL_SIZE, GRID_HEIGHT * CELL_SIZE)
        )
        pygame.display.set_caption("Snake Game")
        clock = pygame.time.Clock()
        game = Game()

        key_to_direction = {
            pygame.K_UP: UP,
            pygame.K_DOWN: DOWN,
            pygame.K_LEFT: LEFT,
            pygame.K_RIGHT: RIGHT,
        }

        while not game.game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key in key_to_direction:
                        game.snake.set_direction(key_to_direction[event.key])

            game.update()

            screen.fill(BACKGROUND_COLOR)

            # Draw food
            fx, fy = game.food.position
            pygame.draw.rect(
                screen,
                FOOD_COLOR,
                pygame.Rect(
                    fx * CELL_SIZE,
                    fy * CELL_SIZE,
                    CELL_SIZE,
                    CELL_SIZE,
                ),
            )

            # Draw snake
            for i, (sx, sy) in enumerate(game.snake.body):
                color = SNAKE_HEAD_COLOR if i == 0 else SNAKE_BODY_COLOR
                pygame.draw.rect(
                    screen,
                    color,
                    pygame.Rect(
                        sx * CELL_SIZE,
                        sy * CELL_SIZE,
                        CELL_SIZE,
                        CELL_SIZE,
                    ),
                )

            pygame.display.flip()
            clock.tick(10)

        # Game over screen
        font = pygame.font.SysFont(None, 48)
        text = font.render(f"Game Over! Score: {game.score}", True, (255, 255, 255))
        screen.blit(text, (20, 20))
        pygame.display.flip()
        pygame.time.wait(2000)
        pygame.quit()

    if __name__ == "__main__":
        run_pygame()
else:  # pragma: no cover
    # If pygame is not available, provide a simple text-based demo
    def run_text_demo():
        game = Game()
        print("Running text demo. Press Ctrl+C to exit.")
        try:
            while not game.game_over:
                game.update()
                print(f"Score: {game.score} | Snake length: {len(game.snake.body)}")
                pygame.time.delay(500)  # Simulate a game tick
        except KeyboardInterrupt:
            print("\nDemo stopped.")

    if __name__ == "__main__":
        run_text_demo()