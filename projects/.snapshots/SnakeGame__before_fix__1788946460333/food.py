import curses
import random
import time
from dataclasses import dataclass, field
from typing import List, Tuple, Optional

# Game constants
BOARD_WIDTH = 40
BOARD_HEIGHT = 20
SNAKE_CHAR = "O"
FOOD_CHAR = "*"
EMPTY_CHAR = " "
SLEEP_TIME = 0.1  # seconds per frame

# Directions
UP = (-1, 0)
DOWN = (1, 0)
LEFT = (0, -1)
RIGHT = (0, 1)
DIRECTION_KEYS = {
    curses.KEY_UP: UP,
    curses.KEY_DOWN: DOWN,
    curses.KEY_LEFT: LEFT,
    curses.KEY_RIGHT: RIGHT,
}

@dataclass
class Food:
    position: Tuple[int, int] = field(default_factory=tuple)

    def spawn(self, snake_body: List[Tuple[int, int]]) -> None:
        """Place food at a random location not occupied by the snake."""
        while True:
            pos = (
                random.randint(1, BOARD_HEIGHT - 2),
                random.randint(1, BOARD_WIDTH - 2),
            )
            if pos not in snake_body:
                self.position = pos
                break

@dataclass
class Snake:
    body: List[Tuple[int, int]] = field(default_factory=list)
    direction: Tuple[int, int] = field(default=RIGHT)

    def __post_init__(self):
        # Start with a snake of length 3 in the middle of the board
        mid_y = BOARD_HEIGHT // 2
        mid_x = BOARD_WIDTH // 2
        self.body = [
            (mid_y, mid_x),
            (mid_y, mid_x - 1),
            (mid_y, mid_x - 2),
        ]

    def move(self, grow: bool = False) -> None:
        """Move the snake in the current direction. If grow is True, do not remove the tail."""
        head_y, head_x = self.body[0]
        delta_y, delta_x = self.direction
        new_head = (head_y + delta_y, head_x + delta_x)
        self.body.insert(0, new_head)
        if not grow:
            self.body.pop()

    def set_direction(self, new_direction: Tuple[int, int]) -> None:
        """Set new direction if it's not directly opposite to current."""
        opposite = (-self.direction[0], -self.direction[1])
        if new_direction != opposite:
            self.direction = new_direction

    def collides_with_self(self) -> bool:
        """Check if the head collides with the body."""
        return self.body[0] in self.body[1:]

    def collides_with_wall(self) -> bool:
        """Check if the head collides with the board walls."""
        head_y, head_x = self.body[0]
        return head_y <= 0 or head_y >= BOARD_HEIGHT - 1 or head_x <= 0 or head_x >= BOARD_WIDTH - 1

@dataclass
class Game:
    snake: Snake = field(default_factory=Snake)
    food: Food = field(default_factory=Food)
    score: int = 0
    over: bool = False

    def reset(self) -> None:
        self.snake = Snake()
        self.score = 0
        self.over = False
        self.food.spawn(self.snake.body)

    def update(self) -> None:
        """Update game state: move snake, handle food consumption, collisions."""
        # Determine if snake will grow
        will_grow = self.snake.body[0] == self.food.position
        self.snake.move(grow=will_grow)
        if will_grow:
            self.score += 1
            self.food.spawn(self.snake.body)
        if self.snake.collides_with_self() or self.snake.collides_with_wall():
            self.over = True

    def render(self, stdscr) -> None:
        """Render the game board to the curses window."""
        stdscr.clear()
        # Draw borders
        for x in range(BOARD_WIDTH):
            stdscr.addch(0, x, "#")
            stdscr.addch(BOARD_HEIGHT - 1, x, "#")
        for y in range(BOARD_HEIGHT):
            stdscr.addch(y, 0, "#")
            stdscr.addch(y, BOARD_WIDTH - 1, "#")
        # Draw food
        food_y, food_x = self.food.position
        stdscr.addch(food_y, food_x, FOOD_CHAR)
        # Draw snake
        for idx, (y, x) in enumerate(self.snake.body):
            char = SNAKE_CHAR if idx == 0 else SNAKE_CHAR.lower()
            stdscr.addch(y, x, char)
        # Draw score
        stdscr.addstr(BOARD_HEIGHT, 0, f"Score: {self.score}   ")
        stdscr.refresh()

def main(stdscr):
    # Configure curses
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(0)

    game = Game()
    game.reset()

    while not game.over:
        # Input handling
        try:
            key = stdscr.getch()
        except Exception:
            key = -1
        if key in DIRECTION_KEYS:
            game.snake.set_direction(DIRECTION_KEYS[key])
        elif key == ord('q'):
            break

        game.update()
        game.render(stdscr)
        time.sleep(SLEEP_TIME)

    # Game over message
    stdscr.nodelay(False)
    stdscr.clear()
    stdscr.addstr(BOARD_HEIGHT // 2, BOARD_WIDTH // 2 - 5, "Game Over!")
    stdscr.addstr(BOARD_HEIGHT // 2 + 1, BOARD_WIDTH // 2 - 7, f"Final Score: {game.score}")
    stdscr.addstr(BOARD_HEIGHT // 2 + 3, BOARD_WIDTH // 2 - 12, "Press any key to exit.")
    stdscr.refresh()
    stdscr.getch()

if __name__ == "__main__":
    curses.wrapper(main)