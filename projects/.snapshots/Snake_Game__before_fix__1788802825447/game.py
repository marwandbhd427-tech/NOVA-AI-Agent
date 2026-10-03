import random
import time
import sys
from typing import List, Tuple, Optional

# Constants
BOARD_WIDTH = 20
BOARD_HEIGHT = 10
SNAKE_CHAR = "O"
FOOD_CHAR = "*"
EMPTY_CHAR = " "
WALL_CHAR = "#"

# Direction vectors
DIRECTIONS = {
    "UP": (0, -1),
    "DOWN": (0, 1),
    "LEFT": (-1, 0),
    "RIGHT": (1, 0),
}


class Snake:
    """Represents the snake on the board."""

    def __init__(self, init_pos: Tuple[int, int]) -> None:
        self.body: List[Tuple[int, int]] = [init_pos]
        self.direction: str = "RIGHT"
        self.grow: bool = False

    def set_direction(self, new_dir: str) -> None:
        """Set a new direction for the snake, preventing 180° turns."""
        if new_dir not in DIRECTIONS:
            return
        # Prevent reverse direction
        opposite = {
            "UP": "DOWN",
            "DOWN": "UP",
            "LEFT": "RIGHT",
            "RIGHT": "LEFT",
        }
        if opposite[new_dir] != self.direction:
            self.direction = new_dir

    def move(self) -> None:
        """Move the snake by adding a new head in the current direction."""
        head_x, head_y = self.body[0]
        dx, dy = DIRECTIONS[self.direction]
        new_head = (head_x + dx, head_y + dy)
        self.body.insert(0, new_head)
        if not self.grow:
            self.body.pop()
        else:
            self.grow = False

    def head(self) -> Tuple[int, int]:
        return self.body[0]

    def collides_with_self(self) -> bool:
        return self.head() in self.body[1:]


class Food:
    """Represents the food on the board."""

    def __init__(self, position: Tuple[int, int]) -> None:
        self.position = position


class Game:
    """Main game logic."""

    def __init__(self) -> None:
        init_x = BOARD_WIDTH // 2
        init_y = BOARD_HEIGHT // 2
        self.snake = Snake((init_x, init_y))
        self.food = self._spawn_food()
        self.score: int = 0
        self.game_over: bool = False

    def _spawn_food(self) -> Food:
        """Spawn food at a random empty position."""
        occupied = set(self.snake.body)
        while True:
            pos = (
                random.randint(1, BOARD_WIDTH - 2),
                random.randint(1, BOARD_HEIGHT - 2),
            )
            if pos not in occupied:
                return Food(pos)

    def update(self) -> None:
        """Advance the game state by one tick."""
        if self.game_over:
            return

        self.snake.move()
        head = self.snake.head()

        # Check wall collision
        if (
            head[0] <= 0
            or head[0] >= BOARD_WIDTH - 1
            or head[1] <= 0
            or head[1] >= BOARD_HEIGHT - 1
        ):
            self.game_over = True
            return

        # Check self collision
        if self.snake.collides_with_self():
            self.game_over = True
            return

        # Check food collision
        if head == self.food.position:
            self.snake.grow = True
            self.score += 1
            self.food = self._spawn_food()

    def get_board(self) -> List[str]:
        """Return a list of strings representing the board."""
        board = [
            [EMPTY_CHAR for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)
        ]

        # Walls
        for x in range(BOARD_WIDTH):
            board[0][x] = WALL_CHAR
            board[BOARD_HEIGHT - 1][x] = WALL_CHAR
        for y in range(BOARD_HEIGHT):
            board[y][0] = WALL_CHAR
            board[y][BOARD_WIDTH - 1] = WALL_CHAR

        # Food
        fx, fy = self.food.position
        board[fy][fx] = FOOD_CHAR

        # Snake
        for idx, (x, y) in enumerate(self.snake.body):
            board[y][x] = SNAKE_CHAR

        return ["".join(row) for row in board]

    def is_over(self) -> bool:
        return self.game_over

    def get_score(self) -> int:
        return self.score


def _render(game: Game) -> None:
    """Print the current game state to the console."""
    board_lines = game.get_board()
    sys.stdout.write("\x1b[H\x1b[J")  # Clear screen (ANSI escape)
    print("\n".join(board_lines))
    print(f"Score: {game.get_score()}")
    print("Move with W/A/S/D keys. Press Q to quit.")


def _get_input() -> Optional[str]:
    """Get a single character input from the user."""
    # This is a simple implementation that requires pressing Enter.
    # For a more responsive game, platform-specific code would be needed.
    try:
        return input("Command (W/A/S/D/Q): ").strip().upper()
    except EOFError:
        return None


def main() -> None:
    game = Game()
    _render(game)

    while not game.is_over():
        cmd = _get_input()
        if cmd is None:
            break
        if cmd == "Q":
            break
        direction_map = {"W": "UP", "A": "LEFT", "S": "DOWN", "D": "RIGHT"}
        if cmd in direction_map:
            game.snake.set_direction(direction_map[cmd])
        game.update()
        _render(game)
        time.sleep(0.2)

    print("Game Over! Final Score:", game.get_score())


if __name__ == "__main__":
    main()