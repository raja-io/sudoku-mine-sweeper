"""Tests for Game, driving moves directly via make_move()."""
import random

from sudoku.board import Board, Cell
from sudoku.game import Game, GameStatus
from sudoku.move import CheckMove, ClearMove, HintMove, MoveOutcome, PlaceMove, QuitMove

MOVE_ACCEPTED = "Move accepted."


class TestPlaceMove:
    def test_accepts_valid_placement(self, sample_game):
        result = sample_game.make_move(PlaceMove(Cell(0, 2), 4))  # A3 4
        assert result.outcome is MoveOutcome.ACCEPTED
        assert result.message == MOVE_ACCEPTED
        assert sample_game.board.get(Cell(0, 2)) == 4

    def test_rejects_prefilled_cell(self, sample_game):
        result = sample_game.make_move(PlaceMove(Cell(0, 0), 6))  # A1 is pre-filled
        assert result.outcome is MoveOutcome.REJECTED
        assert result.message == "Invalid move. A1 is pre-filled."
        assert sample_game.board.get(Cell(0, 0)) == 5

    def test_accepts_move_even_if_it_creates_violation(self, sample_game):
        result = sample_game.make_move(PlaceMove(Cell(0, 2), 3))
        assert result.outcome is MoveOutcome.ACCEPTED
        assert result.message == MOVE_ACCEPTED

    def test_rejects_out_of_range_value_without_raising(self, sample_game):
        result = sample_game.make_move(PlaceMove(Cell(0, 2), 99))
        assert result.outcome is MoveOutcome.REJECTED
        assert "Invalid value 99" in result.message
        assert sample_game.board.is_empty(Cell(0, 2))


class TestClearMove:
    def test_clears_user_filled_cell(self, sample_game):
        sample_game.make_move(PlaceMove(Cell(0, 2), 4))
        result = sample_game.make_move(ClearMove(Cell(0, 2)))
        assert result.outcome is MoveOutcome.ACCEPTED
        assert result.message == MOVE_ACCEPTED
        assert sample_game.board.is_empty(Cell(0, 2))

    def test_rejects_clearing_prefilled(self, sample_game):
        result = sample_game.make_move(ClearMove(Cell(0, 0)))
        assert result.outcome is MoveOutcome.REJECTED
        assert result.message == "Invalid move. A1 is pre-filled."

    def test_clearing_already_empty_cell_reports_status(self, sample_game):
        result = sample_game.make_move(ClearMove(Cell(0, 2)))  # A3 starts empty
        assert result.outcome is MoveOutcome.REJECTED
        assert result.message == "Cell A3 is already empty."
        assert sample_game.board.is_empty(Cell(0, 2))


class TestCheck:
    def test_clean_board_reports_no_violations(self, sample_game):
        result = sample_game.make_move(CheckMove())
        assert result.outcome is MoveOutcome.CHECK_OK
        assert result.message == "No rule violations detected."

    def test_row_violation_reported(self, sample_game):
        sample_game.make_move(PlaceMove(Cell(0, 2), 3))  # A3=3 duplicates A2=3
        result = sample_game.make_move(CheckMove())
        assert result.outcome is MoveOutcome.CHECK_FAILED
        assert result.message == "Number 3 already exists in Row A."

    def test_column_violation_reported(self, sample_game):
        sample_game.make_move(PlaceMove(Cell(2, 0), 5))  # C1=5 duplicates A1=5
        result = sample_game.make_move(CheckMove())
        assert result.outcome is MoveOutcome.CHECK_FAILED
        assert result.message == "Number 5 already exists in Column 1."

    def test_subgrid_violation_reported(self, sample_game):
        sample_game.make_move(PlaceMove(Cell(0, 2), 9))  # A3=9 collides with C2=9 in the same block
        result = sample_game.make_move(CheckMove())
        assert result.outcome is MoveOutcome.CHECK_FAILED
        assert result.message == "Number 9 already exists in the same 3\u00d73 subgrid."


class TestHint:
    def test_hint_fills_an_empty_cell_with_correct_value(self, sample_game):
        result = sample_game.make_move(HintMove())
        assert result.outcome is MoveOutcome.ACCEPTED
        assert result.message.startswith("Hint: Cell ")
        assert "=" in result.message

    def test_hint_on_fully_solved_board_says_none_available(self, solution_grid):
        game = Game(
            puzzle=Board.from_grid(solution_grid),
            solution=Board.from_grid(solution_grid),
            rng=random.Random(0),
        )
        result = game.make_move(HintMove())
        assert result.outcome is MoveOutcome.REJECTED
        assert "no empty cells" in result.message.lower()

    def test_hint_skips_cell_whose_solution_value_would_conflict(self, solution_grid):
        grid = [row[:] for row in solution_grid]
        grid[0][0] = 0
        grid[0][1] = 0
        grid[0][2] = 0
        game = Game(
            puzzle=Board.from_grid(grid),
            solution=Board.from_grid(solution_grid),
            rng=random.Random(0),
        )
        game.make_move(PlaceMove(Cell(0, 2), 5))

        messages = []
        for _ in range(5):
            result = game.make_move(HintMove())
            messages.append(result.message)
            assert game.board.is_empty(Cell(0, 0))
            if "no compatible hint" in result.message.lower():
                break

        assert any("no compatible hint" in m.lower() for m in messages)

    def test_hint_falls_back_to_on_demand_solve_when_stored_solution_conflicts(
        self, solution_grid
    ):
        puzzle_grid = [row[:] for row in solution_grid]
        puzzle_grid[8][3] = 0  # I4, real answer = 2
        # Stored solution disagrees at I4 (9, which already appears in row I).
        wrong_solution_grid = [row[:] for row in solution_grid]
        wrong_solution_grid[8][3] = 9
        game = Game(
            puzzle=Board.from_grid(puzzle_grid),
            solution=Board.from_grid(wrong_solution_grid),
            rng=random.Random(0),
        )
        result = game.make_move(HintMove())
        assert "no compatible hint" not in result.message.lower()
        assert game.board.get(Cell(8, 3)) == 2


class TestQuit:
    def test_quit_sets_status_to_quit(self, sample_game):
        result = sample_game.make_move(QuitMove())
        assert result.outcome is MoveOutcome.QUIT
        assert sample_game.status is GameStatus.QUIT
        assert "goodbye" in result.message.lower() or "bye" in result.message.lower()


class TestCompletion:
    def test_placing_last_correct_value_wins_game(self, solution_grid):
        grid = [row[:] for row in solution_grid]
        grid[8][3] = 0  # blank I4
        game = Game(
            puzzle=Board.from_grid(grid),
            solution=Board.from_grid(solution_grid),
            rng=random.Random(0),
        )
        result = game.make_move(PlaceMove(Cell(8, 3), 2))
        assert result.outcome is MoveOutcome.WON
        assert game.status is GameStatus.WON
        assert result.message == MOVE_ACCEPTED

    def test_completing_grid_with_violations_does_not_win(self, solution_grid):
        grid = [row[:] for row in solution_grid]
        grid[8][3] = 0
        game = Game(
            puzzle=Board.from_grid(grid),
            solution=Board.from_grid(solution_grid),
            rng=random.Random(0),
        )
        result = game.make_move(PlaceMove(Cell(8, 3), 5))  # wrong value, creates a column dup
        assert result.outcome is MoveOutcome.ACCEPTED
        assert game.status is GameStatus.IN_PROGRESS
        assert result.message == MOVE_ACCEPTED


class TestOwnershipIsolation:
    """Game must own its board state independently from the objects passed in."""

    def test_mutating_original_puzzle_after_creation_has_no_effect(self, solution_grid):
        grid = [row[:] for row in solution_grid]
        grid[8][3] = 0
        puzzle = Board.from_grid(grid)
        solution = Board.from_grid(solution_grid)
        game = Game(puzzle=puzzle, solution=solution, rng=random.Random(0))

        # Mutate the original puzzle object after Game creation
        puzzle.set(Cell(8, 3), 9)

        # Game's board must still show the cell as empty
        assert game.board.is_empty(Cell(8, 3))

    def test_mutating_original_solution_after_creation_has_no_effect(self, solution_grid):
        grid = [row[:] for row in solution_grid]
        grid[8][3] = 0
        original_solution = Board.from_grid(solution_grid)
        correct_value = original_solution.get(Cell(8, 3))  # 2
        game = Game(puzzle=Board.from_grid(grid), solution=original_solution, rng=random.Random(0))

        # Change the original solution's internal grid after Game creation
        original_solution._grid[8][3] = 99

        # Game's solution must still hold the original correct value
        assert game.solution.get(Cell(8, 3)) == correct_value

    def test_game_board_mutations_do_not_affect_original_puzzle(self, solution_grid):
        grid = [row[:] for row in solution_grid]
        grid[8][3] = 0
        puzzle = Board.from_grid(grid)
        game = Game(puzzle=puzzle, solution=Board.from_grid(solution_grid), rng=random.Random(0))

        game.make_move(PlaceMove(Cell(8, 3), 2))

        assert puzzle.is_empty(Cell(8, 3))
