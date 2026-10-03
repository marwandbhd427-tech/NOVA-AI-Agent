import random
import time
import sys
from dataclasses import dataclass, field
from typing import List, Tuple, Dict

# ---------- Constants ----------
WIDTH: int = 20
HEIGHT: int = 20

# Direction vectors
DIRECTION_DELTAS: Dict[str, Tuple[int, int]] = {
    "UP": (0, -1),
    "DOWN": (0, 1),
    "LEFT": (-1, 0),
    "RIGHT": (1, 0),
}

# Opposite directions to prevent instant reversal
OPPOSITE: Dict[str, str] = {
    "UP": "DOWN",
    "DOWN": "UP",
    "LEFT": "RIGHT",
    "RIGHT": "LEFT",
}

# ---------- Core Classes ----------
@dataclass
class Snake:
    body: List[Tuple[int, int]] = field(default_factory=lambda: [(WIDTH // 2, HEIGHT // 2)])
    direction: str = "UP"
    grow_pending: int = 0

    def set_direction(self, new_dir: str) -> None:
        """Change direction if not directly opposite."""
        if new_dir in DIRECTION_DELTAS and OPPOSITE[new_dir] != self.direction:
            self.direction = new_dir

    def move(self) -> None:
        """Move snake forward, optionally grow."""
        dx, dy = DIRECTION_DELTAS[self.direction]
        new_head = (self.body[0][0] + dx, self.body[0][1] + dy)
        self.body.insert(0, new_head)
        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            self.body.pop()

    def grow(self, amount: int = 1) -> None:
        """Grow snake by amount."""
        self.grow_pending += amount

    def collides_with_self(self) -> bool:
        """Check if head collides with body."""
        return self.body[0] in self.body[1:]

    def collides_with_wall(self) -> bool:
        """Check if head is outside bounds."""
        x, y = self.body[0]
        return not (0 <= x < WIDTH and 0 <= y < HEIGHT)


@dataclass
class Food:
    position: Tuple[int, int] = (0, 0)

    def spawn(self, occupied: List[Tuple[int, int]]) -> None:
        """Place food on a random unoccupied cell."""
        free_cells = [
            (x, y)
            for x in range(WIDTH)
            for y in range(HEIGHT)
            if (x, y) not in occupied
        ]
        if not free_cells:
            raise RuntimeError("No free space to spawn food.")
        self.position = random.choice(free_cells)


@dataclass
class Game:
    snake: Snake = field(default_factory=Snake)
    food: Food = field(default_factory=Food)
    score: int = 0
    over: bool = False

    def __post_init__(self) -> None:
        self.food.spawn(self.snake.body)

    def step(self) -> None:
        """Advance game state by one tick."""
        if self.over:
            return

        self.snake.move()

        if self.snake.collides_with_wall() or self.snake.collides_with_self():
            self.over = True
            return

        if self.snake.body[0] == self.food.position:
            self.snake.grow()
            self.score += 1
            self.food.spawn(self.snake.body)

    def get_state(self) -> Dict:
        """Return a serializable snapshot of the game state."""
        return {
            "snake": self.snake.body,
            "food": self.food.position,
            "score": self.score,
            "over": self.over,
        }

# ---------- Optional Console UI ----------
def _render_console(game: Game) -> None:
    """Render the game state to the console."""
    grid = [[" " for _ in range(WIDTH)] for _ in range(HEIGHT)]
    for x, y in game.snake.body:
        grid[y][x] = "O"
    fx, fy = game.food.position
    grid[fy][fx] = "*"
    border = "+" + "-" * WIDTH + "+"
    print(border)
    for row in grid:
        print("|" + "".join(row) + "|")
    print(border)
    print(f"Score: {game.score}")
    if game.over:
        print("Game Over!")

def _input_direction() -> str:
    """Non-blocking key read for direction changes."""
    import tty
    import termios
    import select

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        rlist, _, _ = select.select([sys.stdin], [], [], 0.01)
        if rlist:
            key = sys.stdin.read(1)
            if key == "w":
                return "UP"
            if key == "s":
                return "DOWN"
            if key == "a":
                return "LEFT"
            if key == "d":
                return "RIGHT"
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ""

def _run_console_game() -> None:
    game = Game()
    try:
        while not game.over:
            dir_input = _input_direction()
            if dir_input:
                game.snake.set_direction(dir_input)
            game.step()
            _render_console(game)
            time.sleep(0.2)
    except KeyboardInterrupt:
        pass
    finally:
        print("\nFinal Score:", game.score)

# ---------- Main Guard ----------
if __name__ == "__main__":
    _run_console_game()