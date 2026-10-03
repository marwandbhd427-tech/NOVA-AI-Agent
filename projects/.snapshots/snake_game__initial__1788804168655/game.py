import random
from dataclasses import dataclass, field
from typing import List, Tuple, Optional

# Basic constants for the game logic
BLOCK_SIZE = 20
GRID_WIDTH = 30
GRID_HEIGHT = 20
INITIAL_SNAKE_LENGTH = 3
FOOD_TYPES = ["normal", "bonus"]

# Directions represented as (dx, dy)
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)


@dataclass
class Snake:
    """Represents the snake's state."""
    body: List[Tuple[int, int]] = field(default_factory=list)
    direction: Tuple[int, int] = RIGHT
    grow_pending: int = 0

    def __post_init__(self):
        if not self.body:
            # Start in the middle of the grid
            start_x = GRID_WIDTH // 2
            start_y = GRID_HEIGHT // 2
            self.body = [(start_x - i, start_y) for i in range(INITIAL_SNAKE_LENGTH)]

    def set_direction(self, new_direction: Tuple[int, int]):
        """Change direction if it is not directly opposite."""
        opposite = (-self.direction[0], -self.direction[1])
        if new_direction != opposite:
            self.direction = new_direction

    def move(self):
        """Move the snake forward, handling growth."""
        head_x, head_y = self.body[0]
        dx, dy = self.direction
        new_head = ((head_x + dx) % GRID_WIDTH, (head_y + dy) % GRID_HEIGHT)
        self.body.insert(0, new_head)
        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            self.body.pop()

    def grow(self, amount: int = 1):
        """Queue growth for the next moves."""
        self.grow_pending += amount

    def collision_with_self(self) -> bool:
        """Check if the snake collides with itself."""
        return self.body[0] in self.body[1:]

    def collision_with_point(self, point: Tuple[int, int]) -> bool:
        """Check if the snake's head collides with a specific point."""
        return self.body[0] == point


@dataclass
class Food:
    """Represents a food item."""
    position: Tuple[int, int] = (0, 0)
    type: str = "normal"

    def spawn(self, occupied: List[Tuple[int, int]]):
        """Spawn food at a random unoccupied position."""
        available = [
            (x, y)
            for x in range(GRID_WIDTH)
            for y in range(GRID_HEIGHT)
            if (x, y) not in occupied
        ]
        if not available:
            return
        self.position = random.choice(available)
        self.type = random.choices(FOOD_TYPES, weights=[0.9, 0.1])[0]


@dataclass
class GameState:
    """Encapsulates the entire game state."""
    snake: Snake = field(default_factory=Snake)
    food: Food = field(default_factory=Food)
    score: int = 0
    game_over: bool = False
    paused: bool = False

    def __post_init__(self):
        self.food.spawn(self.snake.body)

    def update(self):
        """Advance the game state by one tick."""
        if self.game_over or self.paused:
            return
        self.snake.move()
        if self.snake.collision_with_self():
            self.game_over = True
            return
        if self.snake.collision_with_point(self.food.position):
            if self.food.type == "normal":
                self.score += 1
                self.snake.grow()
            else:  # bonus food
                self.score += 5
                self.snake.grow(3)
            self.food.spawn(self.snake.body)

    def toggle_pause(self):
        self.paused = not self.paused

    def reset(self):
        self.snake = Snake()
        self.food = Food()
        self.score = 0
        self.game_over = False
        self.paused = False
        self.food.spawn(self.snake.body)


def main():
    """Entry point for running the game with a simple Pygame interface."""
    try:
        import pygame
    except ImportError:
        print("Pygame is required to run the graphical interface.")
        return

    pygame.init()
    screen = pygame.display.set_mode((GRID_WIDTH * BLOCK_SIZE, GRID_HEIGHT * BLOCK_SIZE))
    pygame.display.set_caption("Snake")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)

    state = GameState()

    direction_map = {
        pygame.K_UP: UP,
        pygame.K_DOWN: DOWN,
        pygame.K_LEFT: LEFT,
        pygame.K_RIGHT: RIGHT,
    }

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key in direction_map:
                    state.snake.set_direction(direction_map[event.key])
                elif event.key == pygame.K_p:
                    state.toggle_pause()
                elif event.key == pygame.K_r:
                    state.reset()

        state.update()

        screen.fill((0, 0, 0))

        # Draw food
        fx, fy = state.food.position
        pygame.draw.rect(
            screen,
            (255, 0, 0) if state.food.type == "normal" else (0, 255, 0),
            pygame.Rect(fx * BLOCK_SIZE, fy * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE),
        )

        # Draw snake
        for x, y in state.snake.body:
            pygame.draw.rect(
                screen,
                (0, 255, 255),
                pygame.Rect(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE),
            )

        # Draw score
        score_surf = font.render(f"Score: {state.score}", True, (255, 255, 255))
        screen.blit(score_surf, (5, 5))

        if state.game_over:
            over_surf = font.render("Game Over! Press R to restart.", True, (255, 0, 0))
            screen.blit(over_surf, (10, GRID_HEIGHT * BLOCK_SIZE // 2))

        pygame.display.flip()
        clock.tick(10)


if __name__ == "__main__":
    main()