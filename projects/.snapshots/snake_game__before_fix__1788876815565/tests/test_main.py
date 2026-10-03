import random
from dataclasses import dataclass, field
from typing import List, Tuple, Set

# ---------------- Constants ----------------
BOARD_WIDTH = 20
BOARD_HEIGHT = 15
INITIAL_SNAKE_LENGTH = 3
FOOD_COUNT = 1
DIRECTIONS = {
    "UP": (0, -1),
    "DOWN": (0, 1),
    "LEFT": (-1, 0),
    "RIGHT": (1, 0),
}

# ---------------- Data Classes ----------------
@dataclass
class Position:
    x: int
    y: int

    def __add__(self, other: Tuple[int, int]) -> "Position":
        return Position(self.x + other[0], self.y + other[1])

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Position):
            return False
        return self.x == other.x and self.y == other.y

    def __hash__(self) -> int:
        return hash((self.x, self.y))

# ---------------- Snake ----------------
@dataclass
class Snake:
    body: List[Position] = field(default_factory=list)
    direction: Tuple[int, int] = DIRECTIONS["RIGHT"]
    grow_pending: int = 0

    def __post_init__(self):
        if not self.body:
            start_x = BOARD_WIDTH // 2
            start_y = BOARD_HEIGHT // 2
            for i in range(INITIAL_SNAKE_LENGTH):
                self.body.append(Position(start_x - i, start_y))

    def set_direction(self, new_dir: str):
        if new_dir not in DIRECTIONS:
            return
        new_delta = DIRECTIONS[new_dir]
        # Prevent reversing into itself
        if (new_delta[0] == -self.direction[0] and new_delta[1] == -self.direction[1]):
            return
        self.direction = new_delta

    def move(self):
        new_head = self.body[0] + self.direction
        self.body.insert(0, new_head)
        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            self.body.pop()

    def grow(self, segments: int = 1):
        self.grow_pending += segments

    def collides_with_self(self) -> bool:
        return self.body[0] in set(self.body[1:])

    def collides_with_wall(self) -> bool:
        head = self.body[0]
        return not (0 <= head.x < BOARD_WIDTH and 0 <= head.y < BOARD_HEIGHT)

# ---------------- Food ----------------
@dataclass
class Food:
    positions: Set[Position] = field(default_factory=set)

    def spawn(self, snake: Snake):
        available = {
            Position(x, y)
            for x in range(BOARD_WIDTH)
            for y in range(BOARD_HEIGHT)
            if Position(x, y) not in set(snake.body) and Position(x, y) not in self.positions
        }
        if not available:
            return
        self.positions.add(random.choice(list(available)))

    def consume_at(self, pos: Position) -> bool:
        if pos in self.positions:
            self.positions.remove(pos)
            return True
        return False

# ---------------- Game ----------------
@dataclass
class Game:
    snake: Snake = field(default_factory=Snake)
    food: Food = field(default_factory=Food)
    score: int = 0
    _running: bool = False

    def start(self):
        self._running = True
        self.food.spawn(self.snake)

    def stop(self):
        self._running = False

    def update(self):
        if not self._running:
            return
        self.snake.move()
        # Check collisions
        if self.snake.collides_with_wall() or self.snake.collides_with_self():
            self.stop()
            return
        # Check food
        head = self.snake.body[0]
        if self.food.consume_at(head):
            self.snake.grow()
            self.score += 1
            self.food.spawn(self.snake)

    def is_running(self) -> bool:
        return self._running

# ---------------- Entry Point ----------------
def main():
    # Example usage (non-visual)
    game = Game()
    game.start()
    # Simulate a few steps
    for _ in range(10):
        if not game.is_running():
            break
        # Randomly change direction
        game.snake.set_direction(random.choice(list(DIRECTIONS.keys())))
        game.update()
        print(f"Score: {game.score}, Snake Length: {len(game.snake.body)}")
    print("Game ended.")

if __name__ == "__main__":
    # Guarded: the demo will run only when executed directly
    main()