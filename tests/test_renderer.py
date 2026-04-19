"""Tests for Renderer output."""
from sudoku.board import Board
from sudoku.renderer import Renderer


EXPECTED_BOARD_OUTPUT = (
    "    1 2 3 4 5 6 7 8 9\n"
    "  A 5 3 _ _ 7 _ _ _ _\n"
    "  B 6 _ _ 1 9 5 _ _ _\n"
    "  C _ 9 8 _ _ _ _ 6 _\n"
    "  D 8 _ _ _ 6 _ _ _ 3\n"
    "  E 4 _ _ 8 _ 3 _ _ 1\n"
    "  F 7 _ _ _ 2 _ _ _ 6\n"
    "  G _ 6 _ _ _ _ 2 8 _\n"
    "  H _ _ _ 4 1 9 _ _ 5\n"
    "  I _ _ _ _ 8 _ _ 7 9"
)


class TestRender:
    def test_matches_sample_render_exactly(self, puzzle_grid):
        board = Board.from_grid(puzzle_grid)
        assert Renderer().render(board) == EXPECTED_BOARD_OUTPUT

    def test_empty_cells_rendered_as_underscore(self):
        board = Board()
        output = Renderer().render(board)
        assert output.count("_") == 81

    def test_row_headers_a_through_i(self):
        output = Renderer().render(Board())
        for letter in "ABCDEFGHI":
            assert f"  {letter} " in output

    def test_column_header_numbered_1_to_9(self):
        output = Renderer().render(Board())
        first_line = output.splitlines()[0]
        assert first_line == "    1 2 3 4 5 6 7 8 9"

    def test_filled_cells_render_as_digits_not_underscores(self, solution_grid):
        board = Board.from_grid(solution_grid)
        output = Renderer().render(board)
        assert "_" not in output
        assert output.count("1") >= 1
