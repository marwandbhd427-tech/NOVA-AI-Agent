import sys
import os
from dataclasses import dataclass
from typing import List, Tuple, Any

# ------------------------------ Constants ------------------------------
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
CELL_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // CELL_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // CELL_SIZE


def main():
    """
    Launch the Snake game.

    The function lazily imports pygame and configures a dummy video driver
    for environments that lack a display (e.g., CI/CD pipelines or
    head‑less servers). If pygame cannot be initialized, a graceful
    message is printed and the function exits without raising an exception.
    """
    # Ensure pygame prompts are suppressed
    os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
    # Use a dummy video driver if no display is available
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

    try:
        import pygame  # Lazy import to avoid optional dependency during module import
    except ImportError as e:
        print(f"Pygame is not installed: {e}")
        return

    try:
        pygame.init()
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Snake")
        clock = pygame.time.Clock()
    except pygame.error as e:
        print(f"Could not initialize pygame: {e}")
        return

    # ------------------------------ Game Loop ------------------------------
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Clear screen
        screen.fill((0, 0, 0))

        # Update display
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()