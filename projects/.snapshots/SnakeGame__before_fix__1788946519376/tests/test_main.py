import pytest
import curses
from collections import deque

from game import Game
from snake import Snake, Direction, Point
from constants import (
    BOARD_HEIGHT,
    BOARD_WIDTH,
    INITIAL_SNAKE_LENGTH,
    SNAKE_CHAR,
    FOOD_CHAR,
)

# Helper to create a game with a deterministic food position
def create_game_with_food_at(point: Point) -> Game:
    game = Game()
    game.food.position = point
    return game

def test_initial_state():
    game = Game()
    # Snake should start in the middle of the board
    mid_y, mid_x = BOARD_HEIGHT // 2, BOARD_WIDTH // 2
    assert game.snake.body[0] == Point(mid_y, mid_x)
    # Initial snake length
    assert len(game.snake.body) == INITIAL_SNAKE_LENGTH
    # Score starts at zero
    assert game.score == 0
    # Game is not over initially
    assert not game.game_over

def test_move_without_input():
    game = Game()
    initial_head = game.snake.body[0]
    game.update(-1)  # No key pressed
    new_head = game.snake.body[0]
    # Default direction is RIGHT
    assert new_head == initial_head + (0, 1)

def test_prevent_reverse_direction():
    game = Game()
    # Current direction is RIGHT
    game.update(curses.KEY_LEFT)  # Attempt to