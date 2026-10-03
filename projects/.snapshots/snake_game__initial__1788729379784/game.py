import pygame
from dataclasses import dataclass, field
from typing import List, Tuple, Set

# ------------------------------------------------------------------
# Constants
# ------------------------------------------------------------------
SCREEN_WIDTH: int = 600
SCREEN_HEIGHT: int = 400
CELL_SIZE: int = 20
GRID_WIDTH: int = SCREEN_WIDTH // CELL_SIZE
GRID_HEIGHT: int = SCREEN_HEIGHT // CELL_SIZE

# Directions
UP: Tuple[int, int] = (0, -1)
DOWN: Tuple[int, int] = (0, 1)
LEFT: Tuple[int, int] = (-1, 0)
RIGHT: Tuple[int, int] = (1, 0)
DIRECTION_KEYS = {
    pygame.K_UP: UP,
    pygame.K_DOWN: DOWN,
    pygame.K_LEFT: LEFT,
    pygame.K_RIGHT: RIGHT,
}

# Colors
BG_COLOR: Tuple[int, int, int] = (0, 0, 0)
SNAKE_COLOR: Tuple[int, int, int] = (0, 255, 0)
FOOD_COLOR: Tuple[int, int, int] = (255, 0, 0)
TEXT_COLOR: Tuple[int, int, int] = (255, 255, 255)

# ------------------------------------------------------------------
# Utility functions
# ------------------------------------------------------------------
def random_position(exclude: Set[Tuple[int, int]]) -> Tuple[int, int]:
    import random
    while True:
        pos = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
        if pos not in exclude:
            return pos

# ------------------------------------------------------------------
# Snake
# ------------------------------------------------------------------
@dataclass
class Snake:
    body: List[Tuple[int, int]] = field(default_factory=lambda: [(GRID_WIDTH // 2, GRID_HEIGHT // 2)])
    direction: Tuple[int, int] = RIGHT
    grow_pending: int = 0

    def change_direction(self, new_dir: Tuple[int, int]) -> None:
        """Change direction if not directly opposite."""
        opposite = (-self.direction[0], -self.direction[1])
        if new_dir != opposite:
            self.direction = new_dir

    def move(self) -> None:
        """Move snake forward, handling growth."""
        new_head = (self.body[0][0] + self.direction[0], self.body[0][1] + self.direction[1])
        self.body.insert(0, new_head)
        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            self.body.pop()

    def grow(self, amount: int = 1) -> None:
        """Set growth pending."""
        self.grow_pending += amount

    def collides_with_self(self) -> bool:
        """Check if head collides with body."""
        head = self.body[0]
        return head in self.body[1:]

    def collides_with_wall(self) -> bool:
        """Check if head is outside grid."""
        x, y = self.body[0]
        return not (0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT)

# ------------------------------------------------------------------
# Food
# ------------------------------------------------------------------
@dataclass
class Food:
    position: Tuple[int, int] = field(default_factory=lambda: (0, 0))

    def spawn(self, occupied: Set[Tuple[int, int]]) -> None:
        self.position = random_position(occupied)

# ------------------------------------------------------------------
# Game logic
# ------------------------------------------------------------------
@dataclass
class Game:
    snake: Snake = field(default_factory=Snake)
    food: Food = field(default_factory=Food)
    score: int = 0
    game_over: bool = False
    tick_rate: int = 10  # frames per second

    def reset(self) -> None:
        self.snake = Snake()
        self.score = 0
        self.game_over = False
        self.food.spawn(set(self.snake.body))

    def update(self) -> None:
        """Advance game state by one tick."""
        if self.game_over:
            return

        self.snake.move()

        if self.snake.collides_with_wall() or self.snake.collides_with_self():
            self.game_over = True
            return

        if self.snake.body[0] == self.food.position:
            self.snake.grow()
            self.score += 1
            self.food.spawn(set(self.snake.body))

    def render(self, surface: pygame.Surface) -> None:
        """Render the current game state onto the given surface."""
        surface.fill(BG_COLOR)

        # Draw food
        fx, fy = self.food.position
        food_rect = pygame.Rect(fx * CELL_SIZE, fy * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(surface, FOOD_COLOR, food_rect)

        # Draw snake
        for x, y in self.snake.body:
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(surface, SNAKE_COLOR, rect)

        # Draw score
        font = pygame.font.SysFont(None, 24)
        score_surf = font.render(f"Score: {self.score}", True, TEXT_COLOR)
        surface.blit(score_surf, (10, 10))

        if self.game_over:
            over_surf = font.render("Game Over", True, TEXT_COLOR)
            surface.blit(over_surf, (SCREEN_WIDTH // 2 - over_surf.get_width() // 2,
                                     SCREEN_HEIGHT // 2 - over_surf.get_height() // 2))

# ------------------------------------------------------------------
# Main entry point
# ------------------------------------------------------------------
def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Snake")
    clock = pygame.time.Clock()

    game = Game()
    game.reset()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key in DIRECTION_KEYS:
                    game.snake.change_direction(DIRECTION_KEYS[event.key])
                elif event.key == pygame.K_r and game.game_over:
                    game.reset()

        game.update()
        game.render(screen)
        pygame.display.flip()
        clock.tick(game.tick_rate)

if __name__ == "__main__":
    main()