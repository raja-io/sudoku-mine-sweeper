"""Generates a Sudoku puzzle by solving a blank board, then randomly removing
cells until 30 clues remain. The solution is kept alongside the puzzle so the
game can verify answers and provide hints without re-solving."""
from __future__ import annotations

import random
from typing import Optional, Tuple

from sudoku.board import EMPTY, SIZE, Board
from sudoku.solver import Solver

PREFILLED_CLUE_COUNT = 30


class Generator:
    """Produces a (puzzle, solution) pair on each call to generate()."""

    def __init__(self, rng: Optional[random.Random] = None) -> None:
        self._rng = rng or random.Random()

    def generate(self) -> Tuple[Board, Board]:
        """Return (puzzle, solution) where puzzle has PREFILLED_CLUE_COUNT clues.
          The puzzle is a strict subset of the solution"""
        solution = self._build_full_solution()
        puzzle = self._make_puzzle_board(solution, PREFILLED_CLUE_COUNT)
        return puzzle, solution

    def _build_full_solution(self) -> Board:
        solved_board = Solver(self._rng).solve(Board())
        if solved_board is None:
            raise RuntimeError("Failed to generate a valid puzzle")
        return solved_board

    def _make_puzzle_board(self, solution: Board, clue_count: int) -> Board:
        # removes the values to make puzzle Board from a solution Board.
        # It does not verify the puzzle has a unique solution.
        cells = list(solution.all_cells())
        self._rng.shuffle(cells)

        grid = solution.as_grid()
        removal_count = (SIZE * SIZE) - clue_count
        for cell in cells[:removal_count]:
            grid[cell.row][cell.col] = EMPTY

        return Board.from_grid(grid)
