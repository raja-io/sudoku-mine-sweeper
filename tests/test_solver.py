"""Tests for the backtracking solver."""
import random

from sudoku.board import Board, Cell
from sudoku.solver import Solver
from sudoku.validator import Validator


class TestSolve:
    def test_solves_known_puzzle(self, puzzle_grid, solution_grid):
        board = Board.from_grid(puzzle_grid)
        solved = Solver().solve(board)
        assert solved is not None
        assert solved.as_grid() == solution_grid

    def test_returns_none_for_unsolvable(self):
        grid = [[0] * 9 for _ in range(9)]
        grid[0][0] = 1
        grid[0][1] = 1  # row conflict, no solution possible
        board = Board.from_grid(grid)
        assert Solver().solve(board) is None

    def test_empty_board_solves_to_valid_full_grid(self):
        solved = Solver().solve(Board())
        assert solved is not None
        assert solved.is_complete()
        assert Validator().find_first_violation(solved) is None

    def test_solver_does_not_mutate_input(self, puzzle_grid):
        board = Board.from_grid(puzzle_grid)
        original = board.as_grid()
        Solver().solve(board)
        assert board.as_grid() == original

    def test_single_blank_is_filled_correctly(self, solution_grid):
        grid = [row[:] for row in solution_grid]
        grid[4][4] = 0  # blank out E5
        board = Board.from_grid(grid)
        solved = Solver().solve(board)
        assert solved is not None
        assert solved.get(Cell(4, 4)) == solution_grid[4][4]
        assert Validator().find_first_violation(solved) is None

    def test_rng_seed_affects_solution_on_empty_board(self):
        solved_a = Solver(random.Random(1)).solve(Board())
        solved_b = Solver(random.Random(2)).solve(Board())
        assert solved_a is not None
        assert solved_b is not None
        assert solved_a.as_grid() != solved_b.as_grid()

    def test_already_complete_board_is_returned_unchanged(self, solution_grid):
        board = Board.from_grid(solution_grid)
        solved = Solver().solve(board)
        assert solved is not None
        assert solved.as_grid() == solution_grid

    def test_solved_board_preserves_all_prefilled_values(self, puzzle_grid, solution_grid):
        board = Board.from_grid(puzzle_grid)
        solved = Solver().solve(board)
        assert solved is not None
        for r, row in enumerate(puzzle_grid):
            for c, val in enumerate(row):
                if val != 0:
                    assert solved.get(Cell(r, c)) == val

    def test_search_cap_returns_none_with_max_one_node(self, monkeypatch):
        monkeypatch.setattr("sudoku.solver.MAX_SEARCH_NODES", 1)
        assert Solver().solve(Board()) is None
