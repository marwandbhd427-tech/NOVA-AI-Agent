import random
import sys
from dataclasses import dataclass
from typing import List, Tuple, Optional

# ----------------------------------------------------------------------
# Configuration constants
# ----------------------------------------------------------------------
CELL_SIZE = 20          # Size of each grid cell in pixels
GRID_WIDTH = 20         # Number of cells horizontally
GRID_HEIGHT = 20        # Number of cells vertically
INITIAL_SNAKE_LENGTH = 3
MOVE_DELAY = 150        # Milliseconds between moves

# ----------------------------------------------------------------------
# Core data structures
# ----------------------------------------------------------------------
@dataclass(frozen=True)
class Position:
    x: int
    y: int

# ----------------------------------------------------------------------
# Snake implementation
# ----------------------------------------------------------------------
class Snake:
    """Represents the snake, its body, and movement logic."""
    def __init__(self, init_length: int = INITIAL_SNAKE_LENGTH) -> None:
        mid_x = GRID_WIDTH // 2
        mid_y = GRID_HEIGHT // 2
        self.body: List[Position] = [
            Position(mid_x - i, mid_y) for i in range(init_length)
        ]
        self.direction: Tuple[int, int] = (1, 0)  # Initially moving right
        self.pending_growth: int = 0

    def head(self) -> Position:
        return self.body[0]

    def set_direction(self, new_dir: Tuple[int, int]) -> None:
        """Change direction unless it's directly opposite."""
        opposite = (-self.direction[0], -self.direction[1])
        if new_dir != opposite:
            self.direction = new_dir

    def move(self) -> None:
        """Move the snake one step in the current direction."""
        new_head = Position(
            self.head().x + self.direction[0],
            self.head().y + self.direction[1]
        )
        self.body.insert(0, new_head)
        if self.pending_growth > 0:
            self.pending_growth -= 1
        else:
            self.body.pop()

    def grow(self, amount: int = 1) -> None:
        """Increase the snake's length by the specified amount."""
        self.pending_growth += amount

    def collides_with_self(self) -> bool:
        """Check if the head collides with the body."""
        return self.head() in self.body[1:]

    def collides_with_position(self, pos: Position) -> bool:
        return pos in self.body

# ----------------------------------------------------------------------
# Food implementation
# ----------------------------------------------------------------------
class Food:
    """Represents food that appears on the grid."""
    def __init__(self, snake: Snake) -> None:
        self.position: Optional[Position] = None
        self.spawn(snake)

    def spawn(self, snake: Snake) -> None:
        """Place food at a random position not occupied by the snake."""
        available: List[Position] = [
            Position(x, y)
            for x in range(GRID_WIDTH)
            for y in range(GRID_HEIGHT)
            if not snake.collides_with_position(Position(x, y))
        ]
        if not available:
            self.position = None
            return
        self.position = random.choice(available)

# ----------------------------------------------------------------------
# Game logic
# ----------------------------------------------------------------------
class Game:
    """Handles the game state and logic."""
    def __init__(self) -> None:
        self.snake = Snake()
        self.food = Food(self.snake)
        self.score = 0
        self.game_over = False

    def reset(self) -> None:
        self.__init__()

    def update(self) -> None:
        """Advance the game state by one step."""
        if self.game_over:
            return

        self.snake.move()

        # Check wall collision
        head = self.snake.head()
        if not (0 <= head.x < GRID_WIDTH and 0 <= head.y < GRID_HEIGHT):
            self.game_over = True
            return

        # Check self collision
        if self.snake.collides_with_self():
            self.game_over = True
            return

        # Check food collision
        if self.food.position == head:
            self.snake.grow()
            self.score += 1
            self.food.spawn(self.snake)

# ----------------------------------------------------------------------
# Optional GUI using Tkinter
# ----------------------------------------------------------------------
def _run_gui() -> None:
    """Run the Snake game with a Tkinter GUI."""
    try:
        import tkinter as tk
    except ImportError:
        print("Tkinter is not available.", file=sys.stderr)
        return

    root = tk.Tk()
    root.title("Snake")

    canvas = tk.Canvas(
        root,
        width=GRID_WIDTH * CELL_SIZE,
        height=GRID_HEIGHT * CELL_SIZE,
        bg="black"
    )
    canvas.pack()

    game = Game()

    # Mapping of key presses to direction vectors
    key_dir_map = {
        "Left": (-1, 0),
        "Right": (1, 0),
        "Up": (0, -1),
        "Down": (0, 1),
    }

    def on_key(event):
        dir_vec = key_dir_map.get(event.keysym)
        if dir_vec:
            game.snake.set_direction(dir_vec)

    root.bind("<Key>", on_key)

    def draw():
        canvas.delete("all")

        # Draw food
        if game.food.position:
            x, y = game.food.position.x, game.food.position.y
            canvas.create_rectangle(
                x * CELL_SIZE,
                y * CELL_SIZE,
                (x + 1) * CELL_SIZE,
                (y + 1) * CELL_SIZE,
                fill="red",
                outline=""
            )

        # Draw snake
        for segment in game.snake.body:
            x, y = segment.x, segment.y
            canvas.create_rectangle(
                x * CELL_SIZE,
                y * CELL_SIZE,
                (x + 1) * CELL_SIZE,
                (y + 1) * CELL_SIZE,
                fill="green",
                outline=""
            )

        # Draw score
        canvas.create_text(
            10,
            10,
            anchor="nw",
            fill="white",
            font=("Arial", 12),
            text=f"Score: {game.score}"
        )

        if game.game_over:
            canvas.create_text(
                GRID_WIDTH * CELL_SIZE // 2,
                GRID_HEIGHT * CELL_SIZE // 2,
                fill="yellow",
                font=("Arial", 24),
                text="Game Over"
            )
        else:
            root.after(MOVE_DELAY, step)

    def step():
        game.update()
        draw()

    # Start the game loop
    root.after(MOVE_DELAY, step)
    root.mainloop()

# ----------------------------------------------------------------------
# Entry point
# ----------------------------------------------------------------------
if __name__ == "__main__":
    _run_gui