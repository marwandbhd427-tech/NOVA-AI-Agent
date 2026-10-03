import random
import time
import sys
import threading

# Grid dimensions
WIDTH = 20
HEIGHT = 10

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
DIRECTION_MAP = {
    "w": UP,
    "s": DOWN,
    "a": LEFT,
    "d": RIGHT,
}

class SnakeGame:
    """
    A simple snake game logic engine.
    """

    def __init__(self, width=WIDTH, height=HEIGHT):
        self.width = width
        self.height = height
        self.reset()

    def reset(self):
        """Reset the game state."""
        mid_x = self.width // 2
        mid_y = self.height // 2
        self.snake = [(mid_x, mid_y), (mid_x - 1, mid_y), (mid_x - 2, mid_y)]
        self.direction = RIGHT
        self.score = 0
        self.game_over = False
        self.spawn_food()

    def spawn_food(self):
        """Place food at a random location not occupied by the snake."""
        empty_cells = [
            (x, y)
            for x in range(self.width)
            for y in range(self.height)
            if (x, y) not in self.snake
        ]
        if not empty_cells:
            # No space left: player wins
            self.food = None
            self.game_over = True
            return
        self.food = random.choice(empty_cells)

    def change_direction(self, new_direction):
        """Change direction unless it's directly opposite."""
        if (
            (new_direction[0] == -self.direction[0])
            and (new_direction[1] == -self.direction[1])
        ):
            return  # Ignore reverse
        self.direction = new_direction

    def step(self):
        """Advance the game by one tick."""
        if self.game_over:
            return

        head_x, head_y = self.snake[0]
        delta_x, delta_y = self.direction
        new_head = (head_x + delta_x, head_y + delta_y)

        # Check wall collision
        if (
            new_head[0] < 0
            or new_head[0] >= self.width
            or new_head[1] < 0
            or new_head[1] >= self.height
        ):
            self.game_over = True
            return

        # Check self collision
        if new_head in self.snake:
            self.game_over = True
            return

        # Insert new head
        self.snake.insert(0, new_head)

        # Check food
        if new_head == self.food:
            self.score += 1
            self.spawn_food()
        else:
            # Remove tail
            self.snake.pop()

    def get_state(self):
        """Return current game state for rendering or testing."""
        return {
            "snake": list(self.snake),
            "food": self.food,
            "score": self.score,
            "game_over": self.game_over,
        }

    def __str__(self):
        """String representation of the game board."""
        board = [[" " for _ in range(self.width)] for _ in range(self.height)]
        for x, y in self.snake:
            board[y][x] = "O"
        if self.food:
            fx, fy = self.food
            board[fy][fx] = "*"
        lines = ["+" + "-" * self.width + "+"]
        for row in board:
            lines.append("|" + "".join(row) + "|")
        lines.append("+" + "-" * self.width + "+")
        lines.append(f"Score: {self.score}")
        return "\n".join(lines)

def _play_game():
    """Play the game using a simple text UI with curses if available."""
    try:
        import curses
    except ImportError:
        print("Curses module not available. Cannot run interactive mode.")
        return

    def main(stdscr):
        curses.curs_set(0)
        stdscr.nodelay(True)
        stdscr.timeout(100)

        game = SnakeGame()

        key_mapping = {
            curses.KEY_UP: UP,
            curses.KEY_DOWN: DOWN,
            curses.KEY_LEFT: LEFT,
            curses.KEY_RIGHT: RIGHT,
        }

        while not game.game_over:
            try:
                key = stdscr.getch()
            except curses.error:
                key = -1

            if key in key_mapping:
                game.change_direction(key_mapping[key])
            elif key == ord("q"):
                break

            game.step()
            stdscr.clear()
            stdscr.addstr(0, 0, str(game))
            stdscr.refresh()
            time.sleep(0.1)

        stdscr.clear