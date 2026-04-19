"""Shared test fixtures: boards, grids, and game instances."""
import random
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

_PUZZLE_GRID = [
    [5, 3, 0, 0, 7, 0, 0, 0, 0],
    [6, 0, 0, 1, 9, 5, 0, 0, 0],
    [0, 9, 8, 0, 0, 0, 0, 6, 0],
    [8, 0, 0, 0, 6, 0, 0, 0, 3],
    [4, 0, 0, 8, 0, 3, 0, 0, 1],
    [7, 0, 0, 0, 2, 0, 0, 0, 6],
    [0, 6, 0, 0, 0, 0, 2, 8, 0],
    [0, 0, 0, 4, 1, 9, 0, 0, 5],
    [0, 0, 0, 0, 8, 0, 0, 7, 9],
]

_SOLUTION_GRID = [
    [5, 3, 4, 6, 7, 8, 9, 1, 2],
    [6, 7, 2, 1, 9, 5, 3, 4, 8],
    [1, 9, 8, 3, 4, 2, 5, 6, 7],
    [8, 5, 9, 7, 6, 1, 4, 2, 3],
    [4, 2, 6, 8, 5, 3, 7, 9, 1],
    [7, 1, 3, 9, 2, 4, 8, 5, 6],
    [9, 6, 1, 5, 3, 7, 2, 8, 4],
    [2, 8, 7, 4, 1, 9, 6, 3, 5],
    [3, 4, 5, 2, 8, 6, 1, 7, 9],
]

# Second puzzle/solution pair used for long-running e2e coverage.
# Solution is a canonical base-pattern Sudoku; the puzzle blanks every
# other column, giving 40 blanks on an independent board layout.
_ALT_SOLUTION_GRID = [
    [1, 2, 3, 4, 5, 6, 7, 8, 9],
    [4, 5, 6, 7, 8, 9, 1, 2, 3],
    [7, 8, 9, 1, 2, 3, 4, 5, 6],
    [2, 3, 1, 5, 6, 4, 8, 9, 7],
    [5, 6, 4, 8, 9, 7, 2, 3, 1],
    [8, 9, 7, 2, 3, 1, 5, 6, 4],
    [3, 1, 2, 6, 4, 5, 9, 7, 8],
    [6, 4, 5, 9, 7, 8, 3, 1, 2],
    [9, 7, 8, 3, 1, 2, 6, 4, 5],
]

_ALT_PUZZLE_GRID = [
    [1, 0, 3, 0, 5, 0, 7, 0, 9],
    [0, 5, 0, 7, 0, 9, 0, 2, 0],
    [7, 0, 9, 0, 2, 0, 4, 0, 6],
    [0, 3, 0, 5, 0, 4, 0, 9, 0],
    [5, 0, 4, 0, 9, 0, 2, 0, 1],
    [0, 9, 0, 2, 0, 1, 0, 6, 0],
    [3, 0, 2, 0, 4, 0, 9, 0, 8],
    [0, 4, 0, 9, 0, 8, 0, 1, 0],
    [9, 0, 8, 0, 1, 0, 6, 0, 5],
]


@pytest.fixture
def puzzle_grid():
    return [row[:] for row in _PUZZLE_GRID]


@pytest.fixture
def solution_grid():
    return [row[:] for row in _SOLUTION_GRID]


@pytest.fixture
def alt_puzzle_grid():
    return [row[:] for row in _ALT_PUZZLE_GRID]


@pytest.fixture
def alt_solution_grid():
    return [row[:] for row in _ALT_SOLUTION_GRID]


@pytest.fixture
def sample_game(puzzle_grid, solution_grid):
    from sudoku.board import Board
    from sudoku.game import Game

    return Game(
        puzzle=Board.from_grid(puzzle_grid),
        solution=Board.from_grid(solution_grid),
        rng=random.Random(0),
    )
