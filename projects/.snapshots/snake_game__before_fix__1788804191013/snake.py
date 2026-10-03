import pygame
import random
import sys

# Game constants
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
FPS = 10

# Colors
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 155, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)


class Snake:
    """Represents the snake in the game."""

    def __init__(self, initial_position=None):
        if initial_position is None:
            initial_position = (GRID_WIDTH // 2, GRID_HEIGHT // 2)
        self.positions = [initial_position]
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
        self.growing = 0

    def head_position(self):
        return self.positions[0]

    def turn(self, dir):
        """Change direction unless it's directly opposite."""
        if (
            (dir[0] * -1, dir[1] * -1) != self.direction
            and len(self.positions) > 1
        ):
            self.direction = dir

    def move(self):
        """Move snake forward in current direction."""
        cur = self.head_position()
        x, y = cur
        dx, dy = self.direction
        new = ((x + dx) % GRID_WIDTH, (y + dy) % GRID_HEIGHT)
        if self.growing:
            self.positions.insert(0, new)
            self.growing -= 1
        else:
            self.positions = [new] + self.positions[:-1]

    def grow(self, amount=1):
        """Grow the snake by amount."""
        self.growing += amount

    def collision_with_self(self):
        """Check if snake collides with itself."""
        return self.head_position() in self.positions[1:]

    def draw(self, surface):
        for pos in self.positions:
            rect = pygame.Rect(
                pos[0] * GRID_SIZE,
                pos[1] * GRID_SIZE,
                GRID_SIZE,
                GRID_SIZE,
            )
            pygame.draw.rect(surface, DARK_GREEN, rect)
            pygame.draw.rect(surface, GREEN, rect, 1)


class Food:
    """Represents food that appears on the grid."""

    def __init__(self, snake_positions):
        self.position = self._random_position(snake_positions)

    def _random_position(self, snake_positions):
        positions = [
            (x, y)
            for x in range(GRID_WIDTH)
            for y in range(GRID_HEIGHT)
            if (x, y) not in snake_positions
        ]
        return random.choice(positions)

    def spawn(self, snake_positions):
        self.position = self._random_position(snake_positions)

    def draw(self, surface):
        rect = pygame.Rect(
            self.position[0] * GRID_SIZE,
            self.position[1] * GRID_SIZE,
            GRID_SIZE,
            GRID_SIZE,
        )
        pygame.draw.rect(surface, RED, rect)
        pygame.draw.rect(surface, WHITE, rect, 1)


class Game:
    """Encapsulates the game logic and state."""

    def __init__(self):
        self.snake = Snake()
        self.food = Food(self.snake.positions)
        self.score = 0
        self.clock = pygame.time.Clock()
        self.running = True

    def update(self):
        """Update game state."""
        self.snake.move()
        if self.snake.head_position() == self.food.position:
            self.snake.grow()
            self.score += 1
            self.food.spawn(self.snake.positions)

        if self.snake.collision_with_self():
            self.running = False

    def render(self, surface):
        surface.fill(BLACK)
        self.food.draw(surface)
        self.snake.draw(surface)
        # Draw score
        font = pygame.font.SysFont(None, 24)
        text = font.render(f"Score: {self.score}", True, WHITE)
        surface.blit(text, (5, 5))

    def run(self):
        """Main loop."""
        while self.running:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.snake.turn(UP)
                    elif event.key == pygame.K_DOWN:
                        self.snake.turn(DOWN)
                    elif event.key == pygame.K_LEFT:
                        self.snake.turn(LEFT)
                    elif event.key == pygame.K_RIGHT:
                        self.snake.turn(RIGHT)

            self.update()
            self.render(self.screen)
            pygame.display.flip()

        self.game_over()

    def game_over(self):
        """Handle game over state."""
        font = pygame.font.SysFont(None, 48)
        text = font.render("Game Over", True, RED)
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(text, rect)
        pygame.display.flip()
        pygame.time.delay(2000)
        pygame.quit()
        sys.exit()


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Snake")
    game = Game()
    game.screen = screen
    game.run()


if __name__ == "__main__":
    main()