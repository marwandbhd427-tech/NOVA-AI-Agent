import curses
from snake_game import SnakeGame

def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(100)

    game = SnakeGame(stdscr)
    while not game.is_over():
        key = stdscr.getch()
        game.process_input(key)
        game.update()
        game.render()
    stdscr.nodelay(False)
    stdscr.addstr(game.height // 2, game.width // 2 - 5, "GAME OVER")
    stdscr.refresh()
    stdscr.getch()

if __name__ == "__main__":
    curses.wrapper(main)