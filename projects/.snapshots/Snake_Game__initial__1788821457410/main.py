import curses
import random
import time
from dataclasses import dataclass, field
from typing import List, Tuple

# Constants
WIDTH = 40
HEIGHT = 20
SNAKE_CHAR = "O"
FOOD_CHAR = "*"
EMPTY_CHAR = " "
INITIAL_SPEED = 0.15  # seconds between moves
SPEED_INCREMENT = 0.01
MAX_SPEED = 0.05


@dataclass
class Point:
    y: int
    x: int


@dataclass
class Snake:
    body: List[Point] = field(default_factory=list)
    direction: Tuple[int, int] = (0, 1)  # start moving right

    def __post_init__(self):
        if not self.body:
            mid = Point(y=HEIGHT // 2, x=WIDTH // 2)
            self.body.append(mid)

    def move(self, grow: bool = False):
        head = self.body[0]
        dy, dx = self.direction
        new_head = Point(y=head.y + dy, x=head.x + dx)
        self.body.insert(0, new_head)
        if not grow:
            self.body.pop()

    def set_direction(self, key):
        if key == curses.KEY_UP and self.direction != (1, 0):
            self.direction = (-1, 0)
        elif key == curses.KEY_DOWN and self.direction != (-1, 0):
            self.direction = (1, 0)
        elif key == curses.KEY_LEFT and self.direction != (0, 1):
            self.direction = (0, -1)
        elif key == curses.KEY_RIGHT and self.direction != (0, -1):
            self.direction = (0, 1)

    def collides_with_self(self) -> bool:
        head = self.body[0]
        return any(segment.y == head.y and segment.x == head.x for segment in self.body[1:])

    def collides_with_wall(self) -> bool:
        head = self.body[0]
        return not (0 < head.y < HEIGHT - 1 and 0 < head.x < WIDTH - 1)


@dataclass
class Food:
    position: Point = field(default_factory=lambda: Point(0, 0))

    def spawn(self, snake_body: List[Point]):
        while True:
            y = random.randint(1, HEIGHT - 2)
            x = random.randint(1, WIDTH - 2)
            if all(segment.y != y or segment.x != x for segment in snake_body):
                self.position = Point(y, x)
                break


class Game:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.snake = Snake()
        self.food = Food()
        self.score = 0
        self.speed = INITIAL_SPEED
        self.game_over = False

    def init_screen(self):
        curses.curs_set(0)
        self.stdscr.nodelay(True)
        self.stdscr.keypad(True)
        self.stdscr.clear()
        self.draw_borders()

    def draw_borders(self):
        for x in range(WIDTH):
            self.stdscr.addch(0, x, "#")
            self.stdscr.addch(HEIGHT - 1, x, "#")
        for y in range(HEIGHT):
            self.stdscr.addch(y, 0, "#")
            self.stdscr.addch(y, WIDTH - 1, "#")

    def render(self):
        self.stdscr.clear()
        self.draw_borders()
        # Draw food
        self.stdscr.addch(self.food.position.y, self.food.position.x, FOOD_CHAR)
        # Draw snake
        for idx, segment in enumerate(self.snake.body):
            ch = SNAKE_CHAR if idx == 0 else SNAKE_CHAR.lower()
            self.stdscr.addch(segment.y, segment.x, ch)
        # Draw score
        score_text = f"Score: {self.score}"
        self.stdscr.addstr(HEIGHT, 0, score_text)
        self.stdscr.refresh()

    def update(self, key):
        self.snake.set_direction(key)
        self.snake.move(grow=False)

        if self.snake.collides_with_wall() or self.snake.collides_with_self():
            self.game_over = True
            return

        head = self.snake.body[0]
        if head.y == self.food.position.y and head.x == self.food.position.x:
            self.score += 1
            self.snake.move(grow=True)  # grow on next move
            self.food.spawn(self.snake.body)
            # Slow down speed (i.e., increase speed)
            self.speed = max(MAX_SPEED, self.speed - SPEED_INCREMENT)

    def run(self):
        self.init_screen()
        self.food.spawn(self.snake.body)
        while not self.game_over:
            key = self.stdscr.getch()
            self.update(key)
            self.render()
            time.sleep(self.speed)
        self.show_game_over()

    def show_game_over(self):
        msg = "Game Over! Press any key to exit."
        self.stdscr.addstr(HEIGHT // 2, (WIDTH - len(msg)) // 2, msg)
        self.stdscr.nodelay(False)
        self.stdscr.getch()


def main(stdscr):
    game = Game(stdscr)
    game.run()


if __name__ == "__main__":
    curses.wrapper(main)