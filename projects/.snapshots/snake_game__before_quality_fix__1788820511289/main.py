import random
import sys

# Attempt to import pygame, but allow tests to run without it
try:
    import pygame
    from pygame.locals import QUIT, KEYDOWN, K_UP, K_DOWN, K_LEFT, K_RIGHT, K_ESCAPE
except Exception:
    pygame = None
    QUIT = KEYDOWN = K_UP = K_DOWN = K_LEFT = K_RIGHT = K_ESCAPE = None

# --- constants --------------------------------------------------------------
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
DARK_GREEN = (0, 155, 0)

FPS = 10

# --- helper functions --------------------------------------------------------
def random_position(exclude=None):
    """Return a random grid position not in exclude."""
    while True:
        pos = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
        if exclude and pos in exclude:
            continue
        return pos

# --- classes ---------------------------------------------------------------
class Snake:
    """Represents the snake."""
    def __init__(self, init_position=(GRID_WIDTH // 2, GRID_HEIGHT // 2)):
        self.positions = [init_position]
        self.direction = (0, -1)  # start moving up
        self.grow_pending = 0

    def move(self):
        head_x, head_y = self.positions[0]
        dir_x, dir_y = self.direction
        new_head = ((head_x + dir_x) % GRID_WIDTH, (head_y + dir_y) % GRID_HEIGHT)
        self.positions.insert(0, new_head)
        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            self.positions.pop()

    def grow(self):
        self.grow_pending += 1

    def set_direction(self, new_dir):
        # Prevent reversing into itself
        opposite = (-self.direction[0], -self.direction[1])
        if new_dir != opposite:
            self.direction = new_dir

    def collision(self):
        head = self.positions[0]
        # Self collision
        return head in self.positions[1:]

    def draw(self, surface):
        if pygame is None:
            return
        for pos in self.positions:
            rect = pygame.Rect(pos[0] * GRID_SIZE, pos[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(surface, DARK_GREEN, rect)
            pygame.draw.rect(surface, GREEN, rect, 1)

class Food:
    """Represents the food item."""
    def __init__(self, snake_positions):
        self.position = random_position(exclude=snake_positions)

    def respawn(self, snake_positions):
        self.position = random_position(exclude=snake_positions)

    def draw(self, surface):
        if pygame is None:
            return
        rect = pygame.Rect(self.position[0] * GRID_SIZE, self.position[1] * GRID_SIZE,
                           GRID_SIZE, GRID_SIZE)
        pygame.draw.rect(surface, RED, rect)
        pygame.draw.rect(surface, WHITE, rect, 1)

class Game:
    """Main game logic."""
    def __init__(self, width=SCREEN_WIDTH, height=SCREEN_HEIGHT):
        if pygame is None:
            raise RuntimeError("pygame is required to run the game.")
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Snake")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 24)

        self.snake = Snake()
        self.food = Food(self.snake.positions)
        self.score = 0
        self.running = True

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.running = False
                elif event.key == K_UP:
                    self.snake.set_direction((0, -1))
                elif event.key == K_DOWN:
                    self.snake.set_direction((0, 1))
                elif event.key == K_LEFT:
                    self.snake.set_direction((-1, 0))
                elif event.key == K_RIGHT:
                    self.snake.set_direction((1, 0))

    def update(self):
        self.snake.move()
        if self.snake.collision():
            self.running = False
            return
        if self.snake.positions[0] == self.food.position:
            self.snake.grow()
            self.score += 1
            self.food.respawn(self.snake.positions)

    def draw_grid(self):
        for x in range(0, SCREEN_WIDTH, GRID_SIZE):
            pygame.draw.line(self.screen, BLACK, (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
            pygame.draw.line(self.screen, BLACK, (0, y), (SCREEN_WIDTH, y))

    def draw(self):
        self.screen.fill(WHITE)
        self.draw_grid()
        self.snake.draw(self.screen)
        self.food.draw(self.screen)
        score_surf = self.font.render(f"Score: {self.score}", True, BLACK)
        self.screen.blit(score_surf, (5, 5))
        pygame.display.flip()

    def run(self):
        while self.running:
            self.clock.tick(FPS)
            self.handle_events()
            self.update()
            self.draw()
        self.game_over()

    def game_over(self):
        self.screen.fill(WHITE)
        over_surf = self.font.render("Game Over!", True, RED)
        score_surf = self.font.render(f"Final Score: {self.score}", True, BLACK)
        self.screen.blit(over_surf, (SCREEN_WIDTH // 2 - over_surf.get_width() // 2,
                                     SCREEN_HEIGHT // 2 - over_surf.get_height()))
        self.screen.blit(score_surf, (SCREEN_WIDTH // 2 - score_surf.get_width() // 2,
                                      SCREEN_HEIGHT // 2 + 10))
        pygame.display.flip()
        pygame.time.wait(2000)
        pygame.quit()

# --- entry point -------------------------------------------------------------
if __name__ == "__main__":
    try:
        game = Game()
        game.run()
    except RuntimeError as e:
        print(e, file=sys.stderr)
        sys.exit(1)