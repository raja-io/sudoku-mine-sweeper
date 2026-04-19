"""Tests for the CLI with mocked input and output."""
import random

from sudoku.cli import COMMAND_PROMPT, CLI

WELCOME = "Welcome to Sudoku!"


def _run_cli_capture(commands):
    inputs = iter(commands)
    output_lines: list[str] = []

    def mock_input(_prompt):
        try:
            return next(inputs)
        except StopIteration as exc:
            raise EOFError from exc

    def mock_output(line):
        output_lines.append(line)

    CLI(input_fn=mock_input, output_fn=mock_output, rng=random.Random(15)).run()
    return output_lines


def _run_cli_smoke(commands):
    return "\n".join(_run_cli_capture(commands))


class TestCliSmoke:
    def test_welcome_and_puzzle_displayed(self):
        output_text = _run_cli_smoke(["quit"])
        assert WELCOME in output_text
        assert "Here is your puzzle:" in output_text
        assert "1 2 3 4 5 6 7 8 9" in output_text

    def test_accepts_place_move_and_shows_updated_grid(self):
        output_text = _run_cli_smoke(["hint", "quit"])
        assert "Hint: Cell" in output_text
        assert "Current grid:" in output_text

    def test_invalid_input_prints_error_and_continues(self):
        output_text = _run_cli_smoke(["nonsense", "quit"])
        assert any(
            s in output_text
            for s in ("Unrecognised command", "Empty command", "Invalid")
        )
        assert "Goodbye" in output_text

    def test_check_command_output_lines_validation_result(self):
        output_text = _run_cli_smoke(["check", "quit"])
        assert "No rule violations detected." in output_text

    def test_default_generator_produces_30_clue_board(self):
        lines = _run_cli_capture(["quit"])
        header_idx = lines.index("Here is your puzzle:")
        grid_block = lines[header_idx + 1]
        digit_count = sum(ch.isdigit() for ch in grid_block)
        filled = digit_count - 9  # "    1 2 3 4 5 6 7 8 9" column header
        blanks = grid_block.count("_")
        assert filled == 30
        assert blanks == 51

    def test_command_prompt_shown_before_every_input(self):
        lines = _run_cli_capture(["hint", "check", "quit"])
        assert lines.count(COMMAND_PROMPT) == 3

    def test_multiple_consecutive_parse_errors_do_not_crash(self):
        output_text = _run_cli_smoke(["", "xx", "A99 9", "quit"])
        assert "Goodbye!" in output_text

    def test_welcome_banner_is_followed_by_puzzle_header(self):
        lines = _run_cli_capture(["quit"])
        assert lines[0] == f"{WELCOME}\n"
        assert lines[1] == "Here is your puzzle:"
