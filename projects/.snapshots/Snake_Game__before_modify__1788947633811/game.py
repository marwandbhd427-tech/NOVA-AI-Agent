import curses
import time
from snake import Snake
from food import Food
from constants import WIDTH, HEIGHT, DELAY

class Store:
    def __init__(self):
        self.items = {}

    def add_item(self, name, quantity=1):
        self.items[name] = self.items.get(name, 0) + quantity

    def get_items(self):
        return self.items.copy()

    def __repr__(self):
        return f"Store(items={self.items})"

def display_store(stdscr, store):
    stdscr.clear()
    stdscr.addstr(0, 0, "Store")
    items = store.get_items()
    if items:
        for idx, (name, qty) in enumerate(items.items(), start=1):
            stdscr.addstr(idx, 0, f"{name}: {qty}")
    else:
        stdscr.addstr(1, 0, "Store is empty.")
    stdscr.addstr(HEIGHT + 2, 0, "Press any key to return.")
    stdscr.refresh()
    stdscr.getch()

def draw(stdscr, snake, food):
    stdscr.clear()
    # Draw borders
    for x in range(WIDTH + 2):
        stdscr.addch(0, x, '#')
        stdscr.addch(HEIGHT + 1, x, '#')
    for y in range(1, HEIGHT + 1):
        stdscr.addch(y, 0, '#')
        stdscr.addch(y, WIDTH + 1, '#')

    # Draw food
    fx, fy = food.position
    stdscr.addch(fy + 1, fx + 1, '*')

    # Draw snake
    for idx, (x, y) in enumerate(snake.body):
        ch = 'O' if idx == 0 else 'o'
        stdscr.addch(y + 1, x + 1, ch)

    # Draw score
    stdscr.addstr(HEIGHT + 3, 0, f"Score: {snake.score}")
    stdscr.refresh()

def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(DELAY)

    snake = Snake()
    food = Food(snake.body)
    store = Store()
    store.add_item('speed', 1)
    store.add_item('length', 2)

    while True:
        key = stdscr.getch()
        if key != -1:
            if key in [curses.KEY_UP, curses.KEY_DOWN, curses.KEY_LEFT, curses.KEY_RIGHT]:
                snake.set_direction(key)
            elif key in [ord('q'), ord('Q')]:
                break
            elif key in [ord('i'), ord('I')]:
                display_store(stdscr, store)
                continue

        snake.move()
        if snake.check_collision():
            break

        if snake.head == food.position:
            snake.grow()
            food.spawn(snake.body)

        draw(stdscr, snake, food)

    stdscr.nodelay(False)
    stdscr.addstr(HEIGHT // 2, WIDTH // 2 - 5, "Game Over!")
    stdscr.addstr(HEIGHT // 2 + 1, WIDTH // 2 - 7, f"Final Score: {snake.score}")
    stdscr.addstr(HEIGHT // 2 + 3, WIDTH // 2 - 12, "Press any key to exit.")
    stdscr.getch()

if __name__ == "__main__":
    curses.wrapper(main)