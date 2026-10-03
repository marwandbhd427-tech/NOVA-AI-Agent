import pygame
from game import SnakeGame

def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((400, 400))
    pygame.display.set_caption("Snake")
    clock = pygame.time.Clock()
    game = SnakeGame(screen, clock)
    game.run()

if __name__ == "__main__":
    main()