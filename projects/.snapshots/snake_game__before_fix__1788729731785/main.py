def run() -> None:
    """
    Start the Snake game. Imports pygame and the game module lazily to avoid
    pulling in optional graphical dependencies during unit tests.
    """
    import pygame  # Imported lazily to keep import lightweight
    from game import Game

    game = Game()
    game.run()


if __name__ == "__main__":
    run()