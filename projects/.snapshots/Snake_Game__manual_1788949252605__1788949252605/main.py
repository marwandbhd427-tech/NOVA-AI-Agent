import sys
from game import Game
from store import Store


def main() -> None:
    """
    Entry point for the Snake game.

    The function creates a Game instance and starts the main loop.
    It is guarded by a try/except block so that a KeyboardInterrupt
    (Ctrl+C) terminates the program gracefully.
    """
    game = Game()

    # Initialize the store and display its items before the game starts.
    store = Store()
    print("\nStore initialized with the following items:")
    for item in store.list_items():
        print(f" - {item.name}: {item.description}")

    # Allow the player to purchase items before starting the game.
    # This simple prompt accepts the name of an item and attempts to buy it.
    # If the store or purchase method is not implemented, we silently ignore.
    try:
        choice = input("\nEnter the name of an item to purchase (or press Enter to skip): ").strip()
        if choice:
            try:
                store.purchase(choice)
                print(f"Purchased '{choice}'.")
            except Exception as e:
                print(f"Could not purchase '{choice}': {e}")
    except (EOFError, KeyboardInterrupt):
        # If input is interrupted, just proceed to the game.
        pass

    try:
        game.run()
    except KeyboardInterrupt:
        print("\nGame interrupted by user. Exiting...")


if __name__ == "__main__":
    main()