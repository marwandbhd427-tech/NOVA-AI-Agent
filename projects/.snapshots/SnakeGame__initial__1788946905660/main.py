import random
import tkinter as tk
from dataclasses import dataclass, field
from typing import List, Tuple

# --------------------- Constants --------------------- #
CELL_SIZE = 20          # Size of each grid cell in pixels
GRID_WIDTH = 20         # Number of cells horizontally
GRID_HEIGHT = 20        # Number of cells vertically
INITIAL_SNAKE_LENGTH = 3
MOVE_DELAY = 150        # Milliseconds between moves

# --------------------- Data Structures --------------------- #
@dataclass
class Snake:
    body: List[Tuple[int, int]] = field(default_factory=list)
    direction: Tuple[int, int] = (0, -1)  # Initially moving up

    def __post_init__(self):
        if not self.body:
            center_x = GRID_WIDTH // 2
            center_y = GRID_HEIGHT // 2
            self.body = [(center_x, center_y + i) for i in range(INITIAL_SNAKE_LENGTH)]

    def move(self, grow: bool = False):
        head_x, head_y = self.body[0]
        dir_x, dir_y = self.direction
        new_head = (head_x + dir_x, head_y + dir_y)

        # Insert new head
        self.body.insert(0, new_head)

        # Remove tail unless growing
        if not grow:
            self.body.pop()

    def set_direction(self, new_dir: Tuple[int, int]):
        # Prevent reversing directly
        opposite = (-self.direction[0], -self.direction[1])
        if new_dir != opposite:
            self.direction = new_dir

    def collides_with_self(self) -> bool:
        return self.body[0] in self.body[1:]

    def collides_with_wall(self) -> bool:
        head_x, head_y = self.body[0]
        return not (0 <= head_x < GRID_WIDTH and 0 <= head_y < GRID_HEIGHT)

@dataclass
class Food:
    position: Tuple[int, int] = (0, 0)

    def spawn(self, snake_body: List[Tuple[int, int]]):
        available = [
            (x, y) for x in range(GRID_WIDTH) for y in range(GRID_HEIGHT)
            if (x, y) not in snake_body
        ]
        if not available:
            raise RuntimeError("No space left to spawn food")
        self.position = random.choice(available)

# --------------------- Game Logic --------------------- #
class SnakeGame:
    def __init__(self):
        self.snake = Snake()
        self.food = Food()
        self.food.spawn(self.snake.body)
        self.score = 0
        self.running = False
        self.root = None
        self.canvas = None

    def start(self):
        self.running = True
        self._setup_gui()
        self._game_loop()

    def _setup_gui(self):
        self.root = tk.Tk()
        self.root.title("Snake")
        self.canvas = tk.Canvas(
            self.root,
            width=GRID_WIDTH * CELL_SIZE,
            height=GRID_HEIGHT * CELL_SIZE,
            bg="black"
        )
        self.canvas.pack()
        self.root.bind("<Key>", self._key_handler)

    def _key_handler(self, event):
        key_map = {
            "Up": (0, -1),
            "Down": (0, 1),
            "Left": (-1, 0),
            "Right": (1, 0),
        }
        if event.keysym in key_map:
            self.snake.set_direction(key_map[event.keysym])

    def _draw(self):
        self.canvas.delete("all")
        # Draw food
        fx, fy = self.food.position
        self.canvas.create_rectangle(
            fx * CELL_SIZE,
            fy * CELL_SIZE,
            (fx + 1) * CELL_SIZE,
            (fy + 1) * CELL_SIZE,
            fill="red"
        )
        # Draw snake
        for idx, (x, y) in enumerate(self.snake.body):
            color = "green" if idx == 0 else "lightgreen"
            self.canvas.create_rectangle(
                x * CELL_SIZE,
                y * CELL_SIZE,
                (x + 1) * CELL_SIZE,
                (y + 1) * CELL_SIZE,
                fill=color
            )
        # Draw score
        self.canvas.create_text(
            5, 5,
            anchor="nw",
            fill="white",
            font=("Arial", 12),
            text=f"Score: {self.score}"
        )

    def _game_loop(self):
        if not self.running:
            return
        # Determine if snake eats food
        grow = self.snake.body[0] == self.food.position
        if grow:
            self.score += 1
            self.food.spawn(self.snake.body)
        self.snake.move(grow)
        if self.snake.collides_with_wall() or self.snake.collides_with_self():
            self.running = False
            self._game_over()
            return
        self._draw()
        self.root.after(MOVE_DELAY, self._game_loop)

    def _game_over(self):
        self.canvas.create_text(
            (GRID_WIDTH * CELL_SIZE) // 2,
            (GRID_HEIGHT * CELL_SIZE) // 2,
            fill="white",
            font=("Arial", 24),
            text=f"Game Over! Score: {self.score}"
        )

# --------------------- Entry Point --------------------- #
if __name__ == "__main__":
    game = SnakeGame()
    game.start()