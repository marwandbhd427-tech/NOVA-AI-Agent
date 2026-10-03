import curses
import random
import time
from typing import List, Tuple

# Type alias for coordinates
Coord = Tuple[int, int]


class SnakeGame:
    """
    A simple Snake game logic that can be run in a terminal using curses.
    The class can be used programmatically for testing without starting the
    curses UI loop.
    """

    DIRECTIONS = {
        curses.KEY_UP: (0, -1),
        curses.KEY_DOWN: (0, 1),
        curses.KEY_LEFT: (-1, 0),
        curses.KEY_RIGHT: (1, 0),
    }

    def __init__(self, width: int = 40, height: int = 20, speed: float = 0.1):
        """
        Initialize the game state.

        :param width: Width of the game area (excluding borders)
        :param height: Height of the game area (excluding borders)
        :param speed: Delay between moves in seconds
        """
        self.width = width
        self.height = height
        self.speed = speed
        self.reset()

    def reset(self):
        """Reset the game to the initial state."""
        self.snake: List[Coord] = [(self.width // 2, self.height // 2)]
        self.direction: Coord = (1, 0)  # start moving right
        self.spawn_food()
        self.score = 0
        self.game_over = False
        self.last_move_time = time.time()

    def spawn_food(self):
        """Place food at a random location not occupied by the snake."""
        while True:
            x = random.randint(1, self.width - 2)
            y = random.randint(1, self.height - 2)
            if (x, y) not in self.snake:
                self.food = (x, y)
                break

    def change_direction(self, key: int):
        """Change snake direction based on key press."""
        if key in self.DIRECTIONS:
            new_dir = self.DIRECTIONS[key]
            # Prevent reversing into itself
            if (new_dir[0] != -self.direction[0] or new_dir[1] != -self.direction[1]):
                self.direction = new_dir

    def move(self):
        """Move the snake one step in the current direction."""
        if self.game_over:
            return

        head_x, head_y = self.snake[0]
        delta_x, delta_y = self.direction
        new_head = (head_x + delta_x, head_y + delta_y)

        # Check wall collision
        if (
            new_head[0] <= 0
            or new_head[0] >= self.width - 1
            or new_head[1] <= 0
            or new_head[1] >= self.height - 1
        ):
            self.game_over = True
            return

        # Check self collision
        if new_head in self.snake:
            self.game_over = True
            return

        # Add new head
        self.snake.insert(0, new_head)

        # Check food
        if new_head == self.food:
            self.score += 1
            self.spawn_food()
        else:
            # Remove tail
            self.snake.pop()

    def update(self):
        """Update the game state if enough time has passed."""
        now = time.time()
        if now - self.last_move_time >= self.speed:
            self.move()
            self.last_move_time = now

    def draw(self, stdscr):
        """Draw the current state to the screen."""
        stdscr.clear()
        # Draw borders
        for x in range(self.width):
            stdscr.addch(0, x, "#")
            stdscr.addch(self.height - 1, x, "#")
        for y in range(self.height):
            stdscr.addch(y, 0, "#")
            stdscr.add