import random
from dataclasses import dataclass
from typing import List, Tuple, Optional

@dataclass(frozen=True)
class Point:
    x: int
    y: int

class SnakeGame:
    """A simple, test‑friendly snake game logic.

    The game operates on a rectangular grid of width × height.  The snake
    starts in the middle of the grid, moving to the right, and grows each
    time it eats food.  Collisions with the walls or the snake's own
    body end the game.
    """

    # Directions as (dx, dy)
    DIR_UP: Tuple[int, int] = (0, -1)
    DIR_DOWN: Tuple[int, int] = (0, 1)
    DIR_LEFT: Tuple[int, int] = (-1, 0)
    DIR_RIGHT: Tuple[int, int] = (1, 0)

    def __init__(self, width: int, height: int, initial_length: int = 3) -> None:
        if width < 3 or height < 3:
            raise ValueError("Grid must be at least 3x3.")
        self.width = width
        self.height = height
        self.initial_length = initial_length
        self.reset()

    def reset(self) -> None:
        """Reset the game to its initial state."""
        center = Point(self.width // 2, self.height // 2)
        self.snake: List[Point] = [center]
        # Place initial segments to the left of the head
        for i in range(1, self.initial_length):
            self.snake.append(Point(center.x - i, center.y))
        self.direction = self.DIR_RIGHT
        self.spawn_food()
        self.score = 0
        self.alive = True

    def spawn_food(self) -> None:
        """Place food at a random location not occupied by the snake."""
        empty_spaces = [
            Point(x, y)
            for x in range(self.width)
            for y in range(self.height)
            if Point(x, y) not in self.snake
        ]
        if not empty_spaces:
            # No space left; the snake has filled the board
            self.food = None
            return
        self.food = random.choice(empty_spaces)

    def change_direction(self, new_dir: Tuple[int, int]) -> None:
        """Change the snake's direction unless it would reverse."""
        if (
            (self.direction[0] + new_dir[0] == 0)
            and (self.direction[1] + new_dir[1] == 0)
        ):
            # Ignore reverse direction
            return
        self.direction = new_dir

    def _next_head(self) -> Point:
        head = self.snake[0]
        dx, dy = self.direction
        return Point(head.x + dx, head.y + dy)

    def move(self) -> None:
        """Advance the snake one step.  Update score, food, and alive status."""
        if not self.alive:
            return

        new_head = self._next_head()

        # Check wall collision
        if not (0 <= new_head.x < self.width and 0 <= new_head.y < self.height):
            self.alive = False
            return

        # Check self collision
        if new_head in self.snake:
            self.alive = False
            return

        # Insert new head
        self.snake.insert(0, new_head)

        # Check food
        if self.food and new_head == self.food:
            self.score += 1
            self.spawn_food()
        else:
            # Remove tail if no food eaten
            self.snake.pop()

    def get_state(self) -> dict:
        """Return a dictionary representation of the current game state."""
        return {
            "snake": [(p.x, p.y) for p in self.snake],
            "food": (self.food.x, self.food.y) if self.food else None,
            "score": self.score,
            "alive": self.alive,
            "width": self.width,
            "height": self.height,
        }

    def __repr__(self) -> str:
        return f"<SnakeGame alive={self.alive} score={self.score}>"


# Simple console demo (only runs if executed directly)
if __name__ == "__main__":
    import time
    import sys
    import tty
    import termios

    def _getch() -> str:
        """Read a single character from stdin without echo."""
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

    WIDTH, HEIGHT = 20, 10
    game = SnakeGame(WIDTH, HEIGHT)
    print("Use WASD to move, Q to quit.")
    while game.alive:
        state = game.get_state()
        # Render grid
        grid = [[" " for _ in range(WIDTH)] for _ in range(HEIGHT)]
        for x, y in state["snake"]:
            grid[y][x] = "█"
        if state["food"]:
            fx, fy = state["food"]
            grid[fy][fx] = "★"
        print("\n".join("".join(row) for row in grid))
        print(f"Score: {state['score']}")
        print("Press key: ", end="", flush=True)
        key = _getch()
        print(key)
        if key.lower() == "q":
            break
        elif key.lower() == "w":
            game.change_direction(SnakeGame.DIR_UP)
        elif key.lower() == "s":
            game.change_direction(SnakeGame.DIR_DOWN)
        elif key.lower() == "a":
            game.change_direction(SnakeGame.DIR_LEFT)
        elif key.lower() == "d":
            game.change_direction(SnakeGame.DIR_RIGHT)
        game.move()
        time.sleep(0.2)
    print("Game over! Final score:", game.score)