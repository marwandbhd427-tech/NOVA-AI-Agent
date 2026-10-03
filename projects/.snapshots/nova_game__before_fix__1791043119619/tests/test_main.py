import pygame
from constants import BLOCK_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT, GRID_WIDTH, GRID_HEIGHT
from snake import Snake
from food import Food


class Game:
    """
    Handles the game loop and rendering using pygame.
    This class is only instantiated when the script is run directly.
    """

    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Snake")
        self.clock = pygame.time.Clock()
        self.snake = Snake(init_position=(GRID_WIDTH // 2, GRID_HEIGHT // 2))
        self.food = Food(self.snake)
        self.score: int = 0
        self.font = pygame.font.SysFont(None, 36)

    def draw_grid(self) -> None:
        """
        Draw the grid lines on the game screen.
        """
        for x in range(0, SCREEN_WIDTH, BLOCK_SIZE):
            pygame.draw.line(
                self.screen,
                (40, 40, 40),
                (x, 0),
                (x, SCREEN_HEIGHT),
            )
        for y in range(0, SCREEN_HEIGHT, BLOCK_SIZE):
            pygame.draw.line(
                self.screen,
                (40, 40, 40),
                (0, y),
                (SCREEN_WIDTH, y),
            )

    def draw(self) -> None:
        """
        Render the snake, food, grid, and score on the screen.
        """
        self.screen.fill((0, 0, 0))
        self.draw_grid()

        # Draw snake
        for pos in self.snake.positions:
            rect = pygame.Rect(
                pos[0] * BLOCK_SIZE,
                pos[1] * BLOCK_SIZE,
                BLOCK_SIZE,
                BLOCK_SIZE,
            )
            pygame.draw.rect(self.screen, (0, 255, 0), rect)

        # Draw food
        food_rect = pygame.Rect(
            self.food.position[0] * BLOCK_SIZE,
            self.food.position[1] * BLOCK_SIZE,
            BLOCK_SIZE,
            BLOCK_SIZE,
        )
        pygame.draw.rect(self.screen, (255, 0, 0), food_rect)

        # Draw score
        score_text = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (10, 10))

        pygame.display.flip()

    def run(self) -> None:
        """
        Main game loop.
        """
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.snake.set_direction((0, -1))
                    elif event.key == pygame.K_DOWN:
                        self.snake.set_direction((0, 1))
                    elif event.key == pygame.K_LEFT:
                        self.snake.set_direction((-1, 0))
                    elif event.key == pygame.K_RIGHT:
                        self.snake.set_direction((1, 0))

            self.snake.move()

            if self.snake.collides_with_wall() or self.snake.collides_with_self():
                running = False

            if self.snake.positions[0] == self.food.position:
                self.snake.grow()
                self.score += 1
                self.food.respawn(self.snake)

            self.draw()
            self.clock.tick(10)

        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()