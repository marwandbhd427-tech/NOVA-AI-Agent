import random
import sys
from dataclasses import dataclass, field
from typing import List, Tuple, Optional

# Optional pygame import – used only when running the GUI.
try:
    import pygame  # type: ignore
except Exception:
    pygame = None


# ---------- Constants ----------
GRID_SIZE = 20          # Size of each grid cell in pixels (used only for rendering)
WINDOW_WIDTH = 600      # Width of the game window (in pixels)
WINDOW_HEIGHT = 400     # Height of the game window (in pixels)
GRID_WIDTH = WINDOW_WIDTH // GRID_SIZE
GRID_HEIGHT = WINDOW_HEIGHT // GRID_SIZE

# Movement directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
OPPOSITE = {UP: DOWN, DOWN: UP, LEFT: RIGHT, RIGHT: LEFT}


# ---------- Data Classes ----------
@dataclass
class Snake:
    body: List[Tuple[int, int]] = field(default_factory=lambda: [(GRID_WIDTH // 2, GRID_HEIGHT // 2)])
    direction: Tuple[int, int] = RIGHT
    grow: bool = False

    def move(self) -> None:
        """Move the snake in the current direction."""
        new_head = (self.body[0][0] + self.direction[0],
                    self.body[0][1] + self.direction[1])
        self.body.insert(0, new_head)
        if not self.grow:
            self.body.pop()
        else:
            self.grow = False

    def change_direction(self, new_dir: Tuple[int, int]) -> None:
        """Change direction if not opposite to current direction."""
        if new_dir != OPPOSITE.get(self.direction):
            self.direction = new_dir

    def collides_with_self(self) -> bool:
        """Return True if the snake collides with itself."""
        return self.body[0] in self.body[1:]

    def collides_with_wall(self) -> bool:
        """Return True if the snake collides with the walls."""
        x, y = self.body[0]
        return not (0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT)


@dataclass
class Food:
    position: Tuple[int, int] = (0, 0)

    def spawn(self, snake_body: List[Tuple[int, int]]) -> None:
        """Spawn food at a random position not occupied by the snake."""
        empty_cells = [(x, y) for x in range(GRID_WIDTH) for y in range(GRID_HEIGHT)
                       if (x, y) not in snake_body]
        if not empty_cells:
            raise RuntimeError("No space left to spawn food.")
        self.position = random.choice(empty_cells)


@dataclass
class Game:
    snake: Snake = field(default_factory=Snake)
    food: Food = field(default_factory=Food)
    score: int = 0
    game_over: bool = False

    def __post_init__(self):
        self.food.spawn(self.snake.body)

    def update(self) -> None:
        """Advance the game state by one tick."""
        if self.game_over:
            return

        self.snake.move()

        if self.snake.collides_with_wall() or self.snake.collides_with_self():
            self.game_over = True
            return

        if self.snake.body[0] == self.food.position:
            self.score += 1
            self.snake.grow = True
            self.food.spawn(self.snake.body)

    def get_state(self) -> dict:
        """Return a snapshot of the game state."""
        return {
            "snake_body": self.snake.body.copy(),
            "snake_direction": self.snake.direction,
            "food_position": self.food.position,
            "score": self.score,
            "game_over": self.game_over,
        }


# ---------- GUI (Pygame) ----------
def run_gui() -> None:
    if pygame is None:
        print("Pygame is not installed. Cannot run GUI.", file=sys.stderr)
        return

    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Snake")
    clock = pygame.time.Clock()
    game = Game()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    game.snake.change_direction(UP)
                elif event.key == pygame.K_DOWN:
                    game.snake.change_direction(DOWN)
                elif event.key == pygame.K_LEFT:
                    game.snake.change_direction(LEFT)
                elif event.key == pygame.K_RIGHT:
                    game.snake.change_direction(RIGHT)

        game.update()

        screen.fill((0, 0, 0))
        # Draw snake
        for x, y in game.snake.body:
            rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(screen, (0, 255, 0), rect)
        # Draw food
        fx, fy = game.food.position
        food_rect = pygame.Rect(fx * GRID_SIZE, fy * GRID_SIZE, GRID_SIZE, GRID_SIZE)
        pygame.draw.rect(screen, (255, 0, 0), food_rect)

        # Draw score
        font = pygame.font.SysFont(None, 24)
        score_surf = font.render(f"Score: {game.score}", True, (255, 255, 255))
        screen.blit(score_surf, (5, 5))

        if game.game_over:
            over_surf = font.render("Game Over!", True, (255, 0, 0))
            screen.blit(over_surf, (WINDOW_WIDTH // 2 - over_surf.get_width() // 2,
                                    WINDOW_HEIGHT // 2 - over_surf.get_height() // 2))

        pygame.display.flip()
        clock.tick(10)  # 10 frames per second


# ---------- Entry Point ----------
if __name__ == "__main__" and pygame is not None:
    run_gui()
elif __name__ == "__main__":
    print("Pygame not available; running in headless mode. Use 'python main.py' with pygame installed to play.")
    # In headless mode we simply demonstrate a single update cycle.
    game = Game()
    print("Initial state:", game.get_state())
    game.update()
    print("After one update:", game.get_state())