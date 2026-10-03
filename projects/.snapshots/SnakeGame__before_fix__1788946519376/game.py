import curses
import random
import time
from dataclasses import dataclass, field
from typing import List, Tuple

# Direction constants as (dy, dx)
UP: Tuple[int, int] = (-1, 0)
DOWN: Tuple[int, int] = (1, 0)
LEFT: Tuple[int, int] = (0, -1)
RIGHT: Tuple[int, int] = (0, 1)

# Key mapping from curses to directions
KEY_MAP = {
    curses.KEY_UP: UP,
    curses.KEY_DOWN: DOWN,
    curses.KEY_LEFT: LEFT,
    curses.KEY_RIGHT: RIGHT,
    ord('w'): UP,
    ord('s'): DOWN,
    ord('a'): LEFT,
    ord('d'): RIGHT,
}

@dataclass
class Snake:
    body: List[Tuple[int, int]] = field(default_factory=list)
    direction: Tuple[int, int] = UP

    def __post_init__(self):
        if not self.body:
            # Start in the middle of a 20x20 board
            self.body = [(10, 10), (10, 9), (10, 8)]

    def move(self, grow: bool = False) -> None:
        """Move the snake in the current direction.
        If grow is True, the snake grows by not removing the tail."""
        head_y, head_x = self.body[0]
        dy, dx = self.direction
        new_head = (head_y + dy, head_x + dx)
        self.body.insert(0, new_head)
        if not grow:
            self.body.pop()

    def set_direction(self, new_direction: Tuple[int, int]) -> None:
        """Set new direction if it's not directly opposite."""
        opposite = (-self.direction[0], -self.direction[1])
        if new_direction != opposite:
            self.direction = new_direction

    def collides_with_self(self) -> bool:
        """Check if the snake's head collides with its body."""
        head = self.body[0]
        return head in self.body[1:]

    def collides_with_point(self, point: Tuple[int, int]) -> bool:
        return point in self.body

@dataclass
class Food:
    position: Tuple[int, int] = (0, 0)

    def spawn(self, board_height: int, board_width: int, snake: Snake) -> None:
        """Generate a new food position not occupied by the snake."""
        while True:
            y = random.randint(1, board_height - 2)
            x = random.randint(1, board_width - 2)
            if not snake.collides_with_point((y, x)):
                self.position = (y, x)
                break

@dataclass
class Game:
    height: int = 20
    width: int = 40
    snake: Snake = field(default_factory=Snake)
    food: Food = field(default_factory=Food)
    score: int = 0
    speed: int = 100  # milliseconds per loop

    def __post_init__(self):
        self.food.spawn(self.height, self.width, self.snake)

    def update(self, grow: bool = False) -> None:
        """Move snake, check collisions, and handle food consumption."""
        self.snake.move(grow=grow)
        # Check collision with walls
        head_y, head_x = self.snake.body[0]
        if head_y <= 0 or head_y >= self.height - 1 or head_x <= 0 or head_x >= self.width - 1:
            raise RuntimeError("Collision with wall")
        # Check self collision
        if self.snake.collides_with_self():
            raise RuntimeError("Self collision")
        # Check food
        if (head_y, head_x) == self.food.position:
            self.score += 1
            self.food.spawn(self.height, self.width, self.snake)

    def render(self, stdscr) -> None:
        """Draw the current game state to the screen."""
        stdscr.clear()
        # Draw border
        for y in range(self.height):
            for x in range(self.width):
                if y == 0 or y == self.height - 1 or x == 0 or x == self.width - 1:
                    stdscr.addch(y, x, '#')
        # Draw food
        fy, fx = self.food.position
        stdscr.addch(fy, fx, '*')
        # Draw snake
        for idx, (sy, sx) in enumerate(self.snake.body):
            char = 'O' if idx == 0 else 'o'
            stdscr.addch(sy, sx, char)
        # Draw score
        stdscr.addstr(0, 2, f" Score: {self.score} ")
        stdscr.refresh()

def run_game(stdscr):
    # Curses setup
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(100)

    game = Game()
    while True:
        try:
            key = stdscr.getch()
            if key == ord('q'):
                break
            if key in KEY_MAP:
                game.snake.set_direction(KEY_MAP[key])

            # Determine if we should grow (food eaten)
            grow = (game.snake.body[0] == game.food.position)
            game.update(grow=grow)
            game.render(stdscr)
            time.sleep(game.speed / 1000.0)
        except RuntimeError:
            # Game over
            stdscr.clear()
            msg = f"Game Over! Final Score: {game.score}"
            stdscr.addstr(game.height // 2, (game.width - len(msg)) // 2, msg)
            stdscr.refresh()
            time.sleep(2)
            break

def main():
    curses.wrapper(run_game)

if __name__ == "__main__":
    main()