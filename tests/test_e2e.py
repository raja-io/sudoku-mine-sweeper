"""Full-game (e2e) driven through the CLI with scripted I/O."""
import random

import pytest

from sudoku.board import Board
from sudoku.cli import CLI

WELCOME = "Welcome to Sudoku!"
WIN_MESSAGE = "You have successfully completed the Sudoku puzzle!"
GOODBYE = "Goodbye!"
PUZZLE_HEADER = "Here is your puzzle:"
NO_VIOLATIONS = "No rule violations detected."


def _run_cli_e2e(commands, *, puzzle_provider):
    inputs = iter(commands)
    output_lines: list[str] = []

    def mock_input(_prompt):
        try:
            return next(inputs)
        except StopIteration as exc:
            raise EOFError from exc

    def mock_output(line):
        output_lines.append(line)

    CLI(
        input_fn=mock_input,
        output_fn=mock_output,
        rng=random.Random(0),
        puzzle_provider=puzzle_provider,
    ).run()
    return "\n".join(output_lines)


def _puzzle_with_one_blank(solution_grid, row, col):
    grid = [r[:] for r in solution_grid]
    grid[row][col] = 0
    return Board.from_grid(grid), Board.from_grid(solution_grid)


@pytest.mark.e2e
class TestFullPlaythrough:
    def test_player_wins_with_single_correct_placement(self, solution_grid):
        puzzle, solution = _puzzle_with_one_blank(solution_grid, 8, 3)

        printed_text = _run_cli_e2e(
            ["I4 2", "quit"],
            puzzle_provider=lambda: (puzzle, solution),
        )

        assert WELCOME in printed_text
        assert PUZZLE_HEADER in printed_text
        assert WIN_MESSAGE in printed_text
        grid_idx = printed_text.index("Current grid:")
        win_idx = printed_text.index(WIN_MESSAGE, grid_idx)
        prompt_idx = printed_text.index("Press any key and enter to play again...", win_idx)
        assert grid_idx < win_idx < prompt_idx
        assert GOODBYE in printed_text

    def test_hint_alone_can_drive_game_to_win(self, solution_grid):
        puzzle, solution = _puzzle_with_one_blank(solution_grid, 0, 2)

        printed_text = _run_cli_e2e(
            ["hint", "quit"],
            puzzle_provider=lambda: (puzzle, solution),
        )

        assert "Hint: Cell A3 = 4" in printed_text
        assert WIN_MESSAGE in printed_text

    def test_replay_prompt_accepts_any_non_quit_input(self, solution_grid):
        puzzle, solution = _puzzle_with_one_blank(solution_grid, 8, 3)

        printed_text = _run_cli_e2e(
            ["I4 2", "y", "I4 2", "quit"],
            puzzle_provider=lambda: (puzzle, solution),
        )

        assert printed_text.count(PUZZLE_HEADER) == 2
        assert printed_text.count(WIN_MESSAGE) == 2

    def test_commands_are_case_insensitive_end_to_end(self, solution_grid):
        puzzle, solution = _puzzle_with_one_blank(solution_grid, 0, 2)

        printed_text = _run_cli_e2e(
            ["HINT", "Quit"],
            puzzle_provider=lambda: (puzzle, solution),
        )

        assert "Hint: Cell A3 = 4" in printed_text
        assert GOODBYE in printed_text

    def test_invalid_input_then_valid_move_recovers(self, solution_grid):
        puzzle, solution = _puzzle_with_one_blank(solution_grid, 8, 3)

        printed_text = _run_cli_e2e(
            ["Hello..Game", "I4 2", "quit"],
            puzzle_provider=lambda: (puzzle, solution),
        )

        assert "Unrecognised command" in printed_text
        assert WIN_MESSAGE in printed_text

    def test_quit_before_any_move_exits_without_win(self, solution_grid):
        puzzle, solution = _puzzle_with_one_blank(solution_grid, 8, 3)

        printed_text = _run_cli_e2e(
            ["quit"],
            puzzle_provider=lambda: (puzzle, solution),
        )

        assert WIN_MESSAGE not in printed_text
        assert GOODBYE in printed_text

    def test_check_reports_violation_then_clears_after_fix(self, solution_grid):
        puzzle, solution = _puzzle_with_one_blank(solution_grid, 8, 3)

        printed_text = _run_cli_e2e(
            ["I4 9", "check", "I4 clear", "check", "quit"],
            puzzle_provider=lambda: (puzzle, solution),
        )

        assert "Number 9 already exists in" in printed_text
        assert NO_VIOLATIONS in printed_text

    def test_placing_on_prefilled_cell_is_rejected(self, puzzle_grid, solution_grid):
        puzzle = Board.from_grid(puzzle_grid)
        solution = Board.from_grid(solution_grid)

        printed_text = _run_cli_e2e(
            ["A1 9", "quit"],
            puzzle_provider=lambda: (puzzle, solution),
        )

        assert "Invalid move. A1 is pre-filled." in printed_text

    def test_eof_mid_game_exits_cleanly(self, solution_grid):
        puzzle, solution = _puzzle_with_one_blank(solution_grid, 8, 3)

        printed_text = _run_cli_e2e(
            [],
            puzzle_provider=lambda: (puzzle, solution),
        )

        assert WELCOME in printed_text
        assert WIN_MESSAGE not in printed_text

    def test_rejected_move_still_shows_board(self, puzzle_grid, solution_grid):
        puzzle = Board.from_grid(puzzle_grid)
        solution = Board.from_grid(solution_grid)

        printed_text = _run_cli_e2e(
            ["A1 9", "quit"],
            puzzle_provider=lambda: (puzzle, solution),
        )

        reject_idx = printed_text.index("Invalid move. A1 is pre-filled.")
        grid_idx = printed_text.index("Current grid:", reject_idx)
        assert reject_idx < grid_idx

    def test_clear_recovers_from_wrong_placement(self, solution_grid):
        puzzle, solution = _puzzle_with_one_blank(solution_grid, 8, 3)

        printed_text = _run_cli_e2e(
            ["I4 5", "I4 clear", "I4 2", "quit"],
            puzzle_provider=lambda: (puzzle, solution),
        )

        assert WIN_MESSAGE in printed_text

    def test_invalid_value_rejected_end_to_end(self, solution_grid):
        puzzle, solution = _puzzle_with_one_blank(solution_grid, 8, 3)

        printed_text = _run_cli_e2e(
            ["I4 99", "I4 2", "quit"],
            puzzle_provider=lambda: (puzzle, solution),
        )

        assert "Value 99 out of range 1-9." in printed_text
        assert WIN_MESSAGE in printed_text

    def test_hint_on_multi_blank_board(self, solution_grid):
        grid = [row[:] for row in solution_grid]
        grid[0][0] = 0
        grid[0][1] = 0
        grid[0][2] = 0
        puzzle = Board.from_grid(grid)
        solution = Board.from_grid(solution_grid)

        printed_text = _run_cli_e2e(
            ["hint", "quit"],
            puzzle_provider=lambda: (puzzle, solution),
        )

        assert "Hint: Cell " in printed_text
        assert WIN_MESSAGE not in printed_text

    @pytest.mark.parametrize(
        "row,col,command",
        [
            (0, 0, "A1 5"),
            (4, 4, "E5 5"),
            (8, 8, "I9 9"),
            (3, 6, "D7 4"),
            (6, 2, "G3 1"),
            (2, 7, "C8 6"),
        ],
    )
    def test_single_correct_placement_wins_across_cells(
        self, solution_grid, row, col, command
    ):
        puzzle, solution = _puzzle_with_one_blank(solution_grid, row, col)

        printed_text = _run_cli_e2e(
            [command, "quit"],
            puzzle_provider=lambda: (puzzle, solution),
        )

        assert WIN_MESSAGE in printed_text

    def test_long_running_game_with_mixed_commands(self, solution_grid):
        """Drive a puzzle with ten blanks to a win via a long mix of commands."""
        blanks = [
            (0, 2), (0, 5), (1, 1), (2, 0), (3, 1),
            (4, 1), (5, 1), (6, 0), (7, 0), (8, 0),
        ]
        grid = [row[:] for row in solution_grid]
        for r, c in blanks:
            grid[r][c] = 0
        puzzle = Board.from_grid(grid)
        solution = Board.from_grid(solution_grid)

        commands = [
            "A3 4",        # correct
            "A6 9",        # wrong: duplicates A7's 9 in row A
            "check",       # expect violation
            "A6 clear",
            "A6 8",        # correct
            "B2 7",
            "C1 1",
            "D2 5",
            "E2 2",
            "check",       # still valid mid-game
            "F2 1",
            "G1 9",
            "H1 2",
            "hint",        # only I1 left; hint fills it and wins
            "quit",
        ]

        printed_text = _run_cli_e2e(
            commands, puzzle_provider=lambda: (puzzle, solution)
        )

        assert "Number 9 already exists in" in printed_text
        assert NO_VIOLATIONS in printed_text
        assert "Hint: Cell I1 = 3" in printed_text
        assert WIN_MESSAGE in printed_text
        assert GOODBYE in printed_text

    def test_full_flow_two_rounds_exercises_every_command(self, solution_grid):
        """Covers place, clear, check, hint, win, replay, and quit in one flow."""
        puzzle, solution = _puzzle_with_one_blank(solution_grid, 8, 3)

        commands = [
            "check",       # clean board
            "I4 5",        # wrong: duplicates I3's 5 in row I
            "check",       # violation reported
            "I4 clear",
            "check",       # clean again
            "I4 2",        # win round 1
            "y",           # any non-quit answer replays
            "hint",        # single blank -> win round 2
            "quit",
        ]

        printed_text = _run_cli_e2e(
            commands, puzzle_provider=lambda: (puzzle, solution)
        )

        assert printed_text.count(NO_VIOLATIONS) >= 2
        assert "Number 5 already exists in Row I." in printed_text
        assert "Hint: Cell I4 = 2" in printed_text
        assert printed_text.count(WIN_MESSAGE) == 2
        assert printed_text.count(PUZZLE_HEADER) == 2
        assert GOODBYE in printed_text

    def test_full_conftest_puzzle_solved_via_repeated_hints(
        self, puzzle_grid, solution_grid
    ):
        puzzle = Board.from_grid(puzzle_grid)
        solution = Board.from_grid(solution_grid)

        # 51 blanks in _PUZZLE_GRID; 51 hints should fill them all and win.
        commands = ["hint"] * 51 + ["quit"]

        printed_text = _run_cli_e2e(
            commands, puzzle_provider=lambda: (puzzle, solution)
        )

        assert printed_text.count("Hint: Cell ") == 51
        assert WIN_MESSAGE in printed_text
        assert GOODBYE in printed_text

    def test_long_playthrough_on_alternative_board(
        self, alt_puzzle_grid, alt_solution_grid
    ):
        """Long mixed playthrough on the 40-blank alternative board."""
        puzzle = Board.from_grid(alt_puzzle_grid)
        solution = Board.from_grid(alt_solution_grid)

        # Row A solved is 1 2 3 4 5 6 7 8 9; A1, A3, A5, A7, A9 are pre-filled.
        commands = (
            [
                "A2 2",       # correct
                "A4 3",       # wrong: duplicates A3's 3 in row A
                "check",      # expect violation
                "A4 clear",
                "A4 4",       # correct
                "A6 6",       # correct
                "A8 8",       # correct
            ]
            + ["hint"] * 36   # fill the remaining 36 blanks
            + ["quit"]
        )

        printed_text = _run_cli_e2e(
            commands, puzzle_provider=lambda: (puzzle, solution)
        )

        assert "Number 3 already exists in Row A." in printed_text
        assert printed_text.count("Hint: Cell ") == 36
        assert WIN_MESSAGE in printed_text
        assert GOODBYE in printed_text

    def test_replay_uses_fresh_board_not_mutated_state(self, solution_grid):
        """Round 2 must start from a clean puzzle, not round 1's mutated board."""
        puzzle, solution = _puzzle_with_one_blank(solution_grid, 8, 3)

        printed_text = _run_cli_e2e(
            ["I4 2", "", "I4 2", "quit"],
            puzzle_provider=lambda: (puzzle, solution),
        )

        # Row I in the fixture has I4 as 2 in the solved grid.
        blank_row = "  I 3 4 5 _ 8 6 1 7 9"
        solved_row = "  I 3 4 5 2 8 6 1 7 9"

        # Both rounds must win.
        assert printed_text.count(WIN_MESSAGE) == 2
        # The puzzle screen in each round must show I4 as blank again.
        assert printed_text.count(blank_row) == 2
        # The completed grid in each round must show the solved I row.
        assert printed_text.count(solved_row) == 2
