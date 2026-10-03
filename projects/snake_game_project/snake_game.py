import curses
import time
from snake_game import SnakeGame

def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(100)

    game = SnakeGame(stdscr)

    while True:
        key = stdscr.getch()
        if key == ord('q'):
            break
        game.update(key)
        game.render()
        if game.game_over:
            break
        time.sleep(game.delay)

if __name__ == "__main__":
    curses.wrapper(main)