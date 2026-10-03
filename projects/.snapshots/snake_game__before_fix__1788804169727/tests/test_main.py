import random
from dataclasses import dataclass, field
from typing import List, Tuple, Set

# Constants
BOARD_WIDTH = 20
BOARD_HEIGHT = 20
INITIAL_SNAKE_LENGTH = 3
DIRECTIONS = {
    "UP": (0, -1),
    "DOWN": (0, 1),
    "LEFT": (-1, 0),
    "RIGHT": (1, 0),
}
OPPOSITE_DIRECTIONS = {
    "UP": "DOWN",
    "DOWN": "UP",
    "LEFT": "RIGHT",
    "RIGHT": "LEFT",
}

Position = Tuple[int, int]

@dataclass
class Snake:
    """Represents the snake."""
    body: List[Position] = field(default_factory=list)
    direction: str = "RIGHT"
    grow_pending: int = 0

    def __post_init__(self):
        if not self.body:
            # Initialize snake in the middle of the board
            mid_x = BOARD_WIDTH // 2
            mid_y = BOARD_HEIGHT // 2
            self.body = [(mid_x - i, mid_y) for i in range(INITIAL_SNAKE_LENGTH)]
            self.body.reverse()

    def set_direction(self, new_direction: str):
        """Set new direction if it's not directly opposite."""
        if new_direction not in DIRECTIONS:
            raise ValueError(f"Invalid direction: {new_direction}")
        if OPPOSITE_DIRECTIONS[new_direction] != self.direction:
            self.direction = new_direction

    def move(self):
        """Move the snake by adding a new head in the current direction."""
        dx, dy = DIRECTIONS[self.direction]
        new_head = (self.body[0][0] + dx, self.body[0][1] + dy)
        self.body.insert(0, new_head)
        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            self.body.pop()

    def grow(self, segments: int = 1):
        """Increase the snake's length by the specified number of segments."""
        self.grow_pending += segments

    def head(self) -> Position:
        return self.body[0]

    def collides_with_self(self) -> bool:
        return self.head() in self.body[1:]

    def collides_with_wall(self) -> bool:
        x, y = self.head()
        return not (0 <= x < BOARD_WIDTH and 0 <= y < BOARD_HEIGHT)

    def __len__(self) -> int:
        return len(self.body)

@dataclass
class Food:
    """Represents food on the board."""
    position: Position = None

    def spawn(self, snake: Snake):
        """Spawn food at a random location not occupied by the snake."""
        available_positions: Set[Position] = {
            (x, y) for x in range(BOARD_WIDTH) for y in range(BOARD_HEIGHT)
        } - set(snake.body)
        if not available_positions:
            raise RuntimeError("No space left to spawn food.")
        self.position = random.choice(list(available_positions))

@dataclass
class Game:
    """Encapsulates the game state."""
    snake: Snake = field(default_factory=Snake)
    food: Food = field(default_factory=Food)
    score: int = 0
    game_over: bool = False

    def __post_init__(self):
        self.food.spawn(self.snake)

    def step(self):
        """Advance the game by one tick."""
        if self.game_over:
            return
        self.snake.move()
        if self.snake.collides_with_wall() or self.snake.collides_with_self():
            self.game_over = True
            return
        if self.snake.head() == self.food.position:
            self.score += 1
            self.snake.grow()
            self.food.spawn(self.snake)

    def get_state(self):
        """Return a dictionary representation of the current game state."""
        return {
            "snake": list(self.snake.body),
            "food": self.food.position,
            "score": self.score,
            "game_over": self.game_over,
        }

    def reset(self):
        """Reset the game to initial state."""
        self.snake = Snake()
        self.food = Food()
        self.score = 0
        self.game_over = False
        self.food.spawn(self.snake)

# Example console-based play loop (not used in tests)
if __name__ == "__main__":
    import sys
    import time

    game = Game()
    print("Simple Snake Game (console). Use WASD to control. Press Ctrl+C to exit.")
    direction_map = {"w": "UP", "a": "LEFT", "s": "DOWN", "d": "RIGHT"}

    try:
        while not game.game_over:
            print("\n" + "=" * (BOARD_WIDTH * 2))
            board = [["  " for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]
            for x, y in game.snake.body:
                board[y][x] = "🐍"
            fx, fy = game.food.position
            board[fy][fx] = "🍎"
            for row in board:
                print("".join(row))
            print(f"Score: {game.score}")
            move = input("Move (WASD): ").lower()
            if move in direction_map:
                game.snake.set_direction(direction_map[move])
            game.step()
            time.sleep(0.1)
        print("Game Over! Final Score:", game.score)
    except KeyboardInterrupt:
        sys.exit(0)