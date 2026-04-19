"""Parses user input into Move commands.

Converts raw text input into Move objects, handling case-insensitive commands
and trimming whitespaces.
"""
from __future__ import annotations

from sudoku.board import MAX_VALUE, MIN_VALUE, ROW_LETTERS, SIZE, Cell
from sudoku.move import CheckMove, ClearMove, HintMove, Move, PlaceMove, QuitMove

MAX_COMMAND_LENGTH = 256


class ParseError(ValueError):
    """Raised when the input doesn't match any supported form."""


class CommandParser:
    """Parses a single line of input into a Move. Raises ParseError on bad input."""

    def parse(self, raw: str) -> Move:
        if len(raw) > MAX_COMMAND_LENGTH:
            raise ParseError(
                f"Command too long (max {MAX_COMMAND_LENGTH} chars)."
            )
        tokens = raw.strip().split()
        if not tokens:
            raise ParseError("Empty command.")

        head = tokens[0].lower()
        if head == "hint" and len(tokens) == 1:
            return HintMove()
        if head == "check" and len(tokens) == 1:
            return CheckMove()
        if head == "quit" and len(tokens) == 1:
            return QuitMove()

        if len(tokens) != 2:
            raise ParseError(
                "Unrecognised command. Try '<cell> <value>', '<cell> clear', "
                "'hint', 'check', or 'quit'."
            )

        cell = self._parse_cell(tokens[0])
        action = tokens[1].lower()
        if action == "clear":
            return ClearMove(cell)
        return PlaceMove(cell, self._parse_value(tokens[1]))

    @staticmethod
    def _sanitize_for_display(token: str) -> str:
        """Return token with non-printable characters replaced by '?'."""
        return "".join(ch if ch.isprintable() else "?" for ch in token)

    @staticmethod
    def _parse_cell(token: str) -> Cell:
        if len(token) < 2:
            raise ParseError(f"Invalid cell reference: '{CommandParser._sanitize_for_display(token)}'.")
        row_letter = token[0].upper()
        col_token = token[1:]
        if row_letter not in ROW_LETTERS:
            raise ParseError(
                f"Invalid row '{CommandParser._sanitize_for_display(row_letter)}'. Must be A-I."
            )
        try:
            col_number = int(col_token)
        except ValueError as exc:
            raise ParseError(
                f"Invalid column '{CommandParser._sanitize_for_display(col_token)}'. Must be 1-9."
            ) from exc
        if not (1 <= col_number <= SIZE):
            raise ParseError(f"Column {col_number} out of range 1-9.")
        return Cell(ROW_LETTERS.index(row_letter), col_number - 1)

    @staticmethod
    def _parse_value(token: str) -> int:
        try:
            value = int(token)
        except ValueError as exc:
            raise ParseError(
                f"Invalid value '{CommandParser._sanitize_for_display(token)}'. Must be 1-9."
            ) from exc
        if not (MIN_VALUE <= value <= MAX_VALUE):
            raise ParseError(f"Value {value} out of range 1-9.")
        return value
