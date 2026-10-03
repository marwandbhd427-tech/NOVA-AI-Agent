import game

def main() -> None:
    """
    Entry point for the Snake game.
    This function starts the game loop by delegating to the `run` function
    defined in the `game` module. The actual game logic and rendering
    are handled there, keeping this file lightweight and test‑friendly.
    """
    game.run()

if __name__ == "__main__":
    main()