import random
import time
import curses
from dataclasses import dataclass
from typing import List, Tuple, Optional

# ---------- Core Data Structures ----------

@dataclass(frozen=True)
class Position:
    y: int
    x: int

class Snake:
    """Represents the snake."""
    def __init__(self, init_pos: Position, init_dir: Tuple[int, int]):
        self.body: List[Position] = [init_pos]
        self.direction: Tuple[int, int] = init_dir
        self.grow_pending: int = 0

    def set_direction(self, new_dir: Tuple[int, int]) -> None:
        # Prevent reverse direction
        if (self.direction[0] * -1, self.direction[1] * -1) != new_dir:
            self.direction = new_dir

    def move(self) -> None:
        head = self.body[0]
        new_head = Position(head.y + self.direction[0], head.x + self.direction[1])
        self.body.insert(0, new_head)
        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            self.body.pop()

    def grow(self, amount: int = 1) -> None:
        self.grow_pending += amount

    def collides_with_self(self) -> bool:
        return self.body[0] in self.body[1:]

    def collides_with(self, pos: Position) -> bool:
        return pos in self.body

class Food:
    """Represents the food item."""
    def __init__(self, position: Position):
        self.position = position

# ---------- Game Logic ----------

class Game:
    """Encapsulates the game state and logic."""
    def __init__(self, height: int = 20, width: int = 40):
        self.height = height
        self.width = width
        init_pos = Position(height // 2, width // 2)
        self.snake = Snake(init_pos, (0, 1))  # moving right initially
        self.food = self.spawn_food()
        self.score = 0
        self.game_over = False

    def spawn_food(self) -> Food:
        while True:
            pos = Position(
                random.randint(1, self.height - 2),
                random.randint(1, self.width - 2)
            )
            if not self.snake.collides_with(pos):
                return Food(pos)

    def update(self) -> None:
        """Advance the game state by one tick."""
        if self.game_over:
            return
        self.snake.move()

        # Check wall collision
        head = self.snake.body[0]
        if head.y <= 0 or head.y >= self.height - 1 or head.x <= 0 or head.x >= self.width - 1:
            self.game_over = True
            return

        # Check self collision
        if self.snake.collides_with_self():
            self.game_over = True
            return

        # Check food collision
        if head == self.food.position:
            self.snake.grow()
            self.score += 1
            self.food = self.spawn_food()

    def render(self, stdscr) -> None:
        """Render the current state to the curses window."""
        stdscr.clear()
        # Draw borders
        for x in range(self.width):
            stdscr.addch(0, x, '#')
            stdscr.addch(self.height - 1, x, '#')
        for y in range(self.height):
            stdscr.addch(y, 0, '#')
            stdscr.addch(y, self.width - 1, '#')

        # Draw food
        stdscr.addch(self.food.position.y, self.food.position.x, '*')

        # Draw snake
        for idx, segment in enumerate(self.snake.body):
            char = 'O' if idx == 0 else 'o'
            stdscr.addch(segment.y, segment.x, char)

        # Draw score
        stdscr.addstr(self.height, 0, f"Score: {self.score}  Press 'q' to quit")
        stdscr.refresh()

    def run(self, stdscr) -> None:
        """Main game loop."""
        curses.curs_set(0)
        stdscr.nodelay(True)
        stdscr.timeout(100)  # milliseconds

        while not self.game_over:
            key = stdscr.getch()
            if key != -1:
                self.handle_input(key)

            self.update()
            self.render(stdscr)
            time.sleep(0.1)

        # Game over screen
        stdscr.nodelay(False)
        stdscr.addstr(self.height // 2, self.width // 2 - 5, "GAME OVER")
        stdscr.addstr(self.height // 2 + 1, self.width // 2 - 8, f"Final Score: {self.score}")
        stdscr.addstr(self.height // 2 + 3, self.width // 2 - 12, "Press any key to exit.")
        stdscr.refresh()
        stdscr.getch()

    def handle_input(self, key: int) -> None:
        """Translate key presses to snake direction changes."""
        if key in (curses.KEY_UP, ord('w')):
            self.snake.set_direction((-1, 0))
        elif key in (curses.KEY_DOWN, ord('s')):
            self.snake.set_direction((1, 0))
        elif key in (curses.KEY_LEFT, ord('a')):
            self.snake.set_direction((0, -1))
        elif key in (curses.KEY_RIGHT, ord('d')):
            self.snake.set_direction((0, 1))
        elif key in (ord('q'), ord('Q')):
            self.game_over = True

# ---------- Entry Point ----------

def main() -> None:
    curses.wrapper(lambda stdscr: Game().run(stdscr))

if __name__ == "__main__":
    main()