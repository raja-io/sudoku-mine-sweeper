"""Tests for Board state and mutation."""
import pytest

from sudoku.board import Board, Cell, EMPTY, PreFilledCellPermissionError


class TestBoardConstruction:
    def test_empty_board_has_all_empty_cells(self):
        board = Board()
        for row in range(9):
            for col in range(9):
                assert board.get(Cell(row, col)) == EMPTY

    def test_board_from_grid_loads_values(self):
        grid = [[0] * 9 for _ in range(9)]
        grid[0][0] = 5
        grid[8][8] = 9
        board = Board.from_grid(grid)
        assert board.get(Cell(0, 0)) == 5
        assert board.get(Cell(8, 8)) == 9

    def test_from_grid_rejects_wrong_shape(self):
        with pytest.raises(ValueError):
            Board.from_grid([[0] * 8] * 9)
        with pytest.raises(ValueError):
            Board.from_grid([[0] * 9] * 8)

    def test_from_grid_rejects_out_of_range_values(self):
        bad = [[0] * 9 for _ in range(9)]
        bad[0][0] = 10
        with pytest.raises(ValueError):
            Board.from_grid(bad)


class TestPreFilledMask:
    def test_from_grid_marks_non_zero_cells_as_prefilled(self):
        grid = [[0] * 9 for _ in range(9)]
        grid[0][0] = 5
        board = Board.from_grid(grid)
        assert board.is_prefilled(Cell(0, 0)) is True
        assert board.is_prefilled(Cell(0, 1)) is False

    def test_user_set_cells_are_not_prefilled(self):
        board = Board()
        board.set(Cell(4, 4), 7)
        assert board.is_prefilled(Cell(4, 4)) is False


class TestSetAndClear:
    def test_set_writes_value(self):
        board = Board()
        board.set(Cell(3, 4), 7)
        assert board.get(Cell(3, 4)) == 7

    def test_clear_resets_to_empty(self):
        board = Board()
        board.set(Cell(3, 4), 7)
        board.clear(Cell(3, 4))
        assert board.get(Cell(3, 4)) == EMPTY

    def test_set_rejects_value_out_of_range(self):
        board = Board()
        with pytest.raises(ValueError):
            board.set(Cell(0, 0), 0)
        with pytest.raises(ValueError):
            board.set(Cell(0, 0), 10)

    def test_set_rejects_prefilled_cell(self):
        grid = [[0] * 9 for _ in range(9)]
        grid[0][0] = 5
        board = Board.from_grid(grid)
        with pytest.raises(PreFilledCellPermissionError):
            board.set(Cell(0, 0), 6)

    def test_clear_rejects_prefilled_cell(self):
        grid = [[0] * 9 for _ in range(9)]
        grid[0][0] = 5
        board = Board.from_grid(grid)
        with pytest.raises(PreFilledCellPermissionError):
            board.clear(Cell(0, 0))


class TestCompletion:
    def test_empty_board_is_not_complete(self):
        assert Board().is_complete() is False

    def test_fully_filled_board_is_complete(self):
        grid = [[((r * 3 + r // 3 + c) % 9) + 1 for c in range(9)] for r in range(9)]
        board = Board.from_grid(grid)
        assert board.is_complete() is True

    def test_partially_filled_board_is_not_complete(self):
        grid = [[((r * 3 + r // 3 + c) % 9) + 1 for c in range(9)] for r in range(9)]
        grid[0][0] = 0
        board = Board.from_grid(grid)
        assert board.is_complete() is False


class TestEmptyCells:
    def test_empty_cells_lists_zeros_only(self):
        grid = [[0] * 9 for _ in range(9)]
        grid[0][0] = 5
        grid[2][3] = 7
        board = Board.from_grid(grid)
        empties = list(board.empty_cells())
        assert Cell(0, 0) not in empties
        assert Cell(2, 3) not in empties
        assert len(empties) == 79


class TestClone:
    def test_clone_is_independent(self):
        board = Board()
        board.set(Cell(0, 0), 5)
        copy = board.clone()
        copy.set(Cell(1, 1), 9)
        assert board.get(Cell(1, 1)) == EMPTY
        assert copy.get(Cell(0, 0)) == 5

    def test_clone_preserves_prefilled_mask(self):
        grid = [[0] * 9 for _ in range(9)]
        grid[0][0] = 5
        board = Board.from_grid(grid)
        copy = board.clone()
        assert copy.is_prefilled(Cell(0, 0)) is True
