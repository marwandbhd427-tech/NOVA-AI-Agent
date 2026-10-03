import sys
import pygame
from game import Game

def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((Game.WIDTH, Game.HEIGHT))
    pygame.display.set_caption("Snake Game")
    clock = pygame.time.Clock()
    game = Game(screen)

    while True:
        dt = clock.tick(Game.FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            game.handle_event(event)
        game.update(dt)
        game.render()