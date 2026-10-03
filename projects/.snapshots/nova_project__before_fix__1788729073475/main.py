import sys

def main() -> None:
    try:
        import pygame
        from game import SnakeGame
    except ImportError as exc:
        raise ImportError(
            "The 'pygame' package is required to run the Snake game. "
            "Please install it before executing the program."
        ) from exc

    pygame.init()
    screen = pygame.display.set_mode((400, 400))
    pygame.display.set_caption("Snake")
    clock = pygame.time.Clock()
    game = SnakeGame(screen, clock)
    game.run()

if __name__ == "__main__":
    main()