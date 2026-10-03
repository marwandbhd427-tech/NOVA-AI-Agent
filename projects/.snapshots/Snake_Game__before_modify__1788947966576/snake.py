import random
import time
import curses
from dataclasses import dataclass
from typing import List, Tuple, Optional

# ---------- Core Data Structures ----------

@dataclass(frozen=True)
class Position:
    y: int
    x: int

class Snake:
    """Represents the snake."""
    def __init__(self, init_pos: Position, init_dir: Tuple[int, int]):
        self.body: List[Position] = [init_pos]
        self.direction: Tuple[int, int] = init_dir
        self.grow_pending: int = 0

    def set_direction(self, new_dir: Tuple[int, int]) -> None:
        # Prevent reverse direction
        if (self.direction[0] * -1, self.direction[1] * -1) != new_dir:
            self.direction = new_dir

    def move(self) -> None:
        head = self.body[0]
        new_head = Position(head.y + self.direction[0], head.x + self.direction[1])
        self.body.insert(0, new_head)
        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            self.body.pop()

    def grow(self, amount: int = 1) -> None:
        self.grow_pending += amount

    def collides_with_self(self) -> bool:
        return self.body[0] in self.body[1:]

    def collides_with(self, pos: Position) -> bool:
        return pos in self.body

class Bot(Snake):
    """Autonomous snake that moves randomly."""
    def __init__(self, init_pos: Position, init_dir: Tuple[int, int], game: 'Game'):
        super().__init__(init_pos, init_dir)
        self.game = game

    def move(self) -> None:
        # Randomly choose a new direction that doesn't reverse
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        reverse = (-self.direction[0], -self.direction[1])
        directions = [d for d in directions if d != reverse]
        self.direction = random.choice(directions)
        super().move()
        # If hit wall, reverse direction and move again
        head = self.body[0]
        if head.y <= 0 or head.y >= self.game.height - 1 or head.x <= 0 or head.x >= self.game.width - 1:
            self.direction = (-self.direction[0], -self.direction[1])
            super().move()

class Food:
    """Represents the food item."""
    def __init__(self, position: Position):
        self.position = position

# ---------- Store Implementation ----------

class Store:
    """
    A simple in-game store that allows the player to purchase items
    using points earned from eating food. Currently supports two items:
    - speed: increases snake speed (placeholder effect)
    - length: grows the snake by 5 segments
    """
    def __init__(self):
        self.items = {
            'speed': {'price': 5, 'effect': 'increase_speed'},
            'length': {'price': 10, 'effect': 'grow'}
        }

    def buy(self, item_name: str, game: 'Game') -> bool:
        """
        Attempt to purchase an item. Returns True if successful.
        """
        if item_name not in self.items:
            return False
        price = self.items[item_name]['price']
        if game.score < price:
            return False
        game.score -= price
        effect = self.items[item_name]['effect']
        if effect == 'grow':
            game.snake.grow(5)
        # Placeholder: speed effect could be implemented by reducing timeout
        return True

# ---------- Game Logic ----------

class Game:
    """Encapsulates the game state and logic."""
    def __init__(self, height: int = 20, width: int = 40):
        self.height = height
        self.width = width
        init_pos = Position(height // 2, width // 2)
        self.snake = Snake(init_pos, (0, 1))  # moving right initially
        self.food = self.spawn_food()
        self.score = 0
        self.game_over = False
        self.store = Store()
        self.bots: List[Snake] = []
        self._create_bots()

    def _create_bots(self) -> None:
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        for _ in range(3):
            pos = self._get_random_empty_position()
            init_dir = random.choice(directions)
            bot = Bot(pos, init_dir, self)