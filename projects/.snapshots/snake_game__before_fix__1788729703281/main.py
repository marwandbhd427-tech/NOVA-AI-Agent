import sys

def main() -> None:
    """
    Main entry point for the Snake game.
    Initializes Pygame, creates the game instance, and runs the main loop.
    """
    # Import heavy or optional dependencies lazily to avoid import-time failures during testing.
    import pygame
    from game import Game
    from constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS

    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Snake")
    clock = pygame.time.Clock()

    game = Game(screen)

    running = True
    while running:
        dt = clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                game.handle_key(event.key)

        game.update(dt)
        game.render()
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()