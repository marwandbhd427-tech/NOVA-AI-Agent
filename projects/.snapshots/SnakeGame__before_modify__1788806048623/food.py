import sys
from food import main as game_main

def main(stdscr):
    """
    Entry point for the Snake game when run in a terminal that supports curses.
    Delegates to the actual game logic implemented in food.main.
    """
    game_main(stdscr)

if __name__ == "__main__":
    # Import curses only when the script is executed directly.
    try:
        import curses
        curses.wrapper(main)
    except Exception as e:
        # If curses is not available or fails (e.g., on Android),
        # provide a clear error message and exit gracefully.
        print(f"Curses error: {e}", file=sys.stderr)
        sys.exit(1)