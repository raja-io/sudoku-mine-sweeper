"""Tests for CommandParser."""
import pytest

from sudoku.board import Cell
from sudoku.move import CheckMove, ClearMove, HintMove, PlaceMove, QuitMove
from sudoku.parser import CommandParser, ParseError


class TestPlaceCommand:
    def test_parses_place_move(self):
        move = CommandParser().parse("A3 4")
        assert move == PlaceMove(Cell(0, 2), 4)

    def test_parses_place_move_case_insensitive(self):
        assert CommandParser().parse("i9 7") == PlaceMove(Cell(8, 8), 7)

    def test_parses_place_move_with_extra_whitespace(self):
        assert CommandParser().parse("  B3   7  ") == PlaceMove(Cell(1, 2), 7)

    def test_rejects_invalid_row_letter(self):
        with pytest.raises(ParseError):
            CommandParser().parse("Z3 4")

    def test_rejects_invalid_column_number(self):
        with pytest.raises(ParseError):
            CommandParser().parse("A0 4")
        with pytest.raises(ParseError):
            CommandParser().parse("A10 4")

    def test_rejects_value_out_of_range(self):
        with pytest.raises(ParseError):
            CommandParser().parse("A3 0")
        with pytest.raises(ParseError):
            CommandParser().parse("A3 10")


class TestClearCommand:
    def test_parses_clear_move(self):
        assert CommandParser().parse("C5 clear") == ClearMove(Cell(2, 4))

    def test_parses_clear_case_insensitive(self):
        assert CommandParser().parse("c5 CLEAR") == ClearMove(Cell(2, 4))


class TestKeywordCommands:
    def test_parses_hint(self):
        assert CommandParser().parse("hint") == HintMove()
        assert CommandParser().parse("HINT") == HintMove()

    def test_parses_check(self):
        assert CommandParser().parse("check") == CheckMove()

    def test_parses_quit(self):
        assert CommandParser().parse("quit") == QuitMove()
        assert CommandParser().parse("QUIT") == QuitMove()


class TestMalformedInput:
    def test_empty_string(self):
        with pytest.raises(ParseError):
            CommandParser().parse("")

    def test_unknown_command(self):
        with pytest.raises(ParseError):
            CommandParser().parse("Hello..Game")

    def test_place_missing_value(self):
        with pytest.raises(ParseError):
            CommandParser().parse("A3")

    def test_place_with_non_numeric_value(self):
        with pytest.raises(ParseError):
            CommandParser().parse("A3 x")

    @pytest.mark.parametrize(
        "cmd", ["hint now", "check please", "quit already", "hint a b"]
    )
    def test_keyword_with_extra_tokens_rejected(self, cmd):
        with pytest.raises(ParseError):
            CommandParser().parse(cmd)


class TestInputHardening:
    def test_rejects_excessively_long_command(self):
        from sudoku.parser import MAX_COMMAND_LENGTH

        huge = "A" * (MAX_COMMAND_LENGTH + 1)
        with pytest.raises(ParseError, match="too long"):
            CommandParser().parse(huge)

    def test_accepts_command_at_max_length(self):
        from sudoku.parser import MAX_COMMAND_LENGTH

        padded = "A3 4" + " " * (MAX_COMMAND_LENGTH - 4)
        assert CommandParser().parse(padded) == PlaceMove(Cell(0, 2), 4)

