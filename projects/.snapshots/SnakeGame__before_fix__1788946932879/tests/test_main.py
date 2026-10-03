import random
import tkinter as tk

# Constants
CELL_SIZE = 20
GRID_WIDTH = 30   # number of cells horizontally
GRID_HEIGHT = 20  # number of cells vertically
WINDOW_WIDTH = GRID_WIDTH * CELL_SIZE
WINDOW_HEIGHT = GRID_HEIGHT * CELL_SIZE
UPDATE_DELAY = 150  # milliseconds per move

# Direction vectors
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

class Snake:
    """Represents the snake as a list of (x, y) positions."""
    def __init__(self, initial_length=3):
        mid_x = GRID_WIDTH // 2
        mid_y = GRID_HEIGHT // 2
        self.body = [(mid_x, mid_y + i) for i in range(initial_length)][::-1]
        self.direction = UP
        self.growing = False

    def set_direction(self, new_direction):
        """Set new direction unless it's directly opposite."""
        opposite = (-self.direction[0], -self.direction[1])
        if new_direction != opposite:
            self.direction = new_direction

    def move(self):
        """Move the snake one step in the current direction."""
        head_x, head_y = self.body[0]
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)
        self.body.insert(0, new_head)
        if not self.growing:
            self.body.pop()
        else:
            self.growing = False

    def grow(self):
        """Make the snake grow on the next move."""
        self.growing = True

    def collides_with_self(self):
        """Return True if the snake's head collides with its body."""
        head = self.body[0]
        return head in self.body[1:]

    def collides_with_wall(self):
        """Return True if the snake's head is outside the grid."""
        head_x, head_y = self.body[0]
        return not (0 <= head_x < GRID_WIDTH and 0 <= head_y < GRID_HEIGHT)

class Food:
    """Represents a food item."""
    def __init__(self):
        self.position = None

    def spawn(self, snake_body):
        """Place food at a random location not occupied by the snake."""
        while True:
            x = random.randint(0, GRID_WIDTH - 1)
            y = random.randint(0, GRID_HEIGHT - 1)
            if (x, y) not in snake_body:
                self.position = (x, y)
                break

class Game:
    """Main game logic without GUI dependencies."""
    def __init__(self):
        self.snake = Snake()
        self.food = Food()
        self.food.spawn(self.snake.body)
        self.score = 0
        self.running = False

    def reset(self):
        """Reset the game to initial state."""
        self.snake = Snake()
        self.food = Food()
        self.food.spawn(self.snake.body)
        self.score = 0
        self.running = False

    def update(self):
        """Advance the game state by one step."""
        if not self.running:
            return
        self.snake.move()
        head = self.snake.body[0]
        # Check collisions
        if self.snake.collides_with_wall() or self.snake.collides_with_self():
            self.running = False
            return
        if head == self.food.position:
            self.snake.grow()
            self.score += 1
            self.food.spawn(self.snake.body)

    def set_direction(self, direction):
        """Set the snake's moving direction."""
        self.snake.set_direction(direction)

    def get_score(self):
        return self.score

    def is_running(self):
        return self.running

# GUI part – only executed when run as a script
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Snake Game")
    canvas = tk.Canvas(root, width=WINDOW_WIDTH, height=WINDOW_HEIGHT, bg="black")
    canvas.pack()

    game = Game()
    game.running = True

    def draw():
        canvas.delete("all")
        # Draw snake
        for x, y in game.snake.body:
            canvas.create_rectangle(
                x * CELL_SIZE,
                y * CELL_SIZE,
                (x + 1) * CELL_SIZE,
                (y + 1) * CELL_SIZE,
                fill="green",
                outline="darkgreen",
            )
        # Draw food
        fx, fy = game.food.position
        canvas.create_rectangle(
            fx * CELL_SIZE,
            fy * CELL_SIZE,
            (fx + 1) * CELL_SIZE,
            (fy + 1) * CELL_SIZE,
            fill="red",
            outline="darkred",
        )
        # Draw score
        canvas.create_text(
            10,
            10,
            anchor="nw",
            text=f"Score: {game.get_score()}",
            fill="white",
            font=("Arial", 12, "bold"),
        )

    def game_loop():
        if game.is_running():
            game.update()
            draw()
            root.after(UPDATE_DELAY, game_loop)
        else:
            canvas.create_text(
                WINDOW_WIDTH // 2,
                WINDOW_HEIGHT // 2,
                text="Game Over",
                fill="white",
                font=("Arial", 24, "bold"),
            )

    def on_key(event):
        key_map = {
            "Up": UP,
            "Down": DOWN,
            "Left": LEFT,
            "Right": RIGHT,
        }
        if event.keysym in key_map:
            game.set_direction(key_map[event.keysym])

    root.bind("<Key>", on_key)
    game_loop()
    root.mainloop()