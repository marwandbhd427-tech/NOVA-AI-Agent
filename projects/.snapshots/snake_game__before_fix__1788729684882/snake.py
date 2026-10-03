import random
from dataclasses import dataclass, field
from typing import List, Tuple, Optional

# Grid dimensions
GRID_WIDTH = 20
GRID_HEIGHT = 20

# Directions represented as (dx, dy)
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
OPPOSITE_DIRECTION = {UP: DOWN, DOWN: UP, LEFT: RIGHT, RIGHT: LEFT}


@dataclass
class Snake:
    """Represents the snake's body and movement."""
    body: List[Tuple[int, int]] = field(default_factory=list)
    direction: Tuple[int, int] = RIGHT
    grow_pending: int = 0

    def __post_init__(self):
        if not self.body:
            # Start in the middle of the grid
            mid_x = GRID_WIDTH // 2
            mid_y = GRID_HEIGHT // 2
            self.body = [(mid_x, mid_y)]

    def set_direction(self, new_direction: Tuple[int, int]) -> None:
        """Change the snake's direction if it's not directly opposite."""
        if new_direction and new_direction != OPPOSITE_DIRECTION.get(self.direction):
            self.direction = new_direction

    def move(self) -> Tuple[int, int]:
        """Move the snake forward, handle growth, and return the new head position."""
        head_x, head_y = self.body[0]
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)
        self.body.insert(0, new_head)

        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            self.body.pop()  # Remove tail segment

        return new_head

    def grow(self, segments: int = 1) -> None:
        """Schedule the snake to grow by a number of segments."""
        self.grow_pending += segments

    def collides_with_self(self) -> bool:
        """Check if the snake's head collides with its body."""
        head = self.body[0]
        return head in self.body[1:]


@dataclass
class Food:
    """Represents a food item on the grid."""
    position: Tuple[int, int] = (0, 0)

    def spawn(self, occupied: List[Tuple[int, int]]) -> None:
        """Spawn food at a random location not occupied by the snake."""
        available = [
            (x, y)
            for x in range(GRID_WIDTH)
            for y in range(GRID_HEIGHT)
            if (x, y) not in occupied
        ]
        if not available:
            raise RuntimeError("No space left to spawn food.")
        self.position = random.choice(available)


@dataclass
class GameState:
    """Encapsulates the entire game state."""
    snake: Snake = field(default_factory=Snake)
    food: Food = field(default_factory=Food)
    score: int = 0
    over: bool = False

    def reset(self) -> None:
        """Reset the game to its initial state."""
        self.snake = Snake()
        self.food = Food()
        self.score = 0
        self.over = False
        self.food.spawn(self.snake.body)

    def step(self) -> None:
        """Advance the game by one tick."""
        if self.over:
            return

        new_head = self.snake.move()

        # Collision with walls
        if not (0 <= new_head[0] < GRID_WIDTH and 0 <= new_head[1] < GRID_HEIGHT):
            self.over = True
            return

        # Collision with self
        if self.snake.collides_with_self():
            self.over = True
            return

        # Collision with food
        if new_head == self.food.position:
            self.snake.grow()
            self.score += 1
            self.food.spawn(self.snake.body)

    def get_grid(self) -> List[List[str]]:
        """Return a 2D representation of the grid for rendering or testing."""
        grid = [["." for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        # Draw food
        fx, fy = self.food.position
        grid[fy][fx] = "F"
        # Draw snake
        for idx, (x, y) in enumerate(self.snake.body):
            grid[y][x] = "H" if idx == 0 else "S"
        return grid


# Example console demo (optional)
if __name__ == "__main__":
    import time
    import sys
    import tty
    import termios

    def get_key() -> Optional[str]:
        """Non-blocking single character input."""
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setcbreak(fd)
            if sys.stdin.read(1):
                return sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)
        return None

    game = GameState()
    game.reset()
    key_map = {
        "w": UP,
        "s": DOWN,
        "a": LEFT,
        "d": RIGHT,
    }

    print("Use WASD to move. Press 'q' to quit.")
    while not game.over:
        key = get_key()
        if key == "q":
            break
        if key in key_map:
            game.snake.set_direction(key_map[key])

        game.step()
        grid = game.get_grid()
        for row in grid:
            print("".join(row))
        print(f"Score: {game.score}")
        time.sleep(0.2)
        print("\n" * 10)

    print("Game Over! Final Score:", game.score)