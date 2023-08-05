# to run unit tests run 'python -m unittest test.test_methods' from project home directory

import io
import unittest
from unittest.mock import patch
from contextlib import redirect_stdout

from oxo_pkg.utils.methods import *


def fill_grid(grid, move_keys, value):
    for key in move_keys:
        setattr(grid, key, Move( key, value))


def remove_move_keys(move_keys):
    some_move_keys = all_move_keys.copy()
    for key in move_keys:
        some_move_keys.remove(key)
    return some_move_keys


class TestMethods(unittest.TestCase):

    def test_health_check(self):
        self.assertEqual(1, 1)

    def test_is_input_valid_false(self):
        self.assertEqual(is_input_valid("x"), False)

    def test_is_input_valid_true(self):
        for values in moves_map.values():
            for input in values:
                self.assertEqual(is_input_valid(input), True)

    def test_input_to_move_key(self):
        self.assertEqual(input_to_move_key("tl"), "topLeft")
        self.assertEqual(input_to_move_key("mm"), "midMid")
        self.assertEqual(input_to_move_key("br"), "bottomRight")

    def test_input_to_move_key_all(self):
        for key, values in moves_map.items():
            for value in values:
                self.assertEqual(input_to_move_key(value), key)


    def test_get_available_move_keys_all(self):
        game = Grid()
        self.assertEqual(get_available_move_keys(game), all_move_keys)

    def test_get_available_move_keys_some(self):
        game = Grid()
        made_moves = ["topLeft", "midMid", "bottomRight"]
        fill_grid(game, made_moves, "O")
        expected = remove_move_keys(made_moves)

        self.assertEqual(get_available_move_keys(game), expected)

    def test_get_available_move_keys_none(self):
        game = Grid()
        fill_grid(game, all_move_keys, "O")
        self.assertEqual(get_available_move_keys(game), [])

    def test_get_available_move_keys_one(self):
        game = Grid()
        almost_all_move_keys = remove_move_keys(["bottomRight"])
        fill_grid(game, almost_all_move_keys, "O")
        self.assertEqual(get_available_move_keys(game), ["bottomRight"])

    def test_is_move_valid_true(self):
        game = Grid()
        self.assertEqual(is_move_valid(game, "midMid"), True)

    def test_is_move_valid_false(self):
        game = Grid()
        setattr(game, "midMid", Move( "midMid", "O"))
        self.assertEqual(is_move_valid(game, "midMid"), False)

    def test_computer_move(self):
        game = Grid()
        almost_all_move_keys = remove_move_keys(["bottomLeft"])
        fill_grid(game, almost_all_move_keys, "X")
        self.assertEqual(computer_move(game), "bottomLeft")

    def test_computer_move_some(self):
        game = Grid()
        made_moves = ["topLeft", "midMid", "bottomRight"]
        fill_grid(game, made_moves, "X")
        remaining_moves = remove_move_keys(made_moves)
        self.assertEqual(computer_move(game) in remaining_moves, True)

    def test_check_for_win_true_x(self):
        game = Grid()
        made_moves = possible_wins[0]
        fill_grid(game, made_moves, "X")
        expected_win = check_for_win(game)
        self.assertEqual(expected_win.win, True)
        self.assertEqual(expected_win.value, "X")

    def test_check_for_win_true_o(self):
        game = Grid()
        made_moves = possible_wins[1]
        fill_grid(game, made_moves, "O")
        expected_win = check_for_win(game)
        self.assertEqual(expected_win.win, True)
        self.assertEqual(expected_win.value, "O")

    def test_check_for_win_false(self):
        game = Grid()
        made_moves_x = ["topMid", "bottomMid"]
        fill_grid(game, made_moves_x, "X")
        setattr(game, "midMid", Move( "midMid", "O"))
        expected_lose = check_for_win(game)
        self.assertEqual(expected_lose.win, False)
        self.assertEqual(expected_lose.value, "-")

    def test_check_for_win_true_all(self):
        for win_set in possible_wins:
            game = Grid()
            fill_grid(game, win_set, "X")
            expected_win = check_for_win(game)
            self.assertEqual(expected_win.win, True)
            self.assertEqual(expected_win.value, "X")


    @patch('oxo_pkg.utils.methods.play_again')
    def test_check_for_win_wrapper_x(self, mock_play_again):

        game = Grid()
        made_moves = possible_wins[0]
        fill_grid(game, made_moves, "X")

        redirected_output = io.StringIO()
        with redirect_stdout(redirected_output):

            check_for_win_wrapper(game, "congratulations! %s's win")

        self.assertIn("congratulations! X's win", redirected_output.getvalue())
        mock_play_again.assert_called()

    @patch('oxo_pkg.utils.methods.play_again')
    def test_check_for_win_wrapper_o(self, mock_play_again):

        game = Grid()
        made_moves = possible_wins[1]
        fill_grid(game, made_moves, "O")

        redirected_output = io.StringIO()
        with redirect_stdout(redirected_output):
            check_for_win_wrapper(game, "you lose! %s's win")

        self.assertIn("you lose! O's win", redirected_output.getvalue())
        mock_play_again.assert_called()

    @patch('oxo_pkg.utils.methods.play_again')
    def test_check_for_draw(self, mock_play_again):

        game = Grid()
        x_moves = ["topRight", "topLeft", "midRight", "bottomLeft", "bottomMid"]
        o_moves = ["topMid", "midLeft", "midMid", "bottomRight"]

        fill_grid(game, x_moves, "X")
        fill_grid(game, o_moves, "O")

        redirected_output = io.StringIO()
        with redirect_stdout(redirected_output):
            check_for_win_wrapper(game, "any string %s")

        self.assertIn("oh ho, its a draw", redirected_output.getvalue())
        mock_play_again.assert_called()

    def test_check_for_draw_false(self):

        game = Grid()
        setattr(game, "topLeft", Move( "topLeft", "X"))
        setattr(game, "bottomRight", Move( "bottomRight", "O"))

        redirected_output = io.StringIO()
        with redirect_stdout(redirected_output):
            check_for_win_wrapper(game, "any string %s")

        self.assertEqual("", redirected_output.getvalue())

    def test_computer_move_hard_goes_for_corners_1(self):
        game = Grid()
        response = computer_move_hard(game)
        self.assertEqual("topLeft", response)

    def test_computer_move_hard_goes_for_corners_2(self):
        game = Grid()
        setattr(game, "topLeft", Move( "topLeft", "X"))
        response = computer_move_hard(game)
        self.assertEqual("topRight", response)

    def test_computer_move_hard_goes_for_corners_3(self):
        game = Grid()
        fill_grid(game, ["topLeft", "topRight"], "X")
        setattr(game, "topMid", Move( "topMid", "O"))
        response = computer_move_hard(game)
        self.assertEqual("bottomLeft", response)

    def test_computer_move_hard_goes_for_corners_4(self):
        game = Grid()
        fill_grid(game, ["topLeft", "topRight"], "O")
        fill_grid(game, ["topMid", "bottomLeft"], "X")
        response = computer_move_hard(game)
        self.assertEqual("bottomRight", response)

    def test_computer_move_hard_blocks_win_1(self):
        game = Grid()
        fill_grid(game, ["topLeft", "topRight"], "X")
        response = computer_move_hard(game)
        self.assertEqual("topMid", response)

    def test_computer_move_hard_blocks_win_2(self):
        game = Grid()
        fill_grid(game, ["bottomLeft", "topRight"], "X")
        fill_grid(game, ["topLeft"], "O")
        response = computer_move_hard(game)
        self.assertEqual("midMid", response)


if __name__ == '__main__':
    unittest.main()
