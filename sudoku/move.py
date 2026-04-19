"""Defines Move commands and their outcomes.

Each Move subclass implements execute() to act on a Game instance.
Supported commands: place, clear, hint, check, quit.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto
from typing import TYPE_CHECKING, List, Optional, Tuple

from sudoku.board import ROW_LETTERS, Cell

if TYPE_CHECKING:
    from sudoku.game import Game


class MoveOutcome(Enum):
    """Move outcomes, independent of its user-facing message."""

    ACCEPTED = auto()       # Move applied successfully, game continues.
    REJECTED = auto()       # Move refused (invalid input, illegal target, no operation).
    CHECK_OK = auto()       # Check command: board has no rule violations.
    CHECK_FAILED = auto()   # Check command: board has a rule violation.
    WON = auto()            # Move completed the puzzle.
    QUIT = auto()           # Player quit the game.


@dataclass(frozen=True)
class MoveResult:
    """The outcome of a move and a user-facing message."""

    outcome: MoveOutcome
    message: str


class Move(ABC):
    @abstractmethod
    def execute(self, game: "Game") -> MoveResult:
        ...

    @staticmethod
    def cell_label(cell: Cell) -> str:
        """Return the command line readable label for a cell, e.g. Cell(0,2) → 'A3'."""
        return f"{ROW_LETTERS[cell.row]}{cell.col + 1}"


@dataclass(frozen=True)
class PlaceMove(Move):
    cell: Cell
    value: int

    def execute(self, game: "Game") -> MoveResult:
        if not game.validator.is_valid_value(self.value):
            return MoveResult(
                MoveOutcome.REJECTED,
                f"Invalid value {self.value}. Must be 1-9.",
            )
        if game.board.is_prefilled(self.cell):
            return MoveResult(
                MoveOutcome.REJECTED,
                f"Invalid move. {Move.cell_label(self.cell)} is pre-filled.",
            )
        # player to find to violations via 'check' command, not auto-rejected.
        game.board.set(self.cell, self.value)
        game.check_for_win()
        outcome = MoveOutcome.WON if game.has_won() else MoveOutcome.ACCEPTED
        return MoveResult(outcome, "Move accepted.")


@dataclass(frozen=True)
class ClearMove(Move):
    cell: Cell

    def execute(self, game: "Game") -> MoveResult:
        if game.board.is_prefilled(self.cell):
            return MoveResult(
                MoveOutcome.REJECTED,
                f"Invalid move. {Move.cell_label(self.cell)} is pre-filled.",
            )
        if game.board.is_empty(self.cell):
            return MoveResult(
                MoveOutcome.REJECTED,
                f"Cell {Move.cell_label(self.cell)} is already empty.",
            )
        game.board.clear(self.cell)
        return MoveResult(MoveOutcome.ACCEPTED, "Move accepted.")


@dataclass(frozen=True)
class HintMove(Move):
    def execute(self, game: "Game") -> MoveResult:
        empty_cells = self._collect_empty_cells(game)
        if not empty_cells:
            return MoveResult(MoveOutcome.REJECTED, "No empty cells to hint.")

        hint_pick = self._choose_hint(game, empty_cells)
        if hint_pick is None:
            return MoveResult(
                MoveOutcome.REJECTED,
                "No compatible hint available - try clearing recent moves. Then place new values or try hint",
            )

        cell, correct_value = hint_pick
        game.board.set(cell, correct_value)
        game.check_for_win()
        return self._format_result(game, cell, correct_value)

    @staticmethod
    def _collect_empty_cells(game: "Game") -> List[Cell]:
        return list(game.board.empty_cells())

    @staticmethod
    def _choose_hint(
        game: "Game", empty_cells: List[Cell]
    ) -> Optional[Tuple[Cell, int]]:
        """Pick a cell and its correct value for a hint.

        Tries to pick hint from the stored solution first.The stored solution can become incompatible if the player placed wrong moves(values).
        In that case it re-solve from the current board rather than give a bad hint.
        Returns (cell, value), or None if no hint is possible and the board is unsolvable.
        """
        compatible = [
            c for c in empty_cells
            if game.validator.is_placement_legal(
                game.board, c, game.solution.get(c)
            )
        ]
        if compatible:
            cell = game.rng.choice(compatible)
            return cell, game.solution.get(cell)

        fallback_solution = game.solver.solve(game.board)
        if fallback_solution is None:
            return None
        cell = game.rng.choice(empty_cells)
        return cell, fallback_solution.get(cell)

    @staticmethod
    def _format_result(game: "Game", cell: Cell, value: int) -> MoveResult:
        msg = f"Hint: Cell {Move.cell_label(cell)} = {value}"
        outcome = MoveOutcome.WON if game.has_won() else MoveOutcome.ACCEPTED
        return MoveResult(outcome, msg)


@dataclass(frozen=True)
class CheckMove(Move):
    def execute(self, game: "Game") -> MoveResult:
        violation = game.validator.find_first_violation(game.board)
        if violation is None:
            return MoveResult(MoveOutcome.CHECK_OK, "No rule violations detected.")
        return MoveResult(MoveOutcome.CHECK_FAILED, violation)


@dataclass(frozen=True)
class QuitMove(Move):
    def execute(self, game: "Game") -> MoveResult:
        game.quit()
        return MoveResult(MoveOutcome.QUIT, "Goodbye!")