import sys
from game import Game

def main() -> None:
    """
    Entry point for the Snake game.
    Initializes the Game instance and starts the main loop.
    """
    game = Game()
    try:
        game.run()
    except KeyboardInterrupt:
        # Graceful exit on Ctrl+C
        print("\nGame interrupted by user. Exiting...")
    finally:
        sys.exit(0)

if __name__ == "__main__":
    main()