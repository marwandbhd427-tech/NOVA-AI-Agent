import random
import tkinter as tk
from dataclasses import dataclass
from typing import List, Tuple, Optional

# ------------------------------
# Constants
# ------------------------------
BLOCK_SIZE = 20          # Size of each square block in pixels
GRID_WIDTH = 30          # Number of blocks horizontally
GRID_HEIGHT = 20         # Number of blocks vertically
INITIAL_SNAKE_LENGTH = 3
UPDATE_DELAY = 100       # Milliseconds between game updates


# ------------------------------
# Utility functions
# ------------------------------
def random_position() -> Tuple[int, int]:
    """Return a random position within the grid that is not on the edges."""
    return (
        random.randint(1, GRID_WIDTH - 2),
        random.randint(1, GRID_HEIGHT - 2)
    )


# ------------------------------
# Snake logic
# ------------------------------
@dataclass
class Snake:
    body: List[Tuple[int, int]]
    direction: Tuple[int, int]  # (dx, dy)
    pending_growth: int = 0

    def __post_init__(self):
        if not self.body:
            raise ValueError("Snake must have an initial body")

    @classmethod
    def create(cls, start_x: int, start_y: int, length: int = INITIAL_SNAKE_LENGTH) -> "Snake":
        body = [(start_x - i, start_y) for i in range(length)]
        return cls(body=body, direction=(1, 0))

    def move(self) -> None:
        """Move the snake one step in the current direction."""
        head_x, head_y = self.body[0]
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)
        self.body.insert(0, new_head)
        if self.pending_growth > 0:
            self.pending_growth -= 1
        else:
            self.body.pop()

    def grow(self) -> None:
        """Increase the snake's length by one block."""
        self.pending_growth += 1

    def set_direction(self, new_direction: Tuple[int, int]) -> None:
        """Set new direction if it is not directly opposite to current."""
        opposite = (-self.direction[0], -self.direction[1])
        if new_direction != opposite:
            self.direction = new_direction

    def collides_with_self(self) -> bool:
        """Check if the snake's head collides with its body."""
        return self.body[0] in self.body[1:]

    def collides_with_wall(self) -> bool:
        """Check if the snake's head collides with the walls."""
        x, y = self.body[0]
        return not (0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT)

    def head_position(self) -> Tuple[int, int]:
        return self.body[0]


# ------------------------------
# Food logic
# ------------------------------
@dataclass
class Food:
    position: Tuple[int, int]

    @classmethod
    def spawn(cls, snake_body: List[Tuple[int, int]]) -> "Food":
        """Spawn food at a random position not occupied by the snake."""
        while True:
            pos = random_position()
            if pos not in snake_body:
                return cls(position=pos)


# ------------------------------
# Game logic
# ------------------------------
class Game:
    def __init__(self):
        self.snake = Snake.create(GRID_WIDTH // 2, GRID_HEIGHT // 2)
        self.food = Food.spawn(self.snake.body)
        self.score = 0
        self.running = True

    def update(self) -> None:
        """Advance the game state by one tick."""
        if not self.running:
            return
        self.snake.move()
        if self.snake.collides_with_wall() or self.snake.collides_with_self():
            self.running = False
            return
        if self.snake.head_position() == self.food.position:
            self.snake.grow()
            self.score += 1
            self.food = Food.spawn(self.snake.body)

    def change_direction(self, key: str) -> None:
        """Change the snake's direction based on arrow key input."""
        key_map = {
            "Up": (0, -1),
            "Down": (0, 1),
            "Left": (-1, 0),
            "Right": (1, 0),
        }
        if key in key_map:
            self.snake.set_direction(key_map[key])


# ------------------------------
# GUI
# ------------------------------
class SnakeGUI(tk.Tk):
    def __init__(self, game: Game):
        super().__init__()
        self.title("Snake")
        self.resizable(False, False)
        self.game = game
        self.canvas = tk.Canvas(
            self,
            width=GRID_WIDTH * BLOCK_SIZE,
            height=GRID_HEIGHT * BLOCK_SIZE,
            bg="black"
        )
        self.canvas.pack()
        self.bind("<Key>", self.on_key)
        self.after(UPDATE_DELAY, self.game_loop)

    def on_key(self, event: tk.Event) -> None:
        self.game.change_direction(event.keysym)

    def game_loop(self) -> None:
        self.game.update()
        self.draw()
        if self.game.running:
            self.after(UPDATE_DELAY, self.game_loop)
        else:
            self.canvas.create_text(
                GRID_WIDTH * BLOCK_SIZE // 2,
                GRID_HEIGHT * BLOCK_SIZE // 2,
                text=f"Game Over! Score: {self.game.score}",
                fill="white",
                font=("Arial", 24)
            )

    def draw(self) -> None:
        self.canvas.delete("all")
        # Draw food
        fx, fy = self.game.food.position
        self.canvas.create_rectangle(
            fx * BLOCK_SIZE,
            fy * BLOCK_SIZE,
            (fx + 1) * BLOCK_SIZE,
            (fy + 1) * BLOCK_SIZE,
            fill="red",
            outline=""
        )
        # Draw snake
        for idx, (x, y) in enumerate(self.game.snake.body):
            color = "green" if idx == 0 else "darkgreen"
            self.canvas.create_rectangle(
                x * BLOCK_SIZE,
                y * BLOCK_SIZE,
                (x + 1) * BLOCK_SIZE,
                (y + 1) * BLOCK_SIZE,
                fill=color,
                outline=""
            )
        # Draw score
        self.canvas.create_text(
            5,
            5,
            anchor="nw",
            text=f"Score: {self.game.score}",
            fill="white",
            font=("Arial", 12)
        )


# ------------------------------
# Entry point
# ------------------------------
def main() -> None:
    game = Game()
    gui = Snake