import random
import sys
import time

# ---------- Constants ----------
GRID_WIDTH = 20
GRID_HEIGHT = 20
CELL_SIZE = 20  # pixel size, used only if rendering
INITIAL_SNAKE_LENGTH = 3
SNAKE_COLOR = (0, 255, 0)
FOOD_COLOR = (255, 0, 0)
BG_COLOR = (0, 0, 0)
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


# ---------- Snake ----------
class Snake:
    """
    Represents the snake in the game.
    """

    def __init__(self, start_pos=None, length=INITIAL_SNAKE_LENGTH):
        if start_pos is None:
            start_pos = (GRID_WIDTH // 2, GRID_HEIGHT // 2)
        self.body = [start_pos]
        self.direction = "RIGHT"
        self.grow_pending = 0
        # initialize body
        for _ in range(1, length):
            self.move()  # use initial direction to build the snake

    def set_direction(self, new_dir):
        """
        Change direction if not opposite to current.
        """
        if new_dir not in DIRECTIONS:
            return
        if OPPOSITE_DIRECTIONS[new_dir] == self.direction:
            return
        self.direction = new_dir

    def move(self):
        """
        Move snake one step in current direction.
        """
        head_x, head_y = self.body[0]
        delta_x, delta_y = DIRECTIONS[self.direction]
        new_head = ((head_x + delta_x) % GRID_WIDTH, (head_y + delta_y) % GRID_HEIGHT)