import curses
import random
from typing import List, Tuple, Optional

# Type alias for coordinates
Coord = Tuple[int, int]

class Snake:
    """Represents the snake with its body segments and movement logic."""
    DIRECTIONS = {
        curses.KEY_UP: (0, -1),
        curses.KEY_DOWN: (0, 1),
        curses.KEY_LEFT: (-1, 0),
        curses.KEY_RIGHT: (1, 0),
    }

    def __init__(self, init_pos: Coord, init_length: int = 3, init_dir: int = curses.KEY_RIGHT):
        self.body: List[Coord] = [init_pos]
        self.direction: int = init_dir
        self.grow_pending: int = 0
        # Initialize snake body
        for _ in range(1, init_length):
            self._move_forward(instant=True)

    def _move_forward(self, instant: bool = False) -> None:
        """Move snake forward in the current direction."""
        dx, dy = self.DIRECTIONS[self.direction]
        head_x, head_y = self.body[0]
        new_head = (head_x + dx, head_y + dy)
        self.body.insert(0, new_head)
        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            self.body.pop()

    def change_direction(self, new_dir: int) -> None:
        """Change direction if it's not directly opposite."""
        if new_dir not in self.DIRECTIONS:
            return
        opposite = {curses.KEY_UP: curses.KEY_DOWN,
                    curses.KEY_DOWN: curses.KEY_UP,
                    curses.KEY_LEFT: curses.KEY_RIGHT,
                    curses.KEY_RIGHT: curses.KEY_LEFT}
        if opposite[new_dir] != self.direction:
            self.direction = new_dir

    def grow(self, amount: int = 1) -> None:
        """Schedule snake to grow by given amount."""
        self.grow_pending += amount

    def get_head(self) -> Coord:
        return self.body[0]

    def collides_with_self(self) -> bool:
        """Check if snake collides with its own body."""
        return self.get_head() in self.body[1:]

    def move(self) -> None:
        """Advance the snake by one step."""
        self._move_forward()


class Food:
    """Represents food item in the game."""
    def __init__(self, width: int, height: int, snake: Snake):
        self.width = width
        self.height = height
        self.snake = snake
        self.position: Optional[Coord] = None
        self.spawn()

    def spawn(self) -> None:
        """Spawn food at a random location not occupied by the snake."""
        available = [(x, y)
                     for x in range(1, self.width - 1)
                     for y in range(1, self.height - 1)
                     if (x, y) not in self.snake.body]
        if not available:
            self.position = None
            return
        self.position = random.choice(available)


class Game:
    """Main game logic, independent of any UI."""
    def __init__(self, width: int = 40, height: int = 20):
        self.width = width
        self.height = height
        init_pos = (width // 2, height // 2)
        self.snake = Snake(init_pos)
        self.food = Food(width, height, self.snake)
        self.score = 0
        self.game_over = False

    def update(self, key: Optional[int]) -> None:
        """Process input and update game state."""
        if key is not None:
            self.snake.change_direction(key)
        self.snake.move()

        # Check wall collision
        head_x, head_y = self.snake.get_head()
        if head_x <= 0 or head_x >= self.width - 1 or head_y <= 0 or head_y >= self.height - 1:
            self.game_over = True
            return

        # Check self collision
        if self.snake.collides_with_self():
            self.game_over = True
            return

        # Check food collision
        if self.snake.get_head() == self.food.position:
            self.snake.grow()
            self.score += 1
            self.food.spawn()

    def get_display(self) -> List[str]:
        """Return a list of strings representing the current screen."""
        screen = [[' ' for _ in range(self.width)] for _ in range(self.height)]

        # Walls
        for x in range(self.width):
            screen[0][x] = '#'
            screen[self.height - 1][x] = '#'
        for y in range(self.height):
            screen[y][0] = '#'
            screen[y][self.width - 1] = '#'

        # Food
        if self.food.position:
            fx, fy = self.food.position
            screen[fy][fx] = '*'

        # Snake
        for idx, (x, y) in enumerate(self.snake.body):
            screen[y][x] = 'O' if idx == 0 else 'o'

        return [''.join(row) for row in screen]


def run(stdscr):
    """Run the game loop using curses. This function is guarded to avoid running during tests."""
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(100)

    game = Game()
    while not game.game_over:
        key = stdscr.getch()
        game.update(key)
        screen_lines = game.get_display()
        for y, line in enumerate(screen_lines):
            stdscr.addstr(y, 0, line)
        stdscr.addstr(game.height, 0, f"Score: {game.score}")
        stdscr.refresh()

    stdscr.nodelay(False)
    stdscr.addstr(game.height // 2, game.width // 2 - 5, "GAME OVER")
    stdscr.addstr(game.height // 2 + 1, game.width // 2 - 7, f"Final Score: {game.score}")
    stdscr.addstr(game.height // 2 + 3, game.width // 2 - 12, "Press any key to exit...")
    stdscr.getch()


if __name__ == "__main__":
    curses.wrapper(run)