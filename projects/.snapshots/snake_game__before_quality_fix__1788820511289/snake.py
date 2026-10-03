def main() -> None:
    """
    Entry point for the Snake game.
    Initializes the Game instance and starts the main loop.
    """
    # Import inside the function to avoid importing pygame during module import
    from game import Game

    game = Game()
    try:
        game.run()
    except KeyboardInterrupt:
        # Graceful exit on Ctrl+C
        print("\nGame interrupted by user. Exiting...")

if __name__ == "__main__":
    main()