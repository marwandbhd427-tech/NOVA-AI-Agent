import unittest
from main import Game

class TestSnackGame(unittest.TestCase):
    def setUp(self):
        self.game = Game(width=5, height=5)

    def test_initial_state(self):
        self.assertEqual(self.game.player, (0, 0))
        self.assertEqual(self.game.snacks, set())
        self.assertEqual(self.game.obstacles, set())
        self.assertEqual(self.game.score, 0)

    def test_add_snack_and_collect(self):
        self.game.add_snack(1, 0)
        self.assertIn((1, 0), self.game.snacks)
        self.game.move_player('d')  # move right to (1,0)
        self.assertEqual(self.game.player, (1, 0))
        self.assertNotIn((1, 0), self.game.snacks)
        self.assertEqual(self.game.score, 1)

    def test_add_obstacle_and_block(self):
        self.game.add_obstacle(1, 0)
        self.game.move_player('d')
        # Player should not move into obstacle
        self.assertEqual(self.game.player, (0, 0))
        self.assertIn((1, 0), self.game.obstacles)

    def test_out_of_bounds_move(self):
        self.game.move_player('w')  # up, out of bounds
        self.assertEqual(self.game.player, (0, 0))
        self.game.move_player('a')  # left, out of bounds
        self.assertEqual(self.game.player, (0, 0))

    def test_is_game_over(self):
        self.game.add_snack(1, 1)
        self.assertFalse(self.game.is_game_over())
        self.game.move_player('d')  # move to (1,0)
        self.game.move_player('s')  # move to (1,1) and collect
        self.assertTrue(self.game.is_game_over())

    def test_render_output(self):
        self.game.add_snack(1, 1)
        self.game.add_obstacle(2, 2)
        self.game.move_player('d')
        self.game.move_player('s')
        rendered = self.game.render()
        expected_lines = [
            "P..",
            ".S.",
            "..#",
            "...",
            "..."
        ]
        self.assertEqual(rendered, "\n".join(expected_lines))

if __name__ == "__main__":
    unittest.main()