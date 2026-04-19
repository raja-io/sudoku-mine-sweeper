"""Grid, Cell, and pre-fill tracking for a 9×9 Sudoku board."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator, List, Sequence

SIZE = 9
SUBGRID = 3
EMPTY = 0
MIN_VALUE = 1
MAX_VALUE = 9
ROW_LETTERS = "ABCDEFGHI"


@dataclass(frozen=True)
class Cell:
    """A zero-indexed (row, col) position on the board."""

    row: int
    col: int

    def __post_init__(self) -> None:
        if not (0 <= self.row < SIZE and 0 <= self.col < SIZE):
            raise ValueError(f"Cell out of bounds: ({self.row}, {self.col})")


class PreFilledCellPermissionError(ValueError):
    """Raised when attempting to modify a pre-filled cell."""


class Board:
    """9×9 Sudoku grid. Cells loaded via from_grid() are pre-filled and immutable."""

    def __init__(self) -> None:
        self._grid: List[List[int]] = [[EMPTY] * SIZE for _ in range(SIZE)]
        self._prefilled: List[List[bool]] = [[False] * SIZE for _ in range(SIZE)]

    @classmethod
    def from_grid(cls, grid: Sequence[Sequence[int]]) -> "Board":
        """Build a Board from a 9x9 grid; non-zero cells count as pre-filled."""
        cls._validate_shape(grid)
        board = cls()
        for r in range(SIZE):
            for c in range(SIZE):
                value = grid[r][c]
                if type(value) is not int:
                    raise ValueError(
                        f"Cell at row {r + 1}, column {c + 1} must be 0 (empty) or a number from 1 to 9."
                    )
                if value != EMPTY and not (MIN_VALUE <= value <= MAX_VALUE):
                    raise ValueError(
                        f"Cell at row {r + 1}, column {c + 1} has value {value} — must be 1 to 9."
                    )
                board._grid[r][c] = value
                board._prefilled[r][c] = value != EMPTY
        return board

    @staticmethod
    def _validate_shape(grid: Sequence[Sequence[int]]) -> None:
        if len(grid) != SIZE or any(len(row) != SIZE for row in grid):
            raise ValueError(f"Grid must be {SIZE}x{SIZE}")

    def get(self, cell: Cell) -> int:
        return self._grid[cell.row][cell.col]

    def is_prefilled(self, cell: Cell) -> bool:
        return self._prefilled[cell.row][cell.col]

    def is_empty(self, cell: Cell) -> bool:
        return self.get(cell) == EMPTY

    def row_values(self, row: int) -> List[int]:
        return list(self._grid[row])

    def column_values(self, col: int) -> List[int]:
        return [self._grid[r][col] for r in range(SIZE)]

    def subgrid_values(self, row: int, col: int) -> List[int]:
        start_row = (row // SUBGRID) * SUBGRID
        start_col = (col // SUBGRID) * SUBGRID
        return [
            self._grid[r][c]
            for r in range(start_row, start_row + SUBGRID)
            for c in range(start_col, start_col + SUBGRID)
        ]

    def as_grid(self) -> List[List[int]]:
        """Return a snapshot of the grid as a plain list of lists."""
        return [row[:] for row in self._grid]

    def set(self, cell: Cell, value: int) -> None:
        if not (MIN_VALUE <= value <= MAX_VALUE):
            raise ValueError(f"Value {value} not in 1-9")
        if self.is_prefilled(cell):
            raise PreFilledCellPermissionError(f"Cell {cell} is pre-filled")
        self._grid[cell.row][cell.col] = value

    def clear(self, cell: Cell) -> None:
        if self.is_prefilled(cell):
            raise PreFilledCellPermissionError(f"Cell {cell} is pre-filled")
        self._grid[cell.row][cell.col] = EMPTY

    def all_cells(self) -> Iterator[Cell]:
        for r in range(SIZE):
            for c in range(SIZE):
                yield Cell(r, c)

    def empty_cells(self) -> Iterator[Cell]:
        for cell in self.all_cells():
            if self.get(cell) == EMPTY:
                yield cell

    def is_complete(self) -> bool:
        """True when every cell has a value filled."""
        return all(not self.is_empty(cell) for cell in self.all_cells())

    def clone(self) -> "Board":
        board_copy = Board()
        board_copy._grid = [row[:] for row in self._grid]
        board_copy._prefilled = [row[:] for row in self._prefilled]
        return board_copy

    def frozen_copy(self) -> "Board":
        """Return an immutable clone by setting all filled cell as pre-filled."""
        copy = self.clone()
        copy._prefilled = [[v != EMPTY for v in row] for row in copy._grid]
        return copy