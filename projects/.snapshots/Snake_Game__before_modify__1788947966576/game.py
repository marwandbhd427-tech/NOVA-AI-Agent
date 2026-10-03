import curses
import time
from snake import Snake
from food import Food
from constants import WIDTH, HEIGHT, DELAY
from store import Store  # Use the comprehensive Store implementation


def display_store(stdscr, store, snake):
    """
    Display the store items and allow the player to purchase one.
    """
    stdscr.clear()
    stdscr.addstr(0, 0, "Store")
    items = store.list_items()
    if items:
        for idx, (name, details) in enumerate(items.items(), start=1):
            stdscr.addstr(idx, 0, f"{idx}. {name} - {details['description']} (Cost: {details['price']})")
        stdscr.addstr(len(items) + 2, 0, "Press the number of the item to buy, or any other key to return.")
        stdscr.refresh()
        key = stdscr.getch()
        # Convert key to integer index if possible
        if key in [ord(str(i)) for i in range(1, len(items) + 1)]:
            idx = int(chr(key)) - 1
            item_name = list(items.keys())[idx]
            # Attempt purchase
            success, message = store.purchase(item_name, snake)
            stdscr.clear()
            stdscr.addstr(0, 0, f"{'Success' if success else 'Failed'}: {message}")
            stdscr.addstr(2, 0, "Press any key to continue.")
            stdscr.refresh()
            stdscr.getch()
    else:
        stdscr.addstr(1, 0, "Store is empty.")
        stdscr.addstr(3, 0, "Press any key to return.")
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
    store = Store()  # Use the store defined in store.py

    while True:
        key = stdscr.getch()
        if key != -1:
            if key in [curses.KEY_UP, curses.KEY_DOWN, curses.KEY_LEFT, curses.KEY_RIGHT]:
                snake.set_direction(key)
            elif key in [ord('q'), ord('Q')]:
                break
            elif key in [ord('i'), ord('I')]:
                display_store(stdscr, store, snake)
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