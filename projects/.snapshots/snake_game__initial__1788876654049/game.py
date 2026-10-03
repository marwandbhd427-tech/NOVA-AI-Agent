import random
import sys
from typing import List, Tuple, Set

# ----------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------
GRID_WIDTH: int = 20
GRID_HEIGHT: int = 15
INITIAL_SNAKE_LENGTH: int = 3
DIRECTIONS: dict[str, Tuple[int, int]] = {
    "UP": (0, -1),
    "DOWN": (0, 1),
    "LEFT": (-1, 0),
    "RIGHT": (1, 0),
}
OPPOSITE_DIRECTIONS: dict[str, str] = {
    "UP": "DOWN",
    "DOWN": "UP",
    "LEFT": "RIGHT",
    "RIGHT": "LEFT",
}

# ----------------------------------------------------------------------
# Snake
# ----------------------------------------------------------------------
class Snake:
    """
    Represents the snake in the game.

    Attributes:
        body (List[Tuple[int, int]]): List of coordinates from head to tail.
        direction (str): Current moving direction ("UP", "DOWN", "LEFT", "RIGHT").
        grow_pending (int): Number of segments to grow (after eating food).
    """

    def __init__(self, start_pos: Tuple[int, int] = (GRID_WIDTH // 2, GRID_HEIGHT // 2)) -> None:
        self.body: List[Tuple[int, int]] = [start_pos]
        self.direction: str = "RIGHT"
        self.grow_pending: int = 0

        # Initialize the snake with the initial length
        for _ in range(INITIAL_SNAKE_LENGTH - 1):
            self._move_forward(init=True)

    def _move_forward(self, init: bool = False) -> None:
        """Move the snake one step in the current direction."""
        head_x, head_y = self.body[0]
        delta_x, delta_y = DIRECTIONS[self.direction]
        new_head = (head_x + delta_x, head_y + delta_y)

        self.body.insert(0, new_head)

        if self.grow_pending > 0 or init:
            # Do not remove tail segment
            if self.grow_pending > 0:
                self.grow_pending -= 1
        else:
            # Remove tail segment
            self.body.pop()

    def set_direction(self, new_direction: str) -> None:
        """
        Change the snake's direction if it's not directly opposite to current.
        """
        if new_direction not in DIRECTIONS:
            return
        if OPPOSITE_DIRECTIONS[new_direction] == self.direction:
            return
        self.direction = new_direction

    def grow(self, segments: int = 1) -> None:
        """Increase the snake's size by the given number of segments."""
        self.grow_pending += segments

    def head_position(self) -> Tuple[int, int]:
        return self.body[0]

    def occupies(self, pos: Tuple[int, int]) -> bool:
        return pos in self.body

    def has_self_collision(self) -> bool:
        head = self.head_position()
        return head in self.body[1:]

# ----------------------------------------------------------------------
# Food
# ----------------------------------------------------------------------
class Food:
    """
    Represents the food in the game.

    Attributes:
        position (Tuple[int, int]): Current position of the food.
    """

    def __init__(self, snake: Snake) -> None:
        self.position: Tuple[int, int] = (0, 0)
        self.spawn(snake)

    def spawn(self, snake: Snake) -> None:
        """Place food at a random position not occupied by the snake."""
        available: Set[Tuple[int, int]] = {
            (x, y) for x in range(GRID_WIDTH) for y in range(GRID_HEIGHT)
        } - set(snake.body)
        if not available:
            # No space left; game over scenario
            self.position = (-1, -1)
            return
        self.position = random.choice(list(available))

# ----------------------------------------------------------------------
# Game
# ----------------------------------------------------------------------
class Game:
    """
    Main game logic.

    Attributes:
        snake (Snake): The player's snake.
        food (Food): The current food item.
        score (int): Current score.
        over (bool): Whether the game is over.
    """

    def __init__(self) -> None:
        self.snake = Snake()
        self.food = Food(self.snake)
        self.score: int = 0
        self.over: bool = False

    def update(self) -> None:
        """Advance the game by one tick."""
        if self.over:
            return

        self.snake._move_forward()

        head_x, head_y = self.snake.head_position()

        # Wall collision
        if not (0 <= head_x < GRID_WIDTH and 0 <= head_y < GRID_HEIGHT):
            self.over = True
            return

        # Self collision
        if self.snake.has_self_collision():
            self.over = True
            return

        # Food collision
        if self.snake.head_position() == self.food.position:
            self.snake.grow()
            self.score += 1
            self.food.spawn(self.snake)

    def set_direction(self, direction: str) -> None:
        """Set the snake's direction."""
        self.snake.set_direction(direction)

    def get_state(self) -> dict:
        """Return a snapshot of the current game state."""
        return {
            "snake": list(self.snake.body),
            "food": self.food.position,
            "score": self.score,
            "over": self.over,
        }

# ----------------------------------------------------------------------
# Console interface (optional)
# ----------------------------------------------------------------------
def _print_grid(game: Game) -> None:
    """Render the game grid to the console."""
    grid: List[List[str]] = [["." for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

    # Draw food
    fx, fy = game.food.position
    if 0 <= fx < GRID_WIDTH and 0 <= fy < GRID_HEIGHT:
        grid[fy][fx] = "F"

    # Draw snake
    for idx, (x, y) in enumerate(game.snake.body):
        if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
            grid[y][x] = "H" if idx == 0 else "S"

    # Print grid
    for row in grid:
        print(" ".join(row))
    print(f"Score: {game.score}")

def _console_loop() -> None:
    """Simple console loop that accepts WASD input."""
    game = Game()
    _print_grid(game)
    print("Controls: W (up), A (left), S (down), D (right), Q (quit)")

    direction_map = {"W": "UP", "A": "LEFT", "S": "DOWN", "D": "RIGHT"}
    try:
        while not game.over:
            move = input("Move: ").strip().upper()
            if move == "Q":
                print("Quitting.")
                break
            if move in direction_map:
                game.set_direction(direction_map[move])
            game.update()
            _print_grid(game)
    except KeyboardInterrupt:
        pass

    if game.over:
        print("Game Over!")
    print(f"Final Score: {game.score}")

# ----------------------------------------------------------------------
# Entry point
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Guard to avoid running the console loop during automated tests.
    # The tests will import Game, Snake, etc. without executing this block.
    _console_loop()