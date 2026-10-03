import pygame
from snake import Snake
from food import Food
from constants import WIDTH, HEIGHT, FPS, BG_COLOR, SNAKE_COLOR, FOOD_COLOR, SCORE_FONT, SCORE_COLOR

def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Snake Game")
    clock = pygame.time.Clock()

    snake = Snake()
    food = Food()
    score = 0

    running = True
    while running:
        clock.tick(FPS)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    snake.set_direction(0, -1)
                elif event.key == pygame.K_DOWN:
                    snake.set_direction(0, 1)
                elif event.key == pygame.K_LEFT:
                    snake.set_direction(-1, 0)
                elif event.key == pygame.K_RIGHT:
                    snake.set_direction(1, 0)

        # Update snake
        snake.move()

        # Collision with food
        if snake.head_position() == food.position:
            snake.grow()
            score += 1
            food.spawn()

        # Collision with walls or self
        if snake.check_collision():
            running = False  # End game on collision

        # Rendering
        screen.fill(BG_COLOR)
        snake.draw(screen)
        food.draw(screen)

        # Draw score
        score_surface = SCORE_FONT.render(f"Score: {score}", True, SCORE_COLOR)
        screen.blit(score_surface, (10, 10))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()