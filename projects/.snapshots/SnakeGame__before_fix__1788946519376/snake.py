import random
import curses
import time

# Direction constants
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

OPPOSITE = {
    UP: DOWN,
    DOWN: UP,
    LEFT: RIGHT,
    RIGHT: LEFT,
}

class SnakeGame:
    """
    Core logic for a Snake game.

    Attributes
    ----------
    width : int
        Width of the playing field.
    height : int
        Height of the playing field.
    snake : list[tuple[int, int]]
        List of coordinates representing the snake body. The first element is
        the head.
    direction : tuple[int, int]
        Current movement direction.
    food : tuple[int, int]
        Coordinate of the current food item.
    score : int
        Number of food items eaten.
    alive : bool
        True while the game is running.
    """

    def __init__(self, width=20, height=20, init_length=3):
        self.width = width
        self.height = height
        self.alive = True
        self.score = 0

        # Start snake in the middle moving to the right
        mid_x = width // 2
        mid_y = height // 2
        self.snake = [(mid_x - i, mid_y) for i in range(init_length)]
        self.direction = RIGHT

        self.food = self._spawn_food()

    def _spawn_food(self):
        """Return a random position not occupied by the snake."""
        empty_spaces = [
            (x, y)
            for x in range(self.width)
            for y in range(self.height)
            if (x, y) not in self.snake
        ]
        if not empty_spaces:
            # No space left: player wins
            self.alive = False
            return None
        return random.choice(empty_spaces)

    def _check_collision(self, pos):
        """Return True if pos is outside the field or collides with the snake."""
        x, y = pos
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return True
        if pos in self.snake:
            return True
        return False

    def move(self, new_direction=None):
        """
        Advance the game by one step.

        Parameters
        ----------
        new_direction : tuple[int, int] or None
            New direction to set. Ignored if it would reverse the snake.
        """
        if not self.alive:
            return

        if new_direction and new_direction in OPPOSITE and new_direction != OPPOSITE[self.direction]:
            self.direction = new_direction

        head_x, head_y = self.snake[0]
        dir_x, dir_y = self.direction
        new_head = (head_x + dir_x, head_y + dir_y)

        if self._check_collision(new_head):
            self.alive = False
            return

        self.snake.insert(0, new_head)

        if new_head == self.food:
            self.score += 1
            self.food = self._spawn_food()
        else:
            self.snake.pop()  # remove tail if no food eaten

    def get_board(self):
        """
        Return a 2D list representation of the board for rendering or testing.

        Empty cells are represented by ' ', snake head by 'H', body by 'S',
        and food by 'F'.
        """
        board = [[" " for _ in range(self.width)] for _ in range(self.height)]
        for x, y in self.snake[1:]:
            board[y][x] = "S"
        head_x, head_y = self.snake[0]
        board[head_y][head_x] = "H"
        if self.food:
            fx, fy = self.food
            board[fy][fx] = "F"
        return board

    def __str__(self):
        """Human readable board string."""
        board = self.get_board()
        lines = ["+" + "-" * self.width + "+"]
        for row in board:
            lines.append("|" + "".join(row) + "|")
        lines.append("+" + "-" * self.width + "+")
        lines.append(f"Score: {self.score}")
        return "\n".join(lines)

def _curses_main(stdscr, game):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(100)

    key_map = {
        curses.KEY_UP: UP,
        curses.KEY_DOWN: DOWN,
        curses.KEY_LEFT: LEFT,
        curses.KEY_RIGHT: RIGHT,
    }

    while game.alive:
        stdscr.clear()
        board = game.get_board()
        for y, row in enumerate(board):
            stdscr.addstr(y, 0, "".join(row))
        stdscr.addstr(game.height + 1, 0, f"Score: {game.score}")
        stdscr.refresh()

        try:
            key = stdscr.getch()
        except curses.error:
            key = -1

        if key in key_map:
            game.move(key_map[key])
        else:
            game.move()

        time.sleep(0.1)

    stdscr.nodelay(False)
    stdscr.addstr(game.height + 3, 0, "Game Over! Press any key to exit.")
    stdscr.getch()

def play(width=20, height=20):
    """
    Launch a console Snake game using curses.

    Parameters
    ----------
    width : int
        Width of the playing field.
    height : int
        Height of the playing field.
    """
    game = SnakeGame(width, height)
    curses.wrapper(_curses_main, game)

if __name__ == "__main__":
    play()