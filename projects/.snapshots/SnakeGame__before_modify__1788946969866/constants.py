import tkinter as tk
import random
from dataclasses import dataclass, field
from typing import List, Tuple

# ---------- Constants ----------
GRID_WIDTH = 20          # number of cells horizontally
GRID_HEIGHT = 20         # number of cells vertically
CELL_SIZE = 20           # pixel size of each cell
INITIAL_SNAKE_LENGTH = 3
FOOD_COLOR = "red"
SNAKE_COLOR = "green"
BG_COLOR = "black"
SCORE_FONT = ("Arial", 14)

# ---------- Helper Types ----------
Position = Tuple[int, int]

# ---------- Snake Class ----------
@dataclass
class Snake:
    """Represents the snake."""
    body: List[Position] = field(default_factory=list)
    direction: Position = (0, 0)   # (dx, dy)

    def __post_init__(self):
        # Initialize snake in the center moving right
        center_x = GRID_WIDTH // 2
        center_y = GRID_HEIGHT // 2
        self.body = [(center_x - i, center_y) for i in range(INITIAL_SNAKE_LENGTH)]
        self.direction = (1, 0)

    def set_direction(self, new_dir: Position):
        """Change direction unless it's directly opposite."""
        opposite = (-self.direction[0], -self.direction[1])
        if new_dir != opposite:
            self.direction = new_dir

    def move(self, grow: bool = False) -> Position:
        """Move snake; returns the new head position."""
        head_x, head_y = self.body[0]
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)
        self.body.insert(0, new_head)
        if not grow:
            self.body.pop()
        return new_head

    def collides_with_self(self) -> bool:
        """Check if the snake collides with itself."""
        head = self.body[0]
        return head in self.body[1:]

    def collides_with_wall(self) -> bool:
        """Check if the snake hits the walls."""
        head_x, head_y = self.body[0]
        return not (0 <= head_x < GRID_WIDTH and 0 <= head_y < GRID_HEIGHT)

# ---------- Food Class ----------
@dataclass
class Food:
    """Represents food."""
    position: Position = (0, 0)

    def spawn(self, occupied: List[Position]):
        """Place food at a random unoccupied position."""
        available = [
            (x, y)
            for x in range(GRID_WIDTH)
            for y in range(GRID_HEIGHT)
            if (x, y) not in occupied
        ]
        if not available:
            raise RuntimeError("No space to spawn food.")
        self.position = random.choice(available)

# ---------- Game Class ----------
class SnakeGame:
    """Main game logic."""
    def __init__(self, master: tk.Tk):
        self.master = master
        self.master.title("Snake")
        self.canvas = tk.Canvas(
            master,
            width=GRID_WIDTH * CELL_SIZE,
            height=GRID_HEIGHT * CELL_SIZE,
            bg=BG_COLOR,
            highlightthickness=0,
        )
        self.canvas.pack()
        self.score_label = tk.Label(master, text="Score: 0", font=SCORE_FONT)
        self.score_label.pack()
        self.snake = Snake()
        self.food = Food()
        self.food.spawn(self.snake.body)
        self.score = 0
        self._draw()
        self._bind_keys()
        self._running = True
        self._game_loop()

    def _draw(self):
        """Render snake and food."""
        self.canvas.delete("all")
        # Draw food
        fx, fy = self.food.position
        self.canvas.create_rectangle(
            fx * CELL_SIZE,
            fy * CELL_SIZE,
            (fx + 1) * CELL_SIZE,
            (fy + 1) * CELL_SIZE,
            fill=FOOD_COLOR,
            outline=FOOD_COLOR,
        )
        # Draw snake
        for x, y in self.snake.body:
            self.canvas.create_rectangle(
                x * CELL_SIZE,
                y * CELL_SIZE,
                (x + 1) * CELL_SIZE,
                (y + 1) * CELL_SIZE,
                fill=SNAKE_COLOR,
                outline=SNAKE_COLOR,
            )
        # Update score
        self.score_label.config(text=f"Score: {self.score}")

    def _bind_keys(self):
        """Set up key bindings."""
        self.master.bind("<Up>", lambda e: self.snake.set_direction((0, -1)))
        self.master.bind("<Down>", lambda e: self.snake.set_direction((0, 1)))
        self.master.bind("<Left>", lambda e: self.snake.set_direction((-1, 0)))
        self.master.bind("<Right>", lambda e: self.snake.set_direction((1, 0)))

    def _game_loop(self):
        """Main game loop using after."""
        if not self._running:
            return
        new_head = self.snake.move()
        # Check collisions
        if self.snake.collides_with_wall() or self.snake.collides_with_self():
            self._running = False
            self.canvas.create_text(
                GRID_WIDTH * CELL_SIZE / 2,
                GRID_HEIGHT * CELL_SIZE / 2,
                text="Game Over",
                fill="white",
                font=("Arial", 24),
            )
            return
        # Check food
        if new_head == self.food.position:
            self.score += 1
            self.food.spawn(self.snake.body)
        else:
            # No growth
            pass
        self._draw()
        # Schedule next move
        self.master.after(150, self._game_loop)

# ---------- Entry Point ----------
def main():
    root = tk.Tk()
    SnakeGame(root)
    root.mainloop()

if __name__ == "__main__":
    main()