"""Sudoku rule validator to check for rows, columns, and 3x3 subgrids violations."""
from __future__ import annotations

from typing import List, Optional

from sudoku.board import (
    EMPTY,
    MAX_VALUE,
    MIN_VALUE,
    ROW_LETTERS,
    SIZE,
    SUBGRID,
    Board,
    Cell,
)


class Validator:
    """Two entry points: find_first_violation for the whole board, is_placement_legal for a single cell."""

    @staticmethod
    def is_valid_value(value: int) -> bool:
        return MIN_VALUE <= value <= MAX_VALUE

    def find_first_violation(self, board: Board) -> Optional[str]:
        """Return the first violation message, or None if the board is clean."""
        if msg := self._scan_rows(board):
            return msg
        if msg := self._scan_columns(board):
            return msg
        if msg := self._scan_subgrids(board):
            return msg
        return None

    def is_placement_legal(self, board: Board, cell: Cell, value: int) -> bool:
        """Check if a value can be placed at a cell without violating rules."""
        if not self.is_valid_value(value):
            return False
        return not (
            self._conflicts_in_row(board, cell, value)
            or self._conflicts_in_column(board, cell, value)
            or self._conflicts_in_subgrid(board, cell, value)
        )

    def _conflicts_in_row(self, board: Board, cell: Cell, value: int) -> bool:
        for c in range(SIZE):
            if c != cell.col and board.get(Cell(cell.row, c)) == value:
                return True
        return False

    def _conflicts_in_column(self, board: Board, cell: Cell, value: int) -> bool:
        for r in range(SIZE):
            if r != cell.row and board.get(Cell(r, cell.col)) == value:
                return True
        return False

    def _conflicts_in_subgrid(self, board: Board, cell: Cell, value: int) -> bool:
        start_row = (cell.row // SUBGRID) * SUBGRID
        start_col = (cell.col // SUBGRID) * SUBGRID
        for r in range(start_row, start_row + SUBGRID):
            for c in range(start_col, start_col + SUBGRID):
                if (r, c) != (cell.row, cell.col) and board.get(Cell(r, c)) == value:
                    return True
        return False

    def _scan_rows(self, board: Board) -> Optional[str]:
        for r in range(SIZE):
            conflicting_value = self._first_conflicting_value(board.row_values(r))
            if conflicting_value is not None:
                return f"Number {conflicting_value} already exists in Row {ROW_LETTERS[r]}."
        return None

    def _scan_columns(self, board: Board) -> Optional[str]:
        for c in range(SIZE):
            conflicting_value = self._first_conflicting_value(board.column_values(c))
            if conflicting_value is not None:
                return f"Number {conflicting_value} already exists in Column {c + 1}."
        return None

    def _scan_subgrids(self, board: Board) -> Optional[str]:
        for box_row in range(0, SIZE, SUBGRID):
            for box_col in range(0, SIZE, SUBGRID):
                conflicting_value = self._first_conflicting_value(
                    board.subgrid_values(box_row, box_col)
                )
                if conflicting_value is not None:
                    return f"Number {conflicting_value} already exists in the same {SUBGRID}\u00d7{SUBGRID} subgrid."
        return None

    def _first_conflicting_value(self, values: List[int]) -> Optional[int]:
        """Return the first duplicated value in the list, ignoring empty cells."""
        seen = set()
        for v in values:
            if v == EMPTY:
                continue
            if v in seen:
                return v
            seen.add(v)
        return None
