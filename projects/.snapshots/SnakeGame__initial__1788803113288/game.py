import curses
import random
from dataclasses import dataclass
from typing import List, Tuple

# ---------- Constants ----------
WIDTH = 40
HEIGHT = 20
INITIAL_SNAKE_LENGTH = 3
SNAKE_CHAR = "O"
FOOD_CHAR = "*"
EMPTY_CHAR = " "
SCORE_POS = (0, 2)

# ---------- Data Structures ----------
@dataclass(frozen=True)
class Point:
    y: int
    x: int

class Snake:
    def __init__(self, start: Point, length: int = INITIAL_SNAKE_LENGTH):
        self.segments: List[Point] = [Point(start.y, start.x - i) for i in range(length)]
        self.direction: Point = Point(0, 1)  # moving right initially
        self.grow_pending: int = 0

    def set_direction(self, new_dir: Point):
        # Prevent reversing
        if (self.direction.x, self.direction.y) == (-new_dir.x, -new_dir.y):
            return
        self.direction = new_dir

    def move(self):
        head = self.segments[0]
        new_head = Point(head.y + self.direction.y, head.x + self.direction.x)
        self.segments.insert(0, new_head)
        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            self.segments.pop()

    def grow(self, amount: int = 1):
        self.grow_pending += amount

    def head(self) -> Point:
        return self.segments[0]

    def collides_with_self(self) -> bool:
        return self.head() in self.segments[1:]

    def collides_with(self, point: Point) -> bool:
        return point in self.segments

class Food:
    def __init__(self, snake: Snake):
        self.position: Point = self._spawn(snake)

    def _spawn(self, snake: Snake) -> Point:
        while True:
            pos = Point(
                random.randint(1, HEIGHT - 2),
                random.randint(1, WIDTH - 2),
            )
            if not snake.collides_with(pos):
                return pos

    def respawn(self, snake: Snake):
        self.position = self._spawn(snake)

# ---------- Game Logic ----------
class Game:
    def __init__(self):
        self.snake = Snake(start=Point(HEIGHT // 2, WIDTH // 2))
        self.food = Food(self.snake)
        self.score = 0
        self.game_over = False

    def update(self):
        self.snake.move()
        if self.snake.head().y <= 0 or self.snake.head().y >= HEIGHT - 1:
            self.game_over = True
            return
        if self.snake.head().x <= 0 or self.snake.head().x >= WIDTH - 1:
            self.game_over = True
            return
        if self.snake.collides_with_self():
            self.game_over = True
            return
        if self.snake.head() == self.food.position:
            self.snake.grow()
            self.score += 1
            self.food.respawn(self.snake)

    def handle_input(self, key: int):
        if key == curses.KEY_UP:
            self.snake.set_direction(Point(-1, 0))
        elif key == curses.KEY_DOWN:
            self.snake.set_direction(Point(1, 0))
        elif key == curses.KEY_LEFT:
            self.snake.set_direction(Point(0, -1))
        elif key == curses.KEY_RIGHT:
            self.snake.set_direction(Point(0, 1))

    def render(self, stdscr):
        stdscr.clear()
        # Draw borders
        for x in range(WIDTH):
            stdscr.addch(0, x, "#")
            stdscr.addch(HEIGHT - 1, x, "#")
        for y in range(HEIGHT):
            stdscr.addch(y, 0, "#")
            stdscr.addch(y, WIDTH - 1, "#")
        # Draw food
        stdscr.addch(self.food.position.y, self.food.position.x, FOOD_CHAR)
        # Draw snake
        for seg in self.snake.segments:
            stdscr.addch(seg.y, seg.x, SNAKE_CHAR)
        # Draw score
        stdscr.addstr(SCORE_POS[0], SCORE_POS[1], f"Score: {self.score}")
        stdscr.refresh()

# ---------- Main Loop ----------
def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(100)

    game = Game()

    while not game.game_over:
        key = stdscr.getch()
        if key == ord('q'):
            break
        if key != -1:
            game.handle_input(key)
        game.update()
        game.render(stdscr)

    stdscr.nodelay(False)
    stdscr.addstr(HEIGHT // 2, WIDTH // 2 - 5, "Game Over!")
    stdscr.addstr(HEIGHT // 2 + 1, WIDTH // 2 - 9, f"Final Score: {game.score}")
    stdscr.addstr(HEIGHT // 2 + 3, WIDTH // 2 - 12, "Press any key to exit.")
    stdscr.getch()

if __name__ == "__main__":
    curses.wrapper(main)