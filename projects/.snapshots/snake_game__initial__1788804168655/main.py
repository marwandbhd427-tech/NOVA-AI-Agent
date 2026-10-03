import random
import sys
import time

# ---------- Constants ----------
GRID_WIDTH = 20
GRID_HEIGHT = 20
CELL_SIZE = 20  # pixel size, used only if rendering
INITIAL_SNAKE_LENGTH = 3
SNAKE_COLOR = (0, 255, 0)
FOOD_COLOR = (255, 0, 0)
BG_COLOR = (0, 0, 0)
DIRECTIONS = {
    "UP": (0, -1),
    "DOWN": (0, 1),
    "LEFT": (-1, 0),
    "RIGHT": (1, 0),
}
OPPOSITE_DIRECTIONS = {
    "UP": "DOWN",
    "DOWN": "UP",
    "LEFT": "RIGHT",
    "RIGHT": "LEFT",
}


# ---------- Snake ----------
class Snake:
    """
    Represents the snake in the game.
    """

    def __init__(self, start_pos=None, length=INITIAL_SNAKE_LENGTH):
        if start_pos is None:
            start_pos = (GRID_WIDTH // 2, GRID_HEIGHT // 2)
        self.body = [start_pos]
        self.direction = "RIGHT"
        self.grow_pending = 0
        # initialize body
        for _ in range(1, length):
            self.move()  # use initial direction to build the snake

    def set_direction(self, new_dir):
        """
        Change direction if not opposite to current.
        """
        if new_dir not in DIRECTIONS:
            return
        if OPPOSITE_DIRECTIONS[new_dir] == self.direction:
            return
        self.direction = new_dir

    def move(self):
        """
        Move snake one step in current direction.
        """
        head_x, head_y = self.body[0]
        delta_x, delta_y = DIRECTIONS[self.direction]
        new_head = ((head_x + delta_x) % GRID_WIDTH, (head_y + delta_y) % GRID_HEIGHT)
        self.body.insert(0, new_head)
        if self.grow_pending:
            self.grow_pending -= 1
        else:
            self.body.pop()

    def grow(self, amount=1):
        """
        Grow snake by amount cells.
        """
        self.grow_pending += amount

    def get_head(self):
        return self.body[0]

    def collides_with_self(self):
        """
        Check if head collides with body.
        """
        return self.get_head() in self.body[1:]


# ---------- Food ----------
class Food:
    """
    Represents the food item on the grid.
    """

    def __init__(self, snake_body):
        self.position = None
        self.spawn(snake_body)

    def spawn(self, snake_body):
        """
        Place food at random location not occupied by snake.
        """
        available = [
            (x, y)
            for x in range(GRID_WIDTH)
            for y in range(GRID_HEIGHT)
            if (x, y) not in snake_body
        ]
        if not available:
            self.position = None
            return
        self.position = random.choice(available)


# ---------- Game ----------
class Game:
    """
    Encapsulates game state and logic.
    """

    def __init__(self):
        self.snake = Snake()
        self.food = Food(self.snake.body)
        self.score = 0
        self.is_over = False

    def update(self):
        """
        Update game state: move snake, handle food consumption, check collisions.
        """
        if self.is_over:
            return
        self.snake.move()
        if self.snake.get_head() == self.food.position:
            self.snake.grow()
            self.score += 1
            self.food.spawn(self.snake.body)
        if self.snake.collides_with_self():
            self.is_over = True

    def get_state(self):
        """
        Return a snapshot of the current game state.
        """
        return {
            "snake": list(self.snake.body),
            "food": self.food.position,
            "score": self.score,
            "is_over": self.is_over,
        }


# ---------- Optional Rendering ----------
try:
    import pygame
except ImportError:
    pygame = None

def run_pygame():
    if pygame is None:
        raise RuntimeError("pygame is required for rendering.")
    pygame.init()
    screen = pygame.display.set_mode((GRID_WIDTH * CELL_SIZE, GRID_HEIGHT * CELL_SIZE))
    pygame.display.set_caption("Snake")
    clock = pygame.time.Clock()
    game = Game()
    font = pygame.font.SysFont(None, 24)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    game.snake.set_direction("UP")
                elif event.key == pygame.K_DOWN:
                    game.snake.set_direction("DOWN")
                elif event.key == pygame.K_LEFT:
                    game.snake.set_direction("LEFT")
                elif event.key == pygame.K_RIGHT:
                    game.snake.set_direction("RIGHT")

        game.update()
        screen.fill(BG_COLOR)

        # Draw food
        if game.food.position:
            fx, fy = game.food.position
            pygame.draw.rect(
                screen,
                FOOD_COLOR,
                pygame.Rect(fx * CELL_SIZE, fy * CELL_SIZE, CELL_SIZE, CELL_SIZE),
            )

        # Draw snake
        for x, y in game.snake.body:
            pygame.draw.rect(
                screen,
                SNAKE_COLOR,
                pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE),
            )

        # Draw score
        score_surf = font.render(f"Score: {game.score}", True, (255, 255, 255))
        screen.blit(score_surf, (5, 5))

        if game.is_over:
            over_surf = font.render("Game Over", True, (255, 0, 0))
            screen.blit(over_surf, (GRID_WIDTH * CELL_SIZE // 2 - 40, GRID_HEIGHT * CELL_SIZE // 2))
            pygame.display.flip()
            time.sleep(2)
            pygame.quit()
            sys.exit()

        pygame.display.flip()
        clock.tick(10)  # 10 frames per second


# ---------- Entry Point ----------
if __name__ == "__main__":
    # Start the game only if pygame is available and user explicitly wants to play.
    # For automated tests, this block will not be executed.
    if len(sys.argv) > 1 and sys.argv[1] == "play":
        run_pygame()
    else:
        print("Run with 'python main.py play' to start the game.")
        print("This script is designed for unit testing logic without launching the GUI.")