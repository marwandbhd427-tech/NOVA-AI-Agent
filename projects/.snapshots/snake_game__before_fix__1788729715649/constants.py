import random
import pygame

# ----------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400
BLOCK_SIZE = 20
FPS = 10

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# ----------------------------------------------------------------------
# Snake Class
# ----------------------------------------------------------------------
class Snake:
    def __init__(self, initial_position=None, initial_length=3):
        if initial_position is None:
            initial_position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.direction = LEFT
        self.positions = [(
            initial_position[0] + i * BLOCK_SIZE,
            initial_position[1]
        ) for i in range(initial_length)][::-1]
        self.growing = False

    def set_direction(self, new_direction):
        """Set the snake's moving direction, preventing 180° turns."""
        opposite = (-self.direction[0], -self.direction[1])
        if new_direction != opposite:
            self.direction = new_direction

    def move(self):
        """Move the snake one block in the current direction."""
        cur_head = self.positions[0]
        new_head = (
            cur_head[0] + self.direction[0] * BLOCK_SIZE,
            cur_head[1] + self.direction[1] * BLOCK_SIZE,
        )
        self.positions.insert(0, new_head)
        if self.growing:
            self.growing = False
        else:
            self.positions.pop()

    def grow(self):
        """Make the snake grow on the next move."""
        self.growing = True

    def head_position(self):
        return self.positions[0]

    def collides_with_self(self):
        return self.head_position() in self.positions[1:]

    def collides_with_wall(self):
        x, y = self.head_position()
        return not (0 <= x < SCREEN_WIDTH and 0 <= y < SCREEN_HEIGHT)

# ----------------------------------------------------------------------
# Food Class
# ----------------------------------------------------------------------
class Food:
    def __init__(self, snake):
        self.position = self._spawn_position(snake)

    def _spawn_position(self, snake):
        """Generate a random position not occupied by the snake."""
        positions = [
            (x, y)
            for x in range(0, SCREEN_WIDTH, BLOCK_SIZE)
            for y in range(0, SCREEN_HEIGHT, BLOCK_SIZE)
        ]
        occupied = set(snake.positions)
        available = [pos for pos in positions if pos not in occupied]
        if not available:
            return None  # No space left
        return random.choice(available)

    def respawn(self, snake):
        self.position = self._spawn_position(snake)

# ----------------------------------------------------------------------
# Game Class
# ----------------------------------------------------------------------
class Game:
    def __init__(self):
        self.snake = Snake()
        self.food = Food(self.snake)
        self.score = 0
        self.game_over = False

    def update(self):
        if self.game_over:
            return
        self.snake.move()
        if self.snake.collides_with_wall() or self.snake.collides_with_self():
            self.game_over = True
            return
        if self.snake.head_position() == self.food.position:
            self.snake.grow()
            self.score += 1
            self.food.respawn(self.snake)

    def draw(self, surface):
        surface.fill(BLACK)
        # Draw food
        if self.food.position:
            pygame.draw.rect(
                surface,
                RED,
                pygame.Rect(
                    self.food.position[0],
                    self.food.position[1],
                    BLOCK_SIZE,
                    BLOCK_SIZE,
                ),
            )
        # Draw snake
        for pos in self.snake.positions:
            pygame.draw.rect(
                surface,
                GREEN,
                pygame.Rect(pos[0], pos[1], BLOCK_SIZE, BLOCK_SIZE),
            )
        # Draw score
        font = pygame.font.SysFont(None, 24)
        score_surf = font.render(f"Score: {self.score}", True, WHITE)
        surface.blit(score_surf, (5, 5))

# ----------------------------------------------------------------------
# Main execution guard
# ----------------------------------------------------------------------
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Snake")
    clock = pygame.time.Clock()
    game = Game()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
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
        game.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)