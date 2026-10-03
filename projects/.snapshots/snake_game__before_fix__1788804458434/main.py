import random
import sys
from dataclasses import dataclass
from typing import List, Tuple, Optional

# Game constants
GRID_WIDTH = 20
GRID_HEIGHT = 20
CELL_SIZE = 20
WINDOW_WIDTH = GRID_WIDTH * CELL_SIZE
WINDOW_HEIGHT = GRID_HEIGHT * CELL_SIZE
FPS = 10

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

@dataclass
class Position:
    x: int
    y: int

    def __add__(self, other: Tuple[int, int]) -> "Position":
        return Position(self.x + other[0], self.y + other[1])

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Position):
            return False
        return self.x == other.x and self.y == other.y

    def in_bounds(self) -> bool:
        return 0 <= self.x < GRID_WIDTH and 0 <= self.y < GRID_HEIGHT

class Snake:
    def __init__(self, start_pos: Position):
        self.body: List[Position] = [start_pos]
        self.direction: Tuple[int, int] = RIGHT
        self.grow_pending: int = 0

    def set_direction(self, new_dir: Tuple[int, int]):
        # Prevent reverse
        opposite = (-self.direction[0], -self.direction[1])
        if new_dir != opposite:
            self.direction = new_dir

    def move(self):
        new_head = self.body[0] + self.direction
        self.body.insert(0, new_head)
        if self.grow_pending:
            self.grow_pending -= 1
        else:
            self.body.pop()

    def grow(self, amount: int = 1):
        self.grow_pending += amount

    def head(self) -> Position:
        return self.body[0]

    def collides_with_self(self) -> bool:
        return self.head() in self.body[1:]

    def collides_with_wall(self) -> bool:
        return not self.head().in_bounds()

class Food:
    def __init__(self, snake: Snake):
        self.position: Position = self._generate_position(snake)

    def _generate_position(self, snake: Snake) -> Position:
        while True:
            pos = Position(random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
            if pos not in snake.body:
                return pos

    def respawn(self, snake: Snake):
        self.position = self._generate_position(snake)

class Game:
    def __init__(self):
        self.snake = Snake(Position(GRID_WIDTH // 2, GRID_HEIGHT // 2))
        self.food = Food(self.snake)
        self.score: int = 0
        self.is_over: bool = False

    def update(self):
        if self.is_over:
            return
        self.snake.move()
        if self.snake.collides_with_self() or self.snake.collides_with_wall():
            self.is_over = True
            return
        if self.snake.head() == self.food.position:
            self.score += 1
            self.snake.grow()
            self.food.respawn(self.snake)

    def get_state(self) -> dict:
        return {
            "snake": [(p.x, p.y) for p in self.snake.body],
            "food": (self.food.position.x, self.food.position.y),
            "score": self.score,
            "is_over": self.is_over,
        }

def run_game():
    """Entry point for the playable game. Guarded to prevent accidental execution during tests."""
    try:
        import pygame
    except ImportError:
        print("Pygame is required to run the game. Install with 'pip install pygame'.")
        sys.exit(1)

    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Snake")
    clock = pygame.time.Clock()

    game = Game()

    # Key mapping
    key_to_dir = {
        pygame.K_UP: UP,
        pygame.K_DOWN: DOWN,
        pygame.K_LEFT: LEFT,
        pygame.K_RIGHT: RIGHT,
    }

    while not game.is_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.is_over = True
            elif event.type == pygame.KEYDOWN:
                if event.key in key_to_dir:
                    game.snake.set_direction(key_to_dir[event.key])

        game.update()

        # Draw
        screen.fill((0, 0, 0))
        # Draw food
        pygame.draw.rect(
            screen,
            (255, 0, 0),
            pygame.Rect(
                game.food.position.x * CELL_SIZE,
                game.food.position.y * CELL_SIZE,
                CELL_SIZE,
                CELL_SIZE,
            ),
        )
        # Draw snake
        for segment in game.snake.body:
            pygame.draw.rect(
                screen,
                (0, 255, 0),
                pygame.Rect(
                    segment.x * CELL_SIZE,
                    segment.y * CELL_SIZE,
                    CELL_SIZE,
                    CELL_SIZE,
                ),
            )
        pygame.display.flip()
        clock.tick(FPS)

    # Game over display
    font = pygame.font.SysFont(None, 48)
    text = font.render(f"Game Over! Score: {game.score}", True, (255, 255, 255))
    text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
    screen.blit(text, text_rect)
    pygame.display.flip()
    pygame.time.wait(2000)
    pygame.quit()

if __name__ == "__main__":
    run_game()