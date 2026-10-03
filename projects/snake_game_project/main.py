import sys

def main():
    try:
        from snake_game import run_game
    except ImportError as e:
        print("Error importing the game module:", e)
        sys.exit(1)
    run_game()

if __name__ == "__main__":
    main()