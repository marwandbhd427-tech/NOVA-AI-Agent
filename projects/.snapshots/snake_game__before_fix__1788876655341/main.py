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

# ---------- Game Logic ----------
class Game:
    """Core game logic without rendering."""
    def __init__(self) -> None:
        self.snake = Snake()
        self.food = Food()
        self.score = 0
        self.food.spawn(self.snake.body)

    def update(self) -> None:
        """Advance the game state by one tick."""
        self.snake.move()
        if self.snake.head() == self.food.position:
            self.score += 1
            self.snake.grow()
            self.food.spawn(self.snake.body)

    def check_collision(self) -> bool:
        """Return True if snake collides with itself."""
        return self.snake.collides_with_self()

    def get_state(self) -> dict:
        """Return a snapshot of the current game state."""
        return {
            "snake_body": list(self.snake.body),
            "food_position": self.food.position,
            "score": self.score,
        }

# ---------- Rendering (Pygame) ----------
def run() -> None:
    """Start the snake game using pygame. This function is guarded to avoid
    importing pygame when the module is imported for testing."""
    import pygame  # Import locally to avoid dependency during tests

    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Snake")
    clock = pygame.time.Clock()

    game = Game()

    running = True
    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    game.snake.turn(UP)
                elif event.key == pygame.K_DOWN:
                    game.snake.turn(DOWN)
                elif event.key == pygame.K_LEFT:
                    game.snake.turn(LEFT)
                elif event.key == pygame.K_RIGHT:
                    game.snake.turn(RIGHT)

        game.update()
        if game.check_collision():
            running = False  # End game on self-collision

        # Draw
        screen.fill((0, 0, 0))  # Black background

        # Draw food
        fx, fy = game.food.position
        pygame.draw.rect(screen, (255, 0, 0), (fx * CELL_SIZE, fy * CELL_SIZE, CELL_SIZE, CELL_SIZE))

        # Draw snake
        for x, y in game.snake.body:
            pygame.draw.rect(screen, (0, 255, 0), (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

        # Draw score
        font = pygame.font.SysFont(None, 24)
        score_surf = font.render(f"Score: {game.score}", True, (255, 255, 255))
        screen.blit(score_surf, (5, 5))

        pygame.display.flip()

    pygame.quit()
    print(f"Game over! Final score: {game.score}")

if __name__ == "__main__":
    run()