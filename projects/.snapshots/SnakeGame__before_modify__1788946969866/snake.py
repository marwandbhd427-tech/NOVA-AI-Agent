import random
import tkinter as tk

# Game configuration constants
CELL_SIZE = 20
GRID_WIDTH = 20
GRID_HEIGHT = 20
INITIAL_SNAKE_LENGTH = 3
SPEED_MS = 150  # milliseconds between moves

# Direction vectors
DIR_VECTORS = {
    "Up": (0, -1),
    "Down": (0, 1),
    "Left": (-1, 0),
    "Right": (1, 0),
}


class Snake:
    """Represents the snake in the game."""

    def __init__(self, start_pos, length=INITIAL_SNAKE_LENGTH):
        self.segments = [start_pos]
        self.direction = "Right"
        # Initialize the rest of the body behind the head
        for i in range(1, length):
            prev_x, prev_y = self.segments[-1]
            self.segments.append((prev_x - 1, prev_y))

    def set_direction(self, new_dir):
        """Set the snake's direction, preventing 180° reversals."""
        if new_dir not in DIR_VECTORS:
            return
        # Prevent reversing onto itself
        opposite = {
            "Up": "Down",
            "Down": "Up",
            "Left": "Right",
            "Right": "Left",
        }
        if opposite[new_dir] == self.direction:
            return
        self.direction = new_dir

    def move(self):
        """Move the snake one cell in the current direction."""
        head_x, head_y = self.segments[0]
        dx, dy = DIR_VECTORS[self.direction]
        new_head = (head_x + dx, head_y + dy)
        # Insert new head and drop the tail
        self.segments = [new_head] + self.segments[:-1]

    def grow(self):
        """Add a new segment at the tail position."""
        tail = self.segments[-1]
        self.segments.append(tail)

    def collision(self):
        """Check if the snake has collided with itself."""
        return len(self.segments) != len(set(self.segments))


class Food:
    """Represents the food item."""

    def __init__(self, width, height, snake_segments):
        self.width = width
        self.height = height
        self.position = self._random_position(snake_segments)

    def _random_position(self, snake_segments):
        """Generate a random position not occupied by the snake."""
        available = [
            (x, y)
            for x in range(self.width)
            for y in range(self.height)
            if (x, y) not in snake_segments
        ]
        if not available:
            # No space left; game will be over
            return None
        return random.choice(available)


class Game:
    """Core game logic."""

    def __init__(self, width=GRID_WIDTH, height=GRID_HEIGHT):
        self.width = width
        self.height = height
        self.snake = Snake(start_pos=(width // 2, height // 2))
        self.food = Food(width, height, self.snake.segments)
        self.score = 0
        self.running = True

    def step(self):
        """Advance the game by one tick."""
        if not self.running:
            return False

        self.snake.move()

        # Check wall collision
        head_x, head_y = self.snake.segments[0]
        if not (0 <= head_x < self.width and 0 <= head_y < self.height):
            self.running = False
            return False

        # Check self collision
        if self.snake.collision():
            self.running = False
            return False

        # Check food collision
        if self.snake.segments[0] == self.food.position:
            self.snake.grow()
            self.score += 1
            self.food = Food(self.width, self.height, self.snake.segments)

        return True


class SnakeGUI:
    """Tkinter GUI for the Snake game."""

    def __init__(self, master):
        self.master = master
        self.master.title("Snake")
        self.canvas = tk.Canvas(
            master,
            width=GRID_WIDTH * CELL_SIZE,
            height=GRID_HEIGHT * CELL_SIZE,
            bg="black",
        )
        self.canvas.pack()
        self.game = Game()
        self._draw()
        self.master.bind("<Key>", self._on_key)
        self._game_loop()

    def _on_key(self, event):
        """Handle arrow key presses."""
        if event.keysym in DIR_VECTORS:
            self.game.snake.set_direction(event.keysym)

    def _draw(self):
        """Render the snake and food."""
        self.canvas.delete("all")
        # Draw food
        fx, fy = self.game.food.position
        self.canvas.create_rectangle(
            fx * CELL_SIZE,
            fy * CELL_SIZE,
            (fx + 1) * CELL_SIZE,
            (fy + 1) * CELL_SIZE,
            fill="red",
            outline="",
        )
        # Draw snake
        for i, (x, y) in enumerate(self.game.snake.segments):
            color = "green" if i == 0 else "lightgreen"
            self.canvas.create_rectangle(
                x * CELL_SIZE,
                y * CELL_SIZE,
                (x + 1) * CELL_SIZE,
                (y + 1) * CELL_SIZE,
                fill=color,
                outline="",
            )