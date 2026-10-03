import random
import sys
import pygame

# ---------- constants ----------
WIDTH, HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = WIDTH // GRID_SIZE
GRID_HEIGHT = HEIGHT // GRID_SIZE
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

# ---------- snake ----------
class Snake:
    def __init__(self):
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = RIGHT
        self.growing = False

    def head_position(self):
        return self.positions[0]

    def turn(self, dir):
        """Change direction unless it's directly opposite."""
        opposite = (-self.direction[0], -self.direction[1])
        if dir != opposite:
            self.direction = dir

    def move(self):
        cur = self.head_position()
        x, y = self.direction
        new = ((cur[0] + x) % GRID_WIDTH, (cur[1] + y) % GRID_HEIGHT)
        if new in self.positions[2:]:
            raise RuntimeError("Snake collided with itself")
        self.positions.insert(0, new)
        if not self.growing:
            self.positions.pop()
        else:
            self.growing = False

    def grow(self):
        self.growing = True

    def draw(self, surface):
        for pos in self.positions:
            rect = pygame.Rect(pos[0]*GRID_SIZE, pos[1]*GRID_SIZE, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(surface, DARK_GREEN, rect)
            pygame.draw.rect(surface, GREEN, rect, 1)

# ---------- food ----------
class Food:
    def __init__(self, snake):
        self.position = self._random_position(snake)

    def _random_position(self, snake):
        while True:
            pos = (random.randint(0, GRID_WIDTH-1), random.randint(0, GRID_HEIGHT-1))
            if pos not in snake.positions:
                return pos

    def draw(self, surface):
        rect = pygame.Rect(self.position[0]*GRID_SIZE, self.position[1]*GRID_SIZE, GRID_SIZE, GRID_SIZE)
        pygame.draw.rect(surface, RED, rect)
        pygame.draw.rect(surface, WHITE, rect, 1)

# ---------- game ----------
class Game:
    def __init__(self):
        self.snake = Snake()
        self.food = Food(self.snake)
        self.score = 0
        self.clock = pygame.time.Clock()
        self.running = True

    def process_events(self):
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

    def update(self):
        try:
            self.snake.move()
        except RuntimeError:
            self.running = False
            return
        if self.snake.head_position() == self.food.position:
            self.snake.grow()
            self.score += 1
            self.food = Food(self.snake)

    def render(self, surface):
        surface.fill(BLACK)
        self.snake.draw(surface)
        self.food.draw(surface)
        font = pygame.font.SysFont('Arial', 18)
        score_surf = font.render(f"Score: {self.score}", True, WHITE)
        surface.blit(score_surf, (5, 5))
        pygame.display.flip()

    def run(self):
        pygame.init()
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Snake")
        while self.running:
            self.process_events()
            self.update()
            self.render(screen)
            self.clock.tick(FPS)
        pygame.quit()
        sys.exit()

# ---------- entry point ----------
if __name__ == "__main__":
    game = Game()
    game.run()