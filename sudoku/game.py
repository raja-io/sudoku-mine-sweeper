"""One Sudoku game session: board state, reference solution, and win/quit status."""
from __future__ import annotations

import random
from enum import Enum, auto
from typing import Optional

from sudoku.board import Board
from sudoku.move import Move, MoveOutcome, MoveResult
from sudoku.solver import Solver
from sudoku.validator import Validator


class GameStatus(Enum):
    IN_PROGRESS = auto()
    WON = auto()
    QUIT = auto()


class Game:
    """Owns the board state for one round; delegates move logic to Move subclasses."""

    def __init__(
        self,
        puzzle: Board,
        solution: Board,
        rng: Optional[random.Random] = None,
    ) -> None:
        self.board: Board = puzzle.clone()
        self.solution: Board = solution.frozen_copy()
        self.rng: random.Random = rng or random.Random()
        self.validator: Validator = Validator()
        self.solver: Solver = Solver(self.rng)
        self.status: GameStatus = GameStatus.IN_PROGRESS

    def make_move(self, move: Move) -> MoveResult:
        """Run the move and return its result. Rejects moves when the game has ended."""
        if self.status is not GameStatus.IN_PROGRESS:
            return MoveResult(MoveOutcome.REJECTED, "Game already ended.")
        return move.execute(self)

    def check_for_win(self) -> None:
        """Set status to WON if the board is complete and no violation found."""
        if (
            self.board.is_complete()
            and self.validator.find_first_violation(self.board) is None
        ):
            self.status = GameStatus.WON

    def has_won(self) -> bool:
        return self.status is GameStatus.WON

    def quit(self) -> None:
        self.status = GameStatus.QUIT
