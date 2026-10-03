import os
import random
import sys
import time
from dataclasses import dataclass, field
from typing import List, Tuple, Set

# ----------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------
class Direction:
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

    @staticmethod
    def opposite(dir1: Tuple[int, int], dir2: Tuple[int, int]) -> bool:
        return dir1[0] == -dir2[0] and dir1[1] == -dir2[1]


@dataclass
class Config:
    width: int = 20
    height: int = 20
    initial_length: int = 3
    speed: float = 0.2  # seconds per tick


# ----------------------------------------------------------------------
# Core game entities
# ----------------------------------------------------------------------
@dataclass
class Snake:
    body: List[Tuple[int, int]] = field(default_factory=list)
    direction: Tuple[int, int] = field(default=Direction.RIGHT)
    grow_pending: int = 0

    def __post_init__(self):
        if not self.body:
            # start at center
            x = Config.width // 2
            y = Config.height // 2
            self.body = [(x - i, y) for i in range(Config.initial_length)]

    def set_direction(self, new_dir: Tuple[int, int]) -> None:
        """Change direction if not opposite to current."""
        if not Direction.opposite(self.direction, new_dir):
            self.direction = new_dir

    def move(self) -> None:
        head_x, head_y = self.body[0]
        delta_x, delta_y = self.direction
        new_head = (head_x + delta_x, head_y + delta_y)
        self.body.insert(0, new_head)
        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            self.body.pop()

    def grow(self, amount: int = 1) -> None:
        self.grow_pending += amount

    def collides_with_self(self) -> bool:
        return self.body[0] in self.body[1:]

    def collides_with(self, point: Tuple[int, int]) -> bool:
        return point in self.body

    def get_head(self) -> Tuple[int, int]:
        return self.body[0]


@dataclass
class Food:
    position: Tuple[int, int] = field(default_factory=tuple)

    def random_position(self, occupied: Set[Tuple[int, int]]) -> None:
        """Place food at a random position not occupied by the snake."""
        while True:
            x = random.randint(0, Config.width - 1)
            y = random.randint(0, Config.height - 1)
            if (x, y) not in occupied:
                self.position = (x, y)
                break


# ----------------------------------------------------------------------
# Game logic
# ----------------------------------------------------------------------
class SnakeGame:
    def __init__(self, config: Config = Config()) -> None:
        self.config = config
        self.snake = Snake()
        self.food = Food()
        self.score = 0
        self.game_over = False
        self._place_food()

    def _place_food(self) -> None:
        occupied = set(self.snake.body)
        self.food.random_position(occupied)

    def update(self) -> None:
        """Advance the game by one tick."""
        if self.game_over:
            return

        self.snake.move()
        head = self.snake.get_head()

        # Wall collision
        if not (0 <= head[0] < self.config.width and 0 <= head[1] < self.config.height):
            self.game_over = True
            return

        # Self collision
        if self.snake.collides_with_self():
            self.game_over = True
            return

        # Food collision
        if head == self.food.position:
            self.snake.grow()
            self.score += 1
            self._place_food()

    def is_game_over(self) -> bool:
        return self.game_over

    def get_score(self) -> int:
        return self.score

    def get_state(self) -> Tuple[Set[Tuple[int, int]], Tuple[int, int]]:
        """Return a set of snake positions and the food position."""
        return set(self.snake.body), self.food.position

    def set_direction(self, dir_char: str) -> None:
        mapping = {
            'w': Direction.UP,
            's': Direction.DOWN,
            'a': Direction.LEFT,
            'd': Direction.RIGHT,
        }
        if dir_char.lower() in mapping:
            self.snake.set_direction(mapping[dir_char.lower()])

    # ------------------------------------------------------------------
    # Rendering helpers for the console
    # ------------------------------------------------------------------
    def _clear_screen(self) -> None:
        os.system('cls' if os.name == 'nt' else 'clear')

    def _render(self) -> None:
        board = [[' ' for _ in range(self.config.width)] for _ in range(self.config.height)]

        # Draw food
        fx, fy = self.food.position
        board[fy][fx] = '*'

        # Draw snake
        for idx, (x, y) in enumerate(self.snake.body):
            board[y][x] = 'O' if idx == 0 else 'o'

        # Draw borders
        top_bottom = '+' + '-' * self.config.width + '+'
        print(top_bottom)
        for row in board:
            print('|' + ''.join(row) + '|')
        print(top_bottom)
        print(f"Score: {self.score}")

    def run(self) -> None:
        """Run the game loop in the console."""
        self._clear_screen()
        print("Snake Game")
        print("Controls: w/a/s/d to move, q to quit")
        time.sleep(1)

        while not self.game_over:
            self._clear_screen()
            self._render()

            # Non-blocking input
            start_time = time.time()
            while time.time() - start_time < self.config.speed:
                if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                    cmd = sys.stdin.readline().strip()
                    if cmd == 'q':
                        self.game_over = True
                        break
                    self.set_direction(cmd)
                time.sleep(0.01)

            self.update()

        self._clear_screen()
        self._render()
        print("Game Over!")


# ----------------------------------------------------------------------
# Entry point
# ----------------------------------------------------------------------
def main() -> None:
    game = SnakeGame()
    try:
        game.run()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()