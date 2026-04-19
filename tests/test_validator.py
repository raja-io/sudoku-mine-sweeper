"""Tests for rule validation."""
import pytest

from sudoku.board import Board, Cell
from sudoku.validator import Validator


def _empty_grid():
    return [[0] * 9 for _ in range(9)]


class TestFindFirstViolation:
    def test_empty_board_has_no_violation(self):
        assert Validator().find_first_violation(Board()) is None

    def test_row_duplicate_reported_with_row_letter(self):
        grid = _empty_grid()
        grid[0][1] = 3
        grid[0][2] = 3  # duplicate in row A
        board = Board.from_grid(grid)
        message = Validator().find_first_violation(board)
        assert message == "Number 3 already exists in Row A."

    def test_column_duplicate_reported_with_column_number(self):
        grid = _empty_grid()
        grid[0][0] = 5
        grid[2][0] = 5  # duplicate in column 1
        board = Board.from_grid(grid)
        message = Validator().find_first_violation(board)
        assert message == "Number 5 already exists in Column 1."

    def test_subgrid_duplicate_reported(self):
        grid = _empty_grid()
        grid[0][2] = 8
        grid[1][0] = 8  # same top-left 3x3 block
        board = Board.from_grid(grid)
        message = Validator().find_first_violation(board)
        assert message == "Number 8 already exists in the same 3\u00d73 subgrid."

    def test_row_violation_takes_precedence_over_column(self):
        grid = _empty_grid()
        grid[0][0] = 3
        grid[0][5] = 3  # row A
        grid[4][8] = 7
        grid[6][8] = 7  # column 9
        board = Board.from_grid(grid)
        message = Validator().find_first_violation(board)
        assert message.startswith("Number 3 already exists in Row A")


class TestRowLabels:
    @pytest.mark.parametrize("idx,letter", list(enumerate("ABCDEFGHI")))
    def test_row_labeled_with_its_letter(self, idx, letter):
        grid = _empty_grid()
        grid[idx][0] = 2
        grid[idx][1] = 2
        board = Board.from_grid(grid)
        message = Validator().find_first_violation(board)
        assert f"Row {letter}" in message


class TestColumnLabels:
    @pytest.mark.parametrize("col", range(9))
    def test_column_labeled_with_its_number(self, col):
        grid = _empty_grid()
        grid[0][col] = 4
        grid[1][col] = 4
        board = Board.from_grid(grid)
        message = Validator().find_first_violation(board)
        assert f"Column {col + 1}" in message


class TestValueRange:
    def test_is_valid_value_accepts_1_to_9(self):
        validator = Validator()
        for i in range(1, 10):
            assert validator.is_valid_value(i) is True

    def test_is_valid_value_rejects_out_of_range(self):
        validator = Validator()
        assert validator.is_valid_value(0) is False
        assert validator.is_valid_value(10) is False
        assert validator.is_valid_value(-1) is False


class TestCellLegality:
    def test_legal_placement_when_no_conflict(self):
        grid = _empty_grid()
        grid[0][0] = 5
        board = Board.from_grid(grid)
        assert Validator().is_placement_legal(board, Cell(4, 4), 7) is True

    @pytest.mark.parametrize(
        "target,reason",
        [
            (Cell(0, 5), "row"),
            (Cell(5, 0), "column"),
            (Cell(2, 2), "subgrid"),
        ],
    )
    def test_illegal_when_value_already_in_same_unit(self, target, reason):
        grid = _empty_grid()
        grid[0][0] = 5  # shares row 0, col 0, and top-left block with all targets
        board = Board.from_grid(grid)
        assert not Validator().is_placement_legal(board, target, 5), (
            f"expected {reason} conflict to block placement"
        )
