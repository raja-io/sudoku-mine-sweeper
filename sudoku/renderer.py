"""Formats a Board as text, to display in the command line output."""
from __future__ import annotations

from typing import List

from sudoku.board import EMPTY, ROW_LETTERS, SIZE, Board

EMPTY_CELL_CHAR = "_"


class Renderer:

    def render(self, board: Board) -> str:
        """Return the board as a printable string. Empty cells appear as '_'."""
        lines = [self._header()]
        grid = board.as_grid()
        for r in range(SIZE):
            lines.append(self._row_line(ROW_LETTERS[r], grid[r]))
        return "\n".join(lines)

    @staticmethod
    def _header() -> str:
        return "    " + " ".join(str(c + 1) for c in range(SIZE))

    @staticmethod
    def _row_line(label: str, values: List[int]) -> str:
        cells = " ".join(EMPTY_CELL_CHAR if v == EMPTY else str(v) for v in values)
        return f"  {label} {cells}"
