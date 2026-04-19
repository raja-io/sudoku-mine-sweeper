"""Solves a Sudoku puzzle using backtracking."""
from __future__ import annotations

import random
from typing import List, Optional

from sudoku.board import SIZE, Board, Cell
from sudoku.validator import Validator

# Safety cap to bail out on unsolvable or degenerate boards; well above the ~100k nodes visited by a typical puzzle,
# but low enough to avoid hours of searching on an extreme input.
MAX_SEARCH_NODES = 500_000


class Solver:
    """Backtracking solver. Never modifies the input board. Returns a solved clone or None."""

    def __init__(self, rng: Optional[random.Random] = None) -> None:
        self._rng = rng or random.Random()
        self._validator = Validator()
        self._nodes_visited = 0

    def solve(self, board: Board) -> Optional[Board]:
        """Return a solved clone of `board`, or None if no solution exists.

        Returns None when the board already violates a rule, when no valid completion is possible or when the search
        exceeds MAX_SEARCH_NODES (a safety cap against extreme inputs).
        """
        if self._validator.find_first_violation(board) is not None:
            return None
        work = board.clone()
        self._nodes_visited = 0
        if self._backtrack(work):
            return work
        return None

    def _backtrack(self, board: Board) -> bool:
        self._nodes_visited += 1
        if self._nodes_visited > MAX_SEARCH_NODES:
            return False
        cell = self._next_empty_cell(board)
        if cell is None:
            return True
        for value in self._attempt_values():
            if self._validator.is_placement_legal(board, cell, value):
                board.set(cell, value)
                if self._backtrack(board):
                    return True
                board.clear(cell)
        return False

    @staticmethod
    def _next_empty_cell(board: Board) -> Optional[Cell]:
        for r in range(SIZE):
            for c in range(SIZE):
                if board.is_empty(Cell(r, c)):
                    return Cell(r, c)
        return None

    def _attempt_values(self) -> List[int]:
        values = list(range(1, 10))
        self._rng.shuffle(values)
        return values
