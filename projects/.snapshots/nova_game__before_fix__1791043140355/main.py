import sys
from dataclasses import dataclass
from typing import List, Tuple

# Try to import pygame, but allow the module to be imported even if pygame is not installed.
try:
    import pygame  # type: ignore
except ImportError:
    pygame = None  # type: ignore

# ------------------------------ Constants ------------------------------
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
CELL_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // CELL_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // CELL_SIZE
FPS = 10

# Colors (R, G, B)
COLOR_BG = (0, 0, 0)
COLOR_SNAKE = (0, 255, 0)
COLOR_FOOD = (255, 0, 0)
COLOR_TEXT = (255, 255, 255)

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# ------------------------------ Data Classes ------------------------------
@dataclass
class Snake:
    body: List[Tuple[int, int]]
    direction: Tuple[int, int]
    grow: bool = False

    def move(self):
        head_x, head_y = self.body[0]
        dir_x, dir_y = self.direction
        new_head = ((head_x + dir_x) % GRID_WIDTH, (head_y + dir_y) % GRID_HEIGHT)
        self.body.insert(0, new_head)
        if self.grow:
            self.grow = False
        else:
            self.body.pop()

    def change_direction(self, new_dir: Tuple[int, int]):
        # Prevent reversing
        if (new_dir[0] == -self.direction[0] and new_dir[1] == -self.direction[1]):
            return
        self.direction = new_dir

    def collides_with_self(self) -> bool:
        return self.body[0] in self.body[1:]

@dataclass
class Food:
    position: Tuple[int, int]

    @staticmethod
    def spawn(snake_body: List[Tuple[int, int]]) -> 'Food':
        import random
        while True:
            pos = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
            if pos not in snake_body:
                return Food(position=pos)

# ------------------------------ Game Logic ------------------------------
class Game:
    def __init__(self):
        self.snake = Snake(body=[(GRID_WIDTH // 2, GRID_HEIGHT // 2)], direction=RIGHT)
        self.food = Food.spawn(self.snake.body)
        self.score = 0
        self.running = True

        # Define direction mapping only if pygame is available
        if pygame:
            self.DIRECTION_MAP = {
                pygame.K_UP: UP,
                pygame.K_DOWN: DOWN,
                pygame.K_LEFT: LEFT,
                pygame.K_RIGHT: RIGHT
            }
        else:
            self.DIRECTION_MAP = {}

    def update(self):
        self.snake.move()
        if self.snake.body[0] == self.food.position:
            self.snake.grow = True
            self.score += 1
            self.food = Food.spawn(self.snake.body)
        if self.snake.collides_with_self():
            self.running = False

    def handle_input(self, event: 'pygame.event.Event'):
        if not pygame:
            return
        if event.type == pygame.KEYDOWN and event.key in self.DIRECTION_MAP:
            self.snake.change_direction(self.DIRECTION_MAP[event.key])

    def draw(self, surface: 'pygame.Surface'):
        surface.fill(COLOR_BG)
        # Draw food
        fx, fy = self.food.position
        food_rect = pygame.Rect(fx * CELL_SIZE, fy * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(surface, COLOR_FOOD, food_rect)
        # Draw snake
        for idx, (sx, sy) in enumerate(self.snake.body):
            rect = pygame.Rect(sx * CELL_SIZE, sy * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(surface, COLOR_SNAKE, rect)
        # Draw score
        font = pygame.font.SysFont(None, 36)
        score_surf = font.render(f"Score: {self.score}", True, COLOR_TEXT)
        surface.blit(score_surf, (10, 10))

    def run(self):
        if not pygame:
            raise RuntimeError("pygame is required to run the game")
        pygame.init()
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Snake")
        clock = pygame.time.Clock()
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                else:
                    self.handle_input(event)
            self.update()
            self.draw(screen)
            pygame.display.flip()
            clock.tick(FPS)
        pygame.quit()
        sys.exit()

# ------------------------------ Entry Point ------------------------------
if __name__ == "__main__":
    game = Game()
    game.run()