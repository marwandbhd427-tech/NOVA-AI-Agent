import random
from dataclasses import dataclass, field
from typing import List, Tuple, Optional

# --------------------
# Constants
# --------------------
BLOCK_SIZE = 20
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400
FPS = 10

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
DIRECTION_NAMES = {
    UP: "UP",
    DOWN: "DOWN",
    LEFT: "LEFT",
    RIGHT: "RIGHT",
}

# --------------------
# Core classes
# --------------------
@dataclass
class Snake:
    body: List[Tuple[int, int]] = field(default_factory=lambda: [(5, 5), (4, 5), (3, 5)])
    direction: Tuple[int, int] = RIGHT
    _grow_pending: int = 0

    def set_direction(self, new_direction: Tuple[int, int]) -> None:
        """Change direction unless it's directly opposite."""
        opposite = (-self.direction[0], -self.direction[1])
        if new_direction != opposite:
            self.direction = new_direction

    def move(self) -> None:
        """Move the snake one step in the current direction."""
        new_head = (self.body[0][0] + self.direction[0],
                    self.body[0][1] + self.direction[1])
        self.body.insert(0, new_head)
        if self._grow_pending > 0:
            self._grow_pending -= 1
        else:
            self.body.pop()

    def grow(self, segments: int = 1) -> None:
        """Grow the snake by a number of segments."""
        self._grow_pending += segments

    def collides_with_self(self) -> bool:
        """Check if the snake collides with itself."""
        head = self.body[0]
        return head in self.body[1:]

    def collides_with_wall(self) -> bool:
        """Check if the snake collides with the screen boundaries."""
        head = self.body[0]
        x, y = head
        return not (0 <= x < SCREEN_WIDTH // BLOCK_SIZE and
                    0 <= y < SCREEN_HEIGHT // BLOCK_SIZE)

@dataclass
class Food:
    position: Tuple[int, int] = field(default_factory=lambda: (0, 0))

    def spawn(self, snake_body: List[Tuple[int, int]]) -> None:
        """Spawn food at a random position not occupied by the snake."""
        max_x = SCREEN_WIDTH // BLOCK_SIZE
        max_y = SCREEN_HEIGHT // BLOCK_SIZE
        while True:
            x = random.randint(0, max_x - 1)
            y = random.randint(0, max_y - 1)
            if (x, y) not in snake_body:
                self.position = (x, y)
                break

@dataclass
class Game:
    snake: Snake = field(default_factory=Snake)
    food: Food = field(default_factory=Food)
    score: int = 0
    _game_over: bool = False

    def __post_init__(self):
        self.food.spawn(self.snake.body)

    def update(self) -> None:
        """Advance the game state by one tick."""
        if self._game_over:
            return

        self.snake.move()

        # Check collisions
        if self.snake.collides_with_wall() or self.snake.collides_with_self():
            self._game_over = True
            return

        # Check food consumption
        if self.snake.body[0] == self.food.position:
            self.snake.grow()
            self.score += 1
            self.food.spawn(self.snake.body)

    def is_game_over(self) -> bool:
        return self._game_over

    def get_state(self) -> dict:
        """Return a snapshot of the current game state."""
        return {
            "snake_body": list(self.snake.body),
            "snake_direction": DIRECTION_NAMES[self.snake.direction],
            "food_position": self.food.position,
            "score": self.score,
            "game_over": self._game_over,
        }

# --------------------
# Optional Pygame UI
# --------------------
def run_pygame_game() -> None:
    """Run the game using pygame if it is available."""
    try:
        import pygame
    except ImportError:
        print("pygame is not installed. Install it to play the game.")
        return

    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Snake Game")
    clock = pygame.time.Clock()

    game = Game()

    while not game.is_game_over():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game._game_over = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    game.snake.set_direction(UP)
                elif event.key == pygame.K_DOWN:
                    game.snake.set_direction(DOWN)
                elif event.key == pygame.K_LEFT:
                    game.snake.set_direction(LEFT)
                elif event.key == pygame.K_RIGHT:
                    game.snake.set_direction(RIGHT)

        game.update()

        # Drawing
        screen.fill((0, 0, 0))
        # Draw food
        fx, fy = game.food.position
        pygame.draw.rect(screen, (255, 0, 0),
                         pygame.Rect(fx * BLOCK_SIZE, fy * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
        # Draw snake
        for i, (x, y) in enumerate(game.snake.body):
            color = (0, 255, 0) if i == 0 else (0, 200, 0)
            pygame.draw.rect(screen, color,
                             pygame.Rect(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))

        # Draw score
        font = pygame.font.SysFont(None, 24)
        score_surf = font.render(f"Score: {game.score}", True, (255, 255, 255))
        screen.blit(score_surf, (5, 5))

        pygame