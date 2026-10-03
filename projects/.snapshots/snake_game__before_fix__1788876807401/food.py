# main.py
"""
Entry point for the Snake game.

This module contains a minimal interface that can be imported
without pulling in optional dependencies such as pygame.
The actual game loop is only started when the module is
executed as a script, ensuring that importing the module
does not require pygame to be installed.
"""

def run_game() -> None:
    """
    Start the Snake game.

    The pygame library is imported lazily inside this function
    to avoid import errors when the module is imported in
    environments where pygame is not available (e.g., during
    automated testing).
    """
    import pygame  # Imported lazily to keep the module importable without pygame
    from game import Game

    # Initialize pygame and set up the display
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Snake")

    # Create and run the game
    game = Game(screen)
    game.run()


# Guarded entry point for manual execution
if __name__ == "__main__":
    run_game()