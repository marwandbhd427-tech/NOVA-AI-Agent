import sys
from game import Game


def main() -> None:
    """
    Entry point for the Snake game.

    The function creates a Game instance and starts the main loop.
    It is guarded by a try/except block so that a KeyboardInterrupt
    (Ctrl+C) terminates the program gracefully.
    """
    game = Game()
    try:
        game.run()
    except KeyboardInterrupt:
        print("\nGame interrupted by user. Exiting...")


if __name__ == "__main__":
    main()